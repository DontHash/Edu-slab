import sqlite3
from pathlib import Path

# Connect to database
db_path = Path(__file__).parent / "eduassess.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("USERS TABLE:")
print("=" * 80)

# First check what columns exist
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
col_names = [col[1] for col in columns]
print("\nColumns:", ", ".join(col_names))

# Get user data
cursor.execute("SELECT id, email, name, current_level, math_level, science_level, english_level, fit_to_teach_level FROM users")
users = cursor.fetchall()
print(f"\nTotal users: {len(users)}\n")
for user in users:
    print(f"ID: {user[0]}")
    print(f"Email: {user[1]}")
    print(f"Name: {user[2]}")
    print(f"Current Level: {user[3]}")
    print(f"Math Level: {user[4]}")
    print(f"Science Level: {user[5]}")
    print(f"English Level: {user[6]}")
    print(f"Fit to Teach: {user[7]}")
    print("-" * 80)

conn.close()
print("=" * 80)
