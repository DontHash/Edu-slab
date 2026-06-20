"""
Database migration to add communication features:
- Location fields to users
- Communication methods to sessions
- Chat messages table
- Shared resources table
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings


def run_migration():
    """Add communication features to database"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("Starting migration: Adding communication features...")
        
        # Add location fields to users table
        print("\n1. Adding location fields to users table...")
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN city VARCHAR"))
            print("   ✓ Added city column")
        except Exception as e:
            print(f"   - city column may already exist: {e}")
        
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN state VARCHAR"))
            print("   ✓ Added state column")
        except Exception as e:
            print(f"   - state column may already exist: {e}")
        
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN zip_code VARCHAR"))
            print("   ✓ Added zip_code column")
        except Exception as e:
            print(f"   - zip_code column may already exist: {e}")
        
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN locality VARCHAR"))
            print("   ✓ Added locality column")
        except Exception as e:
            print(f"   - locality column may already exist: {e}")
        
        # Add communication fields to tutoring_sessions table
        print("\n2. Adding communication fields to tutoring_sessions...")
        try:
            conn.execute(text("ALTER TABLE tutoring_sessions ADD COLUMN communication_method VARCHAR DEFAULT 'text'"))
            print("   ✓ Added communication_method column")
        except Exception as e:
            print(f"   - communication_method column may already exist: {e}")
        
        try:
            conn.execute(text("ALTER TABLE tutoring_sessions ADD COLUMN meeting_link VARCHAR"))
            print("   ✓ Added meeting_link column")
        except Exception as e:
            print(f"   - meeting_link column may already exist: {e}")
        
        try:
            conn.execute(text("ALTER TABLE tutoring_sessions ADD COLUMN meeting_location VARCHAR"))
            print("   ✓ Added meeting_location column")
        except Exception as e:
            print(f"   - meeting_location column may already exist: {e}")
        
        # Create chat_messages table
        print("\n3. Creating chat_messages table...")
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER NOT NULL,
                    sender_id INTEGER NOT NULL,
                    receiver_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    message_type VARCHAR DEFAULT 'text',
                    file_url VARCHAR,
                    file_name VARCHAR,
                    file_size INTEGER,
                    file_type VARCHAR,
                    is_read BOOLEAN DEFAULT 0,
                    read_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (match_id) REFERENCES peer_matches(id),
                    FOREIGN KEY (sender_id) REFERENCES users(id),
                    FOREIGN KEY (receiver_id) REFERENCES users(id)
                )
            """))
            print("   ✓ Created chat_messages table")
        except Exception as e:
            print(f"   - chat_messages table may already exist: {e}")
        
        # Create shared_resources table
        print("\n4. Creating shared_resources table...")
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS shared_resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER NOT NULL,
                    uploader_id INTEGER NOT NULL,
                    title VARCHAR NOT NULL,
                    description TEXT,
                    resource_type VARCHAR NOT NULL,
                    file_url VARCHAR,
                    file_name VARCHAR,
                    file_size INTEGER,
                    external_link VARCHAR,
                    subject VARCHAR,
                    chapter VARCHAR,
                    tags JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (match_id) REFERENCES peer_matches(id),
                    FOREIGN KEY (uploader_id) REFERENCES users(id)
                )
            """))
            print("   ✓ Created shared_resources table")
        except Exception as e:
            print(f"   - shared_resources table may already exist: {e}")
        
        # Create indexes for performance
        print("\n5. Creating indexes...")
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_chat_match ON chat_messages(match_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_chat_sender ON chat_messages(sender_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_chat_receiver ON chat_messages(receiver_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_resources_match ON shared_resources(match_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_locality ON users(locality)"))
            print("   ✓ Created indexes")
        except Exception as e:
            print(f"   - Indexes may already exist: {e}")
        
        conn.commit()
        print("\n✓ Migration completed successfully!")


if __name__ == "__main__":
    run_migration()
