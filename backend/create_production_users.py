#!/usr/bin/env python3
"""
Create test users for portal authentication on PRODUCTION
This script can be run on Render or any environment with DATABASE_URL set
"""

import hashlib
import secrets
import os
import sys

# Add backend directory to path so we can import database module
sys.path.insert(0, os.path.dirname(__file__))

from database.connection import get_db_connection

def hash_password(password: str) -> str:
    """Hash password using SHA-256 (matches portal.py)"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_user_id() -> str:
    """Generate unique user ID"""
    return f"usr_{secrets.token_urlsafe(16)}"

def create_test_users():
    """Create test users for portal access"""
    print("Creating portal test users...")
    print(f"Database type: {os.getenv('DATABASE_URL', 'SQLite (local)')[:20]}...")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        try:
            # Check if test organization exists
            cursor.execute("SELECT org_id FROM organizations WHERE org_name = 'Test Organization' LIMIT 1")
            org = cursor.fetchone()

            if not org:
                # Create test organization
                org_id = f"org_{secrets.token_urlsafe(16)}"
                cursor.execute("""
                    INSERT INTO organizations (org_id, org_name, tier, seats_purchased, subscription_start, subscription_end, status)
                    VALUES (?, ?, ?, ?, CURRENT_DATE, CURRENT_DATE + INTERVAL '1 year', ?)
                """, (org_id, "Test Organization", "professional", 50, "active"))
                print(f"✅ Created test organization: {org_id}")
            else:
                org_id = org["org_id"] if isinstance(org, dict) else org[0]
                print(f"✅ Using existing organization: {org_id}")

            # Create admin user (for customer portal)
            admin_email = "admin@test.com"
            cursor.execute("SELECT user_id FROM users WHERE email = ?", (admin_email,))
            if not cursor.fetchone():
                admin_user_id = generate_user_id()
                admin_password = hash_password("admin123")  # Simple password for testing

                cursor.execute("""
                    INSERT INTO users (user_id, org_id, email, password_hash, role, first_name, last_name, is_active,
                                       customer_portal_access, founder_portal_access)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (admin_user_id, org_id, admin_email, admin_password, "admin", "Admin", "User", True, True, False))

                print(f"✅ Created admin user:")
                print(f"   Email: {admin_email}")
                print(f"   Password: admin123")
                print(f"   Role: admin (customer portal access)")
            else:
                print(f"✅ Admin user already exists: {admin_email}")

            # Create Seleen Internal organization for super admin
            cursor.execute("SELECT org_id FROM organizations WHERE org_name = 'Seleen Internal' LIMIT 1")
            seleen_org = cursor.fetchone()

            if not seleen_org:
                seleen_org_id = f"org_{secrets.token_urlsafe(16)}"
                cursor.execute("""
                    INSERT INTO organizations (org_id, org_name, tier, seats_purchased, subscription_start, subscription_end, status)
                    VALUES (?, ?, ?, ?, CURRENT_DATE, CURRENT_DATE + INTERVAL '10 years', ?)
                """, (seleen_org_id, "Seleen Internal", "enterprise", 100, "active"))
                print(f"✅ Created Seleen Internal organization: {seleen_org_id}")
            else:
                seleen_org_id = seleen_org["org_id"] if isinstance(seleen_org, dict) else seleen_org[0]
                print(f"✅ Using existing Seleen Internal organization: {seleen_org_id}")

            # Create super_admin user (for founder portal) in Seleen Internal org
            super_admin_email = "founder@seleen.com"
            cursor.execute("SELECT user_id FROM users WHERE email = ?", (super_admin_email,))
            if not cursor.fetchone():
                super_admin_user_id = generate_user_id()
                super_admin_password = hash_password("founder123")  # Simple password for testing

                cursor.execute("""
                    INSERT INTO users (user_id, org_id, email, password_hash, role, first_name, last_name, is_active,
                                       customer_portal_access, founder_portal_access)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (super_admin_user_id, seleen_org_id, super_admin_email, super_admin_password, "super_admin",
                      "Founder", "Admin", True, False, True))

                print(f"✅ Created super_admin user:")
                print(f"   Email: {super_admin_email}")
                print(f"   Password: founder123")
                print(f"   Role: super_admin (founder portal access)")
            else:
                print(f"✅ Super admin user already exists: {super_admin_email}")

            conn.commit()
            print("\n🎉 Test users created successfully!")
            print("\nYou can now log in to:")
            print(f"  Customer Portal: {admin_email} / admin123")
            print(f"  Founder Portal: {super_admin_email} / founder123")

        except Exception as e:
            conn.rollback()
            print(f"❌ Error creating test users: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    create_test_users()
