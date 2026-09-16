import streamlit as st
import requests
import uuid

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Infera AI",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deep Sapphire & Obsidian Glassmorphism Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #070b14 !important;
        background-image: radial-gradient(at 10% 15%, #0f1c3f 0px, transparent 55%), 
                          radial-gradient(at 90% 85%, #082f49 0px, transparent 55%) !important;
        color: #f1f5f9 !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    [data-testid="stBottom"], [data-testid="stBottom"] > div {
        background-color: #070b14 !important;
        border-top: 1px solid rgba(56, 189, 248, 0.12) !important;
    }

    [data-testid="stSidebar"], [data-testid="stSidebarContent"] {
        background-color: #04070e !important;
        border-right: 1px solid rgba(56, 189, 248, 0.15) !important;
    }

    .brand-title {
        font-size: 1.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 12px;
    }

    /* Primary New Chat Button */
    .new-chat-btn button {
        background: linear-gradient(135deg, #0284c7 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35) !important;
        transition: all 0.2s ease !important;
    }
    .new-chat-btn button:hover {
        opacity: 0.95 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.5) !important;
    }

    /* Recents Session Item Buttons */
    .history-btn button {
        background: rgba(15, 23, 42, 0.6) !important;
        color: #cbd5e1 !important;
        border: 1px solid rgba(56, 189, 248, 0.08) !important;
        border-radius: 8px !important;
        text-align: left !important;
        padding: 8px 12px !important;
        font-size: 0.85rem !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        width: 100% !important;
        transition: all 0.15s ease !important;
    }
    .history-btn button:hover {
        background: rgba(30, 41, 59, 0.8) !important;
        color: #38bdf8 !important;
        border-color: rgba(56, 189, 248, 0.3) !important;
    }

    /* Active Session Highlight */
    .active-history-btn button {
        background: rgba(56, 189, 248, 0.15) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        font-weight: 600 !important;
    }

    /* Delete Button Styling */
    .delete-btn button {
        background: transparent !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
        color: #ef4444 !important;
        padding: 8px 0px !important;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
        width: 100% !important;
        transition: all 0.15s ease !important;
    }
    .delete-btn button:hover {
        background: rgba(239, 68, 68, 0.15) !important;
        border-color: rgba(239, 68, 68, 0.6) !important;
        color: #f87171 !important;
    }

    /* Clear All Button */
    .clear-all-btn button {
        background: transparent !important;
        border: none !important;
        color: #94a3b8 !important;
        font-size: 0.75rem !important;
        padding: 2px 4px !important;
        text-decoration: underline !important;
    }
    .clear-all-btn button:hover {
        color: #ef4444 !important;
    }

    /* Main Welcome Cards */
    div[data-testid="stMainBlockContainer"] .stButton > button {
        background: rgba(12, 19, 34, 0.75) !important;
        border: 1px solid rgba(56, 189, 248, 0.18) !important;
        border-radius: 14px !important;
        padding: 16px !important;
        color: #e2e8f0 !important;
        text-align: left !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
        backdrop-filter: blur(12px) !important;
    }

    div[data-testid="stChatMessage"] {
        background: rgba(12, 19, 34, 0.6) !important;
        border: 1px solid rgba(56, 189, 248, 0.12) !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        backdrop-filter: blur(8px) !important;
    }

    [data-testid="stChatInput"] {
        background-color: #0c1322 !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        border-radius: 16px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 1. State Management: Multi-Chat Architecture
if "sessions" not in st.session_state:
    initial_id = str(uuid.uuid4())[:8]
    st.session_state.sessions = {
        initial_id: {"title": "New Chat", "messages": []}
    }
    st.session_state.current_session_id = initial_id

if "current_session_id" not in st.session_state or st.session_state.current_session_id not in st.session_state.sessions:
    st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]

# 2. Fetch Models and Personas from Backend
try:
    health_resp = requests.get(f"{API_BASE_URL}/", timeout=2).json()
    available_models = health_resp.get("available_models", ["Auto Free Route", "Llama 3 8B (Free)", "Mistral 7B (Free)", "DeepSeek R1 (Free)"])
    available_personas = health_resp.get("available_personas", ["Helpful Assistant", "Senior Code Reviewer", "Academic Examiner"])
except Exception:
    available_models = ["Auto Free Route", "Llama 3 8B (Free)", "Mistral 7B (Free)", "DeepSeek R1 (Free)"]
    available_personas = ["Helpful Assistant", "Senior Code Reviewer", "Academic Examiner"]

# 3. Sidebar: Navigation & Session Controls
with st.sidebar:
    st.markdown('<div class="brand-title">💠 Infera AI</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
    if st.button("➕ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())[:8]
        st.session_state.sessions[new_id] = {"title": "New Chat", "messages": []}
        st.session_state.current_session_id = new_id
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("⚙️ Engine & Persona Settings", expanded=False):
        selected_persona = st.selectbox("System Persona", available_personas)
        selected_model = st.selectbox("Inference Engine", available_models)

    st.markdown("---")
    
    # Recents Header with Clear All
    col_h1, col_h2 = st.columns([0.65, 0.35])
    with col_h1:
        st.caption("RECENTS")
    with col_h2:
        st.markdown('<div class="clear-all-btn">', unsafe_allow_html=True)
        if st.button("Clear all", help="Delete all chat history"):
            fresh_id = str(uuid.uuid4())[:8]
            st.session_state.sessions = {fresh_id: {"title": "New Chat", "messages": []}}
            st.session_state.current_session_id = fresh_id
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Render Sessions with Individual Delete Icon
    for sess_id, sess_data in reversed(list(st.session_state.sessions.items())):
        is_active = sess_id == st.session_state.current_session_id
        btn_class = "active-history-btn" if is_active else "history-btn"
        display_title = sess_data["title"][:16] + "..." if len(sess_data["title"]) > 16 else sess_data["title"]
        
        c1, c2 = st.columns([0.80, 0.20])
        with c1:
            st.markdown(f'<div class="{btn_class}">', unsafe_allow_html=True)
            if st.button(f"💬 {display_title}", key=f"btn_{sess_id}", use_container_width=True):
                st.session_state.current_session_id = sess_id
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{sess_id}", help="Delete this chat", use_container_width=True):
                del st.session_state.sessions[sess_id]
                if not st.session_state.sessions:
                    fresh_id = str(uuid.uuid4())[:8]
                    st.session_state.sessions[fresh_id] = {"title": "New Chat", "messages": []}
                    st.session_state.current_session_id = fresh_id
                elif st.session_state.current_session_id == sess_id:
                    st.session_state.current_session_id = list(st.session_state.sessions.keys())[-1]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# Active chat session shortcut
current_chat = st.session_state.sessions[st.session_state.current_session_id]

# 4. Input handling
prompt = st.chat_input("Message Infera AI...")
if prompt:
    if len(current_chat["messages"]) == 0:
        current_chat["title"] = prompt[:20]
    current_chat["messages"].append({"role": "user", "content": prompt})

# 5. Welcome Screen Cards
if len(current_chat["messages"]) == 0:
    st.markdown("<h2 style='text-align: center; margin-top: 50px; margin-bottom: 30px; font-weight:700;'>What can I help with?</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💡 **System Architecture**\n\nDesign a scalable microservice architecture for ML APIs", use_container_width=True):
            current_chat["title"] = "System Architecture"
            current_chat["messages"].append({"role": "user", "content": "Design a scalable microservice architecture for ML APIs"})
            st.rerun()
        if st.button("💻 **Code Review & Optimization**\n\nAnalyze time complexity and suggest vectorization improvements", use_container_width=True):
            current_chat["title"] = "Code Review"
            current_chat["messages"].append({"role": "user", "content": "Analyze time complexity and suggest vectorization improvements"})
            st.rerun()
    with col2:
        if st.button("🔬 **Viva & Concept Defense**\n\nExplain the mathematical derivation of Self-Attention mechanism", use_container_width=True):
            current_chat["title"] = "Self-Attention Math"
            current_chat["messages"].append({"role": "user", "content": "Explain the mathematical derivation of Self-Attention mechanism"})
            st.rerun()
        if st.button("📑 **Technical Documentation**\n\nGenerate a structured markdown README for a GitHub repository", use_container_width=True):
            current_chat["title"] = "Technical Docs"
            current_chat["messages"].append({"role": "user", "content": "Generate a structured markdown README for a GitHub repository"})
            st.rerun()

# 6. Render Active Chat Messages
for msg in current_chat["messages"]:
    avatar = "🔴" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# 7. Stream Assistant Response
if current_chat["messages"] and current_chat["messages"][-1]["role"] == "user":
    with st.chat_message("assistant", avatar="🤖"):
        response_container = st.empty()
        full_response = ""

        payload = {
            "messages": current_chat["messages"],
            "persona": selected_persona if 'selected_persona' in locals() else "Helpful Assistant",
            "model_name": selected_model if 'selected_model' in locals() else "Auto Free Route"
        }

        try:
            with requests.post(f"{API_BASE_URL}/chat/stream", json=payload, stream=True, timeout=(10, 45)) as r:
                if r.status_code == 200:
                    for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                        if chunk:
                            full_response += chunk
                            response_container.markdown(full_response + "▌")
                    response_container.markdown(full_response)
                else:
                    err_msg = f"API Error ({r.status_code}): {r.text}"
                    response_container.error(err_msg)
                    full_response = err_msg
        except requests.exceptions.Timeout:
            err_msg = "⏱️ Gateway Timeout: The inference provider queue is currently congested. Please select another engine from settings and retry."
            response_container.error(err_msg)
            full_response = err_msg
        except requests.exceptions.ConnectionError:
            err_msg = "Connection Refused: FastAPI backend gateway is offline. Run `uvicorn api:app --reload --port 8000`."
            response_container.error(err_msg)
            full_response = err_msg
        except Exception as e:
            err_msg = f"Inference Failure: {str(e)}"
            response_container.error(err_msg)
            full_response = err_msg