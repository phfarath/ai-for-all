"""FastAPI entrypoint for the AI learning platform."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.core.config import settings

app = FastAPI(
    title="AI Learning Platform API",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint returning a welcome message."""
    return {
        "message": "Welcome to the AI Learning Platform API",
        "docs": "/docs",
        "health": f"{settings.api_v1_prefix}/health",
    }
