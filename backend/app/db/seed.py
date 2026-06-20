"""
Seed database with sample data for development/testing
"""
from app.core.security import get_password_hash
from app.db.database import SessionLocal
from app.models.assessment import DifficultyLevel, Question, QuestionType
from app.models.progress import Progress
from app.models.resource import Resource
from app.models.school import School
from app.models.user import User, UserRole
from sqlalchemy.orm import Session


def seed_schools(db: Session):
    """Create sample schools"""
    schools = [
        School(
            name="Lincoln Elementary School",
            address="123 Main St",
            city="Springfield",
            state="IL",
            zip_code="62701",
            phone="555-0100",
            email="info@lincoln.edu",
            principal_name="Dr. Sarah Johnson"
        ),
        School(
            name="Washington High School",
            address="456 Oak Ave",
            city="Chicago",
            state="IL",
            zip_code="60601",
            phone="555-0200",
            email="info@washington.edu",
            principal_name="Mr. Michael Chen"
        )
    ]
    
    for school in schools:
        db.add(school)
    db.commit()
    print(f"✓ Created {len(schools)} schools")


def seed_users(db: Session):
    """Create sample users"""
    # bcrypt has a 72 byte limit, so use shorter passwords
    users = [
        User(
            email="admin@eduassess.com",
            name="Admin User",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        ),
        User(
            email="teacher@eduassess.com",
            name="Jane Teacher",
            hashed_password=get_password_hash("teacher123"),
            role=UserRole.TEACHER,
            school_id=1,
            is_active=True
        ),
        User(
            email="student@eduassess.com",
            name="John Student",
            hashed_password=get_password_hash("student123"),
            role=UserRole.STUDENT,
            school_id=1,
            current_level=5,
            math_level=4,
            science_level=5,
            english_level=6,
            is_active=True
        ),
    ]
    
    for user in users:
        db.add(user)
    db.commit()
    print(f"✓ Created {len(users)} users")


def seed_questions(db: Session):
    """Create sample questions"""
    questions = [
        # Math Questions - Grade 3
        Question(
            subject="Math",
            topic="Addition",
            difficulty=DifficultyLevel.BEGINNER,
            question_type=QuestionType.MULTIPLE_CHOICE,
            grade_level=3,
            question_text="What is 15 + 27?",
            options=["32", "42", "52", "62"],
            correct_answer="42",
            explanation="15 + 27 = 42",
            points=1
        ),
        Question(
            subject="Math",
            topic="Multiplication",
            difficulty=DifficultyLevel.INTERMEDIATE,
            question_type=QuestionType.MULTIPLE_CHOICE,
            grade_level=3,
            question_text="What is 8 × 7?",
            options=["54", "56", "64", "72"],
            correct_answer="56",
            explanation="8 × 7 = 56",
            points=1
        ),
        
        # Reading Questions - Grade 4
        Question(
            subject="Reading",
            topic="Vocabulary",
            difficulty=DifficultyLevel.BEGINNER,
            question_type=QuestionType.MULTIPLE_CHOICE,
            grade_level=4,
            question_text="What does 'enormous' mean?",
            options=["Very small", "Very large", "Very fast", "Very slow"],
            correct_answer="Very large",
            explanation="Enormous means extremely large or huge.",
            points=1
        ),
        Question(
            subject="Reading",
            topic="Comprehension",
            difficulty=DifficultyLevel.INTERMEDIATE,
            question_type=QuestionType.SHORT_ANSWER,
            grade_level=4,
            question_text="What is the main idea of a paragraph?",
            correct_answer="the most important point",
            explanation="The main idea is the central or most important point in a paragraph.",
            points=2
        ),
        
        # Science Questions - Grade 5
        Question(
            subject="Science",
            topic="Biology",
            difficulty=DifficultyLevel.INTERMEDIATE,
            question_type=QuestionType.MULTIPLE_CHOICE,
            grade_level=5,
            question_text="What is the process by which plants make food?",
            options=["Respiration", "Photosynthesis", "Digestion", "Reproduction"],
            correct_answer="Photosynthesis",
            explanation="Plants use photosynthesis to convert sunlight into energy.",
            points=1
        ),
        Question(
            subject="Science",
            topic="Earth Science",
            difficulty=DifficultyLevel.BEGINNER,
            question_type=QuestionType.TRUE_FALSE,
            grade_level=5,
            question_text="The Earth revolves around the Sun.",
            correct_answer="true",
            explanation="The Earth takes approximately 365 days to revolve around the Sun.",
            points=1
        ),
    ]
    
    for question in questions:
        db.add(question)
    db.commit()
    print(f"✓ Created {len(questions)} sample questions")


def seed_resources(db: Session):
    """Create sample learning resources"""
    resources = [
        # Mathematics Resources
        Resource(
            type="video",
            title="Introduction to Algebra",
            description="Learn the basics of algebraic expressions and equations with step-by-step examples",
            subject="Mathematics",
            difficulty="Beginner",
            level=6,
            duration="15 min",
            url="https://example.com/algebra-intro"
        ),
        Resource(
            type="video",
            title="Advanced Algebra Techniques",
            description="Master advanced algebraic concepts including quadratic equations and factoring",
            subject="Mathematics",
            difficulty="Advanced",
            level=8,
            duration="25 min",
            url="https://example.com/algebra-advanced"
        ),
        Resource(
            type="exercise",
            title="Multiplication Practice",
            description="Interactive exercises to master multiplication tables up to 12",
            subject="Mathematics",
            difficulty="Beginner",
            level=3,
            duration="20 min",
            url="https://example.com/multiplication-practice"
        ),
        
        # English Resources
        Resource(
            type="article",
            title="Essay Writing Techniques",
            description="Master the art of writing compelling essays with proper structure and arguments",
            subject="English",
            difficulty="Intermediate",
            level=7,
            duration="10 min",
            url="https://example.com/essay-writing"
        ),
        Resource(
            type="exercise",
            title="Grammar Practice",
            description="Interactive exercises to improve your grammar skills including punctuation and sentence structure",
            subject="English",
            difficulty="Beginner",
            level=5,
            duration="15 min",
            url="https://example.com/grammar-practice"
        ),
        Resource(
            type="video",
            title="Reading Comprehension Strategies",
            description="Learn effective strategies to understand and analyze complex texts",
            subject="English",
            difficulty="Intermediate",
            level=6,
            duration="18 min",
            url="https://example.com/reading-comprehension"
        ),
        
        # Science Resources
        Resource(
            type="video",
            title="Introduction to Photosynthesis",
            description="Understand how plants convert sunlight into energy through photosynthesis",
            subject="Science",
            difficulty="Beginner",
            level=5,
            duration="12 min",
            url="https://example.com/photosynthesis"
        ),
        Resource(
            type="article",
            title="The Solar System",
            description="Explore the planets, moons, and other celestial bodies in our solar system",
            subject="Science",
            difficulty="Beginner",
            level=4,
            duration="15 min",
            url="https://example.com/solar-system"
        ),
        Resource(
            type="exercise",
            title="Scientific Method Practice",
            description="Apply the scientific method to real-world problems and experiments",
            subject="Science",
            difficulty="Intermediate",
            level=6,
            duration="25 min",
            url="https://example.com/scientific-method"
        ),
        
        # Flashcard Resources
        Resource(
            type="flashcard",
            title="Vocabulary Builder",
            description="Expand your vocabulary with common academic words and their meanings",
            subject="English",
            difficulty="Intermediate",
            level=5,
            duration="10 min",
            content='[{"term": "Analyze", "definition": "To examine in detail"}, {"term": "Synthesize", "definition": "To combine elements to form a whole"}]'
        ),
    ]
    
    for resource in resources:
        db.add(resource)
    db.commit()
    print(f"✓ Created {len(resources)} learning resources")


def seed_progress(db: Session):
    """Create sample progress data for test student"""
    # Create progress for the test student (ID 3)
    progress = Progress(
        student_id=3,
        overall_progress=65.5,
        total_assessments=5,
        total_tests_completed=12,
        subject_progress={
            "Mathematics": {
                "level": 4,
                "progress": 60,
                "completed_lessons": 15,
                "completed_tests": 4
            },
            "English": {
                "level": 5,
                "progress": 70,
                "completed_lessons": 20,
                "completed_tests": 5
            },
            "Science": {
                "level": 6,
                "progress": 68,
                "completed_lessons": 18,
                "completed_tests": 3
            }
        },
        strengths=["Reading Comprehension", "Problem Solving", "Scientific Method"],
        weaknesses=["Grammar", "Algebra", "Essay Writing"],
        recommended_topics=["Advanced Grammar", "Quadratic Equations", "Persuasive Writing"],
        attendance_rate=92.5
    )
    
    db.add(progress)
    db.commit()
    print(f"✓ Created progress data for test student")


def seed_database():
    """Seed the database with sample data"""
    db = SessionLocal()
    
    try:
        print("\n🌱 Seeding database...")
        
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("⚠️  Database already contains data. Skipping seed.")
            return
        
        seed_schools(db)
        seed_users(db)
        seed_questions(db)
        seed_resources(db)
        seed_progress(db)
        
        print("\n✅ Database seeding completed successfully!")
        print("\nSample credentials:")
        print("  Admin:   admin@eduassess.com / admin123")
        print("  Teacher: teacher@eduassess.com / teacher123")
        print("  Student: student@eduassess.com / student123")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
