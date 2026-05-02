-- orders_report.sql — daily reporting queries

-- BUG: missing parentheses — AND binds before OR, wrong rows returned
SELECT * FROM orders
WHERE status = 'active' OR status = 'pending' AND created_at > NOW() - INTERVAL '7 days';

-- CRITICAL: dynamic SQL with injection via concatenation
EXECUTE 'SELECT * FROM ' || table_name || ' WHERE customer_id = ' || customer_id;

-- BUG: HAVING without GROUP BY — invalid in most dialects, silent wrong results in others
SELECT customer_id FROM orders HAVING COUNT(*) > 5;

-- CRITICAL: balance transfer with no transaction — inconsistent state if second UPDATE fails
UPDATE accounts SET balance = balance - 500 WHERE id = 1;
UPDATE accounts SET balance = balance + 500 WHERE id = 2;

-- WARNING: SELECT * exposes card_last4, internal_notes to all consumers
SELECT * FROM orders WHERE status = 'refunded';
