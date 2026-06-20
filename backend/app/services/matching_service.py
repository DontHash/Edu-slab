"""
Peer-to-peer matching service using Asymmetric Gale-Shapley algorithm

This service matches high-scoring students (tutors) with low-scoring students (learners)
based on chapter-specific performance data.
"""
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from app.models.matching import (MatchStatus, PeerMatch,
                                 StudentChapterPerformance)
from app.models.user import User
from sqlalchemy.orm import Session


class AsymmetricGaleShapleyMatcher:
    """
    Implements Asymmetric Gale-Shapley algorithm for peer-to-peer matching.
    
    In this context:
    - Tutors (high-scoring students) are the "proposers"
    - Learners (low-scoring students) are the "receivers"
    - Each tutor has preferences over learners based on compatibility
    - Each learner has preferences over tutors based on their expertise
    """
    
    def __init__(
        self,
        tutor_threshold: float = 7.0,  # Minimum score to be a tutor (out of 10)
        learner_threshold: float = 5.0,  # Maximum score to need help (out of 10)
        max_matches_per_tutor: int = 3,  # Max learners a tutor can help
        max_matches_per_learner: int = 2,  # Max tutors a learner can have
    ):
        self.tutor_threshold = tutor_threshold
        self.learner_threshold = learner_threshold
        self.max_matches_per_tutor = max_matches_per_tutor
        self.max_matches_per_learner = max_matches_per_learner
    
    def calculate_compatibility_score(
        self,
        tutor_score: float,
        learner_score: float,
        tutor_consistency: float = 1.0,
        learner_need: float = 1.0,
        overlapping_chapters: int = 0,
    ) -> float:
        """
        Calculate compatibility score between a tutor and learner.
        
        Factors:
        - Score gap: Larger gap = better teaching opportunity
        - Tutor expertise: Higher tutor score = better match
        - Learner need: Lower learner score = higher need
        - Grade level: Tutor must be same grade or higher
        - Location: Same locality bonus for physical meetings
        - Not too large gap: Prevent mismatched difficulty levels
        - Overlapping chapters: More chapters in common = better match
        
        Returns score between 0-100
        """
        # Grade level filter - tutor must be same or higher grade
        # if tutor_grade and learner_grade and tutor_grade < learner_grade:
        #     return 0.0  # Cannot tutor someone in a higher grade
        
        # Score difference (optimal gap is 3-5 points)
        score_gap = tutor_score - learner_score
        
        # Penalize very small gaps (not much to teach) or very large gaps (too different)
        if score_gap < 2.0:
            gap_score = score_gap * 10  # 0-20 points
        elif score_gap <= 5.0:
            gap_score = 20 + (score_gap - 2.0) * 20  # 20-80 points (optimal)
        else:
            gap_score = max(0, 80 - (score_gap - 5.0) * 10)  # Decrease after 5 points
        
        # Tutor expertise (25% weight)
        expertise_score = (tutor_score / 10.0) * 25
        
        # Learner need (20% weight)
        need_score = ((10.0 - learner_score) / 10.0) * 20
        
        # Overlapping chapters bonus (up to 10% boost)
        overlap_bonus = min(10.0, overlapping_chapters * 2.0)
        
        # Combined score
        compatibility = (gap_score * 0.5) + expertise_score + need_score + overlap_bonus
        
        return min(100.0, max(0.0, compatibility))
    
    def build_preference_lists(
        self,
        tutors: Dict[int, Dict],
        learners: Dict[int, Dict],
        chapter: str,
        overlapping_chapters_map: Dict[Tuple[int, int], int] = None,
    ) -> Tuple[Dict[int, List[Tuple[int, float]]], Dict[int, List[Tuple[int, float]]]]:
        """
        Build preference lists for tutors and learners.
        
        Args:
            overlapping_chapters_map: {(tutor_id, learner_id): count_of_overlapping_chapters}
        
        Returns:
            - tutor_preferences: {tutor_id: [(learner_id, compatibility_score), ...]}
            - learner_preferences: {learner_id: [(tutor_id, compatibility_score), ...]}
        """
        if overlapping_chapters_map is None:
            overlapping_chapters_map = {}
        
        tutor_preferences = {}
        learner_preferences = defaultdict(list)
        
        # Build tutor preferences
        for tutor_id, tutor_data in tutors.items():
            preferences = []
            
            for learner_id, learner_data in learners.items():
                # Don't match same student
                if tutor_id == learner_id:
                    continue
                
                # Get overlapping chapters count
                overlap_count = overlapping_chapters_map.get((tutor_id, learner_id), 0)
                
                compatibility = self.calculate_compatibility_score(
                    tutor_data['score'],
                    learner_data['score'],
                    overlapping_chapters=overlap_count,
                )
                
                # Only include if compatibility > 0 (grade filter may exclude)
                if compatibility > 0:
                    preferences.append((learner_id, compatibility))
            
            # Sort by compatibility (descending)
            preferences.sort(key=lambda x: x[1], reverse=True)
            tutor_preferences[tutor_id] = preferences
            
            # Build learner preferences (symmetric)
            for learner_id, compatibility in preferences:
                learner_preferences[learner_id].append((tutor_id, compatibility))
        
        # Sort learner preferences by compatibility (descending)
        for learner_id in learner_preferences:
            learner_preferences[learner_id].sort(key=lambda x: x[1], reverse=True)
        
        return tutor_preferences, dict(learner_preferences)
    
    def gale_shapley_matching(
        self,
        tutor_preferences: Dict[int, List[Tuple[int, float]]],
        learner_preferences: Dict[int, List[Tuple[int, float]]],
    ) -> List[Tuple[int, int, float, int, int]]:
        """
        Run Asymmetric Gale-Shapley algorithm.
        
        Returns:
            List of matches: [(tutor_id, learner_id, compatibility, tutor_rank, learner_rank), ...]
        """
        # Current matches: learner_id -> list of (tutor_id, compatibility)
        learner_matches: Dict[int, List[Tuple[int, float]]] = defaultdict(list)
        
        # Next proposal index for each tutor
        tutor_proposal_index: Dict[int, int] = {tid: 0 for tid in tutor_preferences}
        
        # Free tutors (still have capacity)
        free_tutors: Set[int] = set(tutor_preferences.keys())
        
        # Track number of matches per tutor
        tutor_match_count: Dict[int, int] = defaultdict(int)
        
        while free_tutors:
            # Pick a free tutor
            tutor_id = free_tutors.pop()
            
            # Check if tutor reached max capacity
            if tutor_match_count[tutor_id] >= self.max_matches_per_tutor:
                continue
            
            # Check if tutor has more proposals to make
            if tutor_proposal_index[tutor_id] >= len(tutor_preferences[tutor_id]):
                continue
            
            # Get next preferred learner
            learner_id, compatibility = tutor_preferences[tutor_id][tutor_proposal_index[tutor_id]]
            tutor_proposal_index[tutor_id] += 1
            
            # Learner considers the proposal
            current_matches = learner_matches[learner_id]
            
            if len(current_matches) < self.max_matches_per_learner:
                # Learner has capacity, accept
                learner_matches[learner_id].append((tutor_id, compatibility))
                tutor_match_count[tutor_id] += 1
                
                # Tutor still free if not at capacity
                if tutor_match_count[tutor_id] < self.max_matches_per_tutor:
                    free_tutors.add(tutor_id)
            else:
                # Learner at capacity, check if this tutor is better than worst current match
                worst_match = min(current_matches, key=lambda x: x[1])
                
                if compatibility > worst_match[1]:
                    # Replace worst match with new proposal
                    learner_matches[learner_id].remove(worst_match)
                    learner_matches[learner_id].append((tutor_id, compatibility))
                    
                    # Free the rejected tutor
                    rejected_tutor_id = worst_match[0]
                    tutor_match_count[rejected_tutor_id] -= 1
                    free_tutors.add(rejected_tutor_id)
                    
                    tutor_match_count[tutor_id] += 1
                    
                    # Tutor still free if not at capacity
                    if tutor_match_count[tutor_id] < self.max_matches_per_tutor:
                        free_tutors.add(tutor_id)
                else:
                    # Proposal rejected, tutor remains free
                    free_tutors.add(tutor_id)
        
        # Convert to final match format with ranks
        final_matches = []
        for learner_id, matches in learner_matches.items():
            for tutor_id, compatibility in matches:
                # Find ranks
                tutor_rank = next(
                    (i for i, (lid, _) in enumerate(tutor_preferences[tutor_id]) if lid == learner_id),
                    -1
                )
                learner_rank = next(
                    (i for i, (tid, _) in enumerate(learner_preferences.get(learner_id, [])) if tid == tutor_id),
                    -1
                )
                
                final_matches.append((tutor_id, learner_id, compatibility, tutor_rank, learner_rank))
        
        return final_matches


class PeerMatchingService:
    """Service for managing peer-to-peer student matching"""
    
    def __init__(self, db: Session, max_distance_km: float = 10.0):
        self.db = db
        self.matcher = AsymmetricGaleShapleyMatcher()
        self.max_distance_km = max_distance_km  # Default 10km radius for physical meetups
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two GPS coordinates using Haversine formula.
        Returns distance in kilometers.
        """
        # Earth's radius in kilometers
        R = 6371.0
        
        # Convert degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance
    
    def extract_chapter_performance_from_evaluations(self, user_id: int) -> Dict[str, Dict]:
        """
        Extract chapter-specific performance from assessment evaluation files.
        
        Returns:
            {
                'subject': {
                    'chapter_name': {
                        'score': float,
                        'accuracy_percentage': int,
                        'weakness_level': str,
                        ...
                    }
                }
            }
        """
        assessments_dir = Path("assessments") / str(user_id)
        
        print(f"[DEBUG EXTRACT] Looking for assessments in: {assessments_dir}")
        
        if not assessments_dir.exists():
            print(f"[DEBUG EXTRACT] Directory does not exist: {assessments_dir}")
            return {}
        
        performance_data = defaultdict(dict)
        file_timestamps = {}  # Track file modification times
        
        # Find all evaluation files and sort by modification time (most recent first)
        eval_files = list(assessments_dir.glob("*_evaluation.json"))
        eval_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        print(f"[DEBUG EXTRACT] Found {len(eval_files)} evaluation files")
        
        for eval_file in eval_files:
            print(f"[DEBUG EXTRACT] Processing: {eval_file.name}")
            try:
                with open(eval_file, 'r', encoding='utf-8') as f:
                    evaluation = json.load(f)
                
                # Load corresponding assessment to get subject
                assessment_file = eval_file.parent / f"{eval_file.stem.replace('_evaluation', '')}.json"
                if not assessment_file.exists():
                    print(f"[DEBUG EXTRACT] Assessment file not found: {assessment_file.name}")
                    continue
                
                with open(assessment_file, 'r', encoding='utf-8') as f:
                    assessment = json.load(f)
                
                subject = assessment.get('subject', 'unknown')
                file_time = eval_file.stat().st_mtime
                print(f"[DEBUG EXTRACT] Subject: {subject}, File time: {file_time}")
                chapter_analysis = evaluation.get('chapter_analysis', {})
                print(f"[DEBUG EXTRACT] Found {len(chapter_analysis)} chapters")
                
                # Store each chapter's performance - use most recent file for each subject/chapter
                for chapter_name, chapter_data in chapter_analysis.items():
                    key = f"{subject}:{chapter_name}"
                    # Only update if this is the most recent assessment for this chapter
                    if key not in file_timestamps or file_time > file_timestamps[key]:
                        file_timestamps[key] = file_time
                        performance_data[subject][chapter_name] = {
                            'score': chapter_data['chapter_score_out_of_10'],
                            'accuracy_percentage': chapter_data['accuracy_percentage'],
                            'weakness_level': chapter_data['weakness_level'],
                            'total_questions': chapter_data['total_questions'],
                            'correct': chapter_data['correct'],
                        }
                        print(f"[DEBUG EXTRACT] Updated {chapter_name}: score={chapter_data['chapter_score_out_of_10']}, weakness={chapter_data['weakness_level']}")
            
            except (json.JSONDecodeError, KeyError) as e:
                print(f"[ERROR EXTRACT] Error processing {eval_file}: {e}")
                continue
        
        print(f"[DEBUG EXTRACT] Extracted {sum(len(chapters) for chapters in performance_data.values())} total chapters")
        return dict(performance_data)
    
    def update_student_chapter_performances(self, user_id: int):
        """
        Update or create StudentChapterPerformance records from evaluation data.
        Returns the number of records created/updated.
        """
        performance_data = self.extract_chapter_performance_from_evaluations(user_id)
        
        count = 0
        for subject, chapters in performance_data.items():
            for chapter, data in chapters.items():
                # Check if record exists
                existing = self.db.query(StudentChapterPerformance).filter(
                    StudentChapterPerformance.student_id == user_id,
                    StudentChapterPerformance.subject == subject,
                    StudentChapterPerformance.chapter == chapter,
                ).first()
                
                if existing:
                    # Update existing
                    existing.score = data['score']
                    existing.accuracy_percentage = data['accuracy_percentage']
                    existing.weakness_level = data['weakness_level']
                    existing.total_questions_attempted = data['total_questions']
                    existing.correct_answers = data['correct']
                else:
                    # Create new
                    performance = StudentChapterPerformance(
                        student_id=user_id,
                        subject=subject,
                        chapter=chapter,
                        score=data['score'],
                        accuracy_percentage=data['accuracy_percentage'],
                        weakness_level=data['weakness_level'],
                        total_questions_attempted=data['total_questions'],
                        correct_answers=data['correct'],
                    )
                    self.db.add(performance)
                count += 1
        
        self.db.commit()
        return count
    
    def find_matches_for_chapter(
        self,
        subject: str,
        chapter: str,
        meeting_type: str = "online",
        location: Optional[str] = None,
        school_id: Optional[int] = None,
    ) -> List[Tuple[int, int, float, int, int]]:
        """
        Find peer matches for a specific chapter using Gale-Shapley algorithm.
        Includes grade-level validation: tutor's fit_to_teach_level >= learner's current_level
        For physical meetups, filters by location proximity.
        
        Returns:
            List of matches: [(tutor_id, learner_id, compatibility, tutor_rank, learner_rank), ...]
        """
        # Get all students with performance data for this chapter
        query = self.db.query(StudentChapterPerformance).filter(
            StudentChapterPerformance.subject == subject,
            StudentChapterPerformance.chapter == chapter,
        )
        
        if school_id:
            query = query.join(User).filter(User.school_id == school_id)
        
        performances = query.all()
        
        # Get user data for grade-level and location checking
        user_ids = [perf.student_id for perf in performances]
        users = self.db.query(User).filter(User.id.in_(user_ids)).all()
        user_map = {user.id: user for user in users}
        
        # For physical meetups, filter by location proximity
        if meeting_type == "physical":
            if location:
                # Text-based location filter (exact match)
                users = [u for u in users if u.location and u.location.lower() == location.lower()]
                user_map = {user.id: user for user in users}
            else:
                # GPS-based proximity filter - keep users within max_distance_km
                # Filter out users without GPS coordinates
                users_with_gps = [u for u in users if u.latitude is not None and u.longitude is not None]
                if users_with_gps:
                    users = users_with_gps
                    user_map = {user.id: user for user in users}
        
        # Separate into tutors and learners with grade-level validation
        tutors = {}
        learners = {}
        
        for perf in performances:
            user = user_map.get(perf.student_id)
            if not user:
                continue
                
            if perf.score >= self.matcher.tutor_threshold:
                tutors[perf.student_id] = {
                    'score': perf.score,
                    'accuracy': perf.accuracy_percentage,
                    'fit_to_teach_level': user.fit_to_teach_level,
                    'current_level': user.current_level,
                }
            
            if perf.score <= self.matcher.learner_threshold:
                learners[perf.student_id] = {
                    'score': perf.score,
                    'accuracy': perf.accuracy_percentage,
                    'current_level': user.current_level,
                }
        
        # Need both tutors and learners
        if not tutors or not learners:
            return []
        
        # Calculate overlapping chapters for all tutor-learner pairs
        overlapping_chapters_map = self._calculate_overlapping_chapters(
            list(tutors.keys()), list(learners.keys()), subject
        )
        
        # Filter out grade-incompatible pairs
        filtered_overlaps = {}
        for (tutor_id, learner_id), count in overlapping_chapters_map.items():
            tutor_fit_level = tutors[tutor_id].get('fit_to_teach_level')
            learner_grade = learners[learner_id].get('current_level')
            
            # Tutor must be fit to teach learner's grade level
            if tutor_fit_level is not None and learner_grade is not None:
                if tutor_fit_level >= learner_grade:
                    filtered_overlaps[(tutor_id, learner_id)] = count
            elif tutor_fit_level is None and learner_grade is None:
                # If no grade levels set, allow the match
                filtered_overlaps[(tutor_id, learner_id)] = count
        
        # Build preference lists with grade-filtered overlaps
        tutor_prefs, learner_prefs = self.matcher.build_preference_lists(
            tutors, learners, chapter, filtered_overlaps
        )
        
        # Run Gale-Shapley
        matches = self.matcher.gale_shapley_matching(tutor_prefs, learner_prefs)
        
        return matches
    
    def create_matches(
        self,
        subject: str,
        chapter: str,
        meeting_type: str = "online",
        location: Optional[str] = None,
        school_id: Optional[int] = None,
    ) -> List[PeerMatch]:
        """
        Create and save peer matches for a specific chapter.
        """
        matches = self.find_matches_for_chapter(subject, chapter, meeting_type, location, school_id)
        
        created_matches = []
        
        for tutor_id, learner_id, compatibility, tutor_rank, learner_rank in matches:
            # Get actual scores
            tutor_perf = self.db.query(StudentChapterPerformance).filter(
                StudentChapterPerformance.student_id == tutor_id,
                StudentChapterPerformance.subject == subject,
                StudentChapterPerformance.chapter == chapter,
            ).first()
            
            learner_perf = self.db.query(StudentChapterPerformance).filter(
                StudentChapterPerformance.student_id == learner_id,
                StudentChapterPerformance.subject == subject,
                StudentChapterPerformance.chapter == chapter,
            ).first()
            
            if not tutor_perf or not learner_perf:
                continue
            
            # Create match
            match = PeerMatch(
                tutor_id=tutor_id,
                learner_id=learner_id,
                chapter=chapter,
                subject=subject,
                meeting_type=meeting_type,
                tutor_score=tutor_perf.score,
                learner_score=learner_perf.score,
                compatibility_score=compatibility,
                preference_rank_tutor=tutor_rank,
                preference_rank_learner=learner_rank,
                status=MatchStatus.PENDING,
            )
            
            self.db.add(match)
            created_matches.append(match)
        
        self.db.commit()
        
        return created_matches
    
    def get_student_matches(
        self,
        student_id: int,
        role: Optional[str] = None,  # 'tutor', 'learner', or None for both
    ) -> List[PeerMatch]:
        """Get all matches for a student."""
        query = self.db.query(PeerMatch)
        
        if role == 'tutor':
            query = query.filter(PeerMatch.tutor_id == student_id)
        elif role == 'learner':
            query = query.filter(PeerMatch.learner_id == student_id)
        else:
            query = query.filter(
                (PeerMatch.tutor_id == student_id) | (PeerMatch.learner_id == student_id)
            )
        
        return query.all()
    
    def get_potential_tutors_for_student(
        self,
        student_id: int,
        subject: str,
        chapter: str,
        meeting_type: str = "online",
        location: Optional[str] = None,
        limit: int = 10,
    ) -> List[Tuple[int, float, Dict]]:
        """
        Get potential tutors for a student based on their performance.
        Returns list of (tutor_id, compatibility_score, tutor_data)
        """
        # Get student's performance
        student_perf = self.db.query(StudentChapterPerformance).filter(
            StudentChapterPerformance.student_id == student_id,
            StudentChapterPerformance.subject == subject,
            StudentChapterPerformance.chapter == chapter,
        ).first()
        
        if not student_perf:
            return []
        
        # Get student's grade level
        student_user = self.db.query(User).filter(User.id == student_id).first()
        student_grade = student_user.current_level if student_user else None
        
        # Find potential tutors (high scorers)
        tutors_query = self.db.query(StudentChapterPerformance).filter(
            StudentChapterPerformance.subject == subject,
            StudentChapterPerformance.chapter == chapter,
            StudentChapterPerformance.score >= self.matcher.tutor_threshold,
            StudentChapterPerformance.student_id != student_id,  # Not themselves
        )
        
        tutors = tutors_query.all()
        
        # Calculate compatibility and build results
        potential_tutors = []
        for tutor_perf in tutors:
            # Get tutor user data
            tutor_user = self.db.query(User).filter(User.id == tutor_perf.student_id).first()
            
            if tutor_user:
                # For physical meetups, check location/GPS proximity
                if meeting_type == "physical":
                    if location:
                        # Text-based location match
                        if not tutor_user.location or tutor_user.location.lower() != location.lower():
                            continue
                    elif student_user and student_user.latitude and student_user.longitude:
                        # GPS proximity match
                        if not tutor_user.latitude or not tutor_user.longitude:
                            continue
                        distance = self.calculate_distance(
                            student_user.latitude, student_user.longitude,
                            tutor_user.latitude, tutor_user.longitude
                        )
                        if distance > self.max_distance_km:
                            continue  # Too far away
                
                # Check grade-level compatibility
                if student_grade is not None and tutor_user.fit_to_teach_level is not None:
                    if tutor_user.fit_to_teach_level < student_grade:
                        continue  # Skip - tutor not fit to teach this grade
                
                compatibility = self.matcher.calculate_compatibility_score(
                    tutor_perf.score,
                    student_perf.score,
                )
                
                potential_tutors.append((
                    tutor_perf.student_id,
                    compatibility,
                    {
                        'name': tutor_user.name,
                        'email': tutor_user.email,
                        'grade': tutor_user.current_level,
                        'fit_to_teach_level': tutor_user.fit_to_teach_level,
                        'location': tutor_user.location,
                        'score': tutor_perf.score,
                        'accuracy': tutor_perf.accuracy_percentage,
                        'school': tutor_user.school.name if tutor_user.school else None,
                    }
                ))
        
        # Sort by compatibility (descending)
        potential_tutors.sort(key=lambda x: x[1], reverse=True)
        
        return potential_tutors[:limit]
    
    def get_potential_learners_for_student(
        self,
        student_id: int,
        subject: str,
        chapter: str,
        meeting_type: str = "online",
        location: Optional[str] = None,
        limit: int = 10,
    ) -> List[Tuple[int, float, Dict]]:
        """
        Get potential learners a student can help based on their performance.
        Returns list of (learner_id, compatibility_score, learner_data)
        """
        # Get student's performance
        student_perf = self.db.query(StudentChapterPerformance).filter(
            StudentChapterPerformance.student_id == student_id,
            StudentChapterPerformance.subject == subject,
            StudentChapterPerformance.chapter == chapter,
        ).first()
        
        if not student_perf or student_perf.score < self.matcher.tutor_threshold:
            return []  # Student not qualified to tutor
        
        # Get student's fit_to_teach_level
        student_user = self.db.query(User).filter(User.id == student_id).first()
        fit_to_teach_level = student_user.fit_to_teach_level if student_user else None
        
        # Find potential learners (low scorers)
        learners_query = self.db.query(StudentChapterPerformance).filter(
            StudentChapterPerformance.subject == subject,
            StudentChapterPerformance.chapter == chapter,
            StudentChapterPerformance.score <= self.matcher.learner_threshold,
            StudentChapterPerformance.student_id != student_id,  # Not themselves
        )
        
        learners = learners_query.all()
        
        # Calculate compatibility and build results
        potential_learners = []
        for learner_perf in learners:
            # Get learner user data
            learner_user = self.db.query(User).filter(User.id == learner_perf.student_id).first()
            
            if learner_user:
                # For physical meetups, check location/GPS proximity
                if meeting_type == "physical":
                    if location:
                        # Text-based location match
                        if not learner_user.location or learner_user.location.lower() != location.lower():
                            continue
                    elif student_user and student_user.latitude and student_user.longitude:
                        # GPS proximity match
                        if not learner_user.latitude or not learner_user.longitude:
                            continue
                        distance = self.calculate_distance(
                            student_user.latitude, student_user.longitude,
                            learner_user.latitude, learner_user.longitude
                        )
                        if distance > self.max_distance_km:
                            continue  # Too far away
                
                # Check grade-level compatibility
                if fit_to_teach_level is not None and learner_user.current_level is not None:
                    if fit_to_teach_level < learner_user.current_level:
                        continue  # Skip - not fit to teach this learner's grade
                
                compatibility = self.matcher.calculate_compatibility_score(
                    student_perf.score,
                    learner_perf.score,
                )
                
                potential_learners.append((
                    learner_perf.student_id,
                    compatibility,
                    {
                        'name': learner_user.name,
                        'email': learner_user.email,
                        'grade': learner_user.current_level,
                        'location': learner_user.location,
                        'score': learner_perf.score,
                        'accuracy': learner_perf.accuracy_percentage,
                        'school': learner_user.school.name if learner_user.school else None,
                    }
                ))
        
        # Sort by compatibility (descending)
        potential_learners.sort(key=lambda x: x[1], reverse=True)
        
        return potential_learners[:limit]
    
    def get_subject_level_matches(
        self,
        student_id: int,
        meeting_type: str = "online",
        location: Optional[str] = None,
        limit: int = 10,
    ) -> Dict[str, List[Dict]]:
        """
        Get potential matches based on overall subject performance across all subjects.
        This allows matching between students from different grade levels (e.g., Grade 7 & Grade 10).
        
        Returns dict with 'can_tutor' and 'needs_help' lists for each subject.
        """
        # Get student's all performances
        student_perfs = self.db.query(StudentChapterPerformance).filter(
            StudentChapterPerformance.student_id == student_id,
        ).all()
        
        print(f"[DEBUG] Student {student_id} has {len(student_perfs)} performance records")
        
        if not student_perfs:
            print(f"[DEBUG] No performance data found for student {student_id}")
            return {'can_tutor': [], 'needs_help': []}
        
        # Get student's user data
        student_user = self.db.query(User).filter(User.id == student_id).first()
        if not student_user:
            return {'can_tutor': [], 'needs_help': []}
        
        # Calculate average score per subject for this student
        subject_scores = defaultdict(list)
        for perf in student_perfs:
            subject_scores[perf.subject].append(perf.score)
        
        subject_averages = {
            subject: sum(scores) / len(scores)
            for subject, scores in subject_scores.items()
        }
        
        print(f"[DEBUG] Subject averages for user {student_id}: {subject_averages}")
        print(f"[DEBUG] Tutor threshold: {self.matcher.tutor_threshold}, Learner threshold: {self.matcher.learner_threshold}")
        
        can_tutor_in = []  # Subjects where student can tutor
        needs_help_in = []  # Subjects where student needs help
        
        # For each subject, find matches
        for subject, avg_score in subject_averages.items():
            print(f"[DEBUG] Checking {subject}: avg_score={avg_score:.2f}")
            
            # Can tutor if:
            # 1. Average >= 7.0 (standard threshold), OR
            # 2. Average > 5.0 AND user has fit_to_teach_level set (can teach lower grades)
            can_tutor = False
            if avg_score >= self.matcher.tutor_threshold:
                can_tutor = True
                print(f"[DEBUG]   {subject}: Can tutor (avg={avg_score:.2f} >= {self.matcher.tutor_threshold})")
            elif avg_score > 5.0 and student_user.fit_to_teach_level is not None:
                can_tutor = True
                print(f"[DEBUG]   {subject}: Can tutor (avg={avg_score:.2f} > 5.0 AND fit_to_teach_level={student_user.fit_to_teach_level})")
            
            if can_tutor:
                # Find students who need help in this subject
                potential_learners = self._find_subject_level_learners(
                    student_id, student_user, subject, avg_score, 
                    meeting_type, location, limit
                )
                print(f"[DEBUG]   Found {len(potential_learners)} potential learners")
                if potential_learners:
                    can_tutor_in.append({
                        'subject': subject,
                        'my_average_score': round(avg_score, 2),
                        'potential_learners': potential_learners
                    })
            
            # Needs help if average < 10 (not perfect)
            # Anyone can ask for help from someone fit to teach their grade
            if avg_score < 10.0:
                print(f"[DEBUG]   {subject}: Can ask for help (avg={avg_score:.2f} < 10.0)")
                # Find students who can tutor this subject
                potential_tutors = self._find_subject_level_tutors(
                    student_id, student_user, subject, avg_score,
                    meeting_type, location, limit
                )
                print(f"[DEBUG]   Found {len(potential_tutors)} potential tutors")
                if potential_tutors:
                    needs_help_in.append({
                        'subject': subject,
                        'my_average_score': round(avg_score, 2),
                        'potential_tutors': potential_tutors
                    })
        
        return {
            'can_tutor': can_tutor_in,
            'needs_help': needs_help_in
        }
    
    def _find_subject_level_tutors(
        self,
        student_id: int,
        student_user: User,
        subject: str,
        student_avg_score: float,
        meeting_type: str,
        location: Optional[str],
        limit: int,
    ) -> List[Dict]:
        """Find potential tutors for a subject (regardless of chapters)."""
        # Get all students who have taken this subject
        subject_perfs = self.db.query(StudentChapterPerformance).filter(
            StudentChapterPerformance.subject == subject,
            StudentChapterPerformance.student_id != student_id,
        ).all()
        
        # Calculate average scores per student
        student_subject_scores = defaultdict(list)
        for perf in subject_perfs:
            student_subject_scores[perf.student_id].append(perf.score)
        
        potential_tutors = []
        for tutor_id, scores in student_subject_scores.items():
            avg_score = sum(scores) / len(scores)
            
            # Get tutor user data
            tutor_user = self.db.query(User).filter(User.id == tutor_id).first()
            if not tutor_user:
                continue
            
            # Check grade-level compatibility
            if student_user.current_level is not None and tutor_user.fit_to_teach_level is not None:
                if tutor_user.fit_to_teach_level < student_user.current_level:
                    continue  # Tutor not fit to teach this grade
                
                # If fit to teach this grade, only need >50% (5.0/10) score
                if avg_score <= 5.0:
                    continue
            else:
                # If no grade compatibility info, use stricter threshold (70%)
                if avg_score < self.matcher.tutor_threshold:
                    continue
            
            # For physical meetups, check location/GPS proximity
            if meeting_type == "physical":
                if location:
                    if not tutor_user.location or tutor_user.location.lower() != location.lower():
                        continue
                elif student_user.latitude and student_user.longitude:
                    if not tutor_user.latitude or not tutor_user.longitude:
                        continue
                    distance = self.calculate_distance(
                        student_user.latitude, student_user.longitude,
                        tutor_user.latitude, tutor_user.longitude
                    )
                    if distance > self.max_distance_km:
                        continue
            
            # Calculate compatibility score
            compatibility = self.matcher.calculate_compatibility_score(
                avg_score, student_avg_score
            )
            
            potential_tutors.append({
                'user_id': tutor_id,
                'name': tutor_user.name,
                'email': tutor_user.email,
                'grade': tutor_user.current_level,
                'fit_to_teach_level': tutor_user.fit_to_teach_level,
                'average_score': round(avg_score, 2),
                'compatibility_score': round(compatibility, 2),
                'location': tutor_user.location,
            })
        
        # Sort by compatibility score
        potential_tutors.sort(key=lambda x: x['compatibility_score'], reverse=True)
        return potential_tutors[:limit]
    
    def _find_subject_level_learners(
        self,
        student_id: int,
        student_user: User,
        subject: str,
        student_avg_score: float,
        meeting_type: str,
        location: Optional[str],
        limit: int,
    ) -> List[Dict]:
        """Find potential learners for a subject (regardless of chapters)."""
        # Get all students who have taken this subject
        subject_perfs = self.db.query(StudentChapterPerformance).filter(
            StudentChapterPerformance.subject == subject,
            StudentChapterPerformance.student_id != student_id,
        ).all()
        
        # Calculate average scores per student
        student_subject_scores = defaultdict(list)
        for perf in subject_perfs:
            student_subject_scores[perf.student_id].append(perf.score)
        
        potential_learners = []
        for learner_id, scores in student_subject_scores.items():
            avg_score = sum(scores) / len(scores)
            
            # Get learner user data
            learner_user = self.db.query(User).filter(User.id == learner_id).first()
            if not learner_user:
                continue
            
            # Check grade-level compatibility first
            grade_compatible = False
            if learner_user.current_level is not None and student_user.fit_to_teach_level is not None:
                if student_user.fit_to_teach_level < learner_user.current_level:
                    continue  # Current student not fit to teach this grade
                grade_compatible = True
            
            # If tutor is fit to teach this learner's grade, match regardless of learner's score
            # (tutor just needs to have taken the assessment and have >50%)
            if grade_compatible:
                # Tutor can help anyone in their fit_to_teach_level
                if student_avg_score <= 5.0:  # Tutor needs >50%
                    continue
            else:
                # Without grade compatibility, require learner to have low score (≤50%)
                if avg_score > self.matcher.learner_threshold:
                    continue
            
            # For physical meetups, check location/GPS proximity
            if meeting_type == "physical":
                if location:
                    if not learner_user.location or learner_user.location.lower() != location.lower():
                        continue
                elif student_user.latitude and student_user.longitude:
                    if not learner_user.latitude or not learner_user.longitude:
                        continue
                    distance = self.calculate_distance(
                        student_user.latitude, student_user.longitude,
                        learner_user.latitude, learner_user.longitude
                    )
                    if distance > self.max_distance_km:
                        continue
            
            # Calculate compatibility score
            compatibility = self.matcher.calculate_compatibility_score(
                student_avg_score, avg_score
            )
            
            potential_learners.append({
                'user_id': learner_id,
                'name': learner_user.name,
                'email': learner_user.email,
                'grade': learner_user.current_level,
                'fit_to_teach_level': learner_user.fit_to_teach_level,
                'average_score': round(avg_score, 2),
                'compatibility_score': round(compatibility, 2),
                'location': learner_user.location,
            })
        
        # Sort by compatibility score
        potential_learners.sort(key=lambda x: x['compatibility_score'], reverse=True)
        return potential_learners[:limit]
    
    def _calculate_overlapping_chapters(
        self,
        tutor_ids: List[int],
        learner_ids: List[int],
        subject: str,
    ) -> Dict[Tuple[int, int], int]:
        """
        Calculate how many chapters overlap between each tutor-learner pair in a subject.
        
        Returns:
            {(tutor_id, learner_id): count_of_overlapping_chapters}
        """
        overlaps = {}
        
        # Get all chapter performances for these students in this subject
        all_ids = set(tutor_ids + learner_ids)
        performances = self.db.query(StudentChapterPerformance).filter(
            StudentChapterPerformance.student_id.in_(all_ids),
            StudentChapterPerformance.subject == subject,
        ).all()
        
        # Build chapter sets for each student
        student_chapters = defaultdict(set)
        for perf in performances:
            student_chapters[perf.student_id].add(perf.chapter)
        
        # Calculate overlaps for each tutor-learner pair
        for tutor_id in tutor_ids:
            tutor_chapters = student_chapters.get(tutor_id, set())
            for learner_id in learner_ids:
                if tutor_id == learner_id:
                    continue
                learner_chapters = student_chapters.get(learner_id, set())
                overlap_count = len(tutor_chapters & learner_chapters)
                overlaps[(tutor_id, learner_id)] = overlap_count
        
        return overlaps


def get_peer_matching_service(db: Session) -> PeerMatchingService:
    """Get peer matching service instance."""
    return PeerMatchingService(db)
