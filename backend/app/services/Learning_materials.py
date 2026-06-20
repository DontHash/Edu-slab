#!/usr/bin/env python3
"""
Learning Material Generator Service
Integrates with existing assessment system to generate personalized learning plans
"""

import json
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from app.models.learning_material import LearningMaterial
from app.models.diagnostic import TopicPerformance
from dotenv import load_dotenv
from mistralai import Mistral
from sqlalchemy.orm import Session

load_dotenv()
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

SYSTEM = """
You output STRICT JSON ONLY. No markdown. No surrounding text.

CHAPTER JSON SCHEMA REQUIRED:
{
 "chapter_name": string,
 "weakness_level": "severe" | "moderate" | "mild" | "none",
 "priority": integer(1-5),
 "estimated_time_hours": number,
 "prerequisites": [
   {"concept": string, "why": string, "recommended_resource": string}
 ],
 "roadmap_steps": [
   {"step_number": integer, "objective": string, "estimated_time_minutes": integer}
 ],
 "resources": [
   {
     "id": string,
     "type": "video"|"article"|"website"|"exercise",
     "title": string,
     "url": string,
     "description": string,
     "level": "beginner"|"intermediate",
     "estimated_time_minutes": integer
   }
 ]
}

Rules:
- severe → max 4 resources, beginner only, high priority (4-5)
- moderate → max 3 resources, beginner/intermediate, medium priority (3)
- mild → max 2 resources, any level, low priority (1-2)
- none → skip or 1 optional resource for enrichment
- Use only: KhanAcademy, OWL Purdue, BBC Bitesize, EdX, PoetryFoundation, SparkNotes, CrashCourse YouTube, Coursera
- URLs must be real and academic.
"""

def extract_json(response_text):
    """Extract and parse JSON from AI response"""
    text = re.sub(r"```(?:json)?", "", response_text).strip()
    match = re.search(r"\{[\s\S]*\}", text)
    if not match: 
        return None
    try:
        return json.loads(match.group(0))
    except Exception:
        try:
            return json.loads(re.sub(r",\s*([\]}])", r"\1", match.group(0)))
        except:
            return None


def generate_chapter_plan(chapter: str, weakness_level: str, subject: str) -> dict:
    """Generate learning plan for a single chapter using AI"""
    prompt = f"""
Generate JSON for one chapter in {subject}:
chapter_name: "{chapter}"
weakness_level: "{weakness_level}"
subject: "{subject}"

Focus on practical, accessible resources for this weakness level.
    """
    
    for attempt in range(3):  # retry 3 times
        try:
            res = client.chat.complete(
                model="mistral-small-latest", 
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": prompt}
                ], 
                stream=False
            )
            content = res.choices[0].message.content
            data = extract_json(content)
            if data and "chapter_name" in data:
                return data
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue
    
    # Fallback if AI fails
    return {
        "chapter_name": chapter,
        "weakness_level": weakness_level,
        "priority": 3,
        "estimated_time_hours": 4,
        "prerequisites": [],
        "roadmap_steps": [
            {
                "step_number": 1,
                "objective": f"Review fundamental concepts in {chapter}",
                "estimated_time_minutes": 60
            }
        ],
        "resources": [],
        "error": "AI generation failed, using fallback"
    }


def get_student_weakness_data(db: Session, student_id: int, subject: str) -> Dict[str, str]:
    """
    Fetch student's chapter-level weaknesses from database
    Returns: {"chapter_name": "weakness_level", ...}
    """
    # Case-insensitive subject matching
    from sqlalchemy import func
    from app.core.skills import normalize_skill_area

    skill_area = normalize_skill_area(subject)
    performances = db.query(TopicPerformance).filter(
        TopicPerformance.student_id == student_id,
        TopicPerformance.skill_area == skill_area,
    ).all()
    
    print(f"[DEBUG WEAKNESS] Query found {len(performances)} total performance records for student {student_id}, subject {subject}")
    
    weakness_data = {}
    for perf in performances:
        print(f"[DEBUG WEAKNESS] Topic: {perf.topic_name}, weakness: {perf.weakness_level}, score: {perf.score}")
        # Only include chapters with some weakness (not "none")
        if perf.weakness_level in ["severe", "moderate", "mild"]:
            weakness_data[perf.topic_name] = perf.weakness_level
    
    print(f"[DEBUG WEAKNESS] Filtered to {len(weakness_data)} chapters with weakness: {list(weakness_data.keys())}")
    
    return weakness_data


def generate_learning_materials(
    db: Session, 
    student_id: int, 
    subject: str,
    force_regenerate: bool = False
) -> Optional[LearningMaterial]:
    """
    Main service function to generate personalized learning materials
    
    Args:
        db: Database session
        student_id: Student's user ID
        subject: Subject name (e.g., "Mathematics", "English")
        force_regenerate: If True, regenerate even if recent materials exist
    
    Returns:
        LearningMaterial object or None if no weaknesses found
    """
    # Check if we have recent materials (less than 7 days old)
    if not force_regenerate:
        from sqlalchemy import func
        recent_material = db.query(LearningMaterial).filter(
            LearningMaterial.student_id == student_id,
            func.lower(LearningMaterial.subject) == subject.lower(),
            LearningMaterial.is_active == 1,
            LearningMaterial.generated_at > datetime.utcnow() - timedelta(days=7)
        ).first()
        
        if recent_material:
            return recent_material
    
    # Get student's weakness data from database
    weakness_data = get_student_weakness_data(db, student_id, subject)
    
    print(f"[DEBUG LEARNING] Weakness data for user {student_id}, subject {subject}:")
    print(f"[DEBUG LEARNING] Found {len(weakness_data)} chapters: {list(weakness_data.keys())}")
    
    if not weakness_data:
        return None  # No weaknesses found
    
    # Generate learning plan for each weak chapter
    chapters = []
    for chapter, weakness_level in weakness_data.items():
        print(f"[DEBUG LEARNING] Generating plan for {chapter} ({weakness_level})...")
        chapter_plan = generate_chapter_plan(chapter, weakness_level, subject)
        print(f"[DEBUG LEARNING] Generated plan for {chapter}: {chapter_plan.get('chapter_name', 'ERROR')}")
        chapters.append(chapter_plan)
    
    print(f"[DEBUG LEARNING] Total chapters generated: {len(chapters)}")
    
    # Calculate global recommendations based on weaknesses
    severe_count = sum(1 for w in weakness_data.values() if w == "severe")
    moderate_count = sum(1 for w in weakness_data.values() if w == "moderate")
    
    # Determine study duration
    if severe_count >= 3:
        weekly_hours = 8
        min_weeks = 8
    elif severe_count >= 1 or moderate_count >= 4:
        weekly_hours = 6
        min_weeks = 6
    else:
        weekly_hours = 4
        min_weeks = 4
    
    # Build final JSON structure
    content = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema_version": "1.0",
        "generator_model": "mistral-small-latest",
        "subject": subject,
        "chapters": chapters,
        "global_recommendations": {
            "weekly_study_hours": weekly_hours,
            "assessment_checkpoints_weeks": list(range(2, min_weeks + 1, 2)),
            "minimum_duration_weeks": min_weeks,
            "notes": f"Focus on {severe_count} critical areas. Regular practice essential."
        }
    }
    
    # Deactivate old materials for this student/subject
    from sqlalchemy import func
    db.query(LearningMaterial).filter(
        LearningMaterial.student_id == student_id,
        func.lower(LearningMaterial.subject) == subject.lower(),
        LearningMaterial.is_active == 1
    ).update({"is_active": 0})
    
    # Create new learning material record
    learning_material = LearningMaterial(
        student_id=student_id,
        subject=subject,
        content=content,
        generator_model="mistral-small-latest",
        schema_version="1.0",
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    
    db.add(learning_material)
    db.commit()
    db.refresh(learning_material)
    
    return learning_material
