"""
Tests for authentication endpoints
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_register_user():
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "name": "Test User",
            "password": "testpass123",
            "role": "student"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"


def test_login_user():
    """Test user login"""
    # First register
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "name": "Login User",
            "password": "loginpass123",
            "role": "student"
        }
    )
    
    # Then login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@example.com",
            "password": "loginpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
