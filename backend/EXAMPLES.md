# Code Examples

## Example 1: Simple CRUD Endpoint

Here's how to create a complete CRUD endpoint for courses:

```python
# app/api/v1/endpoints/courses.py
"""Course management endpoints."""

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session, get_current_active_user, get_current_admin_user
from app.models import Course, User

router = APIRouter()


@router.get("/", response_model=list[Course])
async def list_courses(
    session: AsyncSession = Depends(get_async_session),
    published_only: bool = True,
) -> list[Course]:
    """
    List all courses.
    
    Args:
        session: Database session.
        published_only: If True, only return published courses.
        
    Returns:
        list[Course]: List of courses.
    """
    query = select(Course)
    if published_only:
        query = query.where(Course.published == True)
    
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/{course_id}", response_model=Course)
async def get_course(
    course_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> Course:
    """
    Get a course by ID.
    
    Args:
        course_id: The course ID.
        session: Database session.
        
    Returns:
        Course: The requested course.
        
    Raises:
        HTTPException: 404 if course not found.
    """
    course = await session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return course


@router.post("/", response_model=Course, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: Course,
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(get_current_admin_user),
) -> Course:
    """
    Create a new course (admin only).
    
    Args:
        course_data: Course data to create.
        session: Database session.
        admin: Current admin user.
        
    Returns:
        Course: The created course.
    """
    session.add(course_data)
    await session.commit()
    await session.refresh(course_data)
    return course_data


@router.patch("/{course_id}", response_model=Course)
async def update_course(
    course_id: UUID,
    course_update: dict,
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(get_current_admin_user),
) -> Course:
    """
    Update a course (admin only).
    
    Args:
        course_id: The course ID to update.
        course_update: Fields to update.
        session: Database session.
        admin: Current admin user.
        
    Returns:
        Course: The updated course.
        
    Raises:
        HTTPException: 404 if course not found.
    """
    course = await session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    for field, value in course_update.items():
        setattr(course, field, value)
    
    session.add(course)
    await session.commit()
    await session.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(get_current_admin_user),
) -> None:
    """
    Delete a course (admin only).
    
    Args:
        course_id: The course ID to delete.
        session: Database session.
        admin: Current admin user.
        
    Raises:
        HTTPException: 404 if course not found.
    """
    course = await session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    await session.delete(course)
    await session.commit()
```

## Example 2: Authentication Endpoints

```python
# app/schemas/auth.py
"""Authentication schemas."""

from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr
    name: str
    password: str


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User response (without sensitive data)."""
    id: str
    email: str
    name: str
    role: str
```

```python
# app/api/v1/endpoints/auth.py
"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session, get_current_active_user
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models import User
from app.schemas.auth import Token, UserLogin, UserRegister, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """
    Register a new user.
    
    Args:
        user_data: User registration data.
        session: Database session.
        
    Returns:
        User: The created user.
        
    Raises:
        HTTPException: 400 if email already exists.
    """
    # Check if user exists
    result = await session.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=get_password_hash(user_data.password),
        role="learner",
    )
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return user


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """
    Login and get access token.
    
    Args:
        credentials: User login credentials.
        session: Database session.
        
    Returns:
        dict: Access token and type.
        
    Raises:
        HTTPException: 401 if credentials are invalid.
    """
    # Find user
    result = await session.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()
    
    # Verify password
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user information.
    
    Args:
        current_user: The authenticated user.
        
    Returns:
        User: Current user information.
    """
    return current_user
```

## Example 3: Service Layer with Business Logic

```python
# app/services/course_service.py
"""Course service with business logic."""

from uuid import UUID
from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Course, Module, Lesson, User


class CourseService:
    """Business logic for course management."""
    
    @staticmethod
    async def get_course_with_content(
        session: AsyncSession,
        course_id: UUID,
    ) -> dict:
        """
        Get course with all modules and lessons.
        
        Args:
            session: Database session.
            course_id: Course ID.
            
        Returns:
            dict: Course data with nested modules and lessons.
            
        Raises:
            ValueError: If course not found.
        """
        # Get course
        course = await session.get(Course, course_id)
        if not course:
            raise ValueError("Course not found")
        
        # Get modules
        modules_result = await session.execute(
            select(Module)
            .where(Module.course_id == course_id)
            .order_by(Module.ord)
        )
        modules = modules_result.scalars().all()
        
        # Get lessons for each module
        course_data = {
            "id": str(course.id),
            "title": course.title,
            "description": course.description,
            "modules": []
        }
        
        for module in modules:
            lessons_result = await session.execute(
                select(Lesson)
                .where(Lesson.module_id == module.id)
                .order_by(Lesson.ord)
            )
            lessons = lessons_result.scalars().all()
            
            course_data["modules"].append({
                "id": str(module.id),
                "title": module.title,
                "summary": module.summary,
                "lessons": [
                    {
                        "id": str(lesson.id),
                        "title": lesson.title,
                        "content_type": lesson.content_type,
                        "duration_minutes": lesson.duration_minutes,
                    }
                    for lesson in lessons
                ]
            })
        
        return course_data
    
    @staticmethod
    async def calculate_course_duration(
        session: AsyncSession,
        course_id: UUID,
    ) -> int:
        """
        Calculate total duration of a course in minutes.
        
        Args:
            session: Database session.
            course_id: Course ID.
            
        Returns:
            int: Total duration in minutes.
        """
        # Get all modules for the course
        modules_result = await session.execute(
            select(Module).where(Module.course_id == course_id)
        )
        modules = modules_result.scalars().all()
        
        total_duration = 0
        
        for module in modules:
            # Get all lessons for each module
            lessons_result = await session.execute(
                select(Lesson).where(Lesson.module_id == module.id)
            )
            lessons = lessons_result.scalars().all()
            
            # Sum up lesson durations
            for lesson in lessons:
                if lesson.duration_minutes:
                    total_duration += lesson.duration_minutes
        
        return total_duration
```

## Example 4: Using the Service in an Endpoint

```python
# app/api/v1/endpoints/courses.py (extended)

from app.services.course_service import CourseService

@router.get("/{course_id}/full", response_model=dict)
async def get_course_full(
    course_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """
    Get course with all modules and lessons.
    
    Args:
        course_id: Course ID.
        session: Database session.
        
    Returns:
        dict: Complete course structure.
        
    Raises:
        HTTPException: 404 if course not found.
    """
    try:
        course_data = await CourseService.get_course_with_content(
            session, course_id
        )
        
        # Add duration
        duration = await CourseService.calculate_course_duration(
            session, course_id
        )
        course_data["total_duration_minutes"] = duration
        
        return course_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
```

## Example 5: Database Query with Filters

```python
# app/api/v1/endpoints/lessons.py
"""Lesson endpoints with advanced filtering."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.models import Lesson

router = APIRouter()


@router.get("/", response_model=list[Lesson])
async def search_lessons(
    session: AsyncSession = Depends(get_async_session),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    min_duration: Optional[int] = Query(None, description="Minimum duration in minutes"),
    max_duration: Optional[int] = Query(None, description="Maximum duration in minutes"),
    published_only: bool = Query(True, description="Only show published lessons"),
    limit: int = Query(50, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
) -> list[Lesson]:
    """
    Search lessons with filters.
    
    Args:
        session: Database session.
        content_type: Filter by content type (video, text, quiz, lab).
        min_duration: Minimum duration filter.
        max_duration: Maximum duration filter.
        published_only: Only return published lessons.
        limit: Maximum number of results.
        offset: Pagination offset.
        
    Returns:
        list[Lesson]: Filtered lessons.
    """
    query = select(Lesson)
    
    # Apply filters
    if content_type:
        query = query.where(Lesson.content_type == content_type)
    
    if min_duration is not None:
        query = query.where(Lesson.duration_minutes >= min_duration)
    
    if max_duration is not None:
        query = query.where(Lesson.duration_minutes <= max_duration)
    
    if published_only:
        query = query.where(Lesson.published == True)
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    # Execute
    result = await session.execute(query)
    return result.scalars().all()
```

## Example 6: Testing

```python
# tests/test_api/test_courses.py
"""Tests for course endpoints."""

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.main import app
from app.models import Course


@pytest.mark.asyncio
async def test_create_course(async_session: AsyncSession):
    """Test creating a course."""
    course_data = {
        "slug": "python-101",
        "title": "Python 101",
        "locale": "pt-BR",
        "description": "Introduction to Python",
        "published": False,
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v1/courses/",
            json=course_data,
            headers={"Authorization": "Bearer test-admin-token"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["slug"] == "python-101"
        assert data["title"] == "Python 101"


@pytest.mark.asyncio
async def test_list_courses():
    """Test listing courses."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/v1/courses/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
```

## Running These Examples

1. Register the new routers in `app/api/v1/router.py`:

```python
from app.api.v1.endpoints import health, auth, courses, lessons

router = APIRouter()

router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(courses.router, prefix="/courses", tags=["courses"])
router.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
```

2. Start the server:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

3. Visit the docs at `http://localhost:8000/docs` to try the endpoints!
