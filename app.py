"""
Main application file for Training Needs Analysis System
"""
import streamlit as st
import logging
from auth import show_auth_page
from utils import load_data
from dashboard import show_dashboard
from cluster_profiles import show_cluster_profiles
from recommendations import show_recommendations
from self_assessment import show_self_assessment
from admin_tools import show_admin_tools
from config import APP_NAME, APP_TAGLINE, APP_DEPARTMENT, ROLE_ADMIN, ROLE_TEACHER
from security import escape_html

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title=f"{APP_NAME} - {APP_TAGLINE}",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def main():
    """Main application function"""
    try:
        

        # Initialize session state for authentication
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        
        if 'username' not in st.session_state:
            st.session_state.username = None
        
        if 'user_role' not in st.session_state:
            st.session_state.user_role = None
        
        # Show auth page if not logged in
        if not st.session_state.logged_in:
            show_auth_page()
            return
        
        # Get user role
        user_role = st.session_state.user_role
        
        # Security: Validate user role
        if user_role not in [ROLE_ADMIN, ROLE_TEACHER]:
            logger.warning(f"Invalid user role detected: {user_role}")
            st.error("Invalid user role. Please login again.")
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_role = None
            st.rerun()
        
        # Main app content (only shown when logged in)
        
        # Custom CSS for professional light blue theme with mobile responsiveness
        st.markdown("""
            <style>
            /* Main theme colors */
            :root {
                --primary-blue: #1E88E5;
                --light-blue: #E3F2FD;
                --dark-blue: #0D47A1;
                --accent-blue: #42A5F5;
            }
            
            /* Mobile-first base styles */
            * {
                box-sizing: border-box;
            }
            
            /* Header styling */
            .main-header {
                background: linear-gradient(135deg, #1E88E5 0%, #42A5F5 100%);
                padding: 1.5rem 1rem;
                border-radius: 10px;
                margin-bottom: 1.5rem;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            
            .main-title {
                color: white;
                font-size: 1.75rem;
                font-weight: 700;
                margin: 0;
                text-align: center;
                word-wrap: break-word;
            }
            
            .main-subtitle {
                color: #E3F2FD;
                font-size: 1rem;
                text-align: center;
                margin-top: 0.5rem;
                word-wrap: break-word;
            }
            
            /* User info badge */
            .user-badge {
                background: white;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-top: 0.5rem;
            }
            
            .user-role {
                font-weight: 600;
                color: #1E88E5;
                font-size: 0.875rem;
            }
            
            .user-name {
                color: #616161;
                font-size: 0.8rem;
            }
            
            /* Navigation buttons - Mobile responsive */
            .stButton > button {
                border-radius: 8px;
                font-weight: 500;
                transition: all 0.3s;
                min-height: 44px;
                font-size: 0.9rem;
                padding: 0.5rem 1rem;
            }
            
            /* Navigation container - Scrollable on mobile */
            .nav-container {
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                margin-bottom: 1rem;
            }
            
            .nav-container::-webkit-scrollbar {
                height: 4px;
            }
            
            .nav-container::-webkit-scrollbar-track {
                background: #f1f1f1;
            }
            
            .nav-container::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 2px;
            }
            
            /* Cards and containers */
            .metric-card {
                background: white;
                padding: 1rem;
                border-radius: 10px;
                border-left: 4px solid #1E88E5;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 1rem;
            }
            
            /* Section headers */
            h1, h2, h3 {
                color: #0D47A1;
                word-wrap: break-word;
            }
            
            h1 { font-size: 1.75rem; }
            h2 { font-size: 1.5rem; }
            h3 { font-size: 1.25rem; }
            
            /* Expanders */
            .streamlit-expanderHeader {
                background-color: #E3F2FD;
                border-radius: 5px;
                border-left: 3px solid #1E88E5;
                padding: 0.75rem;
            }
            
            /* Info boxes */
            .stAlert {
                border-radius: 8px;
                padding: 1rem;
            }
            
            /* Divider */
            hr {
                border-color: #BBDEFB;
                margin: 1rem 0;
            }
            
            /* Form inputs - Touch friendly */
            .stTextInput > div > div > input,
            .stSelectbox > div > div > select,
            .stNumberInput > div > div > input {
                min-height: 44px;
                font-size: 16px; /* Prevents zoom on iOS */
            }
            
            /* Tables - Responsive */
            .dataframe {
                font-size: 0.875rem;
                overflow-x: auto;
                display: block;
            }
            
            /* Make columns stack on mobile */
            @media (max-width: 768px) {
                .main-header {
                    padding: 1rem 0.75rem;
                }
                
                .main-title {
                    font-size: 1.5rem;
                }
                
                .main-subtitle {
                    font-size: 0.9rem;
                }
                
                .user-badge {
                    padding: 0.5rem 0.75rem;
                    font-size: 0.8rem;
                }
                
                .stButton > button {
                    font-size: 0.85rem;
                    padding: 0.5rem 0.75rem;
                    min-height: 48px;
                }
                
                .metric-card {
                    padding: 1rem 0.75rem;
                }
                
                h1 { font-size: 1.5rem; }
                h2 { font-size: 1.25rem; }
                h3 { font-size: 1.1rem; }
                
                /* Stack columns on mobile */
                [data-testid="column"] {
                    width: 100% !important;
                    padding: 0.5rem !important;
                }
                
                /* Make navigation buttons full width on mobile */
                .element-container:has(button) {
                    width: 100%;
                }
            }
            
            /* Very small screens */
            @media (max-width: 480px) {
                .main-title {
                    font-size: 1.25rem;
                }
                
                .main-subtitle {
                    font-size: 0.8rem;
                }
                
                .stButton > button {
                    font-size: 0.8rem;
                    padding: 0.5rem;
                }
                
                h1 { font-size: 1.25rem; }
                h2 { font-size: 1.1rem; }
                h3 { font-size: 1rem; }
            }
            
            /* Prevent horizontal scroll */
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                max-width: 100%;
            }
            
            @media (max-width: 768px) {
                .main .block-container {
                    padding-left: 0.5rem;
                    padding-right: 0.5rem;
                }
            }
            
            /* Responsive charts */
            .js-plotly-plot {
                max-width: 100%;
                height: auto !important;
            }
            
            /* Ensure plots are responsive */
            [data-testid="stPlotlyChart"] {
                width: 100% !important;
                max-width: 100% !important;
            }
            
            /* Mobile-friendly selectboxes */
            .stSelectbox > div > div > select {
                width: 100%;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Header section with XSS protection - Mobile responsive
        # Use responsive columns that stack on mobile
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f'''
                <div class="main-header">
                    <h1 class="main-title">📊 {APP_NAME}</h1>
                    <p class="main-subtitle">{APP_TAGLINE}</p>
                </div>
            ''', unsafe_allow_html=True)
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            role_icon = "🔑" if user_role == ROLE_ADMIN else "👨‍🏫"
            role_text = "Administrator" if user_role == ROLE_ADMIN else "Teacher"
            # Escape username to prevent XSS
            safe_username = escape_html(st.session_state.username or "")
            st.markdown(f'''
                <div class="user-badge">
                    <div class="user-role">{role_icon} {role_text}</div>
                    <div class="user-name">{safe_username}</div>
                </div>
            ''', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪 Logout", type="secondary", use_container_width=True):
                logger.info(f"User logged out: {st.session_state.username}")
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.user_role = None
                st.rerun()
        
        # Load data (no loading skeleton)
        try:
            df = load_data()
            if df is None:
                st.error("Unable to load data. Please check the data file and try again.")
                st.stop()
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            st.error("An error occurred while loading data. Please try again later.")
            st.stop()
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'Dashboard'
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Navigation based on role - Mobile responsive
        # Use smaller column counts on mobile - Streamlit will auto-stack
        if user_role == ROLE_ADMIN:
            # Admin sees all buttons - Use 2 columns on mobile, 5 on desktop
            nav_cols = st.columns([1, 1, 1, 1, 1])
            
            nav_pages = [
                ("Dashboard", "nav_dashboard", "Dashboard"),
                ("Cluster Profiles", "nav_profiles", "Cluster Profiles"),
                ("Recommendations", "nav_recommendations", "Training Recommendations"),
                ("Self Assessment", "nav_assessment", "Self Assessment"),
                ("Admin Tools", "nav_admin", "Admin Tools")
            ]
            
            for i, (btn_text, key, page_name) in enumerate(nav_pages):
                with nav_cols[i]:
                    btn_type = "primary" if st.session_state.current_page == page_name else "secondary"
                    if st.button(btn_text, key=key, use_container_width=True, type=btn_type):
                        st.session_state.current_page = page_name
                        st.rerun()
        else:
            # Teacher sees only Dashboard, Cluster Profiles, and Self Assessment
            nav_cols = st.columns([1, 1, 1])
            
            nav_pages = [
                ("Dashboard", "nav_dashboard", "Dashboard"),
                ("Cluster Profiles", "nav_profiles", "Cluster Profiles"),
                ("Self Assessment", "nav_assessment", "Self Assessment")
            ]
            
            for i, (btn_text, key, page_name) in enumerate(nav_pages):
                with nav_cols[i]:
                    btn_type = "primary" if st.session_state.current_page == page_name else "secondary"
                    if st.button(btn_text, key=key, use_container_width=True, type=btn_type):
                        st.session_state.current_page = page_name
                        st.rerun()
        
        page = st.session_state.current_page
        
        # Security: Check if teacher is trying to access restricted pages
        if user_role == ROLE_TEACHER and page in ['Training Recommendations', 'Admin Tools']:
            logger.warning(f"Teacher user attempted to access restricted page: {page}")
            st.session_state.current_page = 'Dashboard'
            page = 'Dashboard'
        
        st.markdown("---")
        
        # Route to appropriate page with error handling
        try:
            if page == "Dashboard":
                show_dashboard(df)
            elif page == "Cluster Profiles":
                show_cluster_profiles(df)
            elif page == "Training Recommendations":
                if user_role == ROLE_ADMIN:
                    show_recommendations(df)
                else:
                    st.error("🔒 Access Denied: This page is only available to administrators.")
            elif page == "Self Assessment":
                show_self_assessment(df)
            elif page == "Admin Tools":
                if user_role == ROLE_ADMIN:
                    show_admin_tools(df)
                else:
                    st.error("🔒 Access Denied: This page is only available to administrators.")
            else:
                logger.warning(f"Unknown page requested: {page}")
                st.error("Page not found. Redirecting to Dashboard.")
                st.session_state.current_page = 'Dashboard'
                st.rerun()
        except Exception as e:
            logger.error(f"Error displaying page {page}: {e}")
            st.error("An error occurred while loading the page. Please try again.")
            st.exception(e)
    
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        st.error("A fatal error occurred. Please refresh the page or contact support.")
        st.exception(e)


if __name__ == "__main__":
    main()
