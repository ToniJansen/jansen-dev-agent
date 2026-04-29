GRANT SELECT (id,email,role), INSERT, UPDATE ON users TO app_user;
UPDATE users SET is_active = 0 WHERE id = ?;
INSERT INTO users (email, password_hash, role, created_at)
VALUES (?, ?, ?, NOW());
SELECT id, email, role FROM users WHERE role = ?;
SELECT id, email, role FROM audit_log WHERE user_id = ? AND created_at >= NOW() - INTERVAL '30 days' LIMIT 100;
SELECT id FROM users WHERE hashed_password = ?;
SELECT email, created_at FROM users WHERE created_at >= NOW() - INTERVAL '30 days' LIMIT 100;