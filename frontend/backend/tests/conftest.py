import os
os.environ["DATABASE_URL"] = "sqlite:///./test_kishan.db"
os.environ["JWT_SECRET"] = "test-secret-that-is-long-enough"

import pytest
from fastapi.testclient import TestClient
from app.database import Base, engine
from app.main import app

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def auth(client):
    response = client.post("/api/v1/auth/register", json={"name":"Test Farmer","email":"farmer@example.com","password":"strongpass123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
