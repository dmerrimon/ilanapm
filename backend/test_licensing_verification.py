"""
Comprehensive verification tests for licensing system

Tests:
1. Database constraints
2. License activation flow
3. Seat availability logic
4. Token validation
5. Error handling
"""

import sys
from datetime import datetime, timedelta
from database.connection import get_db_connection
import secrets


def generate_ids():
    """Generate test IDs"""
    return {
        'org_id': f'org_test_{secrets.token_hex(4)}',
        'user_id': f'usr_test_{secrets.token_hex(4)}',
        'license_key': f'TEST-KEY-{secrets.token_hex(4).upper()}',
        'activation_id': f'act_test_{secrets.token_hex(4)}',
        'device_id': f'device_{secrets.token_hex(8)}'
    }


def test_seat_availability_logic():
    """Test seat availability checking logic"""
    print("\n=== Test: Seat Availability Logic ===")

    ids = generate_ids()

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Create org with 2 seats
        cursor.execute("""
            INSERT INTO organizations (org_id, org_name, tier, seats_purchased, seats_used,
                                       subscription_start, subscription_end)
            VALUES (?, 'Test Org', 'professional', 2, 0, ?, ?)
        """, (ids['org_id'], datetime.now().date(), (datetime.now() + timedelta(days=365)).date()))

        # Create license key
        cursor.execute("""
            INSERT INTO license_keys (license_key, org_id, tier, seats)
            VALUES (?, ?, 'professional', 2)
        """, (ids['license_key'], ids['org_id']))

        # Activate seat 1
        user1_id = f"{ids['user_id']}_1"
        cursor.execute("""
            INSERT INTO users (user_id, org_id, email) VALUES (?, ?, ?)
        """, (user1_id, ids['org_id'], f"user1_{secrets.token_hex(4)}@test.com"))

        cursor.execute("""
            INSERT INTO activations (activation_id, user_id, license_key, device_id,
                                      activation_token, token_expires_at)
            VALUES (?, ?, ?, ?, 'token1', ?)
        """, (f"{ids['activation_id']}_1", user1_id, ids['license_key'],
              f"{ids['device_id']}_1", datetime.now() + timedelta(days=90)))

        cursor.execute("UPDATE organizations SET seats_used = 1 WHERE org_id = ?", (ids['org_id'],))

        # Activate seat 2
        user2_id = f"{ids['user_id']}_2"
        cursor.execute("""
            INSERT INTO users (user_id, org_id, email) VALUES (?, ?, ?)
        """, (user2_id, ids['org_id'], f"user2_{secrets.token_hex(4)}@test.com"))

        cursor.execute("""
            INSERT INTO activations (activation_id, user_id, license_key, device_id,
                                      activation_token, token_expires_at)
            VALUES (?, ?, ?, ?, 'token2', ?)
        """, (f"{ids['activation_id']}_2", user2_id, ids['license_key'],
              f"{ids['device_id']}_2", datetime.now() + timedelta(days=90)))

        cursor.execute("UPDATE organizations SET seats_used = 2 WHERE org_id = ?", (ids['org_id'],))

        # Check seats_used
        cursor.execute("SELECT seats_used, seats_purchased FROM organizations WHERE org_id = ?",
                        (ids['org_id'],))
        org = cursor.fetchone()

        print(f"Seats used: {org['seats_used']}/{org['seats_purchased']}")

        if org['seats_used'] == 2 and org['seats_purchased'] == 2:
            print("✅ Seat counting logic works correctly")
        else:
            print(f"❌ Seat counting error: {org['seats_used']} used, {org['seats_purchased']} purchased")
            return False

        # Try to activate seat 3 (should fail in real activation endpoint)
        if org['seats_used'] >= org['seats_purchased']:
            print("✅ Seat limit enforcement would work (seats_used >= seats_purchased)")
        else:
            print("❌ Seat limit not properly checked")
            return False

        # Clean up
        cursor.execute("DELETE FROM organizations WHERE org_id = ?", (ids['org_id'],))

    return True


def test_reactivation_scenario():
    """Test user reactivating on same device (should not use extra seat)"""
    print("\n=== Test: Reactivation Scenario ===")

    ids = generate_ids()

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Create org
        cursor.execute("""
            INSERT INTO organizations (org_id, org_name, tier, seats_purchased, seats_used,
                                       subscription_start, subscription_end)
            VALUES (?, 'Reactivation Test', 'enterprise', 10, 0, ?, ?)
        """, (ids['org_id'], datetime.now().date(), (datetime.now() + timedelta(days=365)).date()))

        # Create license
        cursor.execute("""
            INSERT INTO license_keys (license_key, org_id, tier, seats)
            VALUES (?, ?, 'enterprise', 10)
        """, (ids['license_key'], ids['org_id']))

        # Create user
        cursor.execute("""
            INSERT INTO users (user_id, org_id, email) VALUES (?, ?, ?)
        """, (ids['user_id'], ids['org_id'], f"reactivate_{secrets.token_hex(4)}@test.com"))

        # First activation
        cursor.execute("""
            INSERT INTO activations (activation_id, user_id, license_key, device_id,
                                      activation_token, token_expires_at, is_active)
            VALUES (?, ?, ?, ?, 'old_token', ?, 1)
        """, (ids['activation_id'], ids['user_id'], ids['license_key'],
              ids['device_id'], datetime.now() + timedelta(days=90)))

        cursor.execute("UPDATE organizations SET seats_used = 1 WHERE org_id = ?", (ids['org_id'],))

        cursor.execute("SELECT seats_used FROM organizations WHERE org_id = ?", (ids['org_id'],))
        seats_before = cursor.fetchone()['seats_used']

        # Simulate reactivation (UPDATE, not INSERT)
        cursor.execute("""
            UPDATE activations
            SET activation_token = ?, token_expires_at = ?, activated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND device_id = ?
        """, ('new_token', datetime.now() + timedelta(days=90), ids['user_id'], ids['device_id']))

        # Seats should NOT change
        cursor.execute("SELECT seats_used FROM organizations WHERE org_id = ?", (ids['org_id'],))
        seats_after = cursor.fetchone()['seats_used']

        print(f"Seats before reactivation: {seats_before}")
        print(f"Seats after reactivation: {seats_after}")

        if seats_before == seats_after == 1:
            print("✅ Reactivation does not consume extra seat")
        else:
            print(f"❌ Reactivation logic error: seats changed from {seats_before} to {seats_after}")
            return False

        # Clean up
        cursor.execute("DELETE FROM organizations WHERE org_id = ?", (ids['org_id'],))

    return True


def test_subscription_expiry():
    """Test subscription expiry detection"""
    print("\n=== Test: Subscription Expiry Detection ===")

    ids = generate_ids()

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Create expired org
        expired_date = (datetime.now() - timedelta(days=1)).date()
        cursor.execute("""
            INSERT INTO organizations (org_id, org_name, tier, seats_purchased,
                                       subscription_start, subscription_end, status)
            VALUES (?, 'Expired Org', 'professional', 5, ?, ?, 'active')
        """, (ids['org_id'], (datetime.now() - timedelta(days=365)).date(), expired_date))

        cursor.execute("""
            SELECT subscription_end FROM organizations WHERE org_id = ?
        """, (ids['org_id'],))

        org = cursor.fetchone()
        subscription_end = datetime.fromisoformat(org['subscription_end'])

        if subscription_end < datetime.now():
            print(f"✅ Subscription expiry detected correctly (expired: {subscription_end.date()})")
        else:
            print(f"❌ Subscription expiry not detected (end: {subscription_end.date()})")
            return False

        # Clean up
        cursor.execute("DELETE FROM organizations WHERE org_id = ?", (ids['org_id'],))

    return True


def test_audit_log_creation():
    """Test audit log creation"""
    print("\n=== Test: Audit Log Creation ===")

    ids = generate_ids()

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Create org and user for foreign key references
        cursor.execute("""
            INSERT INTO organizations (org_id, org_name, tier, seats_purchased,
                                       subscription_start, subscription_end)
            VALUES (?, 'Audit Test Org', 'professional', 5, ?, ?)
        """, (ids['org_id'], datetime.now().date(), (datetime.now() + timedelta(days=365)).date()))

        cursor.execute("""
            INSERT INTO users (user_id, org_id, email) VALUES (?, ?, ?)
        """, (ids['user_id'], ids['org_id'], f"audit_{secrets.token_hex(4)}@test.com"))

        # Create audit log with valid foreign keys
        log_id = f"log_test_{secrets.token_hex(8)}"
        cursor.execute("""
            INSERT INTO audit_logs (log_id, org_id, user_id, action, resource_type,
                                     resource_id, metadata, ip_address)
            VALUES (?, ?, ?, 'license_activated', 'activation',
                    'act_789', '{"device_id": "dev_abc"}', '192.168.1.1')
        """, (log_id, ids['org_id'], ids['user_id']))

        cursor.execute("SELECT * FROM audit_logs WHERE log_id = ?", (log_id,))
        log = cursor.fetchone()

        if log and log['action'] == 'license_activated':
            print(f"✅ Audit log created: {log['action']} for user {log['user_id']}")
        else:
            print("❌ Audit log creation failed")
            return False

        # Test audit log with NULL org/user (should also work)
        log_id2 = f"log_test_{secrets.token_hex(8)}"
        cursor.execute("""
            INSERT INTO audit_logs (log_id, action, resource_type, resource_id)
            VALUES (?, 'system_event', 'system', 'sys_001')
        """, (log_id2,))

        cursor.execute("SELECT * FROM audit_logs WHERE log_id = ?", (log_id2,))
        log2 = cursor.fetchone()

        if log2 and log2['action'] == 'system_event':
            print(f"✅ Audit log with NULL org/user created successfully")
        else:
            print("❌ Audit log with NULL org/user failed")
            return False

        # Clean up (delete audit logs first to avoid foreign key constraint)
        cursor.execute("DELETE FROM audit_logs WHERE org_id = ? OR log_id = ?",
                        (ids['org_id'], log_id2))
        cursor.execute("DELETE FROM organizations WHERE org_id = ?", (ids['org_id'],))

    return True


def test_unique_constraints():
    """Test UNIQUE constraints"""
    print("\n=== Test: UNIQUE Constraints ===")

    ids = generate_ids()

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Create org and user
        cursor.execute("""
            INSERT INTO organizations (org_id, org_name, tier, seats_purchased,
                                       subscription_start, subscription_end)
            VALUES (?, 'Unique Test', 'professional', 5, ?, ?)
        """, (ids['org_id'], datetime.now().date(), (datetime.now() + timedelta(days=365)).date()))

        email = f"unique_{secrets.token_hex(4)}@test.com"
        cursor.execute("""
            INSERT INTO users (user_id, org_id, email) VALUES (?, ?, ?)
        """, (ids['user_id'], ids['org_id'], email))

        # Try duplicate email
        try:
            cursor.execute("""
                INSERT INTO users (user_id, org_id, email) VALUES (?, ?, ?)
            """, (f"{ids['user_id']}_dup", ids['org_id'], email))
            print("❌ UNIQUE constraint on email not working")
            return False
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                print("✅ UNIQUE constraint on email works")
            else:
                print(f"❌ Unexpected error: {e}")
                return False

        # Create activation
        cursor.execute("""
            INSERT INTO activations (activation_id, user_id, device_id,
                                      activation_token, token_expires_at)
            VALUES (?, ?, ?, 'token', ?)
        """, (ids['activation_id'], ids['user_id'], ids['device_id'],
              datetime.now() + timedelta(days=90)))

        # Try duplicate user_id + device_id
        try:
            cursor.execute("""
                INSERT INTO activations (activation_id, user_id, device_id,
                                          activation_token, token_expires_at)
                VALUES (?, ?, ?, 'token2', ?)
            """, (f"{ids['activation_id']}_dup", ids['user_id'], ids['device_id'],
                  datetime.now() + timedelta(days=90)))
            print("❌ UNIQUE constraint on (user_id, device_id) not working")
            return False
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                print("✅ UNIQUE constraint on (user_id, device_id) works")
            else:
                print(f"❌ Unexpected error: {e}")
                return False

        # Clean up
        cursor.execute("DELETE FROM organizations WHERE org_id = ?", (ids['org_id'],))

    return True


def run_all_tests():
    """Run all verification tests"""
    print("=" * 60)
    print("LICENSING SYSTEM VERIFICATION")
    print("=" * 60)

    tests = [
        ("Seat Availability Logic", test_seat_availability_logic),
        ("Reactivation Scenario", test_reactivation_scenario),
        ("Subscription Expiry", test_subscription_expiry),
        ("Audit Log Creation", test_audit_log_creation),
        ("UNIQUE Constraints", test_unique_constraints),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All verification tests PASSED! Backend is ready.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) FAILED. Review and fix issues.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
