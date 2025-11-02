"""Supabase client dependency for FastAPI routes."""

from functools import lru_cache

from supabase import Client, create_client

from app.core.config import settings


class SupabaseNotConfiguredError(RuntimeError):
    """Raised when the Supabase configuration is missing."""


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Create and cache a Supabase client instance."""
    if not settings.supabase_url or not settings.supabase_key:
        raise SupabaseNotConfiguredError("Supabase credentials not configured")

    return create_client(settings.supabase_url, settings.supabase_key)
