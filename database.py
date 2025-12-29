"""
Database Module - Supabase PostgreSQL Integration
Handles chat sessions and message persistence
"""

from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Optional
import uuid

load_dotenv()


def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        raise ValueError("Supabase credentials not found")
    
    return create_client(url, key)


# ============ CHAT SESSIONS ============

def create_chat_session(user_id: str, title: str = "New conversation") -> Optional[dict]:
    """
    Create a new chat session
    
    Returns:
        Chat session dict or None
    """
    try:
        supabase = get_supabase_client()
        response = supabase.table("chat_sessions").insert({
            "user_id": user_id,
            "title": title
        }).execute()
        
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error creating session: {e}")
        return None


def get_user_sessions(user_id: str) -> List[dict]:
    """
    Get all chat sessions for a user, ordered by most recent
    
    Returns:
        List of session dicts
    """
    try:
        supabase = get_supabase_client()
        response = supabase.table("chat_sessions")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
        
        return response.data if response.data else []
    except Exception as e:
        print(f"Error getting sessions: {e}")
        return []


def update_session_title(session_id: str, title: str) -> bool:
    """Update the title of a chat session"""
    try:
        supabase = get_supabase_client()
        supabase.table("chat_sessions")\
            .update({"title": title})\
            .eq("id", session_id)\
            .execute()
        return True
    except Exception as e:
        print(f"Error updating title: {e}")
        return False


def delete_chat_session(session_id: str) -> bool:
    """Delete a chat session and all its messages"""
    try:
        supabase = get_supabase_client()
        # Messages will be deleted via CASCADE
        supabase.table("chat_sessions")\
            .delete()\
            .eq("id", session_id)\
            .execute()
        return True
    except Exception as e:
        print(f"Error deleting session: {e}")
        return False


# ============ MESSAGES ============

def save_message(session_id: str, role: str, content: str, citations: list = None) -> Optional[dict]:
    """
    Save a message to a chat session
    
    Args:
        session_id: Chat session UUID
        role: 'user' or 'assistant'
        content: Message text
        citations: List of referenced document IDs
    
    Returns:
        Message dict or None
    """
    try:
        supabase = get_supabase_client()
        response = supabase.table("messages").insert({
            "session_id": session_id,
            "role": role,
            "content": content,
            "citations": citations or []
        }).execute()
        
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error saving message: {e}")
        return None


def get_session_messages(session_id: str) -> List[dict]:
    """
    Get all messages for a chat session, ordered by time
    
    Returns:
        List of message dicts
    """
    try:
        supabase = get_supabase_client()
        response = supabase.table("messages")\
            .select("*")\
            .eq("session_id", session_id)\
            .order("created_at", desc=False)\
            .execute()
        
        return response.data if response.data else []
    except Exception as e:
        print(f"Error getting messages: {e}")
        return []


# ============ USER PREFERENCES ============

def get_user_preferences(user_id: str) -> dict:
    """Get user preferences, create if not exists"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("user_preferences")\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()
        
        if response.data:
            return response.data[0]
        
        # Create default preferences
        new_prefs = supabase.table("user_preferences").insert({
            "user_id": user_id,
            "language": "English"
        }).execute()
        
        return new_prefs.data[0] if new_prefs.data else {"language": "English"}
    except Exception as e:
        print(f"Error getting preferences: {e}")
        return {"language": "English"}


def update_user_preferences(user_id: str, language: str) -> bool:
    """Update user preferences"""
    try:
        supabase = get_supabase_client()
        supabase.table("user_preferences")\
            .upsert({
                "user_id": user_id,
                "language": language
            })\
            .execute()
        return True
    except Exception as e:
        print(f"Error updating preferences: {e}")
        return False
