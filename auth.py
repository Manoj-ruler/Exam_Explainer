"""
Authentication Module - Supabase Auth Integration
Handles user login, signup, and session management
"""

import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()


def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        raise ValueError("Supabase credentials not found in environment")
    
    return create_client(url, key)


def signup(email: str, password: str) -> dict:
    """
    Create new user account
    
    Returns:
        dict with 'success' boolean and 'user' or 'error'
    """
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            return {"success": True, "user": response.user}
        else:
            return {"success": False, "error": "Signup failed"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def login(email: str, password: str) -> dict:
    """
    Login existing user
    
    Returns:
        dict with 'success' boolean and 'user'/'session' or 'error'
    """
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            return {
                "success": True, 
                "user": response.user,
                "session": response.session
            }
        else:
            return {"success": False, "error": "Login failed"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def logout() -> bool:
    """Sign out current user"""
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
        return True
    except Exception as e:
        print(f"Logout error: {e}")
        return False


def get_current_user():
    """
    Get currently logged in user from session state
    
    Returns:
        User object or None
    """
    return st.session_state.get("user", None)


def is_authenticated() -> bool:
    """Check if user is logged in"""
    return get_current_user() is not None


def init_auth_state():
    """Initialize authentication session state"""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "session" not in st.session_state:
        st.session_state.session = None


def set_user_session(user, session=None):
    """Store user in session state"""
    st.session_state.user = user
    st.session_state.session = session


def clear_user_session():
    """Clear user from session state"""
    st.session_state.user = None
    st.session_state.session = None


def get_google_oauth_url() -> str:
    """
    Get the Google OAuth sign-in URL (using implicit flow for Streamlit compatibility)
    
    Returns:
        OAuth URL to redirect user to
    """
    try:
        supabase = get_supabase_client()
        redirect_url = os.getenv("REDIRECT_URL", "http://localhost:8501")
        
        # Use implicit flow - returns access_token in URL hash
        # This avoids PKCE code_verifier issues with Streamlit
        response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": redirect_url,
                "skip_browser_redirect": False,
                "query_params": {
                    "access_type": "offline",
                    "prompt": "consent"
                }
            }
        })
        
        return response.url if response else None
    except Exception as e:
        print(f"Google OAuth error: {e}")
        return None


def handle_oauth_callback(access_token: str, refresh_token: str = None) -> dict:
    """
    Handle OAuth callback and set user session
    
    Args:
        access_token: OAuth access token from URL
        refresh_token: Optional refresh token
    
    Returns:
        dict with 'success' and 'user' or 'error'
    """
    try:
        supabase = get_supabase_client()
        
        # Set the session with the tokens
        response = supabase.auth.set_session(access_token, refresh_token or "")
        
        if response.user:
            return {
                "success": True,
                "user": response.user,
                "session": response.session
            }
        return {"success": False, "error": "Failed to set session"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def exchange_code_for_session(code: str) -> dict:
    """
    Exchange OAuth authorization code for session (PKCE flow)
    
    Args:
        code: Authorization code from OAuth redirect
    
    Returns:
        dict with 'success' and 'user' or 'error'
    """
    try:
        supabase = get_supabase_client()
        
        # Exchange code for session
        response = supabase.auth.exchange_code_for_session({"auth_code": code})
        
        if response.user:
            return {
                "success": True,
                "user": response.user,
                "session": response.session
            }
        return {"success": False, "error": "Failed to exchange code"}
    except Exception as e:
        return {"success": False, "error": str(e)}

