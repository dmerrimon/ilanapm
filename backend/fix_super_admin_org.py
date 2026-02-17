#!/usr/bin/env python3
"""
Fix super_admin organization assignment
Moves super_admin users from customer orgs to Seleen Internal org
"""

import secrets
from database.connection import get_db_connection

def fix_super_admin_organization():
    """Move super_admin users to Seleen Internal organization"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        try:
            # Check if Seleen Internal organization exists
            cursor.execute("SELECT org_id FROM organizations WHERE org_name = 'Seleen Internal' LIMIT 1")
            seleen_org = cursor.fetchone()

            if not seleen_org:
                # Create Seleen Internal organization
                seleen_org_id = f"org_{secrets.token_urlsafe(16)}"
                cursor.execute("""
                    INSERT INTO organizations (org_id, org_name, tier, seats_purchased, subscription_start, subscription_end, status)
                    VALUES (?, ?, ?, ?, CURRENT_DATE, CURRENT_DATE + INTERVAL '10 years', ?)
                """, (seleen_org_id, "Seleen Internal", "enterprise", 100, "active"))
                print(f"✅ Created Seleen Internal organization: {seleen_org_id}")
            else:
                seleen_org_id = seleen_org["org_id"] if isinstance(seleen_org, dict) else seleen_org[0]
                print(f"✅ Using existing Seleen Internal organization: {seleen_org_id}")

            # Find all super_admin users NOT in Seleen Internal org
            cursor.execute("""
                SELECT user_id, email, org_id
                FROM users
                WHERE role = 'super_admin'
                AND org_id != ?
            """, (seleen_org_id,))

            misplaced_admins = cursor.fetchall()

            if not misplaced_admins:
                print("✅ All super_admin users are already in Seleen Internal org")
                return

            # Move super_admin users to Seleen Internal org
            for admin in misplaced_admins:
                user_id = admin["user_id"]
                email = admin["email"]
                old_org_id = admin["org_id"]

                cursor.execute("""
                    UPDATE users
                    SET org_id = ?
                    WHERE user_id = ?
                """, (seleen_org_id, user_id))

                print(f"✅ Moved {email} from org {old_org_id[:8]}... to Seleen Internal org")

            conn.commit()
            print(f"\n🎉 Fixed {len(misplaced_admins)} super_admin user(s)")
            print("\nSuper admins now in separate organization - won't appear in customer portals")

        except Exception as e:
            conn.rollback()
            print(f"❌ Error fixing super admin organization: {e}")
            raise

if __name__ == "__main__":
    fix_super_admin_organization()
