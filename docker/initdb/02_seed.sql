-- Demo rows so a DB browser has something to show immediately.

-- 1:1: one user with one profile
INSERT INTO users (email) VALUES ('alice@example.com');
INSERT INTO profiles (user_id, full_name, bio)
VALUES (1, 'Alice Example', 'Demo user for the 1:1 relationship.');

-- 1:N: one customer with three orders
INSERT INTO customers (email, name) VALUES ('acme@example.com', 'ACME Corp');
INSERT INTO orders (customer_id, status, total_cents) VALUES
    (1, 'open', 1999),
    (1, 'shipped', 4250),
    (1, 'delivered', 12900);
