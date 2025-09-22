import sqlite3
import os
from datetime import datetime
from typing import Optional, Tuple, List

class DatabaseManager:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist"""
        self.create_tables()
        self.migrate_database()
    
    def migrate_database(self):
        """Handle database schema migrations"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if old chat_history table structure exists
            cursor.execute("PRAGMA table_info(chat_history)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # If old structure exists (has 'content' column), migrate to new structure
            if 'content' in columns and 'message' not in columns:
                print("Migrating database schema...")
                
                # Create new table with correct schema
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chat_history_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        message TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Migrate existing data if any
                try:
                    cursor.execute("""
                        INSERT INTO chat_history_new (session_id, message, created_at)
                        SELECT session_id, content, created_at 
                        FROM chat_history
                    """)
                    
                    # Drop old table and rename new one
                    cursor.execute("DROP TABLE chat_history")
                    cursor.execute("ALTER TABLE chat_history_new RENAME TO chat_history")
                    
                    print("Database migration completed successfully.")
                    
                except Exception as e:
                    print(f"Error during migration: {e}")
                    # If migration fails, just use the new table
                    cursor.execute("DROP TABLE IF EXISTS chat_history_new")
                
                conn.commit()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def create_tables(self):
        """Create necessary tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    profile_picture TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Chat history table (for LangChain SQLChatMessageHistory)
            # This matches the expected schema for SQLChatMessageHistory
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User sessions table (to track user chat sessions)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_id TEXT NOT NULL,
                    session_name TEXT DEFAULT 'New Chat',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, session_id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_history_session ON chat_history(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON user_sessions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            
            conn.commit()
    
    def create_user(self, first_name: str, last_name: str, email: str, password_hash: str, profile_picture: Optional[str] = None) -> bool:
        """Create a new user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (first_name, last_name, email, password_hash, profile_picture)
                    VALUES (?, ?, ?, ?, ?)
                """, (first_name, last_name, email, password_hash, profile_picture))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def user_exists(self, email: str) -> bool:
        """Check if user exists by email"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
            return cursor.fetchone() is not None
    
    def verify_user(self, email: str, password_hash: str) -> Optional[Tuple]:
        """Verify user credentials and return user data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, first_name, last_name, email 
                FROM users 
                WHERE email = ? AND password_hash = ?
            """, (email, password_hash))
            result = cursor.fetchone()
            if result:
                return tuple(result)
            return None
    
    def get_user_info(self, user_id: int) -> Optional[Tuple]:
        """Get complete user information"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, first_name, last_name, email, created_at, profile_picture
                FROM users 
                WHERE id = ?
            """, (user_id,))
            result = cursor.fetchone()
            if result:
                return tuple(result)
            return None
    
    def get_user_profile_picture(self, user_id: int) -> Optional[str]:
        """Get user's profile picture data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT profile_picture FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                return result[0]
            return None
    
    def update_profile_picture(self, user_id: int, profile_picture_data: str) -> bool:
        """Update user's profile picture"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users 
                    SET profile_picture = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (profile_picture_data, user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating profile picture: {e}")
            return False
    
    def update_user_profile(self, user_id: int, first_name: str, last_name: str, 
                        email: str, password_hash: Optional[str] = None) -> bool:
        """Update user profile information"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if password_hash:
                    cursor.execute("""
                        UPDATE users 
                        SET first_name = ?, last_name = ?, email = ?, password_hash = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (first_name, last_name, email, password_hash, user_id))
                else:
                    cursor.execute("""
                        UPDATE users 
                        SET first_name = ?, last_name = ?, email = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (first_name, last_name, email, user_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False
    
    def create_user_session(self, user_id: int, session_id: str, session_name: str = "New Chat") -> bool:
        """Create or update a user session"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO user_sessions (user_id, session_id, session_name, last_accessed)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """, (user_id, session_id, session_name))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error creating user session: {e}")
            return False
    
    def get_user_sessions(self, user_id: int) -> List[Tuple]:
        """Get all sessions for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, session_name, created_at, last_accessed
                FROM user_sessions 
                WHERE user_id = ?
                ORDER BY last_accessed DESC
            """, (user_id,))
            return cursor.fetchall()
    
    def update_session_name(self, user_id: int, session_id: str, session_name: str) -> bool:
        """Update session name"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE user_sessions 
                    SET session_name = ?, last_accessed = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND session_id = ?
                """, (session_name, user_id, session_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating session name: {e}")
            return False
    
    def update_session_access_time(self, user_id: int, session_id: str) -> bool:
        """Update the last accessed time for a session"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE user_sessions 
                    SET last_accessed = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND session_id = ?
                """, (user_id, session_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating session access time: {e}")
            return False
    
    def delete_user_session(self, user_id: int, session_id: str) -> bool:
        """Delete a user session and its chat history"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete chat history for this session
                cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
                
                # Delete user session record
                cursor.execute("""
                    DELETE FROM user_sessions 
                    WHERE user_id = ? AND session_id = ?
                """, (user_id, session_id))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting user session: {e}")
            return False
    
    def get_user_chat_count(self, user_id: int) -> int:
        """Get total number of chat sessions for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM user_sessions WHERE user_id = ?
            """, (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """Clean up old sessions (older than specified days)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get sessions to delete
                cursor.execute("""
                    SELECT session_id FROM user_sessions 
                    WHERE last_accessed < datetime('now', '-{} days')
                """.format(days))
                
                old_sessions = cursor.fetchall()
                
                if old_sessions:
                    session_ids = [session[0] for session in old_sessions]
                    
                    # Delete chat history for old sessions
                    placeholders = ','.join(['?' for _ in session_ids])
                    cursor.execute(f"DELETE FROM chat_history WHERE session_id IN ({placeholders})", session_ids)
                    
                    # Delete old user sessions
                    cursor.execute(f"DELETE FROM user_sessions WHERE session_id IN ({placeholders})", session_ids)
                    
                    conn.commit()
                    return len(session_ids)
                
                return 0
        except Exception as e:
            print(f"Error cleaning up old sessions: {e}")
            return 0
    
    def get_database_stats(self) -> dict:
        """Get database statistics"""
        stats = {}
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total users
            cursor.execute("SELECT COUNT(*) FROM users")
            stats['total_users'] = cursor.fetchone()[0]
            
            # Total sessions
            cursor.execute("SELECT COUNT(*) FROM user_sessions")
            stats['total_sessions'] = cursor.fetchone()[0]
            
            # Total messages
            cursor.execute("SELECT COUNT(*) FROM chat_history")
            stats['total_messages'] = cursor.fetchone()[0]
            
            # Database size
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            result = cursor.fetchone()
            stats['database_size_bytes'] = result[0] if result else 0
            
        return stats