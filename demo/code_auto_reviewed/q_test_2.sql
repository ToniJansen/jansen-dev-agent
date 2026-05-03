-- q_test_2.sql — reporting queries

-- CRITICAL: Cartesian join (missing ON clause — cross joins all rows)
SELECT o.order_id, c.name
FROM orders o JOIN customers c ON o.customer_id = c.id;

-- WARNING: no LIMIT on monthly revenue report
SELECT DATE_TRUNC('month', created_at), SUM(total_amount)
FROM orders
WHERE created_at >= NOW() - INTERVAL '1 year'
GROUP BY 1
LIMIT 12;

-- WARNING: implicit cast — revenue is NUMERIC, filtered as VARCHAR
SELECT * FROM orders WHERE total_amount = 1500;

-- WARNING: UNION without column type alignment
SELECT id::TEXT, name::TEXT FROM customers
UNION
SELECT order_id::TEXT, created_at::TEXT FROM orders;

-- WARNING: ORDER BY column position (fragile, breaks on schema change)
SELECT customer_id, total_amount, status FROM orders
ORDER BY total_amount DESC;

-- INFO: redundant DISTINCT with GROUP BY
SELECT customer_id, COUNT(*)
FROM orders
GROUP BY customer_id;