-- orders_report.sql — daily reporting queries

-- BUG fixed: added parentheses to correct AND/OR precedence; added LIMIT for report safety
SELECT id, customer_id, status, created_at, total FROM orders
WHERE (status = 'active' OR status = 'pending') AND created_at > NOW() - INTERVAL '7 days'
LIMIT 100;

-- CRITICAL fixed: parameterized dynamic SQL using EXECUTE ... USING to prevent injection
EXECUTE 'SELECT id, customer_id, status, total FROM ' || quote_ident(table_name) || ' WHERE customer_id = $1' USING customer_id;

-- BUG fixed: added GROUP BY to make HAVING valid and results well-defined
SELECT customer_id FROM orders GROUP BY customer_id HAVING COUNT(*) > 5;

-- CRITICAL fixed: wrapped balance transfer in a transaction with exception handling
BEGIN;
DO $$
BEGIN
    UPDATE accounts SET balance = balance - 500 WHERE id = 1;
    UPDATE accounts SET balance = balance + 500 WHERE id = 2;
EXCEPTION WHEN OTHERS THEN
    RAISE;
END;
$$;
COMMIT;

-- WARNING fixed: explicit column list excludes card_last4 and internal_notes
SELECT id, customer_id, status, total FROM orders WHERE status = 'refunded'
LIMIT 100;