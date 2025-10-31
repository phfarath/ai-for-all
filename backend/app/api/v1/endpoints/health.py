"""Health endpoint exposing API readiness details."""

from fastapi import APIRouter

from app.core.config import settings
from app.dependencies.supabase import (
    SupabaseNotConfiguredError,
    get_supabase_client,
)
from app.schemas.health import HealthStatus

router = APIRouter()


@router.get("/", response_model=HealthStatus, summary="API health check")
async def health_check() -> HealthStatus:
    """Return the basic health information for the API."""
    supabase_configured = True
    try:
        get_supabase_client()
    except SupabaseNotConfiguredError:
        supabase_configured = False

    return HealthStatus(
        app=settings.api_v1_prefix.lstrip("/"),
        status="ok",
        environment=settings.environment,
        supabase_configured=supabase_configured,
    )
