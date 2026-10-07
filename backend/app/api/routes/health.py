from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    service: str


class DatabaseHealthResponse(BaseModel):
    status: str
    database: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="API Health Check",
    description="Returns service health status to verify FastAPI instance availability."
)
async def health_check():
    """
    Service health check endpoint for monitoring uptime and CORS communication.
    """
    return {
        "status": "ok",
        "service": "SkillSwap AI API"
    }


@router.get(
    "/health/db",
    response_model=DatabaseHealthResponse,
    summary="Database Health Check",
    description="Verifies database connectivity liveness by executing a lightweight query on PostgreSQL."
)
async def db_health_check(db: Session = Depends(get_db)):
    """
    Database health check endpoint that tests database session execution.
    Exposes no sensitive credentials or connection details.
    """
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )
