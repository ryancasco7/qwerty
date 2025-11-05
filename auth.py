"""
Authentication module with improved security
"""
import streamlit as st
import json
import os
import logging
from datetime import datetime
from typing import Tuple, Optional
from security import hash_password, verify_password, validate_username, validate_password, sanitize_input, escape_html
from config import (
    USERS_FILE, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD,
    ROLE_ADMIN, ROLE_TEACHER, PASSWORD_MIN_LENGTH, USERNAME_MIN_LENGTH,
    APP_NAME, APP_TAGLINE
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Sheets backend removed – using local JSON storage


def load_users() -> dict:
    """
    Load users from JSON file with error handling.
    
    Returns:
        Dictionary of users
    """
    users = {}
    
    # Default admin account with improved security
    default_admin = {
        DEFAULT_ADMIN_USERNAME: {
            'password': hash_password(DEFAULT_ADMIN_PASSWORD),
            'role': ROLE_ADMIN,
            'created_at': '2024-01-01 00:00:00',
            'last_login': None,
            'failed_attempts': 0
        }
    }
    
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
            logger.info("Users loaded from JSON file")
        except Exception as e:
            logger.error(f"Error loading users file: {e}")
            users = default_admin
    else:
        users = default_admin
        save_users(users)
        logger.info("Created new users storage with default admin")
    
    # Ensure admin account always exists with current security standards
    if DEFAULT_ADMIN_USERNAME not in users:
        users[DEFAULT_ADMIN_USERNAME] = default_admin[DEFAULT_ADMIN_USERNAME]
        save_users(users)
    elif ':' not in users[DEFAULT_ADMIN_USERNAME].get('password', ''):
        # Migrate old password hash to new format
        users[DEFAULT_ADMIN_USERNAME]['password'] = hash_password(DEFAULT_ADMIN_PASSWORD)
        save_users(users)
    
    return users


def save_users(users: dict) -> bool:
    """
    Save users to JSON file with error handling.
    
    Args:
        users: Dictionary of users to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create backup
        if os.path.exists(USERS_FILE):
            backup_file = f"{USERS_FILE}.backup"
            try:
                with open(USERS_FILE, 'r', encoding='utf-8') as f:
                    backup_data = f.read()
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(backup_data)
            except Exception:
                pass
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving users file: {e}")
        return False


def signup(username: str, password: str) -> Tuple[bool, str]:
    """
    Register a new user with improved validation.
    
    Args:
        username: Desired username
        password: Desired password
        
    Returns:
        Tuple of (success, message)
    """
    # Sanitize inputs
    username = sanitize_input(username.strip(), max_length=20)
    password = password.strip()
    
    # Validate username
    is_valid, error_msg = validate_username(username)
    if not is_valid:
        return False, error_msg
    
    # Validate password
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        return False, error_msg
    
    # Load users
    users = load_users()
    
    # Check if username already exists
    if username.lower() in [u.lower() for u in users.keys()]:
        return False, "Username already exists"
    
    # Create new user
    try:
        users[username] = {
            'password': hash_password(password),
            'role': ROLE_TEACHER,  # All new signups are teachers
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_login': None,
            'failed_attempts': 0
        }
        
        if save_users(users):
            logger.info(f"New user created: {username}")
            return True, "Teacher account created successfully!"
        else:
            return False, "Error saving user account. Please try again."
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return False, "An error occurred. Please try again."


def login(username: str, password: str) -> Tuple[bool, str, Optional[str]]:
    """
    Authenticate a user with improved security.
    
    Args:
        username: Username
        password: Password
        
    Returns:
        Tuple of (success, message, role)
    """
    # Sanitize inputs
    username = sanitize_input(username.strip(), max_length=20)
    password = password.strip()
    
    if not username or not password:
        return False, "Username and password are required", None
    
    # Load users
    users = load_users()
    
    # Case-insensitive username lookup
    username_lower = username.lower()
    matching_username = None
    for u in users.keys():
        if u.lower() == username_lower:
            matching_username = u
            break
    
    if not matching_username:
        return False, "Invalid username or password", None
    
    user = users[matching_username]
    
    # Verify password
    if not verify_password(password, user.get('password', '')):
        # Track failed attempts
        user['failed_attempts'] = user.get('failed_attempts', 0) + 1
        save_users(users)
        
        if user['failed_attempts'] >= 5:
            return False, "Account locked due to too many failed attempts. Please contact administrator.", None
        
        return False, f"Invalid username or password ({user['failed_attempts']}/5 attempts)", None
    
    # Successful login
    user['last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user['failed_attempts'] = 0
    save_users(users)
    
    role = user.get('role', ROLE_TEACHER)
    logger.info(f"User logged in: {matching_username} ({role})")
    return True, "Login successful!", role


def show_auth_page():
    """Display login/signup page with improved security"""
    
    # Custom CSS for auth page with mobile responsiveness
    st.markdown("""
        <style>
        .auth-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 2rem;
        }
        .auth-header {
            text-align: center;
            color: #1E88E5;
            margin-bottom: 2rem;
        }
        .auth-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #0D47A1;
            margin-bottom: 0.5rem;
            word-wrap: break-word;
        }
        .auth-subtitle {
            font-size: 1.2rem;
            color: #424242;
            font-weight: 400;
            word-wrap: break-word;
        }
        .security-info {
            font-size: 0.85rem;
            color: #666;
            margin-top: 0.5rem;
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            .auth-container {
                padding: 1rem;
                max-width: 100%;
            }
            
            .auth-title {
                font-size: 2rem;
            }
            
            .auth-subtitle {
                font-size: 1rem;
            }
        }
        
        @media (max-width: 480px) {
            .auth-container {
                padding: 0.75rem;
            }
            
            .auth-title {
                font-size: 1.75rem;
            }
            
            .auth-subtitle {
                font-size: 0.9rem;
            }
        }
        
        /* Touch-friendly inputs */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select {
            min-height: 44px;
            font-size: 16px; /* Prevents zoom on iOS */
        }
        
        .stButton > button {
            min-height: 44px;
            font-size: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown(f'''
        <div class="auth-header">
            <div class="auth-title">📚 {APP_NAME}</div>
            <div class="auth-subtitle">{APP_TAGLINE}</div>
        </div>
    ''', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        st.markdown("#### Login to Your Account")
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username", placeholder="Enter your username", max_chars=20)
            password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Login", type="primary", use_container_width=True)
            
            if submit:
                if username and password:
                    success, message, role = login(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_role = role
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter both username and password")
    
    with tab2:
        st.markdown("#### Create New Teacher Account")
        st.info("📌 All new accounts will be registered as Teacher accounts.")
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("signup_form"):
            new_username = st.text_input("Username", key="signup_username", placeholder="Choose a username (3-20 characters, letters, numbers, underscore only)", max_chars=20)
            new_password = st.text_input("Password", type="password", key="signup_password", placeholder=f"Choose a password (min. {PASSWORD_MIN_LENGTH} characters, must include letters and numbers)")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password", placeholder="Re-enter your password")
            st.markdown("<div class='security-info'>🔒 Password must be at least 8 characters and include letters and numbers</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)
            
            if submit:
                if new_username and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("❌ Passwords do not match!")
                    else:
                        success, message = signup(new_username, new_password)
                        if success:
                            st.success(message)
                            st.info("✅ You can now login with your credentials")
                        else:
                            st.error(message)
                else:
                    st.warning("⚠️ Please fill in all fields")
    
    st.markdown('</div>', unsafe_allow_html=True)
