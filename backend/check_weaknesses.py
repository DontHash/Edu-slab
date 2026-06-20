from app.db.database import SessionLocal
from app.models.matching import StudentChapterPerformance

db = SessionLocal()

for subj in ['science', 'english', 'maths']:
    perfs = db.query(StudentChapterPerformance).filter(
        StudentChapterPerformance.student_id == 1,
        StudentChapterPerformance.subject == subj
    ).all()
    
    weak = [p for p in perfs if p.weakness_level in ['severe', 'moderate', 'mild']]
    
    print(f"\n{subj.upper()}: {len(perfs)} total chapters, {len(weak)} with weaknesses")
    
    if weak:
        for p in weak[:5]:
            print(f"  - {p.chapter}: {p.weakness_level} (score: {p.score}/10)")
    else:
        print("  ✓ No weaknesses - all chapters mastered!")

db.close()
