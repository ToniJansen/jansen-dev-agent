-- q_test_1.sql — user management queries

-- CRITICAL: GRANT ALL with no restriction
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;

-- CRITICAL: UPDATE without WHERE (affects all rows)
UPDATE users SET is_active = 0;

-- CRITICAL: hardcoded credentials in INSERT
INSERT INTO users (email, password, role)
VALUES ('admin@corp.com', 'Admin@2024', 'superadmin');

-- WARNING: SELECT * on users table (exposes password hash, PII)
SELECT * FROM users WHERE role = 'admin';

-- WARNING: no LIMIT on audit log query
SELECT * FROM audit_log WHERE user_id > 0;

-- WARNING: comparing hashed password with plaintext
SELECT id FROM users WHERE password = 'mypassword123';

-- INFO: column alias shadows original name
SELECT email AS email, created_at AS created_at FROM users;
