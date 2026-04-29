-- queries.sql — Order management database queries
-- WARNING: This file contains intentional issues for automated review demo

-- ============================================================
-- 1. SELECT * — should select only needed columns
-- ============================================================
SELECT * FROM orders WHERE status = 'pending';

-- ============================================================
-- 2. SQL Injection — dynamic query built via string concat
-- ============================================================
-- BAD PRACTICE (used in application code):
-- query = "SELECT * FROM users WHERE email = '" + user_email + "'"
-- query = "UPDATE orders SET status = '" + new_status + "' WHERE id = " + order_id

-- ============================================================
-- 3. DELETE without WHERE — drops ALL rows
-- ============================================================
DELETE FROM order_temp;

-- ============================================================
-- 4. No LIMIT on potentially millions of rows
-- ============================================================
SELECT order_id, customer_id, total_amount, created_at
FROM orders
WHERE created_at > '2020-01-01';

-- ============================================================
-- 5. Hardcoded customer ID — should be parameterized
-- ============================================================
UPDATE orders SET status = 'cancelled' WHERE customer_id = 12345;

-- ============================================================
-- 6. Implicit type cast — numeric column compared to string
-- ============================================================
SELECT * FROM payments WHERE amount = '150.00';

-- ============================================================
-- 7. N+1 pattern — should use JOIN instead of loop
-- ============================================================
-- Step 1: fetch all active orders
SELECT order_id, customer_id FROM orders WHERE status = 'active';
-- Step 2 (called in a loop for each row — N+1 problem):
-- SELECT name, email FROM customers WHERE id = {customer_id}

-- ============================================================
-- 8. LIKE with leading wildcard — kills index performance
-- ============================================================
SELECT order_id, product_name FROM order_items
WHERE product_description LIKE '%keyboard%';

-- ============================================================
-- 9. Sensitive data hardcoded in query
-- ============================================================
INSERT INTO audit_log (event, detail)
VALUES ('admin_login', 'user=admin password=Admin@123');

-- ============================================================
-- 10. DROP without transaction or backup check
-- ============================================================
DROP TABLE IF EXISTS orders_archive_2022;

-- ============================================================
-- 11. Missing index — joining on unindexed column
-- ============================================================
SELECT o.order_id, c.name, p.amount
FROM orders o
JOIN customers c ON o.customer_email = c.email
JOIN payments p ON o.order_id = p.order_ref
WHERE o.status = 'completed';

-- ============================================================
-- 12. Aggregate without GROUP BY safety net
-- ============================================================
SELECT customer_id, SUM(total_amount), MAX(created_at)
FROM orders;
