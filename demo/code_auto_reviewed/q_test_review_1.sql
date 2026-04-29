GRANT SELECT (id, email, role), INSERT (email, hashed_password, role), UPDATE (is_active) ON users TO app_user;
UPDATE users SET is_active = 0 WHERE id = ?;
INSERT INTO users (email, hashed_password, role)
VALUES (?, ?, ?);
INSERT INTO audit_log (action, target_user_email, performed_at) VALUES ('user_created', ?, NOW());
SELECT id, email, role FROM users WHERE role = ?;
SELECT id, email, role FROM audit_log WHERE user_id = ? LIMIT 100;
SELECT id, hashed_password FROM users WHERE id = ?;
SELECT email, created_at FROM users WHERE created_at IS NOT NULL ORDER BY created_at DESC LIMIT 100;