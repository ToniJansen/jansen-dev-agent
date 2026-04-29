REVOKE ALL ON users FROM app_user;
GRANT SELECT, INSERT, UPDATE ON TABLE users TO app_user;
UPDATE users SET is_active = 0 WHERE id = $1;
INSERT INTO users (email, hashed_password, role)
VALUES ($1, $2, $3);
SELECT id, email, role FROM users WHERE role = $1;
SELECT id, email, role FROM audit_log WHERE user_id = $1 LIMIT 100;
SELECT id FROM users WHERE id = $1;
SELECT email, created_at FROM users LIMIT 100;