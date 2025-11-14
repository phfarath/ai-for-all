"""FastAPI dependencies for API v1 endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_async_session
from app.core.security import decode_access_token
from app.models.user import User

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: AsyncSession = Depends(get_async_session),
) -> Optional[User]:
    """
    Get the current authenticated user from JWT token.
    
    This dependency extracts and validates the JWT token from the
    Authorization header, decodes it, and retrieves the user from
    the database.
    
    Args:
        credentials: HTTP Bearer token credentials from the request.
        session: Async database session.
        
    Returns:
        Optional[User]: The authenticated user if valid token, None otherwise.
        
    Raises:
        HTTPException: 401 if token is invalid or user not found.
        
    Example:
        ```python
        @router.get("/me")
        async def get_me(user: User = Depends(get_current_user)):
            if not user:
                raise HTTPException(status_code=401, detail="Not authenticated")
            return user
        ```
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id_str: Optional[str] = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # In a real implementation, you would query the database:
    # result = await session.execute(select(User).where(User.id == user_id))
    # user = result.scalar_one_or_none()
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found")
    # return user
    
    # For now, return None since we don't have user auth implemented yet
    return None


async def get_current_active_user(
    current_user: Optional[User] = Depends(get_current_user),
) -> User:
    """
    Get the current authenticated and active user.
    
    This dependency ensures the user is authenticated and raises
    an exception if not.
    
    Args:
        current_user: The current user from get_current_user dependency.
        
    Returns:
        User: The authenticated user.
        
    Raises:
        HTTPException: 401 if user is not authenticated.
        
    Example:
        ```python
        @router.get("/protected")
        async def protected_route(user: User = Depends(get_current_active_user)):
            return {"user_id": user.id, "email": user.email}
        ```
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get the current user and verify they have admin role.
    
    Args:
        current_user: The current authenticated user.
        
    Returns:
        User: The admin user.
        
    Raises:
        HTTPException: 403 if user is not an admin.
        
    Example:
        ```python
        @router.delete("/users/{user_id}")
        async def delete_user(
            user_id: UUID,
            admin: User = Depends(get_current_admin_user)
        ):
            # Only admins can delete users
            pass
        ```
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin role required.",
        )
    return current_user
