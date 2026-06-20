from app.db.database import SessionLocal
from app.services.Learning_materials import get_student_weakness_data

db = SessionLocal()

# Test with different capitalizations
for subject in ['Mathematics', 'mathematics', 'Maths', 'maths']:
    weaknesses = get_student_weakness_data(db, student_id=1, subject=subject)
    print(f"\n'{subject}': Found {len(weaknesses)} weaknesses")
    if weaknesses:
        for chapter, level in list(weaknesses.items())[:3]:
            print(f"  - {chapter}: {level}")

db.close()
