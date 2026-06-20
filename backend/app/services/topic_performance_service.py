"""
Sync topic performance from legacy assessment evaluation files into the DB.
Replaces the peer-matching performance sync path.
"""
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict

from app.core.skills import LEGACY_SUBJECT_TO_SKILL
from app.models.diagnostic import TopicPerformance
from sqlalchemy.orm import Session


def _map_subject_to_skill_area(subject: str) -> str:
    key = (subject or "").strip().lower()
    return LEGACY_SUBJECT_TO_SKILL.get(key, key)


def extract_topic_data_from_evaluations(user_id: int) -> Dict[str, Dict[str, dict]]:
    assessments_dir = Path("assessments") / str(user_id)
    if not assessments_dir.exists():
        return {}

    performance_data: dict[str, dict[str, dict]] = defaultdict(dict)
    file_timestamps: dict[str, float] = {}

    eval_files = sorted(
        assessments_dir.glob("*_evaluation.json"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )

    for eval_file in eval_files:
        try:
            with open(eval_file, encoding="utf-8") as f:
                evaluation = json.load(f)

            assessment_file = eval_file.parent / f"{eval_file.stem.replace('_evaluation', '')}.json"
            if not assessment_file.exists():
                continue

            with open(assessment_file, encoding="utf-8") as f:
                assessment = json.load(f)

            subject = assessment.get("subject", "unknown")
            skill_area = _map_subject_to_skill_area(subject)
            file_time = eval_file.stat().st_mtime

            for topic_name, topic_data in evaluation.get("chapter_analysis", {}).items():
                key = f"{skill_area}:{topic_name}"
                if key in file_timestamps and file_time <= file_timestamps[key]:
                    continue

                file_timestamps[key] = file_time
                performance_data[skill_area][topic_name] = {
                    "score": topic_data.get("chapter_score_out_of_10", 0),
                    "accuracy_percentage": topic_data.get("accuracy_percentage"),
                    "weakness_level": topic_data.get("weakness_level", "moderate"),
                    "total_questions": topic_data.get("total_questions", 0),
                    "correct": topic_data.get("correct", 0),
                }
        except (json.JSONDecodeError, KeyError, OSError):
            continue

    return dict(performance_data)


def sync_topic_performances(db: Session, user_id: int) -> int:
    """Upsert TopicPerformance rows from the latest evaluation files."""
    performance_data = extract_topic_data_from_evaluations(user_id)
    count = 0

    for skill_area, topics in performance_data.items():
        for topic_name, data in topics.items():
            existing = (
                db.query(TopicPerformance)
                .filter(
                    TopicPerformance.student_id == user_id,
                    TopicPerformance.skill_area == skill_area,
                    TopicPerformance.topic_name == topic_name,
                )
                .first()
            )

            if existing:
                existing.score = data["score"]
                existing.accuracy_percentage = data["accuracy_percentage"]
                existing.weakness_level = data["weakness_level"]
            else:
                db.add(
                    TopicPerformance(
                        student_id=user_id,
                        skill_area=skill_area,
                        topic_name=topic_name,
                        score=data["score"],
                        accuracy_percentage=data["accuracy_percentage"],
                        weakness_level=data["weakness_level"],
                    )
                )
            count += 1

    db.commit()
    return count
