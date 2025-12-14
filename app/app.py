from functools import wraps
import os
import time
from werkzeug.utils import secure_filename

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from werkzeug.security import generate_password_hash, check_password_hash

from .db import get_connection
from . import config


app = Flask(__name__)
app.secret_key = config.SECRET_KEY


UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS



def get_user_id():
    return session.get("user_id")


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not get_user_id():
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped

def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if session.get("user_role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("index"))
        return view_func(*args, **kwargs)
    return wrapped



@app.route("/")
def index():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
                SELECT p.product_id,
                       p.name,
                       p.price,
                       p.image_url,
                       p.stock_qty,
                       c.name AS category
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                WHERE p.is_active = TRUE
                ORDER BY p.product_id;
                """)
    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", products=products)


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.*, c.name AS category
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE p.product_id = %s;
    """, (product_id,))
    product = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("product_detail.html", product=product)



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].strip()
        full_name = request.form["full_name"].strip()
        password = request.form["password"]

        pw_hash = generate_password_hash(password)

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO users (email, password_hash, full_name, role)
                VALUES (%s, %s, %s, 'customer')
                RETURNING user_id;
            """, (email, pw_hash, full_name))
            user_id = cur.fetchone()["user_id"]
            conn.commit()
        except Exception:
            conn.rollback()
            cur.close()
            conn.close()
            flash("Registration failed (maybe email already used).", "danger")
            return redirect(url_for("register"))

        cur.close()
        conn.close()

        session["user_id"] = user_id
        session["user_role"] = "customer"
        flash("Registration successful.", "success")
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id, password_hash, role
            FROM users
            WHERE email = %s;
        """, (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["user_id"]
            session["user_role"] = user["role"]
            flash("Logged in successfully.", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("index"))



@app.route("/cart")
@login_required
def cart():
    user_id = get_user_id()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.product_id,
               p.name,
               ci.quantity,
               p.price,
               p.stock_qty,
               (ci.quantity * p.price) AS line_total
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.product_id
        WHERE ci.user_id = %s;
    """, (user_id,))
    items = cur.fetchall()
    total = sum(item["line_total"] for item in items) if items else 0
    cur.close()
    conn.close()
    return render_template("cart.html", items=items, total=total)

@app.route("/cart/update/<int:product_id>", methods=["POST"])
@login_required
def update_cart_item(product_id):
    user_id = get_user_id()
    qty = int(request.form.get("quantity", 1))

    conn = get_connection()
    cur = conn.cursor()

    if qty <= 0:
        # treat 0 or negative as remove
        cur.execute("""
            DELETE FROM cart_items
            WHERE user_id = %s AND product_id = %s;
        """, (user_id, product_id))
        flash("Item removed from cart.", "info")
    else:
        cur.execute("""
            UPDATE cart_items
            SET quantity = %s
            WHERE user_id = %s AND product_id = %s;
        """, (qty, user_id, product_id))
        flash("Cart updated.", "success")

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("cart"))


@app.route("/cart/remove/<int:product_id>", methods=["POST"])
@login_required
def remove_from_cart(product_id):
    user_id = get_user_id()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM cart_items
        WHERE user_id = %s AND product_id = %s;
    """, (user_id, product_id))
    conn.commit()
    cur.close()
    conn.close()
    flash("Item removed from cart.", "info")
    return redirect(url_for("cart"))

@app.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    user_id = get_user_id()
    qty = int(request.form.get("quantity", 1))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO cart_items (user_id, product_id, quantity)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id, product_id)
        DO UPDATE SET quantity = cart_items.quantity + EXCLUDED.quantity;
    """, (user_id, product_id, qty))
    conn.commit()
    cur.close()
    conn.close()
    flash("Item added to cart.", "success")
    return redirect(url_for("cart"))

@app.route("/cart/increase/<int:product_id>", methods=["POST"])
@login_required
def increase_cart_item(product_id):
    user_id = get_user_id()

    conn = get_connection()
    cur = conn.cursor()

    # Increase quantity by 1 (checking stock)
    cur.execute("""
        UPDATE cart_items ci
        SET quantity = quantity + 1
        FROM products p
        WHERE ci.user_id = %s
          AND ci.product_id = %s
          AND ci.quantity < p.stock_qty;
    """, (user_id, product_id))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("cart"))


@app.route("/cart/decrease/<int:product_id>", methods=["POST"])
@login_required
def decrease_cart_item(product_id):
    user_id = get_user_id()

    conn = get_connection()
    cur = conn.cursor()

    # Reduce quantity by 1
    cur.execute("""
        UPDATE cart_items
        SET quantity = quantity - 1
        WHERE user_id = %s AND product_id = %s;
    """, (user_id, product_id))

    # Remove if quantity is now 0
    cur.execute("""
        DELETE FROM cart_items
        WHERE user_id = %s AND product_id = %s AND quantity <= 0;
    """, (user_id, product_id))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("cart"))


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    user_id = get_user_id()
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "GET":
        # Show cart summary before confirming
        cur.execute("""
            SELECT p.product_id,
                   p.name,
                   ci.quantity,
                   p.price,
                   (ci.quantity * p.price) AS line_total
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.product_id
            WHERE ci.user_id = %s;
        """, (user_id,))
        items = cur.fetchall()
        total = sum(item["line_total"] for item in items) if items else 0

        cur.close()
        conn.close()
        return render_template("checkout.html", items=items, total=total)

    try:
        # 0) Check stock BEFORE creating order
        cur.execute("""
            SELECT p.product_id,
                   p.name,
                   p.stock_qty,
                   ci.quantity
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.product_id
            WHERE ci.user_id = %s;
        """, (user_id,))
        rows = cur.fetchall()

        if not rows:
            conn.rollback()
            cur.close()
            conn.close()
            flash("Your cart is empty.", "warning")
            return redirect(url_for("cart"))

        insufficient = [
            r for r in rows
            if r["stock_qty"] < r["quantity"]
        ]

        if insufficient:
            details = ", ".join(
                f"{r['name']} (available {r['stock_qty']}, in cart {r['quantity']})"
                for r in insufficient
            )
            conn.rollback()
            cur.close()
            conn.close()
            flash(f"Not enough stock for: {details}", "danger")
            return redirect(url_for("cart"))

        cur.execute("""
            INSERT INTO orders (user_id, status, total_amount)
            VALUES (%s, 'pending', 0)
            RETURNING order_id;
        """, (user_id,))
        order_id = cur.fetchone()["order_id"]

        cur.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, unit_price)
            SELECT %s, ci.product_id, ci.quantity, p.price
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.product_id
            WHERE ci.user_id = %s;
        """, (order_id, user_id))

        cur.execute("""
            UPDATE products p
            SET stock_qty = stock_qty - ci.quantity
            FROM cart_items ci
            WHERE p.product_id = ci.product_id
              AND ci.user_id = %s;
        """, (user_id,))

        cur.execute("""
            UPDATE orders o
            SET total_amount = (
                    SELECT COALESCE(SUM(oi.quantity * oi.unit_price), 0)
                    FROM order_items oi
                    WHERE oi.order_id = o.order_id
                ),
                status = 'paid'
            WHERE o.order_id = %s;
        """, (order_id,))

        cur.execute("DELETE FROM cart_items WHERE user_id = %s;", (user_id,))

        conn.commit()
    except Exception:
        conn.rollback()
        cur.close()
        conn.close()
        raise

    cur.close()
    conn.close()
    flash("Order placed successfully.", "success")
    return redirect(url_for("orders"))

@app.route("/orders")
@login_required
def orders():
    user_id = get_user_id()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT order_id, total_amount, status, created_at
        FROM orders
        WHERE user_id = %s
        ORDER BY created_at DESC;
    """, (user_id,))
    orders = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("orders.html", orders=orders)

@app.route("/orders/<int:order_id>")
@login_required
def order_detail(order_id):
    user_id = get_user_id()
    conn = get_connection()
    cur = conn.cursor()

    # Load order, but only if it belongs to the current user
    cur.execute("""
        SELECT order_id, user_id, total_amount, status, created_at
        FROM orders
        WHERE order_id = %s AND user_id = %s;
    """, (order_id, user_id))
    order = cur.fetchone()

    if not order:
        cur.close()
        conn.close()
        flash("Order not found.", "danger")
        return redirect(url_for("orders"))

    cur.execute("""
        SELECT oi.product_id,
               p.name AS product_name,
               oi.quantity,
               oi.unit_price,
               (oi.quantity * oi.unit_price) AS line_total
        FROM order_items oi
        JOIN products p ON p.product_id = oi.product_id
        WHERE oi.order_id = %s;
    """, (order_id,))
    items = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("order_detail.html", order=order, items=items)
@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template("admin/dashboard.html")

@app.route("/admin/products")
@admin_required
def admin_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT product_id, name, price, stock_qty, is_active
        FROM products
        ORDER BY product_id;
    """)
    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("admin/products.html", products=products)

@app.route("/admin/products/add", methods=["GET", "POST"])
@admin_required
def admin_add_product():
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        name = request.form["name"].strip()
        price = request.form["price"]
        stock = request.form["stock"]
        description = request.form["description"]

        category_id_raw = request.form.get("category_id")
        category_id = int(category_id_raw) if category_id_raw else None

        image_url = request.form["image_url"].strip() or None

        file = request.files.get("image_file")
        if file and file.filename:
            if not allowed_file(file.filename):
                flash("Invalid image type. Allowed: png, jpg, jpeg, gif, webp", "danger")
                cur.close()
                conn.close()
                return redirect(url_for("admin_add_product"))

            filename = secure_filename(file.filename)
            base, ext = os.path.splitext(filename)
            unique_name = f"{base}_{int(time.time())}{ext}"

            save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
            file.save(save_path)

            image_url = f"uploads/{unique_name}"

        cur.execute("""
            INSERT INTO products (category_id, name, price, stock_qty, image_url, description, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, TRUE);
        """, (category_id, name, price, stock, image_url, description))
        conn.commit()
        cur.close()
        conn.close()

        flash("Product added.", "success")
        return redirect(url_for("admin_products"))

    cur.execute("SELECT category_id, name FROM categories ORDER BY name;")
    categories = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("admin/add_product.html", categories=categories)

@app.route("/admin/products/<int:product_id>/delete", methods=["POST"])
@admin_required
def admin_delete_product(product_id):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT 1
            FROM order_items
            WHERE product_id = %s
            LIMIT 1;
        """, (product_id,))
        used_in_orders = cur.fetchone()

        if used_in_orders:
            flash("Cannot delete product — it appears in past orders. You can deactivate it instead.", "danger")
            return redirect(url_for("admin_products"))

        cur.execute("DELETE FROM cart_items WHERE product_id = %s;", (product_id,))

        cur.execute("DELETE FROM products WHERE product_id = %s;", (product_id,))
        conn.commit()

        flash("Product deleted successfully.", "success")

    except Exception as e:
        conn.rollback()
        flash("Error deleting product.", "danger")

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("admin_products"))

@app.route("/admin/products/<int:product_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_product(product_id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        name = request.form["name"].strip()
        price = request.form["price"]
        stock = request.form["stock"]
        description = request.form["description"]
        is_active = True if request.form.get("is_active") == "on" else False

        category_id_raw = request.form.get("category_id")
        category_id = int(category_id_raw) if category_id_raw else None

        current_image_url = request.form.get("current_image_url") or None
        image_url = request.form["image_url"].strip() or current_image_url

        file = request.files.get("image_file")
        if file and file.filename:
            if not allowed_file(file.filename):
                flash("Invalid image type. Allowed: png, jpg, jpeg, gif, webp", "danger")
                cur.close()
                conn.close()
                return redirect(url_for("admin_edit_product", product_id=product_id))

            filename = secure_filename(file.filename)
            base, ext = os.path.splitext(filename)
            unique_name = f"{base}_{int(time.time())}{ext}"

            save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
            file.save(save_path)

            image_url = f"uploads/{unique_name}"

        cur.execute("""
            UPDATE products
            SET category_id = %s,
                name = %s,
                price = %s,
                stock_qty = %s,
                image_url = %s,
                description = %s,
                is_active = %s
            WHERE product_id = %s;
        """, (category_id, name, price, stock, image_url, description, is_active, product_id))
        conn.commit()
        cur.close()
        conn.close()

        flash("Product updated.", "success")
        return redirect(url_for("admin_products"))

    cur.execute("SELECT * FROM products WHERE product_id = %s;", (product_id,))
    product = cur.fetchone()

    cur.execute("SELECT category_id, name FROM categories ORDER BY name;")
    categories = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("admin/edit_product.html", product=product, categories=categories)


@app.route("/admin/orders")
@admin_required
def admin_orders():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT o.order_id,
               u.full_name,
               o.total_amount,
               o.status,
               o.created_at
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        ORDER BY o.created_at DESC;
    """)
    orders = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("admin/orders.html", orders=orders)


@app.route("/admin/orders/<int:order_id>", methods=["GET", "POST"])
@admin_required
def admin_order_detail(order_id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        new_status = request.form["status"]
        cur.execute("""
            UPDATE orders
            SET status = %s
            WHERE order_id = %s;
        """, (new_status, order_id))
        conn.commit()
        flash("Order status updated.", "success")

    cur.execute("""
        SELECT o.order_id,
               o.user_id,
               u.full_name,
               u.email,
               o.total_amount,
               o.status,
               o.created_at
        FROM orders o
        JOIN users u ON u.user_id = o.user_id
        WHERE o.order_id = %s;
    """, (order_id,))
    order = cur.fetchone()

    cur.execute("""
        SELECT oi.product_id,
               p.name AS product_name,
               oi.quantity,
               oi.unit_price,
               (oi.quantity * oi.unit_price) AS line_total
        FROM order_items oi
        JOIN products p ON p.product_id = oi.product_id
        WHERE oi.order_id = %s;
    """, (order_id,))
    items = cur.fetchall()

    cur.close()
    conn.close()

    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for("admin_orders"))

    all_statuses = ["pending", "paid", "shipped", "completed", "cancelled"]

    return render_template(
        "admin/order_detail.html",
        order=order,
        items=items,
        all_statuses=all_statuses,
    )
@app.route("/admin/stats")
@admin_required
def admin_stats():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS cnt FROM users;")
    total_users = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) AS cnt FROM orders;")
    total_orders = cur.fetchone()["cnt"]

    cur.execute("""
        SELECT COALESCE(SUM(total_amount), 0) AS revenue
        FROM orders
        WHERE status IN ('paid', 'shipped', 'completed');
    """)
    total_revenue = cur.fetchone()["revenue"]


    cur.execute("""
        SELECT product_id, name, total_sold
        FROM top_selling_products
        ORDER BY total_sold DESC
        LIMIT 5;
    """)
    top_products = cur.fetchall()

    cur.execute("""
        SELECT month, revenue
        FROM revenue_by_month;
    """)
    revenue_by_month = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "admin/stats.html",
        total_users=total_users,
        total_orders=total_orders,
        total_revenue=total_revenue,
        top_products=top_products,
        revenue_by_month=revenue_by_month,
    )

@app.route("/admin/categories")
@admin_required
def admin_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT category_id, name, description
        FROM categories
        ORDER BY category_id;
    """)
    categories = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("admin/categories.html", categories=categories)


@app.route("/admin/categories/add", methods=["GET", "POST"])
@admin_required
def admin_add_category():
    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form["description"].strip() or None

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO categories (name, description)
            VALUES (%s, %s);
        """, (name, description))
        conn.commit()
        cur.close()
        conn.close()

        flash("Category created.", "success")
        return redirect(url_for("admin_categories"))

    return render_template("admin/add_category.html")


@app.route("/admin/categories/<int:category_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_category(category_id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form["description"].strip() or None

        cur.execute("""
            UPDATE categories
            SET name = %s,
                description = %s
            WHERE category_id = %s;
        """, (name, description, category_id))
        conn.commit()
        cur.close()
        conn.close()

        flash("Category updated.", "success")
        return redirect(url_for("admin_categories"))

    cur.execute("""
        SELECT category_id, name, description
        FROM categories
        WHERE category_id = %s;
    """, (category_id,))
    category = cur.fetchone()
    cur.close()
    conn.close()

    if not category:
        flash("Category not found.", "danger")
        return redirect(url_for("admin_categories"))

    return render_template("admin/edit_category.html", category=category)


@app.route("/admin/categories/<int:category_id>/delete", methods=["POST"])
@admin_required
def admin_delete_category(category_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM categories WHERE category_id = %s;", (category_id,))
        conn.commit()
        flash("Category deleted.", "success")
    except Exception:
        conn.rollback()
        flash("Cannot delete category (probably used by products).", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("admin_categories"))


if __name__ == "__main__":
    app.run(debug=True)
