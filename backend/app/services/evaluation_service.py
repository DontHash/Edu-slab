import json
import os
import re
from pathlib import Path
from typing import Any, Dict

from app.core.config import settings
from mistralai import Mistral


class EvaluationService:
    """Service for evaluating student assessments using Mistral AI"""
    
    STRICT_PROMPT = """
You are a strict, deterministic Assessment Evaluation Engine for Grade 10.

You behave like an automated grading system, not a tutor or assistant.

INPUT

You will receive a JSON object representing a student's assessment.
Each item contains:
- chapter
- question
- answer (student's answer)

EVALUATION RULES (NON-NEGOTIABLE)

- Evaluate strictly according to curriculum expectations.
- Do NOT be lenient.
- Do NOT infer intent beyond the written answer.
- Incorrect formula, incorrect logic, missing steps, or irrelevant text = incorrect.
- Correct method with minor arithmetic mistake = partial.
- Guessing, nonsense, placeholders, or off-topic text = incorrect.
- If an answer does not address the question directly, mark it incorrect.
- Treat each question independently.

PER-QUESTION OUTPUT

For EVERY question, use the question_id as the key and output:
- correctness: one of ["correct", "partial", "incorrect"]
- score: one of [1, 0.5, 0]
- medium_reason:
  - Include ONLY if correctness is "incorrect" or "partial"
  - 10–20 words
  - Focus on the exact conceptual or procedural mistake
  - Do NOT explain the correct solution

PER-CHAPTER ANALYSIS

For EACH chapter, compute:
- total_questions
- correct
- partial
- incorrect
- accuracy_percentage (rounded to nearest integer)
- chapter_score_out_of_10 (based on scores)
- weakness_level:
    - "none" (≥85%)
    - "mild" (70–84%)
    - "moderate" (50–69%)
    - "severe" (<50%)

OVERALL ANALYSIS (FOCUS ON WEAKNESSES)

Compute:
- final_score_out_of_100
- estimated_student_grade_level:
    - 10 if ≥85%
    - 9 if 70–84%
    - 8 if 55–69%
    - 7 if 40–54%
    - 6 if <40%
- strongest_chapters (top 2 by accuracy)
- weakest_chapters (bottom 3 by accuracy)

learning_gap_summary:
- 3–5 short paragraphs (each 1–2 lines)
- Focus primarily on WEAK and SEVERE chapters
- Identify:
    - missing foundational concepts
    - patterns of errors (formula misuse, conceptual gaps, algebraic weakness, etc.)
    - grade-level mismatch indicators
- Avoid generic advice
- Do NOT repeat statistics
- Be diagnostic, not motivational

OUTPUT FORMAT (CRITICAL)

- Return ONLY valid JSON
- Output must start with '{' and end with '}'
- Do NOT include markdown
- Do NOT include comments
- Do NOT include explanations outside JSON
- Do NOT include any extra text
- If evaluation is impossible, return an empty JSON object {}

The output should have this structure:
{
  "chapter_analysis": { "Chapter Name": { ...stats... } },
  "question_analysis": { "question_id": { correctness, score, medium_reason? } },
  "overall_analysis": { final_score_out_of_100, estimated_student_grade_level, strongest_chapters, weakest_chapters, learning_gap_summary }
}
"""
    
    def __init__(self, api_key: str = None):
        # Use provided API key or get from settings
        if api_key is None:
            api_key = settings.MISTRAL_API_KEY if hasattr(settings, 'MISTRAL_API_KEY') else None
        
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not configured in settings")
        
        self.client = Mistral(api_key=api_key)
    
    def _convert_raw_output_to_json(self, raw_text: str) -> Dict[str, Any]:
        """
        Converts raw LLM output (with markdown/code fences) into valid JSON.
        Raises ValueError if JSON is invalid.
        """
        # Remove markdown code fences
        cleaned_text = re.sub(r"```json|```", "", raw_text).strip()
        
        # Extract JSON object
        match = re.search(r"\{[\s\S]*\}", cleaned_text)
        if not match:
            raise ValueError("No JSON object found in model output")
        
        json_text = match.group(0)
        
        try:
            parsed_json = json.loads(json_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        
        return parsed_json
    
    def evaluate_assessment(self, assessment_file_path: Path) -> Dict[str, Any]:
        """
        Evaluate a submitted assessment
        
        Args:
            assessment_file_path: Path to the assessment JSON file
            
        Returns:
            Dictionary containing evaluation results
        """
        # Load assessment data
        with open(assessment_file_path, "r", encoding="utf-8") as f:
            assessment_data = json.load(f)
        
        # Prepare data for evaluation - convert to the format expected by evaluator
        evaluation_input = {
            "subject": assessment_data.get("subject", ""),
            "answers": assessment_data.get("answers", [])
        }
        
        # Call Mistral API
        response = self.client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {
                    "role": "system",
                    "content": self.STRICT_PROMPT
                },
                {
                    "role": "user",
                    "content": json.dumps(evaluation_input)
                }
            ],
            temperature=0.1,
            top_p=0.9,
            stream=False
        )
        
        # Parse response
        raw_output = response.choices[0].message.content
        evaluation_result = self._convert_raw_output_to_json(raw_output)
        
        # Save evaluation alongside assessment
        evaluation_file_path = assessment_file_path.parent / f"{assessment_file_path.stem}_evaluation.json"
        with open(evaluation_file_path, "w", encoding="utf-8") as f:
            json.dump(evaluation_result, f, indent=2)
        
        return evaluation_result


# Singleton instance
_evaluation_service = None

def get_evaluation_service() -> EvaluationService:
    """Get or create evaluation service singleton"""
    global _evaluation_service
    if _evaluation_service is None:
        _evaluation_service = EvaluationService()
    return _evaluation_service
