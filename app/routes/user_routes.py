"""
User routes definition.
Defines FastAPI routes for user operations.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers.user_controller import UserController
from app.schemas.user_schemas import UserCreateSchema, UserUpdateSchema

# Create router for user routes
router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("", summary="Create a new user")
def create_user(
    user_data: UserCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new user.
    
    Args:
        user_data: User creation data
        db: Database session
        
    Returns:
        Response with created user data
    """
    controller = UserController(db)
    return controller.create_user(user_data)


@router.get("/{uuid}", summary="Get user by UUID")
def get_user(
    uuid: str,
    db: Session = Depends(get_db)
):
    """
    Get user by UUID.
    
    Args:
        uuid: User UUID
        db: Database session
        
    Returns:
        Response with user data
    """
    controller = UserController(db)
    return controller.get_user_by_uuid(uuid)


@router.get("", summary="List users with pagination")
def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    List users with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        Response with list of users
    """
    controller = UserController(db)
    return controller.list_users(skip=skip, limit=limit)


@router.put("/{uuid}", summary="Update user information")
def update_user(
    uuid: str,
    user_data: UserUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update user information.
    
    Args:
        uuid: User UUID
        user_data: User update data
        db: Database session
        
    Returns:
        Response with updated user data
    """
    controller = UserController(db)
    return controller.update_user(uuid, user_data)


@router.delete("/{uuid}", summary="Delete user")
def delete_user(
    uuid: str,
    db: Session = Depends(get_db)
):
    """
    Delete user by UUID.
    
    Args:
        uuid: User UUID
        db: Database session
        
    Returns:
        Response confirming deletion
    """
    controller = UserController(db)
    return controller.delete_user(uuid)


@router.get("/search/", summary="Search users by name")
def search_users(
    query: Optional[str] = Query(None, description="General search query for user names"),
    first_name: Optional[str] = Query(None, description="Filter by first name"),
    last_name: Optional[str] = Query(None, description="Filter by last name"),
    db: Session = Depends(get_db)
):
    """
    Search users by name.
    
    Args:
        query: General search query
        first_name: Filter by first name
        last_name: Filter by last name
        db: Database session
        
    Returns:
        Response with matching users
    """
    controller = UserController(db)
    return controller.search_users(
        query=query,
        first_name=first_name,
        last_name=last_name
    ) 