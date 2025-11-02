"""Health check response schema."""

from pydantic import BaseModel


class HealthStatus(BaseModel):
    """Schema returned by the health endpoint."""

    app: str
    status: str
    environment: str
    supabase_configured: bool
