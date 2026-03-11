from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.config import settings, get_settings
 
router = APIRouter(tags=["Health"])
 
 
class HealthResponse(BaseModel):
    status: str = Field(
        description="The health status of the application", example="healthy"
    )
    timestamp: str = Field(
        description="The timestamp of the health check", example="2024-06-01T12:00:00Z"
    )
    version: str = Field(description="Application version", example="1.0.0")
    environment: str = Field(
        description="Application environment", example="development"
    )
 
 
@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of the application.",
)
async def health_check(
    settings: Annotated[settings, Depends(get_settings)],
) -> HealthResponse:
    """Endpoint to check the health status of the application."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(UTC).isoformat(),
        version=settings.app_version,
        environment=settings.environment,
    )