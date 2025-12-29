"""
Exam Explainer Bot - Main Streamlit Application
RAG-based chatbot with Supabase auth and vector database
"""

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modules
from gemini_client import GeminiClient
from prompts import get_system_prompt, LANGUAGE_PROMPTS
from analytics import SessionAnalytics, detect_topic, is_prohibited_query
from auth import (
    init_auth_state, login, signup, logout,
    is_authenticated, get_current_user,
    set_user_session, clear_user_session
)
from database import (
    create_chat_session, get_user_sessions, 
    save_message, get_session_messages,
    delete_chat_session, update_session_title
)
from rag import generate_rag_response, format_citations, get_knowledge_base

# Page configuration
st.set_page_config(
    page_title="Exam Explainer Bot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Modern Premium Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        transition: all 0.2s ease;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, .stDeployButton { visibility: hidden; }
    [data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"] { display: none !important; }
    
    /* ===== MAIN APP BACKGROUND ===== */
    .stApp { 
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ed 100%);
    }
    
    .main .block-container {
        max-width: 800px !important;
        margin: 0 auto !important;
        padding: 2rem 1rem !important;
    }
    
    /* ===== PREMIUM DARK SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
        min-width: 300px !important;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
        padding: 1.5rem !important;
    }
    
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        padding: 0.75rem 1rem !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
    
    [data-testid="stSidebar"] .stTextInput input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
    }
    
    [data-testid="stSidebar"] hr { 
        border-color: rgba(255,255,255,0.1) !important; 
        margin: 1.5rem 0 !important;
    }
    
    .section-label {
        font-size: 0.7rem;
        color: #8b8b9a !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        padding: 1rem 0 0.5rem 0;
    }
    
    /* ===== WELCOME SCREEN ===== */
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 4rem 2rem;
        animation: fadeIn 0.6s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .mascot {
        width: 100px;
        height: 100px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .greeting { text-align: center; }
    .greeting h1 {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin: 0 0 0.5rem 0;
    }
    .greeting h2 {
        font-size: 1.5rem;
        font-weight: 400;
        color: #4a4a6a;
        margin: 0;
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600;
    }
    
    /* ===== QUICK ACTION BUTTONS ===== */
    .stButton > button {
        background: white !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 16px !important;
        color: #1a1a2e !important;
        font-weight: 500 !important;
        padding: 1rem 1.5rem !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .stButton > button:hover { 
        background: white !important;
        border-color: #667eea !important;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
        transform: translateY(-2px);
    }
    
    /* ===== CHAT MESSAGES ===== */
    [data-testid="stChatMessage"] {
        background: white !important;
        border-radius: 20px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        border: none !important;
        box-shadow: 0 2px 15px rgba(0,0,0,0.05);
    }
    
    [data-testid="stChatMessage"] *, 
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] div {
        color: #1a1a2e !important;
    }
    
    /* Chat input */
    .stChatInput > div {
        background: white !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    .stChatInput > div:focus-within {
        border-color: #667eea !important;
        box-shadow: 0 4px 25px rgba(102, 126, 234, 0.2);
    }
    
    /* ===== AUTH/LOGIN PAGE ===== */
    .auth-card {
        background: white;
        border-radius: 24px;
        padding: 3rem;
        box-shadow: 0 10px 50px rgba(0,0,0,0.1);
        max-width: 420px;
        margin: 2rem auto;
    }
    
    .auth-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Form buttons - gradient */
    [data-testid="stForm"] button[type="submit"],
    .stForm button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.9rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    [data-testid="stForm"] button[type="submit"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5);
    }
    
    /* Form inputs */
    .stTextInput input {
        background: #f8f9fa !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 12px !important;
        color: #1a1a2e !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
    }
    
    .stTextInput input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15) !important;
    }
    
    .stTextInput label, .stForm label {
        color: #1a1a2e !important;
        font-weight: 500 !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #6b6b7b !important;
        font-weight: 500 !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 10px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* ===== STATUS BADGES ===== */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .badge-success { background: #d4edda; color: #155724; }
    .badge-info { background: #e7e3ff; color: #5a4fcf; }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    init_auth_state()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "gemini_client" not in st.session_state:
        st.session_state.gemini_client = None
    if "selected_language" not in st.session_state:
        st.session_state.selected_language = "English"
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    if "api_key_set" not in st.session_state:
        st.session_state.api_key_set = False
    if "oauth_processed" not in st.session_state:
        st.session_state.oauth_processed = False


def handle_oauth_callback():
    """Handle OAuth callback - capture tokens from URL hash fragment"""
    import streamlit.components.v1 as components
    params = st.query_params
    
    # Use components.html to execute JavaScript that captures hash fragment
    # This handles email verification and OAuth redirects with tokens in URL hash
    components.html("""
    <script>
        if (window.parent.location.hash && window.parent.location.hash.includes('access_token')) {
            const hash = window.parent.location.hash.substring(1);
            const params = new URLSearchParams(hash);
            const accessToken = params.get('access_token');
            const refreshToken = params.get('refresh_token') || '';
            if (accessToken) {
                window.parent.location.href = window.parent.location.pathname + '?access_token=' + encodeURIComponent(accessToken) + '&refresh_token=' + encodeURIComponent(refreshToken);
            }
        }
    </script>
    """, height=0)
    
    # Check for access_token in query params
    if "access_token" in params and not st.session_state.oauth_processed:
        access_token = params.get("access_token")
        refresh_token = params.get("refresh_token", "")
        
        if access_token:
            from auth import handle_oauth_callback as auth_oauth_callback
            result = auth_oauth_callback(access_token, refresh_token)
            
            if result["success"]:
                set_user_session(result["user"], result.get("session"))
                st.session_state.oauth_processed = True
                st.query_params.clear()
                st.rerun()
            else:
                st.error(f"Login error: {result.get('error')}")
                st.query_params.clear()


def setup_gemini():
    """Setup Gemini client"""
    if not st.session_state.api_key_set:
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            try:
                client = GeminiClient(api_key=api_key)
                client.start_chat(get_system_prompt("", st.session_state.selected_language))
                st.session_state.gemini_client = client
                st.session_state.api_key_set = True
            except Exception as e:
                print(f"Gemini setup error: {e}")


def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 17:
        return "Good Afternoon"
    return "Good Evening"


# ============ AUTH PAGES ============

def render_login_page():
    """Render login/signup page"""
    st.markdown("""
    <div class="welcome-container">
        <div class="mascot">🎓</div>
        <div class="greeting">
            <h1>Welcome to Exam Explainer</h1>
            <h2><span class="gradient-text">Sign in to continue</span></h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if email and password:
                    result = login(email, password)
                    if result["success"]:
                        set_user_session(result["user"], result.get("session"))
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(result.get("error", "Login failed"))
                else:
                    st.warning("Please enter email and password")
    
    with tab2:
        with st.form("signup_form"):
            email = st.text_input("Email", placeholder="your@email.com", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_pass")
            password2 = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Sign Up", use_container_width=True)
            
            if submitted:
                if password != password2:
                    st.error("Passwords don't match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                elif email and password:
                    result = signup(email, password)
                    if result["success"]:
                        st.success("Account created! Please check your email to verify.")
                    else:
                        st.error(result.get("error", "Signup failed"))


# ============ MAIN APP ============

def render_sidebar():
    """Render authenticated sidebar"""
    with st.sidebar:
        user = get_current_user()
        user_email = user.email if user else "User"
        
        st.markdown(f"### 🎓 Exam Explainer")
        st.markdown(f"<small>👤 {user_email}</small>", unsafe_allow_html=True)
        
        # New Chat button
        if st.button("✨ New Chat", use_container_width=True):
            if user:
                session = create_chat_session(user.id)
                if session:
                    st.session_state.current_session_id = session["id"]
                    st.session_state.messages = []
                    st.rerun()
        
        st.markdown("---")
        
        # Chat history
        st.markdown('<div class="section-label">Your Chats</div>', unsafe_allow_html=True)
        
        if user:
            sessions = get_user_sessions(user.id)
            for session in sessions[:10]:  # Show last 10
                title = session.get("title", "New conversation")[:25]
                is_active = session["id"] == st.session_state.current_session_id
                
                col1, col2 = st.columns([5, 1])
                with col1:
                    if st.button(f"💬 {title}", key=f"session_{session['id']}", use_container_width=True):
                        st.session_state.current_session_id = session["id"]
                        st.session_state.messages = get_session_messages(session["id"])
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"del_{session['id']}"):
                        delete_chat_session(session["id"])
                        if session["id"] == st.session_state.current_session_id:
                            st.session_state.current_session_id = None
                            st.session_state.messages = []
                        st.rerun()
        
        st.markdown("---")
        
        # Language
        st.markdown('<div class="section-label">Language</div>', unsafe_allow_html=True)
        language = st.selectbox(
            "Language",
            options=list(LANGUAGE_PROMPTS.keys()),
            index=list(LANGUAGE_PROMPTS.keys()).index(st.session_state.selected_language),
            label_visibility="collapsed"
        )
        if language != st.session_state.selected_language:
            st.session_state.selected_language = language
        
        # Knowledge base status
        st.markdown("---")
        kb = get_knowledge_base()
        doc_count = len(kb.documents) if kb.documents else 0
        st.markdown(f"📚 **Knowledge Base:** {doc_count} chunks")
        
        # Logout
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            clear_user_session()
            st.session_state.messages = []
            st.session_state.current_session_id = None
            st.rerun()


def handle_user_input(user_input: str):
    """Process user input with RAG"""
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Save to database
    if st.session_state.current_session_id:
        save_message(st.session_state.current_session_id, "user", user_input)
        
        # Update session title if first message
        if len(st.session_state.messages) == 1:
            title = user_input[:30] + "..." if len(user_input) > 30 else user_input
            update_session_title(st.session_state.current_session_id, title)
    
    # Check prohibited queries
    if is_prohibited_query(user_input):
        response = "I cannot help with that. I explain exam processes, not predict grades or provide answers."
        st.session_state.messages.append({"role": "assistant", "content": response})
        if st.session_state.current_session_id:
            save_message(st.session_state.current_session_id, "assistant", response)
        return
    
    # Generate RAG response
    try:
        response, sources = generate_rag_response(
            user_input,
            st.session_state.gemini_client,
            st.session_state.selected_language
        )
        
        # Add citations if sources found
        if sources:
            response += format_citations(sources)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        if st.session_state.current_session_id:
            save_message(
                st.session_state.current_session_id, 
                "assistant", 
                response,
                citations=[s.get("id") for s in sources] if sources else []
            )
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        st.session_state.messages.append({"role": "assistant", "content": error_msg})


def render_chat():
    """Render chat interface"""
    # Welcome screen if no messages
    if not st.session_state.messages:
        user = get_current_user()
        name = user.email.split("@")[0] if user else "Student"
        
        st.markdown(f"""
        <div class="welcome-container">
            <div class="mascot">🎓</div>
            <div class="greeting">
                <h1>{get_greeting()}, {name}</h1>
                <h2>How Can I <span class="gradient-text">Assist You Today?</span></h2>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick questions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Explain grading", use_container_width=True):
                handle_user_input("Explain the grading system")
                st.rerun()
            if st.button("📊 CGPA calculation", use_container_width=True):
                handle_user_input("How is CGPA calculated?")
                st.rerun()
        with col2:
            if st.button("🔄 Revaluation", use_container_width=True):
                handle_user_input("What is the revaluation process?")
                st.rerun()
            if st.button("📋 Exam rules", use_container_width=True):
                handle_user_input("What are the exam rules?")
                st.rerun()
    
    # Display messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Chat input
    if st.session_state.api_key_set and st.session_state.gemini_client:
        if prompt := st.chat_input("Message Exam Explainer..."):
            # Create session if needed
            user = get_current_user()
            if user and not st.session_state.current_session_id:
                session = create_chat_session(user.id)
                if session:
                    st.session_state.current_session_id = session["id"]
            
            handle_user_input(prompt)
            st.rerun()


def main():
    """Main entry point"""
    initialize_session_state()
    handle_oauth_callback()  # Handle Google OAuth redirect
    setup_gemini()
    
    # Check authentication
    if not is_authenticated():
        render_login_page()
    else:
        render_sidebar()
        render_chat()


if __name__ == "__main__":
    main()
