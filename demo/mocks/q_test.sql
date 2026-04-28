-- q_test.sql — order queries mock

-- CRITICAL: DELETE without WHERE (drops all rows)
DELETE FROM order_temp;

-- CRITICAL: hardcoded sensitive value in INSERT
INSERT INTO audit_log (event, user, password)
VALUES ('login', 'admin', 'Admin@2024');

-- CRITICAL: SQL injection via string concat (shown in comment pattern)
-- query = "SELECT * FROM users WHERE email = '" + email + "'"

-- WARNING: SELECT * with no LIMIT on large table
SELECT * FROM orders WHERE created_at > '2020-01-01';

-- WARNING: implicit type cast (amount is NUMERIC, compared to VARCHAR)
SELECT * FROM payments WHERE amount = '99.90';

-- WARNING: LIKE with leading wildcard kills index
SELECT order_id FROM order_items WHERE description LIKE '%keyboard%';

-- WARNING: N+1 — should JOIN instead of loop
SELECT order_id, customer_id FROM orders WHERE status = 'active';
-- app loops: SELECT * FROM customers WHERE id = {customer_id}

-- INFO: DROP without transaction guard
DROP TABLE IF EXISTS orders_backup_2023;
