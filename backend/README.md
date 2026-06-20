# EduAssess Backend API

## Overview

Backend API for the EduAssess adaptive learning assessment platform built with FastAPI.

## Features

- ✅ User authentication with JWT tokens
- ✅ Role-based access control (Student, Teacher)
- ✅ School management
- ✅ Adaptive assessments
- ✅ Progress tracking
- ✅ Question bank management
- ✅ Student response tracking
- ✅ Analytics and reporting

## Tech Stack

- **Framework**: FastAPI 0.109+
- **Database**: SQLAlchemy with SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT with python-jose
- **Password Hashing**: passlib with bcrypt
- **Validation**: Pydantic v2
- **Server**: Uvicorn

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── users.py         # User management
│   │   │   ├── assessments.py   # Assessment & questions
│   │   │   ├── schools.py       # School management
│   │   │   └── progress.py      # Progress tracking
│   │   ├── api.py               # API router configuration
│   │   └── deps.py              # Dependencies (auth, db)
│   ├── core/
│   │   ├── config.py            # Settings & configuration
│   │   └── security.py          # Security utilities
│   ├── db/
│   │   ├── database.py          # Database connection
│   │   ├── init_db.py           # Database initialization
│   │   └── seed.py              # Sample data seeding
│   ├── models/
│   │   ├── user.py              # User model
│   │   ├── school.py            # School model
│   │   ├── assessment.py        # Assessment & Question models
│   │   └── progress.py          # Progress tracking model
│   └── schemas/
│       ├── user.py              # User schemas
│       ├── assessment.py        # Assessment schemas
│       ├── school.py            # School schemas
│       └── progress.py          # Progress schemas
├── main.py                       # Application entry point
├── pyproject.toml               # Dependencies
└── .env.example                 # Environment variables example
```

## Getting Started

### Prerequisites

- Python 3.10+
- pip or uv package manager

### Installation

1. **Clone the repository**

```bash
cd backend
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -e .
# Or with uv:
uv pip install -e .
```

4. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**

```bash
python -m app.db.init_db
```

6. **Seed database with sample data (optional)**

```bash
python -m app.db.seed
```

### Running the Server

**Development mode with auto-reload:**

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

### Users

- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user
- `GET /api/v1/users/{user_id}` - Get user by ID (teacher)
- `GET /api/v1/users/` - List all users (teacher)

### Assessments

- `POST /api/v1/assessments/` - Create assessment
- `GET /api/v1/assessments/{id}` - Get assessment
- `GET /api/v1/assessments/student/{id}` - Get student assessments
- `POST /api/v1/assessments/questions` - Create question (teacher)
- `GET /api/v1/assessments/questions/{id}` - Get question
- `GET /api/v1/assessments/questions/` - List questions with filters
- `POST /api/v1/assessments/responses` - Submit answer

### Schools

- `POST /api/v1/schools/` - Create school
- `GET /api/v1/schools/{id}` - Get school
- `GET /api/v1/schools/` - List schools
- `PUT /api/v1/schools/{id}` - Update school
- `DELETE /api/v1/schools/{id}` - Delete school

### Progress

- `GET /api/v1/progress/student/{id}` - Get student progress
- `PUT /api/v1/progress/student/{id}` - Update progress (teacher)

## Sample Credentials (after seeding)

- **Teacher**: teacher@eduassess.com / teacher123
- **Student**: student@eduassess.com / student123

**Note:** AI model for student assessment evaluation is currently being developed by a team member.

## Database Models

### User

- Supports two roles: Student, Teacher
- Tracks student learning levels (current, reading, writing, math)
- Associated with schools

### School

- Manages educational institutions
- Stores contact information and principal details

### Assessment

- Tracks student test attempts
- Adaptive difficulty based on performance
- Calculates scores automatically

### Question

- Multiple question types (multiple choice, true/false, short answer, essay)
- Difficulty levels (beginner, intermediate, advanced)
- Organized by subject, topic, and grade level

### Progress

- Comprehensive student progress tracking
- Subject-specific metrics
- Identifies strengths and weaknesses
- Provides personalized recommendations

## Development

### Adding New Routes

1. Create route file in `app/api/routes/`
2. Define endpoints with FastAPI decorators
3. Add to `app/api/api.py` router

### Adding New Models

1. Create model in `app/models/`
2. Create corresponding schema in `app/schemas/`
3. Import in `app/models/__init__.py`
4. Run database initialization

### Environment Variables

See `.env.example` for all available configuration options.

## Security

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- CORS configuration for frontend integration

## Production Deployment

1. **Set production environment variables**

```bash
DEBUG=False
SECRET_KEY=<strong-random-key>
DATABASE_URL=postgresql://user:pass@localhost/eduassess
```

2. **Use production WSGI server**

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

3. **Set up PostgreSQL database**
4. **Configure HTTPS/SSL**
5. **Set up proper CORS origins**

## License

MIT
