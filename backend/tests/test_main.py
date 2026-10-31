
import os

# Configure a test database before importing the application.
os.environ["DATABASE_URL"] = "sqlite+pysqlite://"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import main
from app.database import Base, get_db

# A single in-memory SQLite connection is shared by the tests.
test_engine = create_engine(
    "sqlite+pysqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route database operations to SQLite, not development PostgreSQL.
main.app.dependency_overrides[get_db] = override_get_db

client = TestClient(main.app)

def setup_function():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

def teardown_function():
    Base.metadata.drop_all(bind=test_engine)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "devopsforge-api"

def test_readiness_endpoint():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["database"] == "connected"

def test_create_release():
    payload = {
        "version": "v0.1.0",
        "git_commit": "abcdef1234567890",
    }
    response = client.post("/api/releases", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["version"] == "v0.1.0"
    assert data["git_commit"] == "abcdef1234567890"
    assert data["status"] == "registered"
    assert "created_at" in data

def test_list_releases():
    client.post(
        "/api/releases",
        json={
            "version": "v0.1.0",
            "git_commit": "abcdef1234567890",
        },
    )

    response = client.get("/api/releases")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["version"] == "v0.1.0"

def test_metrics_count():
    client.post(
        "/api/releases",
        json={
            "version": "v0.1.0",
            "git_commit": "abcdef1234567890",
        },
    )

    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json()["releases_total"] == 1

def test_invalid_release_is_rejected():
    response = client.post(
        "/api/releases",
        json={"version": "", "git_commit": "abc"},
    )
    assert response.status_code == 422
