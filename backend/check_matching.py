import sqlite3
from pathlib import Path

# Connect to database
db_path = Path(__file__).parent / "eduassess.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 70)
print("CHECKING MATCHING SYSTEM DATA")
print("=" * 70)

# Check if student_chapter_performance table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='student_chapter_performance'")
table_exists = cursor.fetchone()

if table_exists:
    print("\n✓ student_chapter_performance table exists")
    
    # Check data
    cursor.execute("SELECT COUNT(*) FROM student_chapter_performance")
    count = cursor.fetchone()[0]
    print(f"  Records: {count}")
    
    if count > 0:
        cursor.execute("SELECT * FROM student_chapter_performance LIMIT 5")
        records = cursor.fetchall()
        print("\n  Sample records:")
        for record in records:
            print(f"    Student {record[1]}: {record[3]} - {record[2]} (Score: {record[4]}/10)")
    else:
        print("  ⚠ No chapter performance data found!")
else:
    print("\n✗ student_chapter_performance table DOES NOT exist")
    print("  You need to run the database migration first!")

# Check users with scores
print("\n" + "=" * 70)
print("USERS WITH SCORES:")
print("=" * 70)
cursor.execute("""
    SELECT id, name, email, math_level, science_level, english_level, fit_to_teach_level
    FROM users 
    WHERE role = 'STUDENT'
""")
users = cursor.fetchall()

for user in users:
    user_id, name, email, math, science, english, fit = user
    print(f"\n{name} ({email}):")
    print(f"  Math: {math if math else 'Not assessed'}")
    print(f"  Science: {science if science else 'Not assessed'}")
    print(f"  English: {english if english else 'Not assessed'}")
    print(f"  Can teach grade: {fit if fit else 'N/A'}")

# Check for assessment files
print("\n" + "=" * 70)
print("ASSESSMENT FILES:")
print("=" * 70)

assessments_dir = Path(__file__).parent / "assessments"
if assessments_dir.exists():
    print(f"✓ Assessments directory exists: {assessments_dir}")
    
    for user_id in [1, 2, 3]:
        user_dir = assessments_dir / str(user_id)
        if user_dir.exists():
            evaluation_files = list(user_dir.glob("*_evaluation.json"))
            print(f"\n  User {user_id}:")
            print(f"    Total evaluation files: {len(evaluation_files)}")
            if evaluation_files:
                for eval_file in evaluation_files[:3]:
                    print(f"      - {eval_file.name}")
        else:
            print(f"\n  User {user_id}: No assessment directory")
else:
    print("✗ Assessments directory not found!")

# Check peer_matches table
print("\n" + "=" * 70)
print("PEER MATCHES:")
print("=" * 70)

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='peer_matches'")
table_exists = cursor.fetchone()

if table_exists:
    cursor.execute("SELECT COUNT(*) FROM peer_matches")
    count = cursor.fetchone()[0]
    print(f"✓ peer_matches table exists: {count} matches")
    
    if count > 0:
        cursor.execute("""
            SELECT pm.id, 
                   t.name as tutor_name, 
                   l.name as learner_name,
                   pm.chapter,
                   pm.tutor_score,
                   pm.learner_score,
                   pm.status
            FROM peer_matches pm
            JOIN users t ON pm.tutor_id = t.id
            JOIN users l ON pm.learner_id = l.id
        """)
        matches = cursor.fetchall()
        for match in matches:
            print(f"\n  {match[1]} (tutor) ↔ {match[2]} (learner)")
            print(f"    Chapter: {match[3]}")
            print(f"    Scores: {match[4]} vs {match[5]}")
            print(f"    Status: {match[6]}")
else:
    print("✗ peer_matches table DOES NOT exist")

conn.close()

print("\n" + "=" * 70)
print("DIAGNOSIS:")
print("=" * 70)
print("""
To fix the matching system:

1. If tables don't exist:
   → Run database migration: 
     cd backend && alembic upgrade head

2. If chapter performance data is missing:
   → Update performance data from evaluations:
     POST /api/matching/update-performance/1
     POST /api/matching/update-performance/2
     POST /api/matching/update-performance/3

3. If evaluation files don't exist:
   → Students need to complete assessments first
   → The evaluation will automatically populate chapter data

4. Create matches (as teacher):
   → POST /api/matching/create-matches
     { "subject": "maths", "chapter": "Real Numbers" }
""")
