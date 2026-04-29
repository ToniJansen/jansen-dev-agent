CREATE INDEX idx_orders_status ON orders (status);
CREATE INDEX idx_orders_customer_email ON orders (customer_email);

SELECT order_id, status FROM orders WHERE status = 'pending';

SELECT order_id, customer_id, total_amount, created_at FROM orders WHERE created_at > '2020-01-01' LIMIT 100;

DELETE FROM order_temp WHERE id = ?;

UPDATE orders SET status = 'cancelled' WHERE customer_id = ?;

SELECT * FROM payments WHERE amount = 150.00;

SELECT o.order_id, c.name, c.email FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.status = 'active';

SELECT order_id, product_name FROM order_items WHERE product_description LIKE '%keyboard%';

INSERT INTO audit_log (event, detail) VALUES ('admin_login', ?);

BEGIN TRANSACTION; DROP TABLE IF EXISTS orders_archive_2022; COMMIT;

SELECT o.order_id, c.name, p.amount FROM orders o JOIN customers c ON o.customer_email = c.email JOIN payments p ON o.order_id = p.order_ref WHERE o.status = 'completed';

SELECT customer_id, SUM(total_amount), MAX(created_at) FROM orders GROUP BY customer_id;