"""
Populate student_chapter_performance table from existing evaluation files
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.services.matching_service import get_peer_matching_service

def populate_chapter_performance():
    db = SessionLocal()
    try:
        matching_service = get_peer_matching_service(db)
        
        # User IDs that have evaluation files
        user_ids = [1, 3]  # User 2 has no evaluations yet
        
        print("=" * 70)
        print("POPULATING CHAPTER PERFORMANCE DATA")
        print("=" * 70)
        
        for user_id in user_ids:
            print(f"\nProcessing User {user_id}...")
            try:
                matching_service.update_student_chapter_performances(user_id)
                print(f"  ✓ Successfully updated performance data for User {user_id}")
            except Exception as e:
                print(f"  ✗ Error for User {user_id}: {e}")
        
        db.commit()
        
        # Check results
        print("\n" + "=" * 70)
        print("RESULTS:")
        print("=" * 70)
        
        from app.models.matching import StudentChapterPerformance
        
        for user_id in user_ids:
            performances = db.query(StudentChapterPerformance).filter(
                StudentChapterPerformance.student_id == user_id
            ).all()
            
            print(f"\nUser {user_id}: {len(performances)} chapter records")
            
            # Group by subject
            subjects = {}
            for perf in performances:
                if perf.subject not in subjects:
                    subjects[perf.subject] = []
                subjects[perf.subject].append(perf)
            
            for subject, perfs in subjects.items():
                print(f"\n  {subject.upper()}:")
                for perf in sorted(perfs, key=lambda x: x.score, reverse=True):
                    status = "🟢 Can teach" if perf.score >= 7 else "🔴 Need help" if perf.score <= 5 else "🟡 Average"
                    print(f"    {status} {perf.chapter}: {perf.score}/10 ({perf.accuracy_percentage}%)")
        
        print("\n" + "=" * 70)
        print("POTENTIAL MATCHES:")
        print("=" * 70)
        
        # Find potential tutors and learners
        all_performances = db.query(StudentChapterPerformance).all()
        
        # Group by chapter
        chapters = {}
        for perf in all_performances:
            key = f"{perf.subject}:{perf.chapter}"
            if key not in chapters:
                chapters[key] = {"tutors": [], "learners": []}
            
            if perf.score >= 7:
                chapters[key]["tutors"].append((perf.student_id, perf.score))
            elif perf.score <= 5:
                chapters[key]["learners"].append((perf.student_id, perf.score))
        
        # Display potential matches
        match_count = 0
        for chapter_key, data in chapters.items():
            subject, chapter = chapter_key.split(":", 1)
            if data["tutors"] and data["learners"]:
                match_count += 1
                print(f"\n{chapter} ({subject}):")
                print(f"  Tutors available: {len(data['tutors'])}")
                for tutor_id, score in data["tutors"]:
                    print(f"    - User {tutor_id}: {score}/10")
                print(f"  Learners need help: {len(data['learners'])}")
                for learner_id, score in data["learners"]:
                    print(f"    - User {learner_id}: {score}/10")
        
        if match_count == 0:
            print("\n⚠ No chapters with both tutors and learners found.")
            print("   This means no automatic matching is possible yet.")
            print("\n   Reasons:")
            print("   - Students may all have similar scores (no clear tutors/learners)")
            print("   - More students need to complete assessments")
            print("   - Adjust thresholds: tutor_threshold (≥7) or learner_threshold (≤5)")
        else:
            print(f"\n✓ Found {match_count} chapters ready for matching!")
            print("\nNext steps:")
            print("  1. Teacher/admin can create matches via UI or API")
            print("  2. POST /api/matching/create-matches")
            print('     { "subject": "<subject>", "chapter": "<chapter>" }')
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    populate_chapter_performance()
