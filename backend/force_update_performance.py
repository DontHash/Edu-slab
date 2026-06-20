"""
Force update chapter performance from evaluation files
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.matching import StudentChapterPerformance
from app.services.matching_service import get_peer_matching_service


def force_update():
    db = SessionLocal()
    try:
        print("=" * 70)
        print("FORCE UPDATING CHAPTER PERFORMANCE FOR USER 2")
        print("=" * 70)
        
        matching_service = get_peer_matching_service(db)
        
        # Update user 2's performance from evaluation files
        print("\nUpdating performance data...")
        count = matching_service.update_student_chapter_performances(2)
        print(f"✓ Updated {count} chapter records")
        
        db.commit()
        
        # Show results
        print("\n" + "=" * 70)
        print("UPDATED PERFORMANCE DATA:")
        print("=" * 70)
        
        performances = db.query(StudentChapterPerformance).filter(
            StudentChapterPerformance.student_id == 2,
            StudentChapterPerformance.subject == 'science'
        ).all()
        
        print(f"\nScience chapters: {len(performances)}")
        for perf in performances:
            print(f"  {perf.chapter}: score={perf.score}/10, weakness={perf.weakness_level}")
        
        # Count weaknesses
        weak_chapters = [p for p in performances if p.weakness_level in ["severe", "moderate", "mild"]]
        print(f"\n✓ Found {len(weak_chapters)} chapters with weaknesses (will appear in learning roadmap)")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    force_update()
