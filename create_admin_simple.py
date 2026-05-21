import sqlite3
import bcrypt

conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

# Check if users table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
if not cursor.fetchone():
    print("Users table not found! Please run backend first.")
    exit()

email = "admin@eshop.com"
password = "admin123"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

cursor.execute("DELETE FROM users WHERE email = ?", (email,))
cursor.execute("""
    INSERT INTO users (email, password_hash, full_name, is_active, is_email_verified, created_at)
    VALUES (?, ?, ?, 1, 1, datetime('now'))
""", (email, hashed.decode(), 'Administrator'))

conn.commit()
print("✅ Admin created successfully!")
print("📧 Email: admin@eshop.com")
print("🔐 Password: admin123")

conn.close()
