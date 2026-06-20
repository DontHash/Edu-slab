"""
Utility functions for the application
"""
from typing import List, Optional
from datetime import datetime


def calculate_grade_level(score: float) -> int:
    """
    Calculate appropriate grade level based on assessment score
    
    Args:
        score: Assessment score (0-100)
    
    Returns:
        Suggested grade level (1-12)
    """
    if score >= 90:
        return min(12, 8)  # Advanced
    elif score >= 80:
        return 7  # Above average
    elif score >= 70:
        return 6  # Average
    elif score >= 60:
        return 5  # Below average
    else:
        return 4  # Needs improvement


def format_time_duration(seconds: int) -> str:
    """
    Format seconds into human-readable duration
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string (e.g., "5m 30s")
    """
    if seconds < 60:
        return f"{seconds}s"
    
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    if remaining_seconds == 0:
        return f"{minutes}m"
    
    return f"{minutes}m {remaining_seconds}s"


def calculate_performance_metrics(
    correct_answers: int,
    total_questions: int,
    time_taken: Optional[int] = None
) -> dict:
    """
    Calculate comprehensive performance metrics
    
    Args:
        correct_answers: Number of correct answers
        total_questions: Total number of questions
        time_taken: Time taken in seconds (optional)
    
    Returns:
        Dictionary with performance metrics
    """
    score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    accuracy = correct_answers / total_questions if total_questions > 0 else 0
    
    metrics = {
        "score": round(score, 2),
        "accuracy": round(accuracy, 4),
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "incorrect_answers": total_questions - correct_answers
    }
    
    if time_taken:
        metrics["time_taken"] = time_taken
        metrics["time_per_question"] = round(time_taken / total_questions, 2) if total_questions > 0 else 0
        metrics["formatted_time"] = format_time_duration(time_taken)
    
    return metrics


def determine_difficulty_adjustment(
    current_difficulty: str,
    score: float
) -> str:
    """
    Determine next difficulty level based on performance
    
    Args:
        current_difficulty: Current difficulty level
        score: Assessment score (0-100)
    
    Returns:
        Suggested next difficulty level
    """
    if score >= 85:
        # High performance - increase difficulty
        if current_difficulty == "beginner":
            return "intermediate"
        elif current_difficulty == "intermediate":
            return "advanced"
        return "advanced"
    elif score < 60:
        # Low performance - decrease difficulty
        if current_difficulty == "advanced":
            return "intermediate"
        elif current_difficulty == "intermediate":
            return "beginner"
        return "beginner"
    
    # Moderate performance - maintain level
    return current_difficulty
