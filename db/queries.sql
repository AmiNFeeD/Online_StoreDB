SELECT p.product_id, p.name, p.price, c.name AS category
FROM products p
LEFT JOIN categories c ON p.category_id = c.category_id
ORDER BY p.product_id;
SELECT o.order_id, o.status, o.total_amount, o.created_at
FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE u.email = 'alice@example.com'
ORDER BY o.created_at DESC;
SELECT p.name, ci.quantity, p.price, (ci.quantity * p.price) AS line_total
FROM cart_items ci
JOIN products p ON ci.product_id = p.product_id
WHERE ci.user_id = 1;