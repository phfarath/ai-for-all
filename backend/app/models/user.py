"""User and learning content models using SQLModel with UUID primary keys."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    """
    User model representing learners and instructors.
    
    Attributes:
        id: Unique identifier (UUID).
        email: User's email address (unique).
        name: User's display name.
        role: User role (learner, instructor, admin).
        hashed_password: Bcrypt hashed password.
        created_at: Account creation timestamp.
        updated_at: Last update timestamp.
    """
    
    __tablename__ = "users"
    
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    email: str = Field(
        unique=True,
        index=True,
        nullable=False,
        max_length=255,
    )
    name: str = Field(
        nullable=False,
        max_length=255,
    )
    role: str = Field(
        default="learner",
        nullable=False,
        max_length=50,
    )
    hashed_password: Optional[str] = Field(
        default=None,
        max_length=255,
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )


class Course(SQLModel, table=True):
    """
    Course model representing a complete learning course.
    
    Attributes:
        id: Unique identifier (UUID).
        slug: URL-friendly identifier.
        title: Course title.
        locale: Language/locale code (e.g., 'pt-BR', 'en-US').
        description: Course description/summary.
        published: Whether the course is published and visible.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """
    
    __tablename__ = "courses"
    
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    slug: str = Field(
        unique=True,
        index=True,
        nullable=False,
        max_length=255,
    )
    title: str = Field(
        nullable=False,
        max_length=500,
    )
    locale: str = Field(
        default="pt-BR",
        nullable=False,
        max_length=10,
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
    )
    published: bool = Field(
        default=False,
        nullable=False,
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )


class Module(SQLModel, table=True):
    """
    Module model representing a section within a learning path.
    
    Modules contain multiple lessons and are ordered sequentially.
    
    Attributes:
        id: Unique identifier (UUID).
        course_id: Reference to parent course.
        ord: Order/sequence number within the course.
        title: Module title.
        summary: Brief module summary/description.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """
    
    __tablename__ = "modules"
    
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    course_id: UUID = Field(
        foreign_key="courses.id",
        nullable=False,
        index=True,
    )
    ord: int = Field(
        nullable=False,
        description="Order sequence within the course",
    )
    title: str = Field(
        nullable=False,
        max_length=500,
    )
    summary: Optional[str] = Field(
        default=None,
        max_length=2000,
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )


class Lesson(SQLModel, table=True):
    """
    Lesson model representing individual learning content.
    
    Lessons can be various types: video, text, quiz, code lab, etc.
    
    Attributes:
        id: Unique identifier (UUID).
        module_id: Reference to parent module.
        slug: URL-friendly identifier.
        title: Lesson title.
        content_type: Type of lesson (video, text, quiz, lab).
        md_url: URL/path to markdown content.
        video_url: Optional video URL.
        duration_minutes: Estimated duration in minutes.
        ord: Order/sequence number within the module.
        published: Whether the lesson is published.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """
    
    __tablename__ = "lessons"
    
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    module_id: UUID = Field(
        foreign_key="modules.id",
        nullable=False,
        index=True,
    )
    slug: str = Field(
        index=True,
        nullable=False,
        max_length=255,
    )
    title: str = Field(
        nullable=False,
        max_length=500,
    )
    content_type: str = Field(
        default="text",
        nullable=False,
        max_length=50,
        description="Type: video, text, quiz, lab, interactive",
    )
    md_url: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="URL or path to markdown content",
    )
    video_url: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="URL to video content",
    )
    duration_minutes: Optional[int] = Field(
        default=None,
        description="Estimated duration in minutes",
    )
    ord: int = Field(
        nullable=False,
        description="Order sequence within the module",
    )
    published: bool = Field(
        default=False,
        nullable=False,
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )
