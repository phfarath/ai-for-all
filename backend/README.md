# AI Learning Platform Backend

This directory contains the FastAPI application that serves the AI Learning Platform API (`/v1`).

## Architecture

The backend follows a **modular monolith** architecture that separates concerns while maintaining a single deployable application. This makes it easy to add new features without major refactoring.

### Structure

```
app/
├── main.py              # FastAPI application with lifespan events
├── core/                # Core infrastructure
│   ├── config.py       # Pydantic settings (env vars)
│   ├── database.py     # Async SQLModel session factory
│   └── security.py     # JWT tokens, password hashing
├── models/              # SQLModel ORM models (UUID PKs)
│   └── user.py         # User, Course, Module, Lesson
├── schemas/             # Pydantic schemas for API
│   └── health.py       # API request/response schemas
├── api/v1/              # API v1 endpoints
│   ├── router.py       # Main router aggregator
│   ├── deps.py         # FastAPI dependencies
│   └── endpoints/      # Individual endpoint modules
│       └── health.py   # Health check endpoint
└── services/            # Business logic layer (future)
```

## Features

- ✅ **Async SQLModel**: Type-safe ORM with Pydantic validation
- ✅ **UUID Primary Keys**: All models use UUID for better distribution
- ✅ **JWT Authentication**: Token-based auth with bcrypt password hashing
- ✅ **Database Agnostic**: Works with PostgreSQL (asyncpg) or SQLite (aiosqlite)
- ✅ **FastAPI Dependencies**: Reusable auth and database session injection
- ✅ **Lifespan Events**: Proper database initialization and cleanup
- ✅ **Modular Structure**: Easy to add new endpoints and features
- ✅ **Type Safety**: Full type hints throughout
- ✅ **Auto Documentation**: OpenAPI/Swagger docs at `/docs`

## Getting Started

1. Install dependencies using uv (faster) or pip:

   ```bash
   cd backend
   
   # Using uv (recommended)
   source .venv/bin/activate
   uv pip install -r requirements.txt
   
   # Or using pip
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Configure environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. Run the development server:

   ```bash
   uvicorn app.main:app --reload
   ```

4. Visit the API:
   - API Root: `http://localhost:8000/`
   - Health Check: `http://localhost:8000/v1/health`
   - API Docs: `http://localhost:8000/docs`

## Available Models

All models use **UUID** primary keys and include timestamps:

- **User**: Users (learners, instructors, admins)
- **Course**: Complete learning courses
- **Module**: Sections within courses (ordered)
- **Lesson**: Individual content (video, text, quiz, lab)

## Development Guides

- **[REFACTOR_GUIDE.md](./REFACTOR_GUIDE.md)**: Complete architecture documentation
- **[EXAMPLES.md](./EXAMPLES.md)**: Code examples for common tasks

## Adding New Features

### 1. Add a New Model

Create or update `app/models/*.py`:

```python
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Field, SQLModel

class Progress(SQLModel, table=True):
    """User progress tracking."""
    __tablename__ = "progress"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    lesson_id: UUID = Field(foreign_key="lessons.id")
    score: int = Field(ge=0, le=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2. Add a New Endpoint

Create `app/api/v1/endpoints/your_feature.py`:

```python
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.api.v1.deps import get_async_session, get_current_user

router = APIRouter()

@router.get("/items")
async def list_items(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user)
):
    """List items with auth and database."""
    # Your logic here
    pass
```

Register in `app/api/v1/router.py`:

```python
from app.api.v1.endpoints import your_feature
router.include_router(your_feature.router, prefix="/items", tags=["items"])
```

### 3. Add Business Logic Service

Create `app/services/your_service.py`:

```python
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models import YourModel

class YourService:
    """Business logic for your feature."""
    
    @staticmethod
    async def do_something(session: AsyncSession, data: dict):
        """Docstring explaining what this does."""
        # Complex business logic here
        pass
```

## Environment Variables

See `.env.example` for all available settings:

- **DATABASE_URL**: Database connection (SQLite or PostgreSQL)
- **SECRET_KEY**: JWT secret (change in production!)
- **SUPABASE_***: Optional Supabase integration
- **CORS_ORIGINS**: Allowed CORS origins

## Testing

The health endpoint confirms everything is working:

```bash
curl http://localhost:8000/v1/health
# {"app":"v1","status":"ok","environment":"development","supabase_configured":false}
```

## Tech Stack

- **FastAPI**: Modern async web framework
- **SQLModel**: SQLAlchemy + Pydantic ORM
- **Pydantic**: Data validation
- **python-jose**: JWT tokens
- **bcrypt**: Password hashing
- **asyncpg**: PostgreSQL async driver
- **aiosqlite**: SQLite async driver

## Next Steps

1. Implement authentication endpoints (register, login)
2. Add course CRUD endpoints
3. Implement enrollment system
4. Add progress tracking
5. Integrate LLM for tutor chat
6. Build analytics endpoints

See **[EXAMPLES.md](./EXAMPLES.md)** for detailed code examples!
