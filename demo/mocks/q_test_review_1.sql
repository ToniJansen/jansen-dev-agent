GRANT SELECT, INSERT, UPDATE ON TABLE users TO app_user;
UPDATE users SET is_active = 0 WHERE id = ?;
INSERT INTO users (email, password, role)
VALUES (?, ?, ?);
SELECT id, email, role FROM users WHERE role = ?;
SELECT id, email, role FROM audit_log WHERE user_id > 0 LIMIT 100;
SELECT id FROM users WHERE hashed_password = ?;
SELECT email, created_at FROM users LIMIT 100;