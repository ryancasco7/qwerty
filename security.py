"""
Security utilities for authentication and input validation
"""
import hashlib
import re
import secrets
from typing import Tuple


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256 with salt.
    For production, consider using bcrypt or argon2.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    # Add salt for better security
    salt = secrets.token_hex(16)
    salted_password = password + salt
    return hashlib.sha256(salted_password.encode()).hexdigest() + ":" + salt


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        password: Plain text password to verify
        hashed_password: Stored hash (format: hash:salt)
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        hash_part, salt = hashed_password.rsplit(":", 1)
        salted_password = password + salt
        computed_hash = hashlib.sha256(salted_password.encode()).hexdigest()
        return secrets.compare_digest(computed_hash, hash_part)
    except (ValueError, AttributeError):
        # Handle legacy passwords without salt
        return hashlib.sha256(password.encode()).hexdigest() == hashed_password


def sanitize_input(text: str, max_length: int = None) -> str:
    """
    Sanitize user input to prevent XSS and injection attacks.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove HTML tags and dangerous characters
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[<>"\']', '', text)
    text = text.strip()
    
    # Limit length
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username format and security.
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Username cannot be empty"
    
    username = username.strip()
    
    # Length validation
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 20:
        return False, "Username must be at most 20 characters"
    
    # Format validation - only alphanumeric and underscore
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    # Reserved usernames
    reserved = ['admin', 'administrator', 'root', 'system', 'null', 'undefined']
    if username.lower() in reserved:
        return False, "This username is reserved"
    
    return True, ""


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password cannot be empty"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if len(password) > 128:
        return False, "Password is too long (maximum 128 characters)"
    
    # Check for at least one letter and one number
    has_letter = re.search(r'[a-zA-Z]', password)
    has_number = re.search(r'[0-9]', password)
    
    if not has_letter or not has_number:
        return False, "Password must contain at least one letter and one number"
    
    return True, ""


def escape_html(text: str) -> str:
    """
    Escape HTML special characters to prevent XSS.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text
    """
    if not text:
        return ""
    
    escape_map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;'
    }
    
    for char, escaped in escape_map.items():
        text = text.replace(char, escaped)
    
    return text

