BEGIN;

INSERT INTO orders (user_id, shipping_address_id, status, total_amount)
VALUES (1, 1, 'pending', 0)
RETURNING order_id;

INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT 42 AS order_id,
       ci.product_id,
       ci.quantity,
       p.price
FROM cart_items ci
JOIN products p ON ci.product_id = p.product_id
WHERE ci.user_id = 1;

UPDATE products p
SET stock_qty = stock_qty - ci.quantity
FROM cart_items ci
WHERE p.product_id = ci.product_id
  AND ci.user_id = 1;

UPDATE orders o
SET total_amount = (
    SELECT SUM(oi.quantity * oi.unit_price)
    FROM order_items oi
    WHERE oi.order_id = o.order_id
)
WHERE o.order_id = 42;

DELETE FROM cart_items
WHERE user_id = 1;

COMMIT;