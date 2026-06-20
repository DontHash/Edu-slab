"""
Migration script to add fit_to_teach_level column to users table
Run this to update existing database
"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "eduassess.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if column already exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'fit_to_teach_level' not in columns:
        print("Adding fit_to_teach_level column...")
        cursor.execute("ALTER TABLE users ADD COLUMN fit_to_teach_level INTEGER")
        conn.commit()
        print("✅ Column added successfully!")
    else:
        print("ℹ️  Column already exists, no migration needed.")
    
    # Reset all subject levels to NULL (remove default 50 values)
    print("\nResetting subject levels to NULL...")
    cursor.execute("""
        UPDATE users 
        SET math_level = NULL, 
            science_level = NULL, 
            english_level = NULL
        WHERE role = 'STUDENT'
    """)
    conn.commit()
    print("✅ Subject levels reset!")
    
    # Display current users
    cursor.execute("SELECT id, name, current_level, math_level, science_level, english_level, fit_to_teach_level FROM users")
    users = cursor.fetchall()
    
    print("\n" + "="*70)
    print("CURRENT USERS:")
    print("="*70)
    for user in users:
        print(f"\nID: {user[0]}")
        print(f"  Name: {user[1]}")
        print(f"  Current Level: {user[2]}")
        print(f"  Math Level: {user[3]}")
        print(f"  Science Level: {user[4]}")
        print(f"  English Level: {user[5]}")
        print(f"  Fit to Teach: Grade {user[6]}" if user[6] else "  Fit to Teach: Not assessed yet")
    
    print("\n" + "="*70)
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()
