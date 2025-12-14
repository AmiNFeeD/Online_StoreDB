CREATE INDEX idx_products_name ON products (name);

CREATE INDEX idx_products_category ON products (category_id);

CREATE INDEX idx_orders_user_created_at ON orders (user_id, created_at);

CREATE INDEX idx_order_items_product ON order_items (product_id);

CREATE INDEX idx_cart_items_user ON cart_items (user_id);