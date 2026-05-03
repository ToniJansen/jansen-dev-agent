-- q_test_1.sql — user management queries

-- CRITICAL: GRANT ALL with no restriction
GRANT SELECT, INSERT ON TABLE specific_table IN SCHEMA public TO app_user;

-- CRITICAL: UPDATE without WHERE (affects all rows)
UPDATE users SET is_active = 0 WHERE id = :target_id;

-- CRITICAL: hardcoded credentials in INSERT
INSERT INTO users (email, password, role)
VALUES (:admin_email, :admin_password, :admin_role);

-- WARNING: SELECT * on users table (exposes password hash, PII)
SELECT id, email, role FROM users WHERE role = 'admin';

-- WARNING: no LIMIT on audit log query
SELECT * FROM audit_log WHERE user_id > 0 LIMIT 500;

-- WARNING: comparing hashed password with plaintext
SELECT id FROM users WHERE password = crypt(:input_password, password);

-- INFO: column alias shadows original name
SELECT email, created_at FROM users;