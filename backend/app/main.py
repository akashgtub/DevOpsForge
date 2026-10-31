
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import ReleaseRecord


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create missing tables for this development version.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="DevOpsForge API",
    description="Deployment management and service health API",
    version="0.2.0",
    lifespan=lifespan,
)


class ReleaseCreate(BaseModel):
    version: str = Field(min_length=1, max_length=50)
    git_commit: str = Field(min_length=7, max_length=40)


class Release(BaseModel):
    id: int
    version: str
    git_commit: str
    status: str
    created_at: datetime


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "devopsforge-api",
        "timestamp": datetime.now(timezone.utc),
    }


@app.get("/ready")
def readiness(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )


@app.post("/api/releases", response_model=Release, status_code=201)
def create_release(
    release: ReleaseCreate,
    db: Session = Depends(get_db),
):
    record = ReleaseRecord(
        version=release.version,
        git_commit=release.git_commit,
        status="registered",
    )

    try:
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save release",
        )


@app.get("/api/releases", response_model=list[Release])
def list_releases(db: Session = Depends(get_db)):
    statement = select(ReleaseRecord).order_by(ReleaseRecord.id)
    return db.scalars(statement).all()


@app.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    total = db.scalar(
        select(func.count()).select_from(ReleaseRecord)
    )
    return {"releases_total": total or 0}
