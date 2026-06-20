"""
Peer-to-peer matching models for student tutoring
"""
import enum
from datetime import datetime

from app.db.database import Base
from sqlalchemy import (JSON, Boolean, Column, DateTime, Enum, Float,
                        ForeignKey, Integer, String, Text)
from sqlalchemy.orm import relationship


class MatchStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"


class MeetingType(str, enum.Enum):
    PHYSICAL = "physical"  # In-person meetup
    ONLINE = "online"      # Virtual session


class RequestType(str, enum.Enum):
    ASKING_HELP = "asking_help"    # Student needs help
    OFFERING_HELP = "offering_help"  # Student can help others


class PeerMatch(Base):
    """Represents a peer-to-peer tutoring match between students"""
    __tablename__ = "peer_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Tutor (high-scoring student)
    tutor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Learner (low-scoring student)
    learner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Chapter-specific matching
    chapter = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    
    # Meeting type
    meeting_type = Column(Enum(MeetingType), default=MeetingType.ONLINE, nullable=False)
    
    # Matching scores
    tutor_score = Column(Float, nullable=False)  # Tutor's score in this chapter (0-10)
    learner_score = Column(Float, nullable=False)  # Learner's score in this chapter (0-10)
    
    # Match quality metrics
    compatibility_score = Column(Float, nullable=True)  # Algorithm-calculated match quality
    preference_rank_tutor = Column(Integer, nullable=True)  # Tutor's preference rank
    preference_rank_learner = Column(Integer, nullable=True)  # Learner's preference rank
    
    # Status and engagement
    status = Column(Enum(MatchStatus), default=MatchStatus.PENDING)
    
    # Timestamps
    matched_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    tutor = relationship("User", foreign_keys=[tutor_id], backref="tutoring_matches")
    learner = relationship("User", foreign_keys=[learner_id], backref="learning_matches")
    sessions = relationship("TutoringSession", back_populates="match")


class TutoringSession(Base):
    """Records individual tutoring sessions between matched peers"""
    __tablename__ = "tutoring_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("peer_matches.id"), nullable=False)
    
    # Session type and location
    meeting_type = Column(Enum(MeetingType), nullable=False)
    meeting_link = Column(String, nullable=True)  # For online sessions
    physical_location = Column(String, nullable=True)  # For physical meetups
    
    # Session details
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Communication method
    communication_method = Column(String, default="text")  # text, video_call, in_person
    meeting_link = Column(String, nullable=True)  # Google Meet link for video calls
    meeting_location = Column(String, nullable=True)  # Physical location for in-person
    
    # Session content
    topics_covered = Column(JSON, nullable=True)  # List of topics discussed
    notes = Column(Text, nullable=True)
    
    # Feedback
    tutor_rating = Column(Integer, nullable=True)  # 1-5 stars
    learner_rating = Column(Integer, nullable=True)  # 1-5 stars
    tutor_feedback = Column(Text, nullable=True)
    learner_feedback = Column(Text, nullable=True)
    
    # Session outcome
    learner_progress = Column(Float, nullable=True)  # Improvement score
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    match = relationship("PeerMatch", back_populates="sessions")


class StudentChapterPerformance(Base):
    """Tracks student performance by chapter for matching algorithm"""
    __tablename__ = "student_chapter_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String, nullable=False)
    chapter = Column(String, nullable=False)
    
    # Performance metrics
    score = Column(Float, nullable=False)  # Score out of 10
    accuracy_percentage = Column(Integer, nullable=False)
    total_questions_attempted = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    
    # Classification
    weakness_level = Column(String, nullable=False)  # none, mild, moderate, severe
    is_strong_chapter = Column(Boolean, default=False)  # Top performing chapters
    is_weak_chapter = Column(Boolean, default=False)  # Bottom performing chapters
    
    # Timestamps
    last_assessed_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("User", backref="chapter_performances")


class HelpRequestStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class HelpRequest(Base):
    """Student requests for help in specific chapters"""
    __tablename__ = "help_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String, nullable=False)
    chapter = Column(String, nullable=False)
    
    # Request type and meeting preference
    request_type = Column(Enum(RequestType), default=RequestType.ASKING_HELP, nullable=False)
    meeting_type = Column(Enum(MeetingType), default=MeetingType.ONLINE, nullable=False)
    preferred_location = Column(String, nullable=True)  # For physical meetups
    
    # Request details
    description = Column(Text, nullable=True)  # What specifically they need help with
    urgency = Column(String, default="normal")  # low, normal, high, urgent
    student_score = Column(Float, nullable=True)  # Their score in this chapter
    
    # Status
    status = Column(Enum(HelpRequestStatus), default=HelpRequestStatus.OPEN)
    
    # Matching
    matched_with = Column(Integer, ForeignKey("users.id"), nullable=True)  # Tutor who accepted
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fulfilled_at = Column(DateTime, nullable=True)
    
    # Relationships
    student = relationship("User", foreign_keys=[student_id], backref="help_requests")
    tutor = relationship("User", foreign_keys=[matched_with], backref="help_requests_accepted")


class HelpOffer(Base):
    """Student offers to help others in specific chapters"""
    __tablename__ = "help_offers"
    
    id = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String, nullable=False)
    chapter = Column(String, nullable=False)
    
    # Offer type and meeting preference
    request_type = Column(Enum(RequestType), default=RequestType.OFFERING_HELP, nullable=False)
    meeting_type = Column(Enum(MeetingType), default=MeetingType.ONLINE, nullable=False)
    available_location = Column(String, nullable=True)  # For physical meetups
    
    # Offer details
    description = Column(Text, nullable=True)  # What they can help with
    availability = Column(String, nullable=True)  # When they're available
    tutor_score = Column(Float, nullable=True)  # Their score in this chapter
    max_students = Column(Integer, default=3)  # How many students they can help
    
    # Status
    is_active = Column(Boolean, default=True)
    current_students = Column(Integer, default=0)  # Number currently helping
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tutor = relationship("User", backref="help_offers")


class ChatMessage(Base):
    """Chat messages between matched peers"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("peer_matches.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Message content
    message = Column(Text, nullable=False)
    message_type = Column(String, default="text")  # text, file, image, link
    
    # File attachment (if any)
    file_url = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)  # in bytes
    file_type = Column(String, nullable=True)  # mime type
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    match = relationship("PeerMatch", backref="chat_messages")
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="received_messages")


class SharedResource(Base):
    """Files and resources shared between matched peers"""
    __tablename__ = "shared_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("peer_matches.id"), nullable=False)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Resource details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    resource_type = Column(String, nullable=False)  # pdf, doc, image, video, link, note
    
    # File information
    file_url = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # For links
    external_link = Column(String, nullable=True)
    
    # Tags and categorization
    subject = Column(String, nullable=True)
    chapter = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)  # List of tags
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    match = relationship("PeerMatch", backref="shared_resources")
    uploader = relationship("User", backref="uploaded_resources")
