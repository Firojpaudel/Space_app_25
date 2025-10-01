"""
K-OSMOS Space Biology Knowledge Engine
Professional dashboard with clean UI inspired by Jony Ive's design principles
"""

import streamlit as st
import asyncio
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Any
import pandas as pd

from config.settings import Settings
from rag_system.chat import SpaceBiologyRAG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Space Biology Knowledge Engine",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS inspired by Jony Ive's design principles
st.markdown("""
<style>
    /* Import clean fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        padding: 2rem 3rem;
    }
    
    /* Clean typography */
    .big-title {
        font-family: 'Inter', sans-serif;
        font-size: 3.5rem;
        font-weight: 300;
        color: #1f1f1f;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        font-weight: 400;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .section-header {
        font-family: 'Inter', sans-serif;
        font-size: 1.8rem;
        font-weight: 500;
        color: #1f1f1f;
        margin: 2rem 0 1rem 0;
        letter-spacing: -0.01em;
    }
    
    /* Enhanced chat interface */
    .chat-container {
        background: #ffffff;
        border-radius: 16px;
        padding: 0;
        margin: 2rem 0;
        border: 1px solid #e8e8e8;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    .chat-messages {
        padding: 2rem;
        max-height: 600px;
        overflow-y: auto;
        background: linear-gradient(to bottom, #ffffff 0%, #fafafa 100%);
    }
    
    /* Custom scrollbar */
    .chat-messages::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-messages::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    .chat-messages::-webkit-scrollbar-thumb {
        background: #007AFF;
        border-radius: 10px;
    }
    
    .chat-messages::-webkit-scrollbar-thumb:hover {
        background: #0056CC;
    }
    
    .user-message {
        background: linear-gradient(135deg, #007AFF 0%, #0056CC 100%);
        color: white;
        padding: 1.2rem 1.8rem;
        border-radius: 20px 20px 6px 20px;
        margin: 1.5rem 0;
        max-width: 75%;
        margin-left: auto;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        box-shadow: 0 2px 12px rgba(0,122,255,0.25);
        position: relative;
    }
    
    .user-message::before {
        content: "👤";
        position: absolute;
        top: -8px;
        right: -8px;
        background: white;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    
    .assistant-message {
        background: #f8f9fa;
        color: #1f1f1f;
        padding: 2rem;
        border-radius: 20px 20px 20px 6px;
        margin: 1.5rem 0;
        max-width: 90%;
        border: 1px solid #e9ecef;
        font-family: 'Inter', sans-serif;
        line-height: 1.7;
        position: relative;
    }
    
    .assistant-message::before {
        content: "🤖";
        position: absolute;
        top: -8px;
        left: -8px;
        background: white;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    
    .ai-response-content {
        font-size: 1rem;
        line-height: 1.7;
        margin-bottom: 1.5rem;
    }
    
    .ai-response-content p {
        margin-bottom: 1rem;
    }
    
    .ai-response-content strong {
        color: #007AFF;
        font-weight: 600;
    }
    
    /* Enhanced source cards */
    .sources-section {
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 2px solid #e9ecef;
    }
    
    .sources-header {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #495057;
        font-size: 1.1rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .source-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .source-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #007AFF, #00D4AA);
    }
    
    .source-card:hover {
        box-shadow: 0 6px 24px rgba(0,0,0,0.15);
        transform: translateY(-3px);
        border-color: #007AFF;
    }
    
    .source-title {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #1f1f1f;
        font-size: 1.1rem;
        margin-bottom: 1rem;
        line-height: 1.4;
    }
    
    .source-title a {
        color: inherit;
        text-decoration: none;
        transition: color 0.3s ease;
    }
    
    .source-title a:hover {
        color: #007AFF;
        text-decoration: underline;
    }
    
    .source-meta {
        font-family: 'Inter', sans-serif;
        color: #6c757d;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        align-items: center;
    }
    
    .source-meta-item {
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }
    
    .similarity-score {
        background: linear-gradient(135deg, #00D4AA, #007AFF);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .paper-link {
        background: #007AFF;
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        text-decoration: none;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.3s ease;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .paper-link:hover {
        background: #0056CC;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,122,255,0.3);
        text-decoration: none;
        color: white;
    }
    
    /* Metrics cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .metric-number {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 300;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: 500;
        opacity: 0.9;
    }
    
    /* Clean sidebar */
    .sidebar .sidebar-content {
        background: #fafafa;
    }
    
    /* Enhanced buttons */
    .stButton > button {
        background: linear-gradient(135deg, #007AFF 0%, #0056CC 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,122,255,0.2);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0056CC 0%, #003D99 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,122,255,0.4);
    }
    
    /* Enhanced chat input */
    .stChatInput > div > div > input {
        border-radius: 25px !important;
        border: 2px solid #e9ecef !important;
        padding: 1rem 1.5rem !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stChatInput > div > div > input:focus {
        border-color: #007AFF !important;
        box-shadow: 0 0 0 3px rgba(0,122,255,0.1) !important;
    }
    
    /* Chat input button */
    .stChatInput button {
        background: #007AFF !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        transition: all 0.3s ease !important;
    }
    
    .stChatInput button:hover {
        background: #0056CC !important;
        transform: scale(1.1) !important;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Loading animation */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(0,122,255,0.3);
        border-radius: 50%;
        border-top-color: #007AFF;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    if 'publications_data' not in st.session_state:
        st.session_state.publications_data = None


@st.cache_data
def load_publications_data():
    """Load enriched publications data from processed files."""
    try:
        # Try enriched dataset first
        enriched_file = Path("data/processed/publications_fully_enriched.json")
        if enriched_file.exists():
            with open(enriched_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return pd.DataFrame(data) if data else pd.DataFrame()
        
        # Fallback to original dataset
        pub_file = Path("data/processed/publications.json")
        if pub_file.exists():
            with open(pub_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return pd.DataFrame(data) if data else pd.DataFrame()
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error loading publications: {e}")
        return pd.DataFrame()


def get_rag_system():
    """Initialize RAG system if not already done."""
    if st.session_state.rag_system is None:
        try:
            settings = Settings()
            st.session_state.rag_system = SpaceBiologyRAG(settings)
        except Exception as e:
            st.error(f"Failed to initialize RAG system: {e}")
            return None
    return st.session_state.rag_system


def display_hero_section():
    """Display the hero section with clean typography."""
    st.markdown("""
    <div style="text-align: center; padding: 4rem 0;">
        <h1 class="big-title">Space Biology Knowledge Engine</h1>
        <p class="subtitle">Explore 607 space biology research papers with AI-powered search</p>
    </div>
    """, unsafe_allow_html=True)


def display_metrics(df):
    """Display key metrics in clean cards."""
    if df.empty:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{len(df)}</div>
            <div class="metric-label">Research Papers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        try:
            # Handle authors column that might contain lists
            if 'authors' in df.columns:
                # Count unique string representations of authors
                unique_authors = len(set(str(author) for author in df['authors'] if pd.notna(author)))
            else:
                unique_authors = 0
        except:
            unique_authors = 0
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{unique_authors}</div>
            <div class="metric-label">Unique Authors</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        try:
            if 'year' in df.columns and not df['year'].empty:
                year_range = f"{int(df['year'].min())}-{int(df['year'].max())}"
            else:
                year_range = "N/A"
        except:
            year_range = "N/A"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{year_range}</div>
            <div class="metric-label">Year Range</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">100%</div>
            <div class="metric-label">FREE APIs</div>
        </div>
        """, unsafe_allow_html=True)


def display_chat_interface():
    """Display the enhanced chat interface."""
    st.markdown('<h2 class="section-header">🤖 AI Research Assistant</h2>', unsafe_allow_html=True)
    
    # Chat container
    st.markdown('<div class="chat-container"><div class="chat-messages">', unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            # Enhanced assistant message with better formatting
            formatted_content = format_ai_response(message["content"])
            st.markdown(f"""
            <div class="assistant-message">
                <div class="ai-response-content">{formatted_content}</div>
                
                {format_sources_section(message.get("sources", []))}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Chat input
    query = st.chat_input("Ask me about space biology research...", key="chat_input")
    
    if query:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": query})
        
        # Get RAG system
        rag_system = get_rag_system()
        if rag_system:
            with st.spinner("🔍 Searching research papers..."):
                # Run async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(rag_system.chat(query))
                    
                    # Add assistant response
                    message = {
                        "role": "assistant",
                        "content": result["response"],
                        "sources": result.get("sources", [])
                    }
                    st.session_state.messages.append(message)
                    
                finally:
                    loop.close()
        
        st.rerun()


def format_ai_response(content):
    """Format AI response content for better display."""
    # Split into paragraphs and format
    paragraphs = content.split('\n\n')
    formatted_paragraphs = []
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        # Make document references bold and colored
        import re
        para = re.sub(r'(Document \d+)', r'<strong style="color: #007AFF;">\1</strong>', para)
        
        # Format quotes
        para = re.sub(r'"([^"]*)"', r'<em>"\1"</em>', para)
        
        formatted_paragraphs.append(f'<p>{para}</p>')
    
    return ''.join(formatted_paragraphs)


def format_sources_section(sources):
    """Format the sources section with enhanced display."""
    if not sources:
        return ""
    
    sources_html = """
    <div class="sources-section">
        <div class="sources-header">
            📚 Research Sources
        </div>
    """
    
    for i, source in enumerate(sources[:3]):  # Show top 3 sources
        title = source.get('title', 'Unknown Title')
        authors = source.get('authors', 'Unknown Authors')
        journal = source.get('journal', 'Unknown Journal')
        year = source.get('year', 'Unknown Year')
        similarity = source.get('score', 0.0)
        url = source.get('url', '')
        
        # If authors is a list, join them
        if isinstance(authors, list):
            authors = ', '.join(authors) if authors else 'Unknown Authors'
        
        # Create paper link
        paper_link = ""
        if url:
            paper_link = f'<a href="{url}" target="_blank" class="paper-link">📄 Read Paper</a>'
        
        sources_html += f"""
        <div class="source-card">
            <div class="source-title">
                {title if not url else f'<a href="{url}" target="_blank">{title}</a>'}
            </div>
            <div class="source-meta">
                <div class="source-meta-item">👨‍🔬 {authors}</div>
                <div class="source-meta-item">📖 {journal}</div>
                <div class="source-meta-item">📅 {year}</div>
                <div class="similarity-score">Match: {similarity:.1%}</div>
            </div>
            {paper_link}
        </div>
        """
    
    sources_html += "</div>"
    return sources_html


def display_quick_queries():
    """Display quick query buttons for common research topics."""
    st.markdown('<h2 class="section-header">🚀 Quick Research Topics</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    quick_queries = [
        "Bone density in microgravity",
        "Muscle atrophy in space",
        "Plant growth in space",
        "Cardiovascular changes",
        "Sleep patterns in space",
        "Radiation effects on cells",
        "Stem cell research in space",
        "ISS experiments overview",
        "Mars mission health risks"
    ]
    
    for i, query in enumerate(quick_queries):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.button(query, key=f"quick_{i}"):
                st.session_state.messages.append({"role": "user", "content": query})
                
                rag_system = get_rag_system()
                if rag_system:
                    with st.spinner("🔍 Searching..."):
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            result = loop.run_until_complete(rag_system.chat(query))
                            message = {
                                "role": "assistant", 
                                "content": result["response"],
                                "sources": result.get("sources", [])
                            }
                            st.session_state.messages.append(message)
                        finally:
                            loop.close()
                st.rerun()


def display_research_trends(df):
    """Display research trends visualization."""
    if df.empty or 'year' not in df.columns:
        return
    
    st.markdown('<h2 class="section-header">📈 Research Trends</h2>', unsafe_allow_html=True)
    
    # Publications per year
    year_counts = df['year'].value_counts().sort_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=year_counts.index,
        y=year_counts.values,
        mode='lines+markers',
        line=dict(color='#007AFF', width=3),
        marker=dict(size=8, color='#007AFF'),
        name='Publications'
    ))
    
    fig.update_layout(
        title=dict(
            text="Space Biology Publications Over Time",
            font=dict(family="Inter", size=20, color='#1f1f1f')
        ),
        xaxis_title="Year",
        yaxis_title="Number of Publications",
        template="plotly_white",
        height=400,
        font=dict(family="Inter")
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_sidebar_info():
    """Display sidebar information."""
    with st.sidebar:
        st.markdown("### 🚀 System Status")
        
        # System health
        try:
            settings = Settings()
            st.success("✅ Gemini API Connected")
            st.success("✅ Pinecone Vector DB")
            st.info(f"📊 {len(st.session_state.publications_data)} Publications Loaded")
        except Exception:
            st.error("❌ System Error")
        
        st.markdown("---")
        
        st.markdown("### 💡 Tips")
        st.markdown("""
        - Ask specific questions about space biology
        - Mention organisms, missions, or body systems
        - Request comparisons between studies
        - Ask for research summaries
        """)
        
        st.markdown("---")
        
        st.markdown("### 🔧 Tech Stack")
        st.markdown("""
        - **AI**: Google Gemini 2.0 Flash
        - **Vector DB**: Pinecone (Free)
        - **Data**: 607 PMC Publications
        - **UI**: Streamlit + Jony Ive Design
        """)
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


def main():
    """Main dashboard function."""
    init_session_state()
    
    # Load data
    if st.session_state.publications_data is None:
        st.session_state.publications_data = load_publications_data()
    
    df = st.session_state.publications_data
    
    # Display sidebar
    display_sidebar_info()
    
    # Main content
    display_hero_section()
    display_metrics(df)
    display_chat_interface()
    display_quick_queries()
    display_research_trends(df)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-family: Inter;">
        <p>Space Biology Knowledge Engine • Built with 100% FREE APIs • NASA Space Apps 2025</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()