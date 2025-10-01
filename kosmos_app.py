"""
K-OSMOS Streamlit Application
"""

import streamlit as st
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Any
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from collections import Counter
import re
import numpy as np

from config.settings import Settings
from rag_system.chat import SpaceBiologyRAG
from utils.chat_database import ChatDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="K-OSMOS | Space Biology Knowledge Engine",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="auto"
)

# Enhanced ChatGPT-inspired CSS with modern design principles
st.markdown("""
<style>
    /* Import professional fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=SF+Pro+Display:wght@100;200;300;400;500;600;700;800;900&display=swap');
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Fix sidebar collapse/expand */
    .css-1d391kg {
        padding-top: 1.5rem;
    }
    
    /* Fixed navbar at top - full width */
    .fixed-navbar {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 9999 !important;
        background: rgba(13, 17, 23, 0.95) !important;
        backdrop-filter: blur(24px) !important;
        border-bottom: 1px solid #30363d !important;
        padding: 1rem 2rem !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        height: 70px !important;
    }
    
    /* Adjust main content to account for fixed navbar only */
    .main-content {
        margin-top: 80px !important;
        margin-left: 0 !important;
        padding-top: 1rem !important;
        width: 100% !important;
    }
    
    /* Enhanced Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%) !important;
        border-right: 1px solid rgba(88, 166, 255, 0.2) !important;
        width: 320px !important;
        box-shadow: 4px 0 12px rgba(0, 0, 0, 0.3) !important;
    }
    
    [data-testid="stSidebar"] > div {
        background: transparent !important;
        padding: 90px 1rem 1rem 1rem !important;
    }
    
    /* Sidebar collapse/expand button - always visible and accessible */
    [data-testid="collapsedControl"] {
        background: linear-gradient(135deg, rgba(88, 166, 255, 0.9) 0%, rgba(31, 111, 235, 0.9) 100%) !important;
        border: 1px solid rgba(88, 166, 255, 0.6) !important;
        border-radius: 8px !important;
        margin-top: 80px !important;
        margin-left: 8px !important;
        width: 40px !important;
        height: 40px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        position: fixed !important;
        z-index: 99999 !important;
        left: 10px !important;
        top: 100px !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        backdrop-filter: blur(10px) !important;
    }
    
    [data-testid="collapsedControl"]:hover {
        background: linear-gradient(135deg, rgba(88, 166, 255, 1) 0%, rgba(31, 111, 235, 1) 100%) !important;
        transform: scale(1.1) translateX(4px) !important;
        box-shadow: 0 6px 16px rgba(88, 166, 255, 0.4) !important;
        border-color: rgba(88, 166, 255, 0.8) !important;
    }
    
    /* Make sure the collapse button icon is visible */
    [data-testid="collapsedControl"] svg {
        color: white !important;
        fill: currentColor !important;
        width: 16px !important;
        height: 16px !important;
    }
    
    /* Ensure no other elements can cover the expand button */
    #custom-expand-btn {
        position: fixed !important;
        z-index: 999999 !important;
        pointer-events: auto !important;
    }
    
    /* Make sure main content doesn't cover the expand button */
    .main .block-container {
        padding-left: 60px !important;
    }
    
    /* Ensure chat input doesn't cover expand button */
    [data-testid="stChatInput"] {
        z-index: 1000 !important;
    }
    
    /* Sidebar open/close button when sidebar is visible */
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] button {
        background: rgba(88, 166, 255, 0.1) !important;
        border: 1px solid rgba(88, 166, 255, 0.3) !important;
        border-radius: 6px !important;
        color: #f0f6fc !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] button:hover {
        background: rgba(88, 166, 255, 0.2) !important;
        border-color: rgba(88, 166, 255, 0.5) !important;
        transform: scale(1.05) !important;
    }
    
    /* Sidebar button improvements */
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        margin-bottom: 0.5rem !important;
        height: auto !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.9rem !important;
    }
    
    /* New Chat button styling */
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #58a6ff 0%, #1f6feb 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(88, 166, 255, 0.3) !important;
    }
    
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4493f8 0%, #1a5cd8 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(88, 166, 255, 0.4) !important;
    }
    
    /* Clear History button styling */
    [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background: rgba(239, 68, 68, 0.1) !important;
        color: #fca5a5 !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        box-shadow: 0 2px 8px rgba(239, 68, 68, 0.2) !important;
    }
    
    [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background: rgba(239, 68, 68, 0.2) !important;
        border-color: rgba(239, 68, 68, 0.5) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3) !important;
    }
    
    /* Session buttons */
    [data-testid="stSidebar"] .stButton > button:not([kind]) {
        background: rgba(33, 38, 45, 0.6) !important;
        color: #f0f6fc !important;
        border: 1px solid rgba(88, 166, 255, 0.2) !important;
        text-align: left !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:not([kind]):hover {
        background: rgba(88, 166, 255, 0.1) !important;
        border-color: rgba(88, 166, 255, 0.4) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 8px rgba(88, 166, 255, 0.2) !important;
    }
    
    /* Sidebar is managed by Streamlit's built-in logic */
    
    /* Direct color definitions for better compatibility */
    
    /* Main container */
    .main {
        padding: 0;
        max-width: 100%;
        background: #0d1117;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
        min-height: 100vh;
        color: #f0f6fc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.6;
    }
    
    /* Enhanced Header - Full width navbar */
    .kosmos-header {
        background: rgba(13, 17, 23, 0.98);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border-bottom: 1px solid #30363d;
        padding: 1rem 2rem;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 9999;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 70px;
        display: flex;
        align-items: center;
    }
    
    .kosmos-logo {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0;
        width: 100%;
    }
    
    .kosmos-brand {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .kosmos-title {
        font-family: 'SF Pro Display', sans-serif;
        font-size: 1.8rem;
        font-weight: 600;
        background: linear-gradient(135deg, #58a6ff 0%, #d2a8ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .kosmos-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        font-weight: 400;
        color: #8b949e;
        margin: 0;
        letter-spacing: 0.02em;
    }
    
    .header-stats {
        display: flex;
        gap: 1.5rem;
        align-items: center;
        font-size: 0.75rem;
        color: var(--text-secondary);
    }
    
    .stat-item {
        display: flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.25rem 0.75rem;
        background: rgba(88, 166, 255, 0.1);
        border-radius: 12px;
        border: 1px solid rgba(88, 166, 255, 0.2);
    }
    
    /* Chat Interface with reduced top spacing */
    .chat-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 60px 2rem 120px 2rem;
        min-height: calc(100vh - 200px);
        width: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Add padding to main content area for chat input */
    .main .block-container {
        padding-bottom: 120px !important;
    }
    
    /* Native Streamlit Chat Input Styling */
    [data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background: rgba(13, 17, 23, 0.98) !important;
        backdrop-filter: blur(24px) !important;
        border-top: 1px solid rgba(88, 166, 255, 0.2) !important;
        padding: 1.5rem 2rem !important;
        z-index: 9999 !important;
        box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.6) !important;
    }
    
    [data-testid="stChatInput"] > div {
        max-width: 1200px !important;
        margin: 0 auto !important;
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
    }
    
    [data-testid="stChatInput"] > div > div:first-child {
        flex: 1 !important;
    }
    
    [data-testid="stChatInput"] input {
        background: rgba(33, 38, 45, 0.8) !important;
        border: 2px solid rgba(88, 166, 255, 0.3) !important;
        border-radius: 24px !important;
        color: #f0f6fc !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        padding: 1rem 1.5rem !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        height: 48px !important;
        box-sizing: border-box !important;
    }
    
    [data-testid="stChatInput"] input:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.1) !important;
        outline: none !important;
    }
    
    [data-testid="stChatInput"] input::placeholder {
        color: #8b949e !important;
    }
    
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #58a6ff 0%, #1f6feb 100%) !important;
        border: none !important;
        border-radius: 50% !important;
        width: 48px !important;
        height: 48px !important;
        min-width: 48px !important;
        min-height: 48px !important;
        color: white !important;
        font-size: 1.2rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3) !important;
        flex-shrink: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    [data-testid="stChatInput"] button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 6px 16px rgba(88, 166, 255, 0.4) !important;
    }
    
    [data-testid="stChatInput"] button:disabled {
        opacity: 0.5 !important;
        transform: none !important;
    }
    
    /* Enhanced Streamlit Chat Messages */
    [data-testid="stChatMessage"] {
        background: rgba(33, 38, 45, 0.6) !important;
        border: 1px solid rgba(88, 166, 255, 0.1) !important;
        border-radius: 16px !important;
        margin: 1.5rem 0 !important;
        padding: 1.5rem !important;
        backdrop-filter: blur(8px) !important;
        animation: fadeInUp 0.5s ease-out !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
    }
    
    [data-testid="stChatMessage"][data-testid*="user"] {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(238, 90, 36, 0.1) 100%) !important;
        border-color: rgba(255, 107, 107, 0.2) !important;
    }
    
    [data-testid="stChatMessage"][data-testid*="assistant"] {
        background: linear-gradient(135deg, rgba(88, 166, 255, 0.1) 0%, rgba(102, 126, 234, 0.1) 100%) !important;
        border-color: rgba(88, 166, 255, 0.2) !important;
    }
    
    /* Chat message avatars */
    [data-testid="stChatMessage"] img {
        width: 40px !important;
        height: 40px !important;
        border-radius: 50% !important;
        border: 2px solid rgba(88, 166, 255, 0.3) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Enhanced message content */
    [data-testid="stChatMessage"] .stMarkdown {
        color: #f0f6fc !important;
        font-family: 'Inter', sans-serif !important;
        line-height: 1.6 !important;
    }
    
    [data-testid="stChatMessage"] .stMarkdown h1,
    [data-testid="stChatMessage"] .stMarkdown h2,
    [data-testid="stChatMessage"] .stMarkdown h3 {
        color: #58a6ff !important;
        font-weight: 600 !important;
        margin: 1.5rem 0 1rem 0 !important;
    }
    
    [data-testid="stChatMessage"] .stMarkdown strong {
        color: #58a6ff !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stChatMessage"] .stMarkdown em {
        color: #d2a8ff !important;
    }
    
    [data-testid="stChatMessage"] .stMarkdown code {
        background: rgba(88, 166, 255, 0.1) !important;
        border: 1px solid rgba(88, 166, 255, 0.2) !important;
        color: #58a6ff !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 4px !important;
        font-family: 'SF Mono', Consolas, monospace !important;
    }
    
    [data-testid="stChatMessage"] .stMarkdown pre {
        background: rgba(22, 27, 34, 0.8) !important;
        border: 1px solid rgba(88, 166, 255, 0.2) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    /* Expander styling for sources */
    [data-testid="stChatMessage"] .streamlit-expanderHeader {
        background: rgba(88, 166, 255, 0.1) !important;
        border: 1px solid rgba(88, 166, 255, 0.2) !important;
        border-radius: 8px !important;
        color: #f0f6fc !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stChatMessage"] .streamlit-expanderContent {
        background: rgba(22, 27, 34, 0.8) !important;
        border: 1px solid rgba(88, 166, 255, 0.1) !important;
        border-radius: 0 0 8px 8px !important;
        border-top: none !important;
    }

    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Enhanced Sources Section */
    .sources-container {
        background: rgba(33, 38, 45, 0.6);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 1.25rem;
        margin-top: 1.5rem;
        backdrop-filter: blur(8px);
    }
    
    .sources-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.9rem;
    }
    
    .source-card {
        background: rgba(22, 27, 34, 0.8);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
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
        height: 2px;
        background: linear-gradient(90deg, var(--accent-blue), var(--accent-green));
        opacity: 0.8;
    }
    
    .source-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-medium);
        border-color: var(--accent-blue);
        background: rgba(22, 27, 34, 0.95);
    }
    
    .source-title {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    .source-meta {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 1rem;
        margin-bottom: 0.75rem;
    }
    
    .source-info {
        flex: 1;
        min-width: 0;
    }
    
    .source-authors {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-bottom: 0.25rem;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .source-journal {
        font-size: 0.75rem;
        color: var(--accent-purple);
        font-weight: 500;
    }
    
    .relevance-badge {
        background: linear-gradient(135deg, rgba(88, 166, 255, 0.2), rgba(210, 168, 255, 0.2));
        color: var(--accent-blue);
        padding: 0.25rem 0.75rem;
        border-radius: 16px;
        font-size: 0.75rem;
        font-weight: 600;
        white-space: nowrap;
        border: 1px solid rgba(88, 166, 255, 0.3);
    }
    
    .source-actions {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .source-link {
        color: var(--accent-blue);
        text-decoration: none;
        font-weight: 500;
        font-size: 0.8rem;
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        transition: all 0.2s ease;
        padding: 0.5rem 1rem;
        background: rgba(88, 166, 255, 0.1);
        border-radius: 20px;
        border: 1px solid rgba(88, 166, 255, 0.2);
    }
    
    .source-link:hover {
        color: white;
        background: var(--accent-blue);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
        text-decoration: none;
    }
    
    /* Sidebar styling */
    .sidebar-container {
        background: rgba(30, 41, 59, 0.95);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid rgba(59, 130, 246, 0.3);
        height: 100vh;
        padding: 1.5rem;
        border-radius: 0;
    }
    
    .sidebar-title {
        font-family: 'SF Pro Display', 'Inter', sans-serif;
        font-size: 1.125rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.3);
    }
    
    .session-item {
        background: rgba(51, 65, 85, 0.6);
        border: 1px solid rgba(59, 130, 246, 0.2);
        padding: 0.875rem;
        border-radius: 12px;
        margin-bottom: 0.75rem;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .session-item:hover {
        background: rgba(59, 130, 246, 0.15);
        border-color: rgba(59, 130, 246, 0.4);
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
    }
    
    .session-item.active {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.25) 0%, rgba(59, 130, 246, 0.15) 100%);
        border-color: #3b82f6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .session-title {
        font-weight: 600;
        color: #f1f5f9;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        line-height: 1.3;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    .session-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 0.5rem;
    }
    
    .session-time {
        font-size: 0.75rem;
        color: #94a3b8;
    }
    
    .session-count {
        background: rgba(59, 130, 246, 0.2);
        color: #93c5fd;
        padding: 0.125rem 0.5rem;
        border-radius: 10px;
        font-size: 0.7rem;
        font-weight: 500;
    }
    
    /* Sidebar button styling - Fixed */
    .stButton > button[data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.875rem 1.25rem !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        text-align: center !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
        width: 100% !important;
        height: auto !important;
    }
    
    .stButton > button[data-testid="baseButton-secondary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4) !important;
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%) !important;
    }
    
    /* New Chat Button specific styling */
    .sidebar-new-chat {
        background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.875rem 1.25rem !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        text-align: center !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
        width: 100% !important;
        display: block !important;
    }
    
    .sidebar-new-chat:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4) !important;
    }
    
    .sidebar-clear-btn {
        background: rgba(239, 68, 68, 0.2) !important;
        color: #fca5a5 !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        border-radius: 8px !important;
        padding: 0.625rem 1rem !important;
        font-size: 0.8rem !important;
        transition: all 0.2s ease !important;
        margin-top: 1rem !important;
    }
    
    .sidebar-clear-btn:hover {
        background: rgba(239, 68, 68, 0.3) !important;
        border-color: rgba(239, 68, 68, 0.5) !important;
        transform: translateY(-1px) !important;
    }
    
    .sidebar-session-btn {
        background: transparent !important;
        color: inherit !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
        text-align: left !important;
    }
    
    .sidebar-session-btn:hover {
        background: transparent !important;
    }
    
    /* Streamlit Text Area Styling */
    .stTextArea > div > div > textarea {
        border: none !important;
        background: transparent !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        color: #f0f6fc !important;
        font-weight: 400 !important;
        resize: none !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextArea > div > div > textarea::placeholder {
        color: #8b949e !important;
        font-style: normal !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        box-shadow: none !important;
        border: none !important;
        outline: none !important;
    }
    
    .stTextArea > div {
        background: transparent !important;
        border: none !important;
    }
    
    /* Form styling in sticky container */
    .sticky-search-container .stForm {
        background: transparent !important;
        border: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .sticky-search-container .stForm > div {
        background: transparent !important;
        border: none !important;
        padding: 0.75rem 1rem !important;
    }
    
    /* Ensure sticky positioning works */
    body > div:last-child {
        position: relative !important;
        z-index: 1 !important;
    }
    
    /* Enhanced Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #58a6ff 0%, #1f6feb 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 50% !important;
        width: 45px !important;
        height: 45px !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
    }
    
    .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 6px 16px rgba(88, 166, 255, 0.4) !important;
        background: linear-gradient(135deg, #4493f8 0%, #1f6feb 100%) !important;
    }
    
    .stButton > button:active {
        transform: scale(0.95) !important;
        box-shadow: 0 2px 8px rgba(88, 166, 255, 0.3) !important;
    }
    
    /* Disabled button styling */
    .stButton > button:disabled {
        background: rgba(139, 148, 158, 0.3) !important;
        color: rgba(139, 148, 158, 0.8) !important;
        cursor: not-allowed !important;
        transform: none !important;
        box-shadow: none !important;
    }
    
    /* Welcome cards hover effect */
    .welcome-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(59, 130, 246, 0.2) !important;
        border-color: rgba(96, 165, 250, 0.5) !important;
    }
    
    /* Enhanced Loading Animation */
    .loading-dots {
        display: inline-block;
        position: relative;
        width: 20px;
        height: 20px;
    }
    
    .loading-dots div {
        position: absolute;
        width: 4px;
        height: 4px;
        border-radius: 50%;
        background: white;
        animation-timing-function: cubic-bezier(0, 1, 1, 0);
    }
    
    .loading-dots div:nth-child(1) {
        left: 8px;
        animation: loading1 0.6s infinite;
    }
    
    .loading-dots div:nth-child(2) {
        left: 8px;
        animation: loading2 0.6s infinite;
    }
    
    .loading-dots div:nth-child(3) {
        left: 14px;
        animation: loading2 0.6s infinite;
    }
    
    @keyframes loading1 {
        0% { transform: scale(0); }
        100% { transform: scale(1); }
    }
    
    @keyframes loading2 {
        0% { transform: translate(0, 0); }
        100% { transform: translate(6px, 0); }
    }
    
    /* Typing indicator for bot messages */
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem 1.5rem;
        background: var(--chat-bot-bg);
        backdrop-filter: blur(12px);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius) var(--border-radius) var(--border-radius) 6px;
        margin: 1.5rem 0;
        color: var(--text-secondary);
        animation: fadeInUp 0.3s ease-out;
    }
    
    .typing-dots {
        display: flex;
        gap: 0.25rem;
    }
    
    .typing-dots span {
        width: 6px;
        height: 6px;
        background: var(--accent-blue);
        border-radius: 50%;
        animation: typing 1.5s ease-in-out infinite;
    }
    
    .typing-dots span:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-dots span:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing {
        0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.4;
        }
        30% {
            transform: translateY(-10px);
            opacity: 1;
        }
    }
    
    /* Welcome screen animations */
    .welcome-card {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .welcome-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: var(--shadow-medium);
    }
    
    /* Pulse animation for new messages */
    @keyframes pulse {
        0% { opacity: 0.8; }
        50% { opacity: 1; }
        100% { opacity: 0.8; }
    }
    
    .message-pulse {
        animation: pulse 2s ease-in-out infinite;
    }
    
    /* Hide empty divs and fix rendering issues */
    div:empty {
        display: none !important;
    }
    
    /* Hide stray HTML tags and text */
    .stMarkdown div:contains("</div>"),
    .stMarkdown div:contains("<div>"),
    .stMarkdown p:contains("</div>"),
    .stMarkdown p:contains("<div>") {
        display: none !important;
    }
    
    /* Clean up source rendering */
    .stMarkdown p:empty,
    .stMarkdown div:empty {
        display: none !important;
    }
    
    /* Fix any stray HTML content */
    .stMarkdown *:contains("&lt;div&gt;"),
    .stMarkdown *:contains("&lt;/div&gt;") {
        display: none !important;
    }
    
    /* Enhanced Responsive Design */
    
    /* Tablet breakpoint */
    @media (max-width: 1024px) {
        .chat-container {
            max-width: 900px;
            padding-left: 1.5rem;
            padding-right: 1.5rem;
        }
        
        .header-stats {
            gap: 1rem;
        }
        
        .stat-item {
            padding: 0.2rem 0.6rem;
            font-size: 0.7rem;
        }
    }
    
    /* Mobile breakpoint */
    @media (max-width: 768px) {
        .kosmos-header {
            padding: 0.75rem 1rem !important;
        }
        
        .header-stats {
            display: none;
        }
        
        .kosmos-title {
            font-size: 1.5rem;
        }
        
        .chat-container {
            padding: 80px 1rem 140px 1rem;
            max-width: 100%;
        }
        
        .sticky-input-container {
            padding: 1rem !important;
        }
        
        .message-content {
            max-width: 85%;
            padding: 1.2rem 1.5rem;
        }
        
        .message-avatar {
            width: 36px;
            height: 36px;
            font-size: 1.1rem;
            margin: 0 0.7rem;
        }
        
        .chat-input-wrapper {
            padding: 0.5rem 1rem;
        }
        
        .welcome-card {
            padding: 1.5rem;
        }
        
        .source-card {
            padding: 0.75rem;
        }
        
        .source-meta {
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .relevance-badge {
            align-self: flex-start;
        }
    }
    
    @media (max-width: 480px) {
        .kosmos-header {
            padding: 0.5rem 1rem !important;
        }
        
        .kosmos-title {
            font-size: 1.3rem;
        }
        
        .kosmos-subtitle {
            font-size: 0.75rem;
        }
        
        .chat-container {
            padding: 70px 0.75rem 130px 0.75rem;
            max-width: 100%;
        }
        
        .message-content {
            max-width: 90%;
            padding: 1rem 1.25rem;
            font-size: 0.9rem;
        }
        
        .message-avatar {
            width: 32px;
            height: 32px;
            font-size: 1rem;
            margin: 0 0.5rem;
        }
        
        .chat-input-wrapper {
            border-radius: 20px;
            padding: 0.5rem 0.75rem;
        }
        
        .sticky-input-container {
            padding: 0.75rem;
        }
    }
    
    /* Ultra-wide screens */
    @media (min-width: 1440px) {
        .chat-container {
            max-width: 1200px;
        }
        
        .fixed-navbar {
            padding: 1rem 3rem;
        }
        
        .sticky-input-container {
            padding: 1.5rem 3rem 2rem 3rem;
        }
    }
        
        .message-content {
            max-width: 90%;
            padding: 0.875rem 1rem;
            font-size: 0.9rem;
        }
        
        .chat-input-wrapper {
            padding: 0.5rem 0.75rem;
        }
        
        .sticky-input-container {
            padding: 0.75rem;
        }
    }
    

    
    /* Print styles */
    @media print {
        .sticky-input-container,
        .sidebar-container,
        .kosmos-header {
            display: none !important;
        }
        
        .chat-container {
            padding-bottom: 0 !important;
        }
        
        .message-content {
            page-break-inside: avoid;
        }
    }
    

</style>

<script>
// Enhanced UI with smart sidebar management
document.addEventListener('DOMContentLoaded', function() {
    
    function initializeUI() {
        // Ensure main content has proper margins for clean layout
        const mainBlock = document.querySelector('.main .block-container');
        if (mainBlock) {
            mainBlock.style.paddingLeft = '0';
            mainBlock.style.maxWidth = '100%';
            mainBlock.style.width = '100%';
        }
        
        // Apply consistent layout
        const mainContent = document.querySelector('.main');
        if (mainContent) {
            mainContent.style.width = '100%';
        }
    }
    
    function cleanHTML() {
        // Clean up any stray HTML content
        const elements = document.querySelectorAll('*');
        elements.forEach(el => {
            if (el.textContent && (el.textContent.trim() === '</div>' || el.textContent.trim() === '<div>')) {
                el.style.display = 'none';
            }
        });
    }
    
    // Run immediately
    initializeUI();
    cleanHTML();
    
    // Watch for DOM changes to handle dynamic updates
    const observer = new MutationObserver(function(mutations) {
        let shouldUpdate = false;
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                shouldUpdate = true;
            }
        });
        
        if (shouldUpdate) {
            setTimeout(() => {
                initializeUI();
                cleanHTML();
            }, 100);
        }
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Listen for window resize events
    window.addEventListener('resize', function() {
        setTimeout(() => {
            // Adjust sessions panel for mobile
            const panel = document.querySelector('.sessions-panel');
            if (panel && window.innerWidth <= 768) {
                if (panel.classList.contains('open')) {
                    panel.style.width = Math.min(320, window.innerWidth - 40) + 'px';
                }
            }
        }, 100);
    });
    
    // Listen for orientation change on mobile
    window.addEventListener('orientationchange', function() {
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
        }, 300);
    });
    
    // Periodically ensure clean UI
    setInterval(() => {
        initializeUI();
        cleanHTML();
    }, 3000);
});
</script>
""", unsafe_allow_html=True)

# Session management completely removed - using simple in-memory chat

@st.cache_resource
def initialize_rag():
    """Initialize the RAG system."""
    try:
        settings = Settings()
        rag = SpaceBiologyRAG(settings)
        return rag
    except Exception as e:
        logger.error(f"Failed to initialize RAG: {e}")
        return None

def create_research_visualizations(messages: List[Dict], sources: List[Dict]) -> Dict[str, Any]:
    """Create real-time visualizations based on actual research data and conversation."""
    viz_data = {}
    
    try:
        # Load actual research data
        pub_file = Path("data/processed/publications.json")
        enriched_file = Path("data/processed/publications_fully_enriched.json")
        
        research_data = []
        if enriched_file.exists():
            try:
                with open(enriched_file, 'r', encoding='utf-8') as f:
                    research_data = json.load(f)
            except:
                pass
        
        if not research_data and pub_file.exists():
            try:
                with open(pub_file, 'r', encoding='utf-8') as f:
                    research_data = json.load(f)
            except:
                pass
        
        # Extract topics from current conversation
        all_text = " ".join([msg.get('content', '') for msg in messages])
        
        # Advanced topic analysis with real data
        topic_patterns = {
            'Microgravity Effects': r'\b(microgravity|weightless|zero.?g|gravitational|gravity|weightlessness)\b',
            'Bone & Muscle Health': r'\b(bone|muscle|skeletal|calcium|osteo|atrophy|density|fracture)\b',
            'Cardiovascular System': r'\b(heart|cardio|blood|vessel|circulation|pressure|cardiac)\b',
            'Neurological Studies': r'\b(brain|neural|neuron|nervous|cognitive|memory|sleep)\b',
            'Plant Biology': r'\b(plant|seed|growth|photosynthesis|agriculture|root|leaf)\b',
            'Cell & Molecular': r'\b(cell|cellular|stem|regeneration|tissue|protein|gene|dna)\b',
            'Radiation Effects': r'\b(radiation|cosmic|solar|dose|exposure|radioprotection)\b',
            'ISS Experiments': r'\b(iss|space.?station|international|experiment|mission)\b',
            'Animal Studies': r'\b(mouse|mice|rat|rodent|animal|mammal|organism)\b',
            'Immune System': r'\b(immune|immunity|antibody|infection|inflammation)\b'
        }
        
        topic_counts = {}
        for topic, pattern in topic_patterns.items():
            matches = len(re.findall(pattern, all_text, re.IGNORECASE))
            if matches > 0:
                topic_counts[topic] = matches
        
        # Enhance with research data analysis
        if research_data:
            # Add data from actual research papers mentioned
            for paper in research_data[:100]:  # Sample for performance
                abstract = paper.get('abstract', '')
                title = paper.get('title', '')
                combined_text = f"{title} {abstract}".lower()
                
                for topic, pattern in topic_patterns.items():
                    if re.search(pattern, combined_text, re.IGNORECASE):
                        topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Create enhanced topic distribution
        if topic_counts:
            # Sort by frequency and take top 8
            sorted_topics = dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:8])
            
            colors = ['#58a6ff', '#7c3aed', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#84cc16']
            
            fig_topics = go.Figure(data=[
                go.Bar(
                    x=list(sorted_topics.keys()),
                    y=list(sorted_topics.values()),
                    marker_color=colors[:len(sorted_topics)],
                    text=list(sorted_topics.values()),
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>Mentions: %{y}<extra></extra>'
                )
            ])
            
            fig_topics.update_layout(
                title=dict(
                    text="🔬 Research Topics in Current Session",
                    font=dict(size=16, color='#f0f6fc'),
                    x=0.5
                ),
                plot_bgcolor='rgba(13, 17, 23, 0.8)',
                paper_bgcolor='rgba(13, 17, 23, 0.8)',
                font=dict(color='#f0f6fc', family='Inter'),
                xaxis=dict(
                    title="Research Areas",
                    tickangle=-45,
                    gridcolor='rgba(48, 54, 61, 0.5)'
                ),
                yaxis=dict(
                    title="Frequency",
                    gridcolor='rgba(48, 54, 61, 0.5)'
                ),
                margin=dict(l=60, r=20, t=60, b=100),
                height=400
            )
            viz_data['topics'] = fig_topics
        
        # Enhanced source relevance with real data
        if sources:
            # Filter and process sources
            valid_sources = [s for s in sources if s.get('score', 0) > 0.3][:10]  # Top 10 relevant sources
            
            if valid_sources:
                scores = [s.get('score', 0) * 100 for s in valid_sources]
                titles = []
                for s in valid_sources:
                    title = s.get('title', 'Unknown Paper')
                    # Truncate long titles
                    if len(title) > 40:
                        title = title[:40] + "..."
                    titles.append(title)
                
                # Create horizontal bar chart for better readability
                fig_relevance = go.Figure(data=[
                    go.Bar(
                        x=scores,
                        y=titles,
                        orientation='h',
                        marker=dict(
                            color=scores,
                            colorscale='Viridis',
                            showscale=True,
                            colorbar=dict(title="Relevance %")
                        ),
                        text=[f"{score:.1f}%" for score in scores],
                        textposition='auto',
                        hovertemplate='<b>%{y}</b><br>Relevance: %{x:.1f}%<extra></extra>'
                    )
                ])
                
                fig_relevance.update_layout(
                    title=dict(
                        text="📊 Source Relevance Scores",
                        font=dict(size=16, color='#f0f6fc'),
                        x=0.5
                    ),
                    plot_bgcolor='rgba(13, 17, 23, 0.8)',
                    paper_bgcolor='rgba(13, 17, 23, 0.8)',
                    font=dict(color='#f0f6fc', family='Inter'),
                    xaxis=dict(
                        title="Relevance Score (%)",
                        gridcolor='rgba(48, 54, 61, 0.5)'
                    ),
                    yaxis=dict(
                        title="Research Papers",
                        gridcolor='rgba(48, 54, 61, 0.5)'
                    ),
                    margin=dict(l=200, r=20, t=60, b=40),
                    height=400
                )
                viz_data['relevance'] = fig_relevance
        
        # Enhanced journal distribution with real data
        if sources or research_data:
            journals = []
            
            # From sources
            for s in sources:
                journal = s.get('journal', '')
                if journal and journal != 'Unknown Journal':
                    journals.append(journal)
            
            # From research data (if available)
            if research_data:
                for paper in research_data[:50]:  # Sample for performance
                    journal = paper.get('journal', '')
                    if journal and journal not in journals:
                        journals.append(journal)
            
            if journals:
                journal_counts = Counter(journals)
                # Take top 8 journals
                top_journals = dict(journal_counts.most_common(8))
                
                colors = ['#58a6ff', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#84cc16', '#f97316']
                
                fig_journals = go.Figure(data=[
                    go.Pie(
                        labels=list(top_journals.keys()),
                        values=list(top_journals.values()),
                        hole=0.4,
                        marker=dict(colors=colors[:len(top_journals)]),
                        textinfo='label+percent',
                        textposition='auto',
                        hovertemplate='<b>%{label}</b><br>Papers: %{value}<br>%{percent}<extra></extra>'
                    )
                ])
                
                fig_journals.update_layout(
                    title=dict(
                        text="📚 Research Sources by Journal",
                        font=dict(size=16, color='#f0f6fc'),
                        x=0.5
                    ),
                    plot_bgcolor='rgba(13, 17, 23, 0.8)',
                    paper_bgcolor='rgba(13, 17, 23, 0.8)',
                    font=dict(color='#f0f6fc', family='Inter'),
                    margin=dict(l=20, r=20, t=60, b=20),
                    height=400,
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05
                    )
                )
                viz_data['journals'] = fig_journals
        
        # Publication timeline from research data
        if research_data:
            years = []
            for paper in research_data:
                year = paper.get('year')
                if year and isinstance(year, (int, str)) and str(year).isdigit():
                    years.append(int(year))
            
            if years:
                year_counts = Counter(years)
                sorted_years = dict(sorted(year_counts.items()))
                
                fig_timeline = go.Figure(data=[
                    go.Scatter(
                        x=list(sorted_years.keys()),
                        y=list(sorted_years.values()),
                        mode='lines+markers',
                        line=dict(color='#58a6ff', width=3),
                        marker=dict(size=8, color='#58a6ff'),
                        fill='tonexty',
                        fillcolor='rgba(88, 166, 255, 0.1)',
                        hovertemplate='<b>Year %{x}</b><br>Publications: %{y}<extra></extra>'
                    )
                ])
                
                fig_timeline.update_layout(
                    title=dict(
                        text="📈 Space Biology Publications Timeline",
                        font=dict(size=16, color='#f0f6fc'),
                        x=0.5
                    ),
                    plot_bgcolor='rgba(13, 17, 23, 0.8)',
                    paper_bgcolor='rgba(13, 17, 23, 0.8)',
                    font=dict(color='#f0f6fc', family='Inter'),
                    xaxis=dict(
                        title="Year",
                        gridcolor='rgba(48, 54, 61, 0.5)'
                    ),
                    yaxis=dict(
                        title="Number of Publications",
                        gridcolor='rgba(48, 54, 61, 0.5)'
                    ),
                    margin=dict(l=60, r=20, t=60, b=40),
                    height=400
                )
                viz_data['timeline'] = fig_timeline
        
        return viz_data
        
    except Exception as e:
        logger.error(f"Error creating visualizations: {e}")
        return {}

def render_visualizations(messages: List[Dict], all_sources: List[Dict]):
    """Render enhanced real-time visualizations with actual research data."""
    if not messages or len([m for m in messages if m['role'] == 'user']) < 1:
        # Show welcome visualizations with real data
        st.markdown("### 📊 Research Database Overview")
        
        try:
            # Load and show overview of actual data
            pub_file = Path("data/processed/publications.json")
            if pub_file.exists():
                with open(pub_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data:
                    # Create overview visualizations
                    years = [p.get('year') for p in data if p.get('year')]
                    years = [int(y) for y in years if str(y).isdigit()]
                    
                    if years:
                        year_counts = Counter(years)
                        sorted_years = dict(sorted(year_counts.items()))
                        
                        fig = go.Figure(data=[
                            go.Bar(
                                x=list(sorted_years.keys()),
                                y=list(sorted_years.values()),
                                marker_color='#58a6ff',
                                hovertemplate='<b>%{x}</b><br>Publications: %{y}<extra></extra>'
                            )
                        ])
                        
                        fig.update_layout(
                            title="📈 Publications by Year",
                            plot_bgcolor='rgba(13, 17, 23, 0.8)',
                            paper_bgcolor='rgba(13, 17, 23, 0.8)',
                            font=dict(color='#f0f6fc'),
                            height=300
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
            st.info("💡 Start a conversation to see personalized analytics!")
        except:
            st.info("💡 Start asking questions to see research analytics!")
        return
    
    # Collect all sources from the conversation
    sources = []
    for msg in messages:
        if msg.get('role') == 'assistant' and msg.get('sources'):
            sources.extend(msg.get('sources', []))
    
    if not sources:
        sources = all_sources
    
    viz_data = create_research_visualizations(messages, sources)
    
    if viz_data:
        st.markdown("### 📊 Session Analytics")
        
        # Create enhanced tabs with icons
        available_tabs = []
        tab_names = []
        
        if 'topics' in viz_data:
            available_tabs.append('topics')
            tab_names.append("🔬 Topics")
        
        if 'relevance' in viz_data:
            available_tabs.append('relevance')
            tab_names.append("📊 Relevance")
            
        if 'journals' in viz_data:
            available_tabs.append('journals')
            tab_names.append("📚 Journals")
            
        if 'timeline' in viz_data:
            available_tabs.append('timeline')
            tab_names.append("📈 Timeline")
        
        if available_tabs:
            tabs = st.tabs(tab_names)
            
            for i, tab_key in enumerate(available_tabs):
                with tabs[i]:
                    if tab_key in viz_data:
                        st.plotly_chart(viz_data[tab_key], use_container_width=True, key=f"chart_{tab_key}")
                        
                        # Add insights based on the chart
                        if tab_key == 'topics':
                            st.markdown("**� Insights:** Topics mentioned most frequently in your conversation.")
                        elif tab_key == 'relevance':
                            st.markdown("**💡 Insights:** Most relevant research papers for your queries.")
                        elif tab_key == 'journals':
                            st.markdown("**💡 Insights:** Leading journals in the retrieved research.")
                        elif tab_key == 'timeline':
                            st.markdown("**💡 Insights:** Publication timeline of relevant research.")
        else:
            st.info("� Analytics will appear as you explore research topics!")

def render_navbar():
    """Render the Chat History button at the top right of the page."""
    
    # Enhanced CSS for proper button targeting and styling
    st.markdown("""
    <style>
    /* Remove default top padding */
    .main .block-container {
        padding-top: 0.5rem !important;
    }
    
    /* Hide any stray HTML div tags in content */
    .stMarkdown div:contains("</div>"):empty,
    .stMarkdown p:contains("</div>"):empty {
        display: none !important;
    }
    
    /* FORCE GREEN STYLING - Multiple selectors to override everything */
    .stApp button[data-testid*="baseButton"],
    .stApp div[data-testid="stButton"] button,
    div[data-testid="column"] div[data-testid="stButton"] button,
    [data-testid="stButton"] > button,
    button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        padding: 10px 18px !important;
        border-radius: 25px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-family: 'Inter', system-ui, sans-serif !important;
        min-height: 40px !important;
        white-space: nowrap !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
    }
    
    /* Hover effects */
    .stApp button[data-testid*="baseButton"]:hover,
    .stApp div[data-testid="stButton"] button:hover,
    div[data-testid="column"] div[data-testid="stButton"] button:hover,
    [data-testid="stButton"] > button:hover,
    button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 30px rgba(16, 185, 129, 0.5) !important;
        color: white !important;
        border-color: rgba(16, 185, 129, 0.5) !important;
    }
    
    /* Override Streamlit's secondary button styles specifically */
    button[data-testid="baseButton-secondary"],
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
    }
    
    button[data-testid="baseButton-secondary"]:hover,
    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: white !important;
        border-color: rgba(16, 185, 129, 0.5) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create a simple container for the button at the top right
    st.markdown("""
    <div style="position: fixed; top: 10px; right: 15px; z-index: 99999;">
        <form action="" method="get">
            <button type="submit" name="page" value="Chat_History" 
                    style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                           color: white; 
                           border: 1px solid rgba(16, 185, 129, 0.3); 
                           border-radius: 25px; 
                           padding: 10px 18px; 
                           font-weight: 700; 
                           font-size: 14px; 
                           box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4); 
                           cursor: pointer; 
                           transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
                           font-family: 'Inter', system-ui, sans-serif; 
                           min-height: 40px; 
                           white-space: nowrap; 
                           backdrop-filter: blur(10px);"
                    onmouseover="this.style.background='linear-gradient(135deg, #059669 0%, #047857 100%)'; this.style.transform='translateY(-2px) scale(1.02)'; this.style.boxShadow='0 8px 30px rgba(16, 185, 129, 0.5)';"
                    onmouseout="this.style.background='linear-gradient(135deg, #10b981 0%, #059669 100%)'; this.style.transform='translateY(0px) scale(1)'; this.style.boxShadow='0 6px 20px rgba(16, 185, 129, 0.4)';">
                📚 Chat History
            </button>
        </form>
    </div>
    """, unsafe_allow_html=True)
    
    # Check for page parameter and switch if needed  
    query_params = st.query_params
    if query_params.get("page") == "Chat_History":
        st.switch_page("pages/Chat_History.py")
    


def render_message(role: str, content: str, sources: List[Dict] = None):
    """Render a message using Streamlit's native chat components for better markdown support."""
    with st.chat_message(role, avatar="👨‍🚀" if role == "user" else "🚀"):
        # Use st.markdown for proper markdown rendering with all features
        st.markdown(content, unsafe_allow_html=False)
        
        # Enhanced Sources section for assistant messages
        if role == "assistant" and sources and len(sources) > 0:
            # Filter and clean sources
            valid_sources = []
            for source in sources:
                if (source and 
                    isinstance(source, dict) and 
                    source.get('title') and 
                    isinstance(source.get('title'), str) and
                    source.get('title').strip() and
                    not any(tag in source.get('title', '') for tag in ['<div>', '</div>', '</', '>', '<'])):
                    valid_sources.append(source)
            
            # Deduplicate sources by title (keep the one with highest score)
            seen_titles = {}
            
            for source in valid_sources:
                title = str(source.get('title', '')).strip().lower()
                score = source.get('score', 0)
                
                if title and title != 'unknown title' and len(title) > 3:
                    if title not in seen_titles or score > seen_titles[title]['score']:
                        seen_titles[title] = source
            
            # Convert back to list and sort by score (highest first)
            unique_sources = list(seen_titles.values())
            unique_sources.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            if unique_sources:
                st.markdown("---")
                st.markdown("**📚 Research Sources**")
                
                # Display sources in a clean format
                for i, source in enumerate(unique_sources[:4], 1):
                    try:
                        title = str(source.get('title', 'Unknown Title')).strip()
                        if not title or len(title) < 5:
                            continue
                            
                        authors = source.get('authors', 'Unknown Authors')
                        if isinstance(authors, list):
                            authors = ', '.join(str(a) for a in authors[:2] if a)
                        
                        relevance = int((source.get('score', 0) * 100))
                        url = source.get('url', '#')
                        
                        # Create an expander for each source
                        with st.expander(f"📄 {title[:60]}{'...' if len(title) > 60 else ''} ({relevance}% match)"):
                            st.write(f"**Authors:** {authors}")
                            if url != '#':
                                st.markdown(f"**Link:** [📖 View Paper]({url})")
                            st.write(f"**Relevance Score:** {relevance}%")
                    
                    except Exception as e:
                        continue

def render_sidebar(db: ChatDatabase, current_session_id: str = None):
    """Render sidebar with chat history - only if user has chat history."""
    # Return early if database is not available
    if not db or not st.session_state.get('database_available', False):
        return None
        
    try:
        sessions = db.get_all_sessions()
    except Exception as e:
        logger.error(f"Failed to get sessions: {e}")
        st.session_state.database_available = False
        return None
    
    # Check if we should show sidebar
    show_sidebar = len(sessions) > 0 or len(st.session_state.get('messages', [])) > 0
    
    # Debug info
    logger.info(f"Sidebar check: {len(sessions)} sessions, {len(st.session_state.get('messages', []))} messages, show_sidebar: {show_sidebar}")
    
    # If we have sessions or messages, show the sidebar
    if show_sidebar:
        with st.sidebar:
            # Header
            st.markdown("""
            <div style="padding: 0 0 1rem 0; border-bottom: 1px solid rgba(88, 166, 255, 0.2); margin-bottom: 1.5rem;">
                <h3 style="color: #f0f6fc; font-size: 1.2rem; margin: 0; font-weight: 600; text-align: center;">
                    💬 Chat History
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            # New Chat Button
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("✨ New Chat", key="new_chat", use_container_width=True, type="primary"):
                    # Create new session
                    try:
                        new_session_id = db.create_session()
                        st.session_state.current_session_id = new_session_id
                    except Exception as e:
                        logger.error(f"Failed to create new session: {e}")
                        st.session_state.current_session_id = None
                        st.session_state.database_available = False
                    
                    st.session_state.messages = []
                    st.session_state.is_processing = False
                    st.rerun()
            
            st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
            
            # Chat History
            if sessions:
                st.markdown("**Recent Conversations**")
                st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
                
                for session in sessions:
                    # Create a container for each session
                    with st.container():
                        is_current = session['id'] == current_session_id
                        
                        # Truncate title appropriately for sidebar
                        display_title = session['title'][:35] + ('...' if len(session['title']) > 35 else '')
                        
                        # Session button
                        if st.button(
                            f"📝 {display_title}",
                            key=f"session_{session['id']}",
                            help=f"💬 {session['message_count']} messages\n🕒 {session['updated_at'][:16]}",
                            use_container_width=True
                        ):
                            # Load session
                            try:
                                st.session_state.current_session_id = session['id']
                                st.session_state.messages = db.get_session_messages(session['id'])
                                st.session_state.is_processing = False
                                st.rerun()
                            except Exception as e:
                                logger.error(f"Failed to load session: {e}")
                                st.error("❌ Failed to load session")
                        
                        # Show compact session metadata
                        st.markdown(f"""
                        <div style="font-size: 0.7rem; color: #8b949e; margin-bottom: 0.5rem; padding: 0 0.5rem; text-align: center;">
                            🕒 {session['updated_at'][5:16]} • {session['message_count']} msg
                        </div>
                        """, unsafe_allow_html=True)
            
            # Clear History Button
            st.markdown("<div style='margin: 1.5rem 0 1rem 0;'></div>", unsafe_allow_html=True)
            
            # Use a smaller button for clear history
            if st.button("🗑️ Clear All", key="clear_history", type="secondary", use_container_width=True):
                if st.session_state.get('confirm_clear', False):
                    # Actually clear
                    try:
                        db.clear_all_history()
                        st.session_state.current_session_id = None
                        st.session_state.messages = []
                        st.session_state.is_processing = False
                        st.session_state.confirm_clear = False
                        st.success("✅ Cleared!")
                        st.rerun()
                    except Exception as e:
                        logger.error(f"Failed to clear history: {e}")
                        st.error("❌ Failed to clear")
                        st.session_state.confirm_clear = False
                else:
                    # Ask for confirmation
                    st.session_state.confirm_clear = True
                    st.warning("⚠️ Click again to confirm")
            
            # Stats - compact version
            total_sessions = len(sessions)
            if total_sessions > 0:
                st.markdown(f"""
                <div style="margin-top: 1.5rem; padding: 0.75rem; background: rgba(88, 166, 255, 0.05); border-radius: 6px; border: 1px solid rgba(88, 166, 255, 0.1);">
                    <div style="text-align: center; color: #8b949e; font-size: 0.75rem;">
                        📊 {total_sessions} session{'s' if total_sessions != 1 else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        # No sidebar needed
        return None
    
    return current_session_id

def main():
    """Main application function with persistent chat."""
    # Initialize database with error handling
    db = None
    try:
        db = ChatDatabase()
        st.session_state.database_available = True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        st.session_state.database_available = False
        st.warning("⚠️ Chat history is temporarily unavailable. Your current session will work but won't be saved.")
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    
    if 'rag_initialized' not in st.session_state:
        st.session_state.rag_initialized = False
    
    # Render navbar
    render_navbar()
    
    # Always try to render sidebar if database is available
    current_session = None
    if db and st.session_state.database_available:
        current_session = render_sidebar(db, st.session_state.current_session_id)
    
    # Main chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Initialize RAG system
    if not st.session_state.rag_initialized:
        with st.spinner("🚀 Initializing K-OSMOS Knowledge Engine..."):
            rag = initialize_rag()
            if rag:
                st.session_state.rag = rag
                st.session_state.rag_initialized = True
            else:
                st.error("❌ Failed to initialize the knowledge engine. Please check your configuration.")
                st.stop()
    
    # Display clean welcome section if no messages
    if not st.session_state.messages:
        # Hero section with minimal top spacing
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem 2rem 2rem 2rem; background: linear-gradient(135deg, rgba(88, 166, 255, 0.05) 0%, rgba(210, 168, 255, 0.05) 100%); border-radius: 20px; margin: 0.5rem 0 1.5rem 0; border: 1px solid rgba(88, 166, 255, 0.1);">
            <h1 style="background: linear-gradient(135deg, #58a6ff 0%, #d2a8ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 700; margin-bottom: 1rem; font-size: 3rem; font-family: system-ui, -apple-system, sans-serif;">
                Welcome to K-OSMOS
            </h1>
            <p style="font-size: 1.3rem; margin-bottom: 0.5rem; color: #f0f6fc; font-weight: 500;">
                Your AI-powered gateway to space biology research
            </p>
            <p style="font-size: 1rem; color: #8b949e; font-weight: 400; max-width: 600px; margin: 0 auto;">
                Explore 600+ research papers, discover groundbreaking experiments, and unlock insights about life in space
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Research areas using Streamlit columns
        st.markdown("### 🔬 Research Areas to Explore")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(88, 166, 255, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%); padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(88, 166, 255, 0.2); text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">🦴</div>
                <h4 style="color: #f0f6fc; margin-bottom: 0.5rem;">Bone & Muscle Health</h4>
                <small style="color: #8b949e;">Microgravity effects on skeletal systems</small>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%); padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(16, 185, 129, 0.2); text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">🌱</div>
                <h4 style="color: #f0f6fc; margin-bottom: 0.5rem;">Space Agriculture</h4>
                <small style="color: #8b949e;">Plant growth in space environments</small>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(239, 68, 68, 0.1) 100%); padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(245, 158, 11, 0.2); text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">❤️</div>
                <h4 style="color: #f0f6fc; margin-bottom: 0.5rem;">Cardiovascular Research</h4>
                <small style="color: #8b949e;">Heart health in space flight</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%); padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(239, 68, 68, 0.2); text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">🧠</div>
                <h4 style="color: #f0f6fc; margin-bottom: 0.5rem;">Neurological Studies</h4>
                <small style="color: #8b949e;">Brain function in space conditions</small>
            </div>
            """, unsafe_allow_html=True)
            
        with col5:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%); padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(139, 92, 246, 0.2); text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">🔬</div>
                <h4 style="color: #f0f6fc; margin-bottom: 0.5rem;">Cell Biology</h4>
                <small style="color: #8b949e;">Cellular behavior in microgravity</small>
            </div>
            """, unsafe_allow_html=True)
            
        with col6:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(88, 166, 255, 0.1) 100%); padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(6, 182, 212, 0.2); text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">☢️</div>
                <h4 style="color: #f0f6fc; margin-bottom: 0.5rem;">Radiation Effects</h4>
                <small style="color: #8b949e;">Cosmic radiation impacts</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Main content area with visualizations toggle
    if st.session_state.messages and len([m for m in st.session_state.messages if m['role'] == 'assistant']) > 0:
        col_main, col_viz = st.columns([2, 1])
        
        with col_main:
            # Display chat messages
            for message in st.session_state.messages:
                render_message(
                    message['role'], 
                    message['content'], 
                    message.get('sources', [])
                )
        
        with col_viz:
            # Collect all sources for visualizations
            all_sources = []
            for msg in st.session_state.messages:
                if msg.get('sources'):
                    all_sources.extend(msg.get('sources', []))
            
            render_visualizations(st.session_state.messages, all_sources)
    else:
        # Display chat messages without visualizations if no assistant messages
        for message in st.session_state.messages:
            render_message(
                message['role'], 
                message['content'], 
                message.get('sources', [])
            )
    
    # Check if we're currently processing a query
    if 'is_processing' not in st.session_state:
        st.session_state.is_processing = False
    
    # Native Streamlit chat input for better UX
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; color: #8b949e; font-size: 0.9rem; margin-bottom: 1rem;">
            💡 Try asking: "What are the effects of microgravity on bone density?" or "Show me ISS plant experiments"
        </div>
        """, unsafe_allow_html=True)
    
    # Use Streamlit's native chat input
    user_input = st.chat_input(
        "Ask me about space biology research, experiments, missions, or any specific topics...",
        disabled=st.session_state.is_processing,
        max_chars=1000
    )
    
    # Process user input
    if user_input and not st.session_state.is_processing:
        # Set processing flag
        st.session_state.is_processing = True
        
        # Create new session if database is available and none exists
        if db and st.session_state.database_available and not st.session_state.current_session_id:
            try:
                st.session_state.current_session_id = db.create_session()
            except Exception as e:
                logger.error(f"Failed to create session: {e}")
                st.session_state.database_available = False
        
        # Add user message to session state
        user_message = {
            'role': 'user',
            'content': user_input,
            'sources': []
        }
        
        # Save to database if available
        if db and st.session_state.database_available and st.session_state.current_session_id:
            try:
                db.add_message(st.session_state.current_session_id, 'user', user_input)
            except Exception as e:
                logger.error(f"Failed to save user message: {e}")
                st.session_state.database_available = False
        
        # Add to session state for immediate display
        st.session_state.messages.append(user_message)
        
        # Rerun to show user message immediately
        st.rerun()
    
    # Show enhanced loading indicator if we're processing
    if st.session_state.is_processing:
        # Show typing indicator using native Streamlit chat
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🔍 K-OSMOS is analyzing research papers..."):
                st.write("Searching through space biology research database...")
                st.empty()  # Placeholder for the response
        
        # Get the last user message to process
        last_user_message = None
        for msg in reversed(st.session_state.messages):
            if msg['role'] == 'user':
                last_user_message = msg['content']
                break
        
        if last_user_message:
            # Get RAG response with conversation history
            try:
                # Prepare conversation history (exclude the current message being processed)
                conversation_history = st.session_state.messages[:-1] if len(st.session_state.messages) > 1 else []
                
                response_data = asyncio.run(st.session_state.rag.chat(
                    last_user_message, 
                    conversation_history=conversation_history
                ))
                
                if response_data.get('success', False):
                    bot_response = response_data['response']
                    sources = response_data.get('sources', [])
                    
                    # Save to database if available
                    if db and st.session_state.database_available and st.session_state.current_session_id:
                        try:
                            db.add_message(st.session_state.current_session_id, 'assistant', bot_response, sources)
                        except Exception as e:
                            logger.error(f"Failed to save assistant message: {e}")
                            st.session_state.database_available = False
                    
                    # Add bot message to session state
                    bot_message = {
                        'role': 'assistant',
                        'content': bot_response,
                        'sources': sources
                    }
                    st.session_state.messages.append(bot_message)
                else:
                    error_message = "I apologize, but I encountered an issue processing your request. Please try again."
                    
                    # Save error to database if available
                    if db and st.session_state.database_available and st.session_state.current_session_id:
                        try:
                            db.add_message(st.session_state.current_session_id, 'assistant', error_message)
                        except Exception as e:
                            logger.error(f"Failed to save error message: {e}")
                            st.session_state.database_available = False
                    
                    bot_message = {
                        'role': 'assistant',
                        'content': error_message,
                        'sources': []
                    }
                    st.session_state.messages.append(bot_message)
            
            except Exception as e:
                logger.error(f"Error getting RAG response: {e}")
                error_message = "I'm experiencing technical difficulties. Please try again in a moment."
                
                # Save error to database if available
                if db and st.session_state.database_available and st.session_state.current_session_id:
                    try:
                        db.add_message(st.session_state.current_session_id, 'assistant', error_message)
                    except Exception as db_error:
                        logger.error(f"Failed to save error message: {db_error}")
                        st.session_state.database_available = False
                
                bot_message = {
                    'role': 'assistant',
                    'content': error_message,
                    'sources': []
                }
                st.session_state.messages.append(bot_message)
        
        # Clear processing flag and rerun to show response
        st.session_state.is_processing = False
        st.rerun()

    
    st.markdown('</div>', unsafe_allow_html=True)

    # Add JavaScript to handle sidebar expand button visibility
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        
        // Create a reliable expand button that's always visible when sidebar is collapsed
        function createExpandButton() {
            // Remove any existing custom button
            const existingBtn = document.querySelector('#custom-expand-btn');
            if (existingBtn) {
                existingBtn.remove();
            }
            
            const expandBtn = document.createElement('div');
            expandBtn.id = 'custom-expand-btn';
            expandBtn.innerHTML = '📂';
            expandBtn.title = 'Open Chat History';
            expandBtn.style.cssText = `
                position: fixed !important;
                top: 50% !important;
                left: 15px !important;
                transform: translateY(-50%) !important;
                width: 50px !important;
                height: 50px !important;
                background: linear-gradient(135deg, #58a6ff 0%, #1f6feb 100%) !important;
                border: 3px solid rgba(255, 255, 255, 0.9) !important;
                border-radius: 50% !important;
                display: none !important;
                align-items: center !important;
                justify-content: center !important;
                color: white !important;
                font-size: 18px !important;
                font-weight: bold !important;
                cursor: pointer !important;
                z-index: 999999 !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                box-shadow: 0 8px 25px rgba(88, 166, 255, 0.6), 0 0 0 0 rgba(88, 166, 255, 0.2) !important;
                backdrop-filter: blur(20px) !important;
                animation: expandButtonPulse 3s ease-in-out infinite !important;
                user-select: none !important;
                -webkit-user-select: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
            `;
            
            // Add enhanced animations
            const animationCSS = `
                <style id="expand-btn-animations">
                @keyframes expandButtonPulse {
                    0%, 100% { 
                        box-shadow: 0 8px 25px rgba(88, 166, 255, 0.6), 0 0 0 0 rgba(88, 166, 255, 0.2);
                        transform: translateY(-50%) scale(1);
                    }
                    50% { 
                        box-shadow: 0 12px 30px rgba(88, 166, 255, 0.8), 0 0 0 8px rgba(88, 166, 255, 0.15);
                        transform: translateY(-50%) scale(1.05);
                    }
                }
                
                @keyframes expandButtonBounce {
                    0%, 20%, 53%, 80%, 100% {
                        transform: translateY(-50%) scale(1);
                    }
                    40%, 43% {
                        transform: translateY(-50%) scale(1.2);
                    }
                    70% {
                        transform: translateY(-50%) scale(1.1);
                    }
                    90% {
                        transform: translateY(-50%) scale(1.05);
                    }
                }
                </style>
            `;
            
            if (!document.querySelector('#expand-btn-animations')) {
                document.head.insertAdjacentHTML('beforeend', animationCSS);
            }
            
            // Enhanced hover effects
            expandBtn.addEventListener('mouseenter', function() {
                this.style.animation = 'expandButtonBounce 0.6s ease-in-out';
                this.style.transform = 'translateY(-50%) scale(1.15)';
                this.style.boxShadow = '0 16px 35px rgba(88, 166, 255, 0.9), 0 0 0 6px rgba(88, 166, 255, 0.25)';
                this.style.borderColor = 'rgba(255, 255, 255, 1)';
                this.innerHTML = '📖';
            });
            
            expandBtn.addEventListener('mouseleave', function() {
                this.style.animation = 'expandButtonPulse 3s ease-in-out infinite';
                this.style.transform = 'translateY(-50%) scale(1)';
                this.style.boxShadow = '0 8px 25px rgba(88, 166, 255, 0.6), 0 0 0 0 rgba(88, 166, 255, 0.2)';
                this.style.borderColor = 'rgba(255, 255, 255, 0.9)';
                this.innerHTML = '📂';
            });
            
            expandBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Add click animation
                this.style.transform = 'translateY(-50%) scale(0.95)';
                setTimeout(() => {
                    this.style.transform = 'translateY(-50%) scale(1)';
                }, 150);
                
                // Try multiple methods to expand sidebar
                const methods = [
                    () => {
                        const collapsedControl = document.querySelector('[data-testid="collapsedControl"]');
                        if (collapsedControl && collapsedControl.offsetParent !== null) {
                            collapsedControl.click();
                            return true;
                        }
                        return false;
                    },
                    () => {
                        const sidebarNavButton = document.querySelector('[data-testid="stSidebar"] button[kind="header"]');
                        if (sidebarNavButton) {
                            sidebarNavButton.click();
                            return true;
                        }
                        return false;
                    },
                    () => {
                        const sidebar = document.querySelector('[data-testid="stSidebar"]');
                        if (sidebar) {
                            sidebar.style.transform = 'translateX(0px)';
                            sidebar.style.marginLeft = '0px';
                            return true;
                        }
                        return false;
                    }
                ];
                
                // Try each method until one works
                for (const method of methods) {
                    if (method()) {
                        break;
                    }
                }
                
                // Check if sidebar expanded after a delay
                setTimeout(() => {
                    checkAndUpdateButtonVisibility();
                }, 300);
            });
            
            document.body.appendChild(expandBtn);
            return expandBtn;
        }
        
        // Function to check if sidebar is collapsed
        function isSidebarCollapsed() {
            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) return false;
            
            const sidebarRect = sidebar.getBoundingClientRect();
            const computedStyle = window.getComputedStyle(sidebar);
            
            // Check multiple indicators of collapsed state
            const isHidden = sidebarRect.left < -250 || 
                           sidebarRect.width < 50 ||
                           computedStyle.transform.includes('translateX(-') ||
                           computedStyle.marginLeft.includes('-') ||
                           sidebar.style.marginLeft.includes('-') ||
                           sidebar.style.transform.includes('translateX(-');
            
            return isHidden;
        }
        
        // Function to show/hide expand button based on sidebar state
        function checkAndUpdateButtonVisibility() {
            const expandBtn = document.querySelector('#custom-expand-btn');
            if (!expandBtn) return;
            
            const collapsed = isSidebarCollapsed();
            
            if (collapsed) {
                // Show button with smooth animation
                expandBtn.style.display = 'flex';
                expandBtn.style.visibility = 'visible';
                setTimeout(() => {
                    expandBtn.style.opacity = '1';
                }, 50);
            } else {
                // Hide button with smooth animation
                expandBtn.style.opacity = '0';
                setTimeout(() => {
                    expandBtn.style.display = 'none';
                    expandBtn.style.visibility = 'hidden';
                }, 300);
            }
        }
        
        // Initialize the expand button
        let expandButton = null;
        
        function initializeExpandButton() {
            if (!expandButton) {
                expandButton = createExpandButton();
            }
            setTimeout(() => {
                checkAndUpdateButtonVisibility();
            }, 100);
        }
        
        // Initial setup
        initializeExpandButton();
        
        // Set up observers to monitor sidebar changes
        const setupObservers = () => {
            // Observer for sidebar element changes
            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            if (sidebar) {
                const sidebarObserver = new MutationObserver(() => {
                    setTimeout(checkAndUpdateButtonVisibility, 50);
                });
                
                sidebarObserver.observe(sidebar, {
                    attributes: true,
                    attributeFilter: ['style', 'class'],
                    childList: false,
                    subtree: false
                });
            }
            
            // Observer for DOM changes that might affect sidebar
            const bodyObserver = new MutationObserver((mutations) => {
                let shouldCheck = false;
                mutations.forEach((mutation) => {
                    if (mutation.type === 'childList' || 
                        (mutation.type === 'attributes' && mutation.target.hasAttribute('data-testid'))) {
                        shouldCheck = true;
                    }
                });
                
                if (shouldCheck) {
                    setTimeout(() => {
                        // Re-create button if it doesn't exist
                        if (!document.querySelector('#custom-expand-btn')) {
                            initializeExpandButton();
                        } else {
                            checkAndUpdateButtonVisibility();
                        }
                    }, 100);
                }
            });
            
            bodyObserver.observe(document.body, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ['style', 'class', 'data-testid']
            });
        };
        
        // Setup observers after a delay to ensure DOM is ready
        setTimeout(setupObservers, 500);
        
        // Periodic check to ensure button stays functional
        setInterval(() => {
            if (!document.querySelector('#custom-expand-btn')) {
                initializeExpandButton();
            } else {
                checkAndUpdateButtonVisibility();
            }
        }, 2000);
        
        // Handle window resize to ensure button stays positioned correctly
        window.addEventListener('resize', () => {
            setTimeout(checkAndUpdateButtonVisibility, 100);
        });
        
        // Handle orientation change on mobile devices
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                checkAndUpdateButtonVisibility();
            }, 500);
        });
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()