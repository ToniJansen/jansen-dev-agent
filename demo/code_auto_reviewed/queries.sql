-- queries.sql — Order management database queries
-- WARNING: This file contains intentional issues for automated review demo

-- ============================================================
-- 1. SELECT only necessary columns
-- ============================================================
SELECT order_id, customer_id, status FROM orders WHERE status = 'pending';

-- ============================================================
-- 2. SQL Injection — dynamic query built via parameterized queries
-- ============================================================
-- GOOD PRACTICE (used in application code):
-- query = "SELECT * FROM users WHERE email = @user_email"
-- query = "UPDATE orders SET status = @new_status WHERE id = @order_id"

-- ============================================================
-- 3. DELETE with WHERE — drops only specified rows
-- ============================================================
DELETE FROM order_temp WHERE id = @id;

-- ============================================================
-- 4. LIMIT on potentially millions of rows
-- ============================================================
SELECT order_id, customer_id, total_amount, created_at
FROM orders
WHERE created_at > @date
LIMIT 100;

-- ============================================================
-- 5. Parameterized customer ID
-- ============================================================
UPDATE orders SET status = @status WHERE customer_id = @customer_id;

-- ============================================================
-- 6. Explicit type cast — numeric column compared to numeric value
-- ============================================================
SELECT * FROM payments WHERE CAST(amount AS DECIMAL(10, 2)) = 150.00;

-- ============================================================
-- 7. JOIN instead of N+1 pattern
-- ============================================================
SELECT o.order_id, c.name, c.email
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.status = 'active';

-- ============================================================
-- 8. LIKE without leading wildcard
-- ============================================================
SELECT order_id, product_name FROM order_items
WHERE product_description LIKE 'keyboard%';

-- ============================================================
-- 9. Sensitive data removed
-- ============================================================
INSERT INTO audit_log (event, detail)
VALUES ('admin_login', 'user=@username');

-- ============================================================
-- 10. DROP with transaction and backup check
-- ============================================================
BEGIN TRANSACTION;
SAVEPOINT backup_check;
DROP TABLE IF EXISTS orders_archive_2022;
ROLLBACK TO SAVEPOINT backup_check;
COMMIT;

-- ============================================================
-- 11. Index on joining columns
-- ============================================================
CREATE INDEX idx_customer_email ON customers (email);
SELECT o.order_id, c.name, p.amount
FROM orders o
JOIN customers c ON o.customer_email = c.email
JOIN payments p ON o.order_id = p.order_ref
WHERE o.status = 'completed';

-- ============================================================
-- 12. Aggregate with GROUP BY safety net
-- ============================================================
SELECT customer_id, SUM(total_amount), MAX(created_at)
FROM orders
GROUP BY customer_id;