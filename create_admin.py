import sqlite3
import bcrypt
from datetime import datetime

# Connect to database
conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

# Password
password = "admin123"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# First, check if column is_phone_verified exists
cursor.execute("PRAGMA table_info(users)")
columns = [column[1] for column in cursor.fetchall()]

# Create admin user with proper fields
if 'is_phone_verified' in columns:
    cursor.execute("""
        INSERT OR REPLACE INTO users (email, password_hash, full_name, is_active, is_email_verified, is_phone_verified, created_at)
        VALUES ('admin@eshop.com', ?, 'Administrator', 1, 1, 1, ?)
    """, (hashed.decode(), datetime.now().isoformat()))
else:
    cursor.execute("""
        INSERT OR REPLACE INTO users (email, password_hash, full_name, is_active, is_email_verified, created_at)
        VALUES ('admin@eshop.com', ?, 'Administrator', 1, 1, ?)
    """, (hashed.decode(), datetime.now().isoformat()))

conn.commit()

print("=" * 50)
print("✅ Admin created successfully!")
print("=" * 50)
print("📧 Email: admin@eshop.com")
print("🔐 Password: admin123")
print("=" * 50)

# Show all users
print("\n📋 All users in database:")
cursor.execute("SELECT id, email, full_name, is_active FROM users")
for row in cursor.fetchall():
    print(f"   ID: {row[0]}, Email: {row[1]}, Name: {row[2]}, Active: {row[3]}")

conn.close()