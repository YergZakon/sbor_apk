"""
Utility script to create the first admin user
Run once during initial setup: python create_admin.py
"""
from modules.database import SessionLocal, User
from modules.auth import create_user
import sys


def main():
    db = SessionLocal()

    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.role == "admin").first()

        if existing_admin:
            print("⚠️  Admin user already exists:")
            print(f"   Username: {existing_admin.username}")
            print(f"   Email: {existing_admin.email}")
            print()

            response = input("Do you want to create another admin? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("❌ Aborted")
                return

        print("=" * 50)
        print("🔐 CREATE ADMIN USER")
        print("=" * 50)
        print()

        # Get admin details
        username = input("Username (admin): ").strip() or "admin"
        email = input("Email (admin@agrodata.kz): ").strip() or "admin@agrodata.kz"
        full_name = input("Full Name (System Administrator): ").strip() or "System Administrator"
        password = input("Password (min 6 characters): ").strip()

        if len(password) < 6:
            print("❌ Password must be at least 6 characters")
            return

        # Check if username exists
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"❌ User with username '{username}' already exists")
            return

        # Check if email exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"❌ User with email '{email}' already exists")
            return

        # Create admin user
        admin_user = create_user(
            db=db,
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role="admin",
            farm_id=None
        )

        print()
        print("=" * 50)
        print("✅ ADMIN USER CREATED SUCCESSFULLY!")
        print("=" * 50)
        print(f"Username: {admin_user.username}")
        print(f"Email: {admin_user.email}")
        print(f"Full Name: {admin_user.full_name}")
        print(f"Role: {admin_user.role}")
        print()
        print("You can now login at: http://localhost:8501")
        print("Navigate to 🔐 Login page")
        print()

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    main()
