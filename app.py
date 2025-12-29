"""
Exam Explainer Bot - Main Streamlit Application
A GenAI-powered chatbot that explains examination and evaluation processes
Clean responsive ChatGPT-style UI
"""

import streamlit as st
import os
from datetime import datetime

# Import our modules
from gemini_client import GeminiClient
from prompts import get_system_prompt, SAMPLE_QUERIES, DISCLAIMER, LANGUAGE_PROMPTS
from knowledge_base import KnowledgeBase
from analytics import SessionAnalytics, detect_topic, is_prohibited_query

# Page configuration
st.set_page_config(
    page_title="Exam Explainer Bot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Responsive ChatGPT style
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', -apple-system, sans-serif; }
    
    /* Hide Streamlit branding but keep header for toggle */
    #MainMenu, footer { visibility: hidden; }
    
    /* HIDE SIDEBAR COLLAPSE BUTTON - Make sidebar always visible */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    .css-1rs6os,
    .css-17lntkn,
    button[aria-label="Close sidebar"],
    button[aria-label="Collapse sidebar"],
    [data-testid="stSidebar"] button[kind="header"],
    [data-testid="baseButton-header"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Main app */
    .stApp { background: #FFFFFF; }
    
    /* ===== RESPONSIVE MAIN CONTENT - CENTERS RELATIVE TO VIEWPORT ===== */
    .main .block-container {
        max-width: 750px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-top: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* Make main area take full available width and center content */
    [data-testid="stAppViewContainer"] > .main {
        width: 100%;
    }
    
    /* ===== DARK SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: #171717 !important;
        width: 260px !important;
        min-width: 260px !important;
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
        border-radius: 10px !important;
        font-size: 0.9rem !important;
        padding: 0.7rem 1rem !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #262626 !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: #262626 !important;
        border: 1px solid #404040 !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: #333 !important;
        margin: 1rem 0 !important;
    }
    
    .section-label {
        font-size: 0.7rem;
        color: #888 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 0.75rem 0 0.5rem 0;
    }
    
    .chat-item {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.6rem 0.75rem;
        font-size: 0.85rem;
        border-radius: 8px;
        margin-bottom: 0.2rem;
        cursor: pointer;
        color: #ccc;
    }
    
    .chat-item:hover, .chat-item.active { background: #262626; color: #fff; }
    
    /* ===== MAIN CONTENT CENTER ===== */
    .content-wrapper {
        max-width: 700px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 3rem 0 2rem 0;
    }
    
    .mascot {
        width: 70px;
        height: 70px;
        background: linear-gradient(135deg, #F3E8FF 0%, #DDD6FE 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.12);
    }
    
    .greeting { text-align: center; }
    
    .greeting h1, .greeting h2 {
        font-size: 1.7rem;
        font-weight: 600;
        color: #171717;
        margin: 0;
        line-height: 1.3;
    }
    
    .gradient-text {
        background: linear-gradient(90deg, #8B5CF6 0%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* ===== QUICK BUTTONS ===== */
    .quick-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        justify-content: center;
        margin-top: 2rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .stButton > button {
        background: #FFFFFF !important;
        border: 1px solid #E5E5E5 !important;
        border-radius: 12px !important;
        color: #374151 !important;
        font-size: 0.9rem !important;
        font-weight: 400 !important;
        padding: 0.75rem 1.25rem !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.15s !important;
    }
    
    .stButton > button:hover {
        background: #F9FAFB !important;
        border-color: #D1D5DB !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    
    /* ===== CHAT MESSAGES ===== */
    [data-testid="stChatMessage"] {
        background: #F7F7F8 !important;
        border-radius: 16px !important;
        padding: 1.25rem !important;
        border: none !important;
        margin-bottom: 1rem;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* ===== CHAT INPUT ===== */
    .stChatInput {
        max-width: 700px !important;
        margin: 0 auto !important;
    }
    
    .stChatInput > div {
        background: #FFFFFF !important;
        border: 1px solid #E5E5E5 !important;
        border-radius: 16px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .stChatInput input {
        background: transparent !important;
        color: #171717 !important;
        font-size: 0.95rem !important;
    }
    
    .stChatInput input::placeholder {
        color: #9CA3AF !important;
    }
    
    /* Hide alert box */
    .stAlert { display: none !important; }
    
    /* Hide deploy button */
    .stDeployButton { display: none !important; }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "gemini_client" not in st.session_state:
        st.session_state.gemini_client = None
    if "knowledge_base" not in st.session_state:
        st.session_state.knowledge_base = KnowledgeBase()
    if "analytics" not in st.session_state:
        st.session_state.analytics = SessionAnalytics()
    if "selected_language" not in st.session_state:
        st.session_state.selected_language = "English"
    if "api_key_set" not in st.session_state:
        st.session_state.api_key_set = False


def setup_gemini_client(api_key: str) -> bool:
    try:
        client = GeminiClient(api_key=api_key)
        context = st.session_state.knowledge_base.get_context_for_query("")
        system_prompt = get_system_prompt(context, st.session_state.selected_language)
        client.start_chat(system_prompt)
        st.session_state.gemini_client = client
        st.session_state.api_key_set = True
        return True
    except:
        return False


def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 17:
        return "Good Afternoon"
    return "Good Evening"


def render_sidebar():
    with st.sidebar:
        st.markdown("### 🎓 Exam Explainer")
        
        if st.button("✨ New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.analytics = SessionAnalytics()
            if st.session_state.gemini_client:
                context = st.session_state.knowledge_base.get_context_for_query("")
                system_prompt = get_system_prompt(context, st.session_state.selected_language)
                st.session_state.gemini_client.reset_chat(system_prompt)
            st.rerun()
        
        st.markdown("---")
        
        st.markdown('<div class="section-label">Today</div>', unsafe_allow_html=True)
        
        title = st.session_state.messages[0]["content"][:20] + "..." if st.session_state.messages else "New conversation"
        st.markdown(f'<div class="chat-item active">💬 {title}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-label">Previous</div>', unsafe_allow_html=True)
        for chat in ["CGPA calculation", "Revaluation process", "Attendance rules"]:
            st.markdown(f'<div class="chat-item">💬 {chat}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown('<div class="section-label">Language</div>', unsafe_allow_html=True)
        language = st.selectbox(
            "Language",
            options=list(LANGUAGE_PROMPTS.keys()),
            index=list(LANGUAGE_PROMPTS.keys()).index(st.session_state.selected_language),
            label_visibility="collapsed"
        )
        if language != st.session_state.selected_language:
            st.session_state.selected_language = language
            if st.session_state.gemini_client:
                context = st.session_state.knowledge_base.get_context_for_query("")
                system_prompt = get_system_prompt(context, language)
                st.session_state.gemini_client.start_chat(system_prompt)


def handle_user_input(user_input: str):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    topic = detect_topic(user_input)
    st.session_state.analytics.record_question(topic, st.session_state.selected_language)
    
    if is_prohibited_query(user_input):
        response = "I cannot help with that. I explain exam processes only, not predict grades or provide answers."
        st.session_state.messages.append({"role": "assistant", "content": response})
        return
    
    context = st.session_state.knowledge_base.get_context_for_query(user_input)
    system_prompt = get_system_prompt(context, st.session_state.selected_language)
    st.session_state.gemini_client._system_prompt = system_prompt
    
    try:
        response = st.session_state.gemini_client.generate_response(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
    except Exception as e:
        st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})


def main():
    initialize_session_state()
    
    # Auto-load API key
    if not st.session_state.api_key_set:
        env_key = os.getenv("GOOGLE_API_KEY")
        if env_key:
            setup_gemini_client(env_key)
    
    render_sidebar()
    
    # Welcome screen
    if not st.session_state.messages:
        st.markdown(f"""
        <div class="content-wrapper">
            <div class="welcome-container">
                <div class="mascot">🎓</div>
                <div class="greeting">
                    <h1>{get_greeting()}, Student</h1>
                    <h2>How Can I <span class="gradient-text">Assist You Today?</span></h2>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick questions
        if st.session_state.api_key_set:
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Centered button layout
            _, c1, c2, _ = st.columns([1, 2, 2, 1])
            
            with c1:
                if st.button("📝 Explain grading", use_container_width=True):
                    handle_user_input("Explain grading system")
                    st.rerun()
                if st.button("📊 CGPA calculation", use_container_width=True):
                    handle_user_input("How is CGPA calculated?")
                    st.rerun()
            
            with c2:
                if st.button("🔄 Revaluation", use_container_width=True):
                    handle_user_input("What is revaluation process?")
                    st.rerun()
                if st.button("📋 Exam rules", use_container_width=True):
                    handle_user_input("What are exam rules?")
                    st.rerun()
    
    # Display messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Chat input - always visible
    if st.session_state.api_key_set and st.session_state.gemini_client:
        if prompt := st.chat_input("Message Exam Explainer..."):
            handle_user_input(prompt)
            st.rerun()


if __name__ == "__main__":
    main()
