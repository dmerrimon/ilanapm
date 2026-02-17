#!/usr/bin/env python3
from database.connection import get_db_connection
import secrets

with get_db_connection() as conn:
    cursor = conn.cursor()
    org_id = f'org_{secrets.token_urlsafe(16)}'
    cursor.execute("INSERT INTO organizations (org_id, org_name, tier, seats_purchased, subscription_start, subscription_end, status) VALUES (%s, %s, %s, %s, CURRENT_DATE, CURRENT_DATE + INTERVAL '10 years', %s)", (org_id, 'Seleen Internal', 'enterprise', 100, 'active'))
    print(f'Created org: {org_id}')
    cursor.execute("UPDATE users SET org_id = %s WHERE role = 'super_admin'", (org_id,))
    print(f'Updated {cursor.rowcount} users')
    conn.commit()
    print('Done!')
