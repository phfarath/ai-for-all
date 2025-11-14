# Backend Refactoring Guide

## Overview

The backend has been refactored into a **modular monolith** architecture that enables adding new features without major refactoring. The structure separates concerns into logical modules while maintaining a single deployable application.

## New Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app with lifespan events
│   │
│   ├── core/                   # Core infrastructure modules
│   │   ├── __init__.py
│   │   ├── config.py          # Pydantic settings (env vars)
│   │   ├── database.py        # Async SQLModel session factory
│   │   └── security.py        # JWT tokens, password hashing
│   │
│   ├── models/                 # SQLModel ORM models
│   │   ├── __init__.py
│   │   └── user.py            # User, Course, Module, Lesson
│   │
│   ├── schemas/                # Pydantic schemas for API requests/responses
│   │   ├── __init__.py
│   │   └── health.py          # Health check schema
│   │
│   ├── api/                    # API endpoints
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py      # Main v1 router aggregator
│   │       ├── deps.py        # FastAPI dependencies (auth, db)
│   │       └── endpoints/     # Individual endpoint modules
│   │           ├── __init__.py
│   │           └── health.py  # Health check endpoint
│   │
│   ├── services/               # Business logic layer (future)
│   │   └── __init__.py
│   │
│   └── dependencies/           # Legacy dependencies
│       ├── __init__.py
│       └── supabase.py        # Supabase client (backward compat)
│
├── requirements.txt
├── .env.example
└── README.md
```

## Key Components

### 1. Core Module (`app/core/`)

#### `config.py`
- Centralized configuration using `pydantic-settings`
- Environment variable management
- Settings categories:
  - Database (DATABASE_URL)
  - Supabase (SUPABASE_URL, SUPABASE_KEY)
  - API (API_V1_PREFIX, CORS_ORIGINS)
  - Security (SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES)

#### `database.py`
- Async SQLModel session management
- Session factory: `get_async_session()` - FastAPI dependency
- Database lifecycle: `init_db()`, `close_db()`
- Supports both PostgreSQL (asyncpg) and SQLite (aiosqlite)

#### `security.py`
- JWT token creation and validation
- Password hashing with bcrypt
- Functions: `create_access_token()`, `decode_access_token()`, `verify_password()`, `get_password_hash()`

### 2. Models Module (`app/models/`)

All models use **SQLModel** (SQLAlchemy + Pydantic) with **UUID** primary keys.

#### Available Models:
- **User**: Learners and instructors
  - Fields: id, email, name, role, hashed_password, created_at, updated_at
  
- **Course**: Complete learning courses
  - Fields: id, slug, title, locale, description, published, created_at, updated_at
  
- **Module**: Sections within courses
  - Fields: id, course_id, ord, title, summary, created_at, updated_at
  
- **Lesson**: Individual learning content (video, text, quiz, lab)
  - Fields: id, module_id, slug, title, content_type, md_url, video_url, duration_minutes, ord, published, created_at, updated_at

### 3. API Dependencies (`app/api/v1/deps.py`)

FastAPI dependencies for common functionality:

#### `get_async_session()`
Provides async database session for endpoints.

```python
@router.get("/users")
async def list_users(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(User))
    return result.scalars().all()
```

#### `get_current_user()`
Extracts and validates JWT token, returns current user (or None).

```python
@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401)
    return user
```

#### `get_current_active_user()`
Ensures user is authenticated, raises 401 if not.

```python
@router.get("/profile")
async def get_profile(user: User = Depends(get_current_active_user)):
    return {"email": user.email, "name": user.name}
```

#### `get_current_admin_user()`
Ensures user has admin role, raises 403 if not.

```python
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    admin: User = Depends(get_current_admin_user)
):
    # Only admins can delete users
    pass
```

### 4. Application Lifespan (`app/main.py`)

The app now uses a **lifespan context manager** for startup/shutdown:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database tables
    await init_db()
    yield
    # Shutdown: Close database connections
    await close_db()

app = FastAPI(lifespan=lifespan)
```

## How to Add New Features

### Adding a New Model

1. Create or update file in `app/models/`
2. Define model with SQLModel:

```python
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Field, SQLModel

class Enrollment(SQLModel, table=True):
    """User enrollment in a course."""
    
    __tablename__ = "enrollments"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    course_id: UUID = Field(foreign_key="courses.id", nullable=False)
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)
```

3. Import in `app/models/__init__.py`

### Adding a New Endpoint

1. Create new file in `app/api/v1/endpoints/` (e.g., `courses.py`)

```python
"""Course management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session, get_current_user
from app.models import Course, User

router = APIRouter()


@router.get("/", response_model=list[Course])
async def list_courses(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> list[Course]:
    """
    List all published courses.
    
    Returns:
        list[Course]: List of published courses.
    """
    result = await session.execute(
        select(Course).where(Course.published == True)
    )
    return result.scalars().all()
```

2. Register in `app/api/v1/router.py`:

```python
from app.api.v1.endpoints import health, courses

router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(courses.router, prefix="/courses", tags=["courses"])
```

### Adding a Service Layer

For complex business logic, create services in `app/services/`:

```python
# app/services/enrollment.py
"""Enrollment business logic."""

from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Enrollment, User, Course


class EnrollmentService:
    """Service for managing course enrollments."""
    
    @staticmethod
    async def enroll_user(
        session: AsyncSession,
        user_id: UUID,
        course_id: UUID
    ) -> Enrollment:
        """
        Enroll a user in a course.
        
        Args:
            session: Database session.
            user_id: ID of user to enroll.
            course_id: ID of course to enroll in.
            
        Returns:
            Enrollment: The created enrollment.
            
        Raises:
            ValueError: If user or course doesn't exist.
        """
        # Check if user exists
        user = await session.get(User, user_id)
        if not user:
            raise ValueError("User not found")
        
        # Check if course exists and is published
        course = await session.get(Course, course_id)
        if not course or not course.published:
            raise ValueError("Course not found or not published")
        
        # Create enrollment
        enrollment = Enrollment(user_id=user_id, course_id=course_id)
        session.add(enrollment)
        await session.commit()
        await session.refresh(enrollment)
        
        return enrollment
```

Use in endpoints:

```python
from app.services.enrollment import EnrollmentService

@router.post("/courses/{course_id}/enroll")
async def enroll(
    course_id: UUID,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    enrollment = await EnrollmentService.enroll_user(
        session, user.id, course_id
    )
    return enrollment
```

## Database Migrations

For production, use Alembic for migrations:

```bash
# Install Alembic
uv pip install alembic

# Initialize Alembic
alembic init alembic

# Configure alembic.ini to use DATABASE_URL from settings

# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head
```

## Testing

Create tests in a `tests/` directory:

```python
# tests/test_api/test_health.py
import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
```

## Environment Variables

Update `.env` file with:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname

# Or for SQLite (development)
DATABASE_URL=sqlite+aiosqlite:///./app.db

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Supabase (optional)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key
```

## Backward Compatibility

All existing endpoints remain functional:
- ✅ `/` - Root welcome message
- ✅ `/v1/health` - Health check
- ✅ Supabase dependencies still available

## Next Steps

1. **Add Authentication Endpoints**: Login, register, token refresh
2. **Implement Course Endpoints**: CRUD for courses, modules, lessons
3. **Add Enrollment System**: User enrollment and progress tracking
4. **Create LLM Integration**: Tutor chat with quota management
5. **Build Analytics**: User progress, instructor dashboards
6. **Add Search**: Full-text search for courses and lessons

## Benefits of This Architecture

1. **Modularity**: Clear separation of concerns
2. **Scalability**: Easy to add new features
3. **Testability**: Dependencies are injectable
4. **Maintainability**: Code is organized by domain
5. **Type Safety**: Full type hints with SQLModel
6. **Documentation**: Auto-generated OpenAPI docs
7. **Async**: Efficient I/O with async/await
8. **Database Agnostic**: Works with PostgreSQL or SQLite
