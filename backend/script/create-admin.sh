#!/bin/bash

set -e

echo "👤 Create Admin User"
echo "===================="
echo ""

read -p "Email: " email
read -p "Username: " username
read -s -p "Password: " password
echo ""

# Create Python script to add admin
cat > /tmp/create_admin.py << PYTHON
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

db = SessionLocal()

try:
    # Check if user exists
    existing = db.query(User).filter(User.email == "$email").first()
    if existing:
        print("❌ User with this email already exists")
        exit(1)
    
    existing = db.query(User).filter(User.username == "$username").first()
    if existing:
        print("❌ User with this username already exists")
        exit(1)
    
    # Create admin user
    admin = User(
        email="$email",
        username="$username",
        hashed_password=get_password_hash("$password"),
        role=UserRole.ADMIN,
        is_active=True
    )
    
    db.add(admin)
    db.commit()
    
    print("✅ Admin user created successfully!")
    print(f"   Email: $email")
    print(f"   Username: $username")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
PYTHON

uv run python /tmp/create_admin.py
rm /tmp/create_admin.py
