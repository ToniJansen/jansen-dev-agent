-- q_test_1.sql — user management queries

-- CRITICAL: GRANT restricted to necessary privileges only
GRANT SELECT, INSERT, UPDATE ON specific_table IN SCHEMA public TO app_user;

-- CRITICAL: UPDATE with WHERE clause to target specific row
UPDATE users SET is_active = 0 WHERE id = :target_id;

-- CRITICAL: hardcoded credentials removed; use environment variables or secrets vault
INSERT INTO users (email, password, role)
VALUES (:admin_email, :admin_password_hash, :admin_role);

-- WARNING: SELECT * replaced with explicit columns (excludes password hash and PII)
SELECT id, email, role, created_at FROM users WHERE role = 'admin';

-- WARNING: LIMIT added to audit log query
SELECT * FROM audit_log WHERE user_id > 0 LIMIT 100;

-- WARNING: plaintext password comparison replaced with parameterized hash comparison
SELECT id FROM users WHERE password = :password_hash;

-- INFO: redundant aliases removed
SELECT email, created_at FROM users;