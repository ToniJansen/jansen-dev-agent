-- q_test_3.sql — data migration queries

-- CRITICAL: DROP without transaction or backup check
DROP TABLE orders_2022;
DROP TABLE payments_2022;

-- CRITICAL: INSERT with hardcoded production IDs
INSERT INTO configs (key, value)
VALUES ('stripe_secret', 'sk_prod_hardcoded_key_123');

-- CRITICAL: UPDATE without WHERE in migration (resets all records)
UPDATE orders SET migrated = true;

-- WARNING: no row count validation before DELETE
DELETE FROM order_items WHERE order_id NOT IN (SELECT id FROM orders);

-- WARNING: ALTER TABLE without checking existing data compatibility
ALTER TABLE payments ALTER COLUMN amount TYPE VARCHAR(20);

-- WARNING: sequence reset to value that may conflict with existing IDs
ALTER SEQUENCE orders_id_seq RESTART WITH 1;

-- INFO: no index created after adding new foreign key column
ALTER TABLE order_items ADD COLUMN warehouse_id INT;
