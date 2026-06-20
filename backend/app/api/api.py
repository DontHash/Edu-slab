"""
API router configuration
"""
from app.api.routes import (assessments, auth, diagnostic, learning_materials,
                            progress, rag_questions, resources, schools, users)
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(diagnostic.router, prefix="/diagnostic", tags=["diagnostic"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])
api_router.include_router(schools.router, prefix="/schools", tags=["schools"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
api_router.include_router(resources.router, prefix="/resources", tags=["resources"])
api_router.include_router(rag_questions.router, prefix="/rag", tags=["rag-questions"])
api_router.include_router(learning_materials.router, prefix="/learning-materials", tags=["learning-materials"])
