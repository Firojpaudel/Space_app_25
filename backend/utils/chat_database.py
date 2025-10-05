"""
Chat Database Management
Handles persistent chat history storage using SQLite
"""

import sqlite3
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import uuid
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ChatDatabase:
    """SQLite database manager for chat sessions and messages."""
    
    def __init__(self, db_path: str = "chat_sessions.db"):
        """Initialize database connection and create tables if needed."""
        # Store database in the main project directory, not in data folder
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist. Handle corruption gracefully."""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                
                # Test if database is accessible
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                
                # Create sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chat_sessions (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        message_count INTEGER DEFAULT 0
                    )
                """)
                
                # Create messages table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chat_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        sources TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON chat_messages(session_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_updated ON chat_sessions(updated_at DESC)")
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except sqlite3.DatabaseError as e:
            if "file is not a database" in str(e).lower():
                logger.warning("Corrupted database detected, recreating...")
                # Try to remove corrupted file with better error handling
                try:
                    import time
                    # Wait a bit in case file is being released
                    time.sleep(0.5)
                    
                    if self.db_path.exists():
                        # Try to delete with backup approach
                        backup_name = f"{self.db_path.stem}_backup_{int(time.time())}{self.db_path.suffix}"
                        backup_path = self.db_path.parent / backup_name
                        
                        try:
                            # Try to rename instead of delete (safer on Windows)
                            self.db_path.rename(backup_path)
                            logger.info(f"Moved corrupted database to {backup_path}")
                        except:
                            # If rename fails, try force delete
                            try:
                                self.db_path.unlink()
                            except PermissionError:
                                logger.warning("Cannot delete corrupted database file, creating new one with different name")
                                # Use a different name if we can't delete the old file
                                import uuid
                                new_name = f"chat_sessions_{uuid.uuid4().hex[:8]}.db"
                                self.db_path = Path(new_name)
                    
                    # Retry initialization with new/cleaned path
                    with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                        cursor = conn.cursor()
                        
                        # Create sessions table
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS chat_sessions (
                                id TEXT PRIMARY KEY,
                                title TEXT NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                message_count INTEGER DEFAULT 0
                            )
                        """)
                        
                        # Create messages table
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS chat_messages (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                session_id TEXT NOT NULL,
                                role TEXT NOT NULL,
                                content TEXT NOT NULL,
                                sources TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
                            )
                        """)
                        
                        # Create indexes for better performance
                        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON chat_messages(session_id)")
                        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_updated ON chat_sessions(updated_at DESC)")
                        
                        conn.commit()
                        logger.info("Database recreated successfully")
                        
                except Exception as recreate_error:
                    logger.error(f"Failed to recreate database: {recreate_error}")
                    # Fallback: continue without database
                    logger.warning("Continuing without persistent chat history")
                    return
            else:
                logger.error(f"Database error: {e}")
                raise
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def create_session(self, title: str = None) -> str:
        """Create a new chat session and return session ID."""
        session_id = str(uuid.uuid4())
        
        if not title:
            title = f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO chat_sessions (id, title, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (session_id, title, datetime.now(), datetime.now()))
                conn.commit()
                logger.info(f"Created new session: {session_id}")
                return session_id
                
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    def add_message(self, session_id: str, role: str, content: str, sources: List[Dict] = None) -> bool:
        """Add a message to a session."""
        try:
            sources_json = json.dumps(sources) if sources else None
            
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                
                # Ensure session exists
                cursor.execute("SELECT id FROM chat_sessions WHERE id = ?", (session_id,))
                if not cursor.fetchone():
                    # Create session if it doesn't exist
                    cursor.execute("""
                        INSERT INTO chat_sessions (id, title, created_at, updated_at)
                        VALUES (?, ?, ?, ?)
                    """, (session_id, f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                          datetime.now(), datetime.now()))
                
                # Add message
                cursor.execute("""
                    INSERT INTO chat_messages (session_id, role, content, sources)
                    VALUES (?, ?, ?, ?)
                """, (session_id, role, content, sources_json))
                
                # Update session
                cursor.execute("""
                    UPDATE chat_sessions 
                    SET updated_at = ?, 
                        message_count = (SELECT COUNT(*) FROM chat_messages WHERE session_id = ?)
                    WHERE id = ?
                """, (datetime.now(), session_id, session_id))
                
                # Update session title based on first message if it's generic
                if role == 'user':
                    cursor.execute("SELECT title FROM chat_sessions WHERE id = ?", (session_id,))
                    current_title_row = cursor.fetchone()
                    if current_title_row:
                        current_title = current_title_row[0]
                        
                        if "Chat Session" in current_title:
                            # Create a smart title from the first 50 characters
                            smart_title = content[:50].strip()
                            if len(content) > 50:
                                smart_title += "..."
                            
                            cursor.execute("UPDATE chat_sessions SET title = ? WHERE id = ?", 
                                         (smart_title, session_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to add message: {e}")
            return False
    
    def get_session_messages(self, session_id: str) -> List[Dict]:
        """Get all messages for a session."""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT role, content, sources, created_at
                    FROM chat_messages
                    WHERE session_id = ?
                    ORDER BY created_at ASC
                """, (session_id,))
                
                messages = []
                for row in cursor.fetchall():
                    role, content, sources_json, created_at = row
                    sources = json.loads(sources_json) if sources_json else []
                    
                    messages.append({
                        'role': role,
                        'content': content,
                        'sources': sources,
                        'timestamp': created_at
                    })
                
                return messages
                
        except Exception as e:
            logger.error(f"Failed to get session messages: {e}")
            return []
    
    def get_all_sessions(self) -> List[Dict]:
        """Get all chat sessions ordered by most recent."""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, title, created_at, updated_at, message_count
                    FROM chat_sessions
                    ORDER BY updated_at DESC
                """)
                
                sessions = []
                for row in cursor.fetchall():
                    session_id, title, created_at, updated_at, message_count = row
                    sessions.append({
                        'id': session_id,
                        'title': title,
                        'created_at': created_at,
                        'updated_at': updated_at,
                        'message_count': message_count
                    })
                
                return sessions
                
        except Exception as e:
            logger.error(f"Failed to get sessions: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages."""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
                conn.commit()
                logger.info(f"Deleted session: {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False
    
    def clear_all_history(self) -> bool:
        """Clear all chat history."""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM chat_messages")
                cursor.execute("DELETE FROM chat_sessions")
                conn.commit()
                logger.info("Cleared all chat history")
                return True
                
        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
            return False
    
    def get_session_count(self) -> int:
        """Get total number of sessions."""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM chat_sessions")
                return cursor.fetchone()[0]
                
        except Exception as e:
            logger.error(f"Failed to get session count: {e}")
            return 0