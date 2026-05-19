# This file is used to manage OTP-based pending user registrations for the Smart Task Manager project, storing temporary registration details until the email verification code is confirmed and then cleaning expired or completed pending records.

from database.db import execute_query


def save_pending_registration(name, email, password_hash, otp_hash):
    query = """
        INSERT INTO pending_registrations (name, email, password_hash, otp_hash, expires_at)
        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP + INTERVAL '10 minutes')
        ON CONFLICT (email)
        DO UPDATE SET
            name = EXCLUDED.name,
            password_hash = EXCLUDED.password_hash,
            otp_hash = EXCLUDED.otp_hash,
            expires_at = EXCLUDED.expires_at,
            created_at = CURRENT_TIMESTAMP
        RETURNING id, name, email, expires_at;
    """
    return execute_query(query, (name, email, password_hash, otp_hash), fetch_one=True)


def find_pending_registration(email):
    query = """
        SELECT id, name, email, password_hash, otp_hash, expires_at
        FROM pending_registrations
        WHERE email = %s AND expires_at > CURRENT_TIMESTAMP;
    """
    return execute_query(query, (email,), fetch_one=True)


def delete_pending_registration(email):
    query = """
        DELETE FROM pending_registrations
        WHERE email = %s
        RETURNING id;
    """
    return execute_query(query, (email,), fetch_one=True)


def delete_expired_pending_registrations():
    query = """
        DELETE FROM pending_registrations
        WHERE expires_at <= CURRENT_TIMESTAMP;
    """
    return execute_query(query)
