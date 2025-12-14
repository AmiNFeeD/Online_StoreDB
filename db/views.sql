CREATE OR REPLACE VIEW order_summary AS
SELECT
    o.order_id,
    o.user_id,
    u.full_name,
    o.total_amount,
    o.status,
    o.created_at
FROM orders o
JOIN users u ON u.user_id = o.user_id;


CREATE OR REPLACE VIEW cart_detailed AS
SELECT
    ci.user_id,
    p.product_id,
    p.name,
    p.price,
    ci.quantity,
    (ci.quantity * p.price) AS line_total
FROM cart_items ci
JOIN products p ON p.product_id = ci.product_id;


CREATE OR REPLACE VIEW top_selling_products AS
SELECT
    p.product_id,
    p.name,
    SUM(oi.quantity) AS total_sold
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name
ORDER BY total_sold DESC;


CREATE OR REPLACE VIEW revenue_by_month AS
SELECT
    DATE_TRUNC('month', created_at) AS month,
    SUM(total_amount) AS revenue
FROM orders
WHERE status IN ('paid', 'shipped', 'completed')
GROUP BY month
ORDER BY month;

