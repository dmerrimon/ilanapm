#!/usr/bin/env python3
"""
Create a test license key for API testing

This script creates:
1. A test organization with active subscription
2. A license key for that organization
3. Outputs the license key to use in your add-in

Usage:
    python create_test_license.py
    python create_test_license.py --tier enterprise --seats 10
"""

import argparse
import secrets
from datetime import datetime, timedelta
from database.connection import get_db_connection


def generate_license_key():
    """Generate a license key in format: ILANA-XXXX-XXXX-XXXX-XXXX"""
    parts = [secrets.token_hex(2).upper() for _ in range(4)]
    return f"ILANA-{'-'.join(parts)}"


def create_test_license(tier='professional', seats=5, org_name='Test Organization'):
    """Create a test organization and license key"""

    # Generate IDs
    org_id = f"org_test_{secrets.token_urlsafe(8)}"
    license_key = generate_license_key()

    # Subscription dates (1 year from today)
    subscription_start = datetime.now().date()
    subscription_end = (datetime.now() + timedelta(days=365)).date()

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Create test organization
        cursor.execute("""
            INSERT INTO organizations (
                org_id, org_name, tier, seats_purchased, seats_used,
                subscription_start, subscription_end, status,
                primary_contact_email, primary_contact_name
            )
            VALUES (?, ?, ?, ?, 0, ?, ?, 'active', ?, ?)
        """, (
            org_id,
            org_name,
            tier,
            seats,
            subscription_start,
            subscription_end,
            'test@ilanapm.com',
            'Test Admin'
        ))

        # Create license key
        cursor.execute("""
            INSERT INTO license_keys (
                license_key, org_id, tier, seats, is_active
            )
            VALUES (?, ?, ?, ?, 1)
        """, (license_key, org_id, tier, seats))

        conn.commit()

    return {
        'license_key': license_key,
        'org_id': org_id,
        'org_name': org_name,
        'tier': tier,
        'seats': seats,
        'subscription_end': subscription_end.isoformat()
    }


def main():
    parser = argparse.ArgumentParser(description='Create a test license key for API testing')
    parser.add_argument('--tier', choices=['professional', 'enterprise'], default='professional',
                        help='License tier (default: professional)')
    parser.add_argument('--seats', type=int, default=5,
                        help='Number of seats (default: 5)')
    parser.add_argument('--org-name', default='Test Organization',
                        help='Organization name (default: Test Organization)')

    args = parser.parse_args()

    print("=" * 70)
    print("Creating Test License Key")
    print("=" * 70)

    result = create_test_license(
        tier=args.tier,
        seats=args.seats,
        org_name=args.org_name
    )

    print(f"\n✅ Test license created successfully!\n")
    print(f"License Key:       {result['license_key']}")
    print(f"Organization ID:   {result['org_id']}")
    print(f"Organization Name: {result['org_name']}")
    print(f"Tier:              {result['tier']}")
    print(f"Seats:             {result['seats']}")
    print(f"Expires:           {result['subscription_end']}")

    print("\n" + "=" * 70)
    print("How to use this license key:")
    print("=" * 70)
    print("\n1. Open your desktop add-in in MS Project")
    print("2. Go to Settings (or License Activation)")
    print(f"3. Enter this license key: {result['license_key']}")
    print("4. Enter any test email (e.g., yourname@test.com)")
    print("5. Click Activate")
    print("\nYour add-in will receive a JWT token valid for 90 days!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
