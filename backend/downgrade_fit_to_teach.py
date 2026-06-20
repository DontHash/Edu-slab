"""
Downgrade script to revert per-subject fit_to_teach columns back to single fit_to_teach_level
"""
from app.db.database import engine
from sqlalchemy import text


def downgrade():
    conn = engine.connect()
    
    print("Starting database downgrade...")
    print("=" * 50)
    
    # First, add back the original fit_to_teach_level column if it doesn't exist
    try:
        conn.execute(text('ALTER TABLE users ADD COLUMN fit_to_teach_level INTEGER'))
        print('✓ Added fit_to_teach_level column')
    except Exception as e:
        print(f'fit_to_teach_level already exists: {e}')
    
    # Copy the highest value from the three subject columns to fit_to_teach_level
    try:
        conn.execute(text('''
            UPDATE users 
            SET fit_to_teach_level = (
                SELECT MAX(level) FROM (
                    SELECT fit_to_teach_math_level as level
                    UNION ALL SELECT fit_to_teach_science_level
                    UNION ALL SELECT fit_to_teach_english_level
                ) WHERE level IS NOT NULL
            )
            WHERE fit_to_teach_math_level IS NOT NULL 
               OR fit_to_teach_science_level IS NOT NULL 
               OR fit_to_teach_english_level IS NOT NULL
        '''))
        print('✓ Migrated data to fit_to_teach_level (using highest subject level)')
    except Exception as e:
        print(f'Warning: Could not migrate data: {e}')
    
    # Remove the three subject-specific columns
    # Note: SQLite doesn't support DROP COLUMN directly before version 3.35.0
    # We need to recreate the table without these columns
    
    try:
        # Create a temporary table with the desired schema
        conn.execute(text('''
            CREATE TABLE users_temp AS 
            SELECT 
                id, email, name, hashed_password, role, is_active,
                school_id, created_at, updated_at,
                current_level, math_level, science_level, english_level,
                fit_to_teach_level, location, latitude, longitude
            FROM users
        '''))
        print('✓ Created temporary table')
        
        # Drop the original table
        conn.execute(text('DROP TABLE users'))
        print('✓ Dropped original users table')
        
        # Rename temp table to users
        conn.execute(text('ALTER TABLE users_temp RENAME TO users'))
        print('✓ Renamed temp table to users')
        
        # Recreate indexes (if any were present)
        conn.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email)'))
        conn.execute(text('CREATE INDEX IF NOT EXISTS ix_users_id ON users (id)'))
        print('✓ Recreated indexes')
        
    except Exception as e:
        print(f'❌ Error during table recreation: {e}')
        print('Rolling back...')
        conn.rollback()
        conn.close()
        return
    
    conn.commit()
    conn.close()
    
    print("=" * 50)
    print('✅ Database downgrade complete!')
    print('\nRemoved columns:')
    print('  - fit_to_teach_math_level')
    print('  - fit_to_teach_science_level')
    print('  - fit_to_teach_english_level')
    print('\nRestored column:')
    print('  - fit_to_teach_level')

if __name__ == "__main__":
    downgrade()
