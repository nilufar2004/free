import hashlib
import secrets
from datetime import datetime
import re

def hash_password(password):
    """Hash a password with a random salt"""
    salt = secrets.token_hex(16)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('ascii'), 100000)
    pwdhash = pwdhash.hex()
    return salt + pwdhash

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    # Safety for empty values
    if not stored_password:
        return False

    stored_password = str(stored_password)
    provided_password = str(provided_password)

    # Preferred format: 32 hex salt + 64 hex hash
    if len(stored_password) == 96 and re.fullmatch(r"[0-9a-fA-F]{96}", stored_password):
        salt = stored_password[:32]
        stored_pwdhash = stored_password[32:]
        pwdhash = hashlib.pbkdf2_hmac(
            'sha256',
            provided_password.encode('utf-8'),
            salt.encode('ascii'),
            100000
        ).hex()
        return pwdhash.lower() == stored_pwdhash.lower()

    # Legacy fallback: some old rows may contain plain text password
    return stored_password == provided_password

def get_current_timestamp():
    """Get current timestamp in readable format"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def format_currency(amount):
    """Format amount as currency"""
    return f"{amount:,.2f}"

def validate_phone_number(phone):
    """Validate phone number format"""
    # Remove any non-digit characters
    clean_phone = ''.join(filter(str.isdigit, phone))
    
    # Check if it starts with 998 (Uzbekistan country code) or has 9 digits
    if clean_phone.startswith('998') and len(clean_phone) == 12:
        return True
    elif len(clean_phone) == 9:  # Local format
        return True
    else:
        return False
