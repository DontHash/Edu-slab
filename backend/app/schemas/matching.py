"""
Pydantic schemas for peer-to-peer matching
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# StudentChapterPerformance Schemas
class StudentChapterPerformanceBase(BaseModel):
    subject: str
    chapter: str
    score: float
    accuracy_percentage: int
    weakness_level: str
    total_questions_attempted: int = 0
    correct_answers: int = 0
    is_strong_chapter: bool = False
    is_weak_chapter: bool = False


class StudentChapterPerformanceCreate(StudentChapterPerformanceBase):
    student_id: int


class StudentChapterPerformance(StudentChapterPerformanceBase):
    id: int
    student_id: int
    last_assessed_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# PeerMatch Schemas
class PeerMatchBase(BaseModel):
    chapter: str
    subject: str
    meeting_type: str = "online"  # physical or online
    tutor_score: float
    learner_score: float
    compatibility_score: Optional[float] = None
    preference_rank_tutor: Optional[int] = None
    preference_rank_learner: Optional[int] = None


class PeerMatchCreate(PeerMatchBase):
    tutor_id: int
    learner_id: int


class PeerMatch(PeerMatchBase):
    id: int
    tutor_id: int
    learner_id: int
    status: str
    matched_at: datetime
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PeerMatchWithDetails(PeerMatch):
    """Match with tutor and learner details"""
    tutor_name: str
    tutor_email: str
    tutor_grade: Optional[int] = None
    tutor_fit_to_teach_level: Optional[int] = None
    tutor_location: Optional[str] = None
    learner_name: str
    learner_email: str
    learner_grade: Optional[int] = None
    learner_location: Optional[str] = None
    tutor_school: Optional[str] = None
    learner_school: Optional[str] = None
    overlapping_chapters: Optional[int] = None


# TutoringSession Schemas
class TutoringSessionBase(BaseModel):
    meeting_type: str  # physical or online
    meeting_link: Optional[str] = None
    physical_location: Optional[str] = None
    topics_covered: Optional[List[str]] = None
    notes: Optional[str] = None
    tutor_rating: Optional[int] = Field(None, ge=1, le=5)
    learner_rating: Optional[int] = Field(None, ge=1, le=5)
    tutor_feedback: Optional[str] = None
    learner_feedback: Optional[str] = None
    learner_progress: Optional[float] = None


class TutoringSessionCreate(TutoringSessionBase):
    match_id: int
    scheduled_at: Optional[datetime] = None


class TutoringSessionUpdate(TutoringSessionBase):
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None


class TutoringSession(TutoringSessionBase):
    id: int
    match_id: int
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Matching Request/Response Schemas
class MatchingRequest(BaseModel):
    subject: str
    chapter: str
    meeting_type: str = "online"  # physical or online
    school_id: Optional[int] = None
    location: Optional[str] = None  # For physical meetups (text-based)
    max_distance_km: Optional[float] = 10.0  # For GPS proximity matching


class MatchingResponse(BaseModel):
    success: bool
    message: str
    matches_created: int
    matches: List[PeerMatchWithDetails]


class StudentMatchesResponse(BaseModel):
    tutoring_matches: List[PeerMatchWithDetails]  # Where student is tutor
    learning_matches: List[PeerMatchWithDetails]  # Where student is learner
    total_matches: int


class MatchStatusUpdate(BaseModel):
    status: str  # 'accepted', 'rejected', 'completed'


class ChapterListResponse(BaseModel):
    """Available chapters for matching"""
    subject: str
    chapters: List[str]
    total_students: int


class MatchingStatsResponse(BaseModel):
    """Statistics about matching"""
    total_potential_tutors: int
    total_potential_learners: int
    chapters_available: List[str]
    subjects_available: List[str]


# Help Request/Offer Schemas
class HelpRequestBase(BaseModel):
    subject: str
    chapter: str
    request_type: str = "asking_help"  # asking_help or offering_help
    meeting_type: str = "online"  # physical or online
    preferred_location: Optional[str] = None
    description: Optional[str] = None
    urgency: str = "normal"  # low, normal, high, urgent


class HelpRequestCreate(HelpRequestBase):
    pass


class HelpRequest(HelpRequestBase):
    id: int
    student_id: int
    student_score: Optional[float] = None
    status: str
    matched_with: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    fulfilled_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class HelpRequestWithDetails(HelpRequest):
    """Help request with student details"""
    student_name: str
    student_email: str
    student_grade: Optional[int] = None
    student_location: Optional[str] = None
    student_school: Optional[str] = None
    tutor_name: Optional[str] = None


class HelpOfferBase(BaseModel):
    subject: str
    chapter: str
    request_type: str = "offering_help"  # asking_help or offering_help
    meeting_type: str = "online"  # physical or online
    available_location: Optional[str] = None
    description: Optional[str] = None
    availability: Optional[str] = None
    max_students: int = 3


class HelpOfferCreate(HelpOfferBase):
    pass


class HelpOffer(HelpOfferBase):
    id: int
    tutor_id: int
    tutor_score: Optional[float] = None
    is_active: bool
    current_students: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class HelpOfferWithDetails(HelpOffer):
    """Help offer with tutor details"""
    tutor_name: str
    tutor_email: str
    tutor_grade: Optional[int] = None
    tutor_fit_to_teach_level: Optional[int] = None
    tutor_location: Optional[str] = None
    tutor_school: Optional[str] = None


# Potential Match Schemas
class PotentialTutor(BaseModel):
    """Potential tutor for a student"""
    student_id: int
    name: str
    email: str
    grade: Optional[int] = None
    fit_to_teach_level: Optional[int] = None
    location: Optional[str] = None
    score: float
    accuracy: int
    compatibility_score: float
    school: Optional[str] = None


class PotentialLearner(BaseModel):
    """Potential learner for a tutor"""
    student_id: int
    name: str
    email: str
    grade: Optional[int] = None
    location: Optional[str] = None
    score: float
    accuracy: int
    compatibility_score: float
    school: Optional[str] = None


class PotentialMatchesResponse(BaseModel):
    """Automatic suggestions for potential matches"""
    subject: str
    chapter: str
    student_score: Optional[float] = None
    can_tutor: bool
    can_learn: bool
    potential_tutors: List[PotentialTutor] = []
    potential_learners: List[PotentialLearner] = []


class DirectMatchRequest(BaseModel):
    """Request to create a direct match with a specific student"""
    peer_student_id: int
    subject: str
    chapter: str
    message: Optional[str] = None


# Chat Message Schemas
class ChatMessageCreate(BaseModel):
    match_id: int
    receiver_id: int
    message: str
    message_type: str = "text"
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None


class ChatMessage(BaseModel):
    id: int
    match_id: int
    sender_id: int
    receiver_id: int
    message: str
    message_type: str
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    sender_name: Optional[str] = None
    receiver_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# Session/Video Call Schemas
class SessionCreate(BaseModel):
    match_id: int
    communication_method: str  # text, video_call, in_person
    scheduled_at: Optional[datetime] = None
    meeting_location: Optional[str] = None


class SessionUpdate(BaseModel):
    meeting_link: Optional[str] = None
    topics_covered: Optional[List[str]] = None
    notes: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class Session(BaseModel):
    id: int
    match_id: int
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    communication_method: str
    meeting_link: Optional[str] = None
    meeting_location: Optional[str] = None
    topics_covered: Optional[List[str]] = None
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Resource Sharing Schemas
class SharedResourceCreate(BaseModel):
    match_id: int
    title: str
    description: Optional[str] = None
    resource_type: str  # pdf, doc, image, video, link, note
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    external_link: Optional[str] = None
    subject: Optional[str] = None
    chapter: Optional[str] = None
    tags: Optional[List[str]] = None


class SharedResource(BaseModel):
    id: int
    match_id: int
    uploader_id: int
    title: str
    description: Optional[str] = None
    resource_type: str
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    external_link: Optional[str] = None
    subject: Optional[str] = None
    chapter: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: datetime
    uploader_name: Optional[str] = None
    
    class Config:
        from_attributes = True
