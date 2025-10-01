"""
Chat History Page - View and manage previous chat sessions
"""
import streamlit as st
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.chat_database import ChatDatabase

def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except:
        return timestamp

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text for preview."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def main():
    st.set_page_config(
        page_title="Chat History - K-OSMOS",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Use the same CSS styling as the main page for consistency
    st.markdown("""
    <style>
    /* Import professional fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=SF+Pro+Display:wght@100;200;300;400;500;600;700;800;900&display=swap');
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Main app styling matching kosmos_app.py */
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
        min-height: 100vh;
        color: #f0f6fc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.6;
    }
    
    /* Main container */
    .main {
        padding: 0;
        max-width: 100%;
        background: #0d1117;
    }
    
    .main .block-container {
        padding-top: 0.2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }
    
    /* Back to Chat Button - Top Right */
    .back-to-chat-btn {
        position: fixed !important;
        top: 5px !important;
        right: 10px !important;
        z-index: 99999 !important;
        background: linear-gradient(135deg, #58a6ff 0%, #1f6feb 100%) !important;
        color: white !important;
        border: none !important;
        padding: 8px 16px !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        box-shadow: 0 4px 15px rgba(88, 166, 255, 0.3) !important;
        transition: all 0.3s ease !important;
        font-family: 'Inter', system-ui, sans-serif !important;
        min-height: 36px !important;
        cursor: pointer !important;
        text-decoration: none !important;
    }
    
    .back-to-chat-btn:hover {
        background: linear-gradient(135deg, #4493f8 0%, #1a5cd8 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(88, 166, 255, 0.4) !important;
        color: white !important;
    }
    
    /* Header styling to match main page */
    .main-header {
        background: linear-gradient(135deg, rgba(88, 166, 255, 0.1) 0%, rgba(210, 168, 255, 0.1) 100%);
        border: 1px solid rgba(88, 166, 255, 0.2);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        text-align: center;
        backdrop-filter: blur(8px);
    }
    
    .main-header h1 {
        background: linear-gradient(135deg, #58a6ff 0%, #d2a8ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        margin-bottom: 1rem;
        font-size: 3rem;
        font-family: 'SF Pro Display', system-ui, sans-serif;
    }
    
    .main-header p {
        color: #8b949e;
        font-size: 1.1rem;
        margin: 0;
    }
    
    /* Session cards to match main page message styling */
    .session-card {
        background: rgba(33, 38, 45, 0.6) !important;
        border: 1px solid rgba(88, 166, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        margin: 1.5rem 0 !important;
        backdrop-filter: blur(8px) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    .session-card:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(88, 166, 255, 0.3) !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3) !important;
    }
    
    .session-title {
        color: #f0f6fc;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-family: 'Inter', sans-serif;
    }
    
    .session-meta {
        color: #8b949e;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    /* Message previews to match chat message styling */
    .message-preview {
        background: rgba(33, 38, 45, 0.8) !important;
        border-left: 4px solid rgba(88, 166, 255, 0.5) !important;
        padding: 0.75rem !important;
        margin: 0.5rem 0 !important;
        border-radius: 0 8px 8px 0 !important;
        color: #f0f6fc !important;
    }
    
    .user-message {
        background: rgba(255, 107, 107, 0.1) !important;
        border-left-color: rgba(255, 107, 107, 0.5) !important;
    }
    
    .assistant-message {
        background: rgba(88, 166, 255, 0.1) !important;
        border-left-color: rgba(88, 166, 255, 0.5) !important;
    }
    
    /* Button styling to match main page */
    .stButton > button {
        background: rgba(33, 38, 45, 0.8) !important;
        color: #f0f6fc !important;
        border: 1px solid rgba(88, 166, 255, 0.3) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stButton > button:hover {
        background: rgba(88, 166, 255, 0.1) !important;
        border-color: rgba(88, 166, 255, 0.5) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(88, 166, 255, 0.2) !important;
    }
    
    /* Primary button (Back to Chat) - Orange/Amber theme */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(245, 158, 11, 0.4) !important;
    }
    
    /* Specific styling for the back button at top right */
    .back-to-chat-btn {
        position: fixed !important;
        top: 10px !important;
        right: 15px !important;
        z-index: 99999 !important;
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: white !important;
        border: none !important;
        padding: 8px 16px !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3) !important;
        transition: all 0.3s ease !important;
        font-family: 'Inter', system-ui, sans-serif !important;
        min-height: 36px !important;
        cursor: pointer !important;
        text-decoration: none !important;
    }
    
    .back-to-chat-btn:hover {
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4) !important;
        color: white !important;
    }
    
    /* Secondary buttons (Delete, Export) */
    .stButton > button[kind="secondary"] {
        background: rgba(239, 68, 68, 0.1) !important;
        color: #fca5a5 !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(239, 68, 68, 0.2) !important;
        border-color: rgba(239, 68, 68, 0.5) !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(33, 38, 45, 0.6) !important;
        color: #f0f6fc !important;
        border-radius: 8px !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(33, 38, 45, 0.3) !important;
        border-radius: 0 0 8px 8px !important;
    }
    
    /* Info and warning boxes */
    .stInfo > div {
        background: rgba(88, 166, 255, 0.1) !important;
        border: 1px solid rgba(88, 166, 255, 0.3) !important;
        color: #f0f6fc !important;
    }
    
    .stWarning > div {
        background: rgba(255, 193, 7, 0.1) !important;
        border: 1px solid rgba(255, 193, 7, 0.3) !important;
        color: #f0f6fc !important;
    }
    
    .stSuccess > div {
        background: rgba(40, 167, 69, 0.1) !important;
        border: 1px solid rgba(40, 167, 69, 0.3) !important;
        color: #f0f6fc !important;
    }
    
    .stError > div {
        background: rgba(220, 53, 69, 0.1) !important;
        border: 1px solid rgba(220, 53, 69, 0.3) !important;
        color: #f0f6fc !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Back to Chat button at top right with similar styling to Chat History button
    st.markdown("""
    <div style="position: fixed; top: 10px; right: 15px; z-index: 99999;">
        <form action="" method="get">
            <button type="submit" name="page" value="kosmos" 
                    style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); 
                           color: white; 
                           border: 1px solid rgba(245, 158, 11, 0.3); 
                           border-radius: 25px; 
                           padding: 10px 18px; 
                           font-weight: 700; 
                           font-size: 14px; 
                           box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4); 
                           cursor: pointer; 
                           transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
                           font-family: 'Inter', system-ui, sans-serif; 
                           min-height: 40px; 
                           white-space: nowrap; 
                           backdrop-filter: blur(10px);"
                    onmouseover="this.style.background='linear-gradient(135deg, #d97706 0%, #b45309 100%)'; this.style.transform='translateY(-2px) scale(1.02)'; this.style.boxShadow='0 8px 30px rgba(245, 158, 11, 0.5)';"
                    onmouseout="this.style.background='linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'; this.style.transform='translateY(0px) scale(1)'; this.style.boxShadow='0 6px 20px rgba(245, 158, 11, 0.4)';">
                ← Back to Chat
            </button>
        </form>
    </div>
    """, unsafe_allow_html=True)
    
    # Check for page parameter and switch if needed  
    query_params = st.query_params
    if query_params.get("page") == "kosmos":
        st.switch_page("kosmos_app.py")
    
    # Header matching main page style with reduced spacing
    st.markdown("""
    <div class="main-header" style="margin: 0.5rem 0 1.5rem 0; padding: 2rem 2rem;">
        <h1>📚 Chat History</h1>
        <p>Browse and revisit your previous conversations with K-OSMOS</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize database
    try:
        db = ChatDatabase()
        
        # Get all sessions
        sessions = db.get_all_sessions()
        
        if not sessions:
            st.info("🔍 No chat history found. Start a conversation to see your history here!")
            return
        
        # Sort sessions by created_at (most recent first)
        sessions.sort(key=lambda x: x['created_at'], reverse=True)
        
        st.subheader(f"📋 Found {len(sessions)} chat sessions")
        
        # Display sessions
        for session in sessions:
            session_id = session['id']  # Fixed: database returns 'id' not 'session_id'
            created_at = session['created_at']
            
            # Get messages for this session
            messages = db.get_session_messages(session_id)
            message_count = len(messages)
            
            # Create session card
            with st.container():
                st.markdown(f"""
                <div class="session-card">
                    <div class="session-title">
                        💬 Session {session_id[:8]}...
                    </div>
                    <div class="session-meta">
                        📅 Created: {format_timestamp(created_at)} | 
                        💬 {message_count} messages
                    </div>
                """, unsafe_allow_html=True)
                
                # Show session details in expander
                with st.expander(f"View Conversation ({message_count} messages)", expanded=False):
                    if messages:
                        for msg in messages:
                            role = msg['role']
                            content = msg['content']
                            timestamp = msg['timestamp']
                            sources = msg.get('sources', [])
                            
                            # Style based on role
                            if role == 'user':
                                st.markdown(f"""
                                <div class="message-preview user-message">
                                    <strong>👤 You</strong> <span style="color: #6c757d; font-size: 0.8rem;">({format_timestamp(timestamp)})</span><br>
                                    {content}
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div class="message-preview assistant-message">
                                    <strong>🤖 KOSMOS</strong> <span style="color: #6c757d; font-size: 0.8rem;">({format_timestamp(timestamp)})</span><br>
                                    {content}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Display sources if available
                                if sources and len(sources) > 0:
                                    st.markdown("**📚 Research Sources:**")
                                    for i, source in enumerate(sources[:4], 1):
                                        try:
                                            title = source.get('title', 'Unknown Title')
                                            authors = source.get('authors', 'Unknown Authors')
                                            if isinstance(authors, list):
                                                authors = ', '.join(str(a) for a in authors[:2] if a)
                                            
                                            relevance = int(source.get('score', 0) * 100) if source.get('score') else 0
                                            
                                            st.markdown(f"""
                                            <div style="background: rgba(88, 166, 255, 0.1); border-left: 3px solid #58a6ff; padding: 0.75rem; margin: 0.5rem 0; border-radius: 0 8px 8px 0;">
                                                <strong style="color: #58a6ff;">📄 {title}</strong><br>
                                                <small style="color: #8b949e;">👨‍🔬 {authors}</small><br>
                                                <small style="color: #8b949e;">🎯 Relevance: {relevance}%</small>
                                            </div>
                                            """, unsafe_allow_html=True)
                                        except Exception as e:
                                            # Skip malformed sources
                                            continue
                    else:
                        st.info("No messages in this session")
                
                # Session actions
                col1, col2, col3 = st.columns([1, 1, 4])
                
                with col1:
                    if st.button(f"🗑️ Delete", key=f"delete_{session_id}"):
                        if st.session_state.get(f"confirm_delete_{session_id}", False):
                            # Actually delete
                            db.delete_session(session_id)
                            st.success("Session deleted!")
                            st.rerun()
                        else:
                            # Show confirmation
                            st.session_state[f"confirm_delete_{session_id}"] = True
                            st.warning("Click again to confirm deletion")
                
                with col2:
                    if st.button(f"📋 Export", key=f"export_{session_id}"):
                        # Export session as text
                        export_text = f"Chat Session {session_id}\n"
                        export_text += f"Created: {format_timestamp(created_at)}\n"
                        export_text += "=" * 50 + "\n\n"
                        
                        for msg in messages:
                            role_label = "You" if msg['role'] == 'user' else "KOSMOS"
                            export_text += f"[{format_timestamp(msg['timestamp'])}] {role_label}:\n"
                            export_text += f"{msg['content']}\n\n"
                        
                        st.download_button(
                            label="💾 Download",
                            data=export_text.encode('utf-8'),
                            file_name=f"chat_session_{session_id[:8]}.txt",
                            mime="text/plain",
                            key=f"download_{session_id}"
                        )
                
                # Close the session-card div properly
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Clear all history button (at the bottom)
        st.markdown("---")
        if st.button("🗑️ Clear All History", type="secondary"):
            if st.session_state.get("confirm_clear_all", False):
                # Actually clear all
                for session in sessions:
                    db.delete_session(session['id'])  # Fixed: database returns 'id' not 'session_id'
                st.success("All chat history cleared!")
                st.rerun()
            else:
                # Show confirmation
                st.session_state["confirm_clear_all"] = True
                st.warning("⚠️ This will delete ALL chat history. Click again to confirm.")
    
    except Exception as e:
        st.error(f"❌ Error loading chat history: {str(e)}")
        st.info("💡 Try refreshing the page or check if the database is accessible.")

if __name__ == "__main__":
    main()
