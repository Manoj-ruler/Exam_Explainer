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
from rag import generate_rag_response, format_citations
from vector_store import get_document_count

# Page configuration
st.set_page_config(
    page_title="Exam Explainer Bot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Inter', -apple-system, sans-serif; }
    
    #MainMenu, footer { visibility: hidden; }
    
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    
    .stApp { background: #FFFFFF; }
    
    .main .block-container {
        max-width: 750px !important;
        margin: 0 auto !important;
        padding-top: 2rem !important;
    }
    
    /* Dark Sidebar */
    [data-testid="stSidebar"] {
        background: #171717 !important;
        min-width: 280px !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: #171717 !important;
        padding: 1rem !important;
    }
    
    [data-testid="stSidebar"] * { color: #ECECEC !important; }
    
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: 1px solid #404040 !important;
        color: #ECECEC !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #262626 !important;
    }
    
    [data-testid="stSidebar"] .stTextInput input {
        background: #262626 !important;
        border: 1px solid #404040 !important;
        border-radius: 8px !important;
        color: #ECECEC !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: #262626 !important;
        border: 1px solid #404040 !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stSidebar"] hr { border-color: #333 !important; }
    
    .section-label {
        font-size: 0.7rem;
        color: #888 !important;
        text-transform: uppercase;
        padding: 0.75rem 0 0.5rem 0;
    }
    
    .chat-item {
        padding: 0.6rem 0.75rem;
        font-size: 0.85rem;
        border-radius: 8px;
        margin-bottom: 0.25rem;
        cursor: pointer;
    }
    
    .chat-item:hover, .chat-item.active { background: #262626; }
    
    /* Welcome */
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 2rem 0;
    }
    
    .mascot {
        width: 70px;
        height: 70px;
        background: linear-gradient(135deg, #F3E8FF 0%, #E9D5FF 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        margin-bottom: 1.5rem;
    }
    
    .greeting { text-align: center; }
    .greeting h1, .greeting h2 {
        font-size: 1.6rem;
        font-weight: 600;
        color: #171717;
        margin: 0;
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #8B5CF6 0%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Buttons */
    .stButton > button {
        background: #FFFFFF !important;
        border: 1px solid #E5E5E5 !important;
        border-radius: 12px !important;
        color: #171717 !important;
    }
    
    .stButton > button:hover { background: #F9FAFB !important; }
    
    /* Chat */
    [data-testid="stChatMessage"] {
        background: #F7F7F8 !important;
        border-radius: 16px !important;
        padding: 1.25rem !important;
        border: none !important;
    }
    
    [data-testid="stChatMessage"] * {
        color: #171717 !important;
    }
    
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] div {
        color: #171717 !important;
    }
    
    .stChatInput > div {
        background: #FFFFFF !important;
        border: 1px solid #E5E5E5 !important;
        border-radius: 16px !important;
    }
    
    /* Auth forms */
    .auth-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    .auth-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Form submit buttons - purple gradient */
    [data-testid="stForm"] button[type="submit"],
    .stForm button {
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stForm"] button[type="submit"]:hover,
    .stForm button:hover {
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important;
    }
    
    /* Form inputs */
    .stTextInput input {
        background: #FFFFFF !important;
        border: 1px solid #E5E5E5 !important;
        border-radius: 8px !important;
        color: #171717 !important;
    }
    
    .stTextInput input:focus {
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
    }
    
    /* Tabs - Login/Sign Up */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #666 !important;
        font-weight: 500 !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #8B5CF6 !important;
        border-bottom-color: #8B5CF6 !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #8B5CF6 !important;
    }
    
    /* Labels */
    .stTextInput label,
    .stForm label {
        color: #171717 !important;
    }
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
        doc_count = get_document_count()
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
