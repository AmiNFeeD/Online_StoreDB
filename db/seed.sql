INSERT INTO users (email, password_hash, full_name, role)
VALUES
('alice@example.com', 'hash1', 'Alice Smith', 'customer'),
('bob@example.com',   'hash2', 'Bob Admin',   'admin');

INSERT INTO categories (name, description) VALUES
('Electronics', 'Phones, laptops, gadgets'),
('Books', 'Fiction and non-fiction'),
('Clothing', 'T-shirts, hoodies, etc.');

INSERT INTO products (category_id, name, description, price, stock_qty, image_url)
VALUES
(1, 'Smartphone X', 'Nice phone', 500.00, 10, 'images/phone.png'),
(1, 'Laptop Y',     'Light laptop', 900.00, 5,  'images/laptop.png'),
(2, 'Novel Z',      'Cool story',   15.00, 100, 'images/book.png');

INSERT INTO users (email, password_hash, full_name, role)
VALUES (
  'anfd@mail.fun',
  'scrypt:32768:8:1$wR69POotq5vbvlsn$8b0d6e4c92c183073361779345e0b62da1608acc6d03898551c41266ed1543ffd91a66628b8cb991eced3c7d67786b337783593ad8e57e941d674c5abc4f4d57',
  'Master Admin',
  'admin'
)
ON CONFLICT (email) DO UPDATE
SET role = EXCLUDED.role,
    full_name = EXCLUDED.full_name;
