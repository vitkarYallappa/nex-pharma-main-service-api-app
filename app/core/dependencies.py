"""
Core dependencies for FastAPI dependency injection.
Provides common dependencies used across the application.
"""
import logging
from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.services.user_service import UserService
from app.services.bedrock_service import BedrockService
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """
    Get user service instance.
    
    Args:
        db: Database session
        
    Returns:
        UserService instance
    """
    return UserService(db)


def get_bedrock_service() -> BedrockService:
    """
    Get Bedrock service instance.
    
    Returns:
        BedrockService instance
    """
    return BedrockService()


def get_storage_service() -> StorageService:
    """
    Get storage service instance.
    
    Returns:
        StorageService instance
    """
    return StorageService()


def validate_uuid(uuid: str) -> str:
    """
    Validate UUID format.
    
    Args:
        uuid: UUID string to validate
        
    Returns:
        Validated UUID string
        
    Raises:
        HTTPException: If UUID format is invalid
    """
    import re
    
    # UUID v4 pattern
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    
    if not uuid or not uuid_pattern.match(uuid):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format"
        )
    
    return uuid


def validate_pagination(skip: int = 0, limit: int = 100) -> tuple[int, int]:
    """
    Validate pagination parameters.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        Tuple of validated (skip, limit)
        
    Raises:
        HTTPException: If pagination parameters are invalid
    """
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skip parameter must be non-negative"
        )
    
    if limit <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit parameter must be positive"
        )
    
    if limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit parameter cannot exceed 1000"
        )
    
    return skip, limit 