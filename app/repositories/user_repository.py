"""
User repository implementation.
Extends BaseRepository with user-specific query methods.
"""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """
    User repository with specific query methods.
    Extends BaseRepository to provide user-specific operations.
    """
    
    def __init__(self, db: Session):
        """
        Initialize user repository.
        
        Args:
            db: Database session
        """
        super().__init__(User, db)
    
    def get_by_uuid(self, uuid: str) -> Optional[User]:
        """
        Get user by UUID.
        
        Args:
            uuid: User UUID
            
        Returns:
            User instance or None if not found
        """
        try:
            return self.db.query(User).filter(User.uuid == uuid).first()
        except Exception as e:
            logger.error(f"Error getting user by UUID {uuid}: {e}")
            raise
    
    def get_by_first_name(self, first_name: str) -> List[User]:
        """
        Get users by first name.
        
        Args:
            first_name: First name to search for
            
        Returns:
            List of users with matching first name
        """
        try:
            return self.db.query(User).filter(
                User.first_name.ilike(f"%{first_name}%")
            ).all()
        except Exception as e:
            logger.error(f"Error getting users by first name {first_name}: {e}")
            raise
    
    def get_by_last_name(self, last_name: str) -> List[User]:
        """
        Get users by last name.
        
        Args:
            last_name: Last name to search for
            
        Returns:
            List of users with matching last name
        """
        try:
            return self.db.query(User).filter(
                User.last_name.ilike(f"%{last_name}%")
            ).all()
        except Exception as e:
            logger.error(f"Error getting users by last name {last_name}: {e}")
            raise
    
    def search_by_name(self, name_query: str) -> List[User]:
        """
        Search users by first name or last name.
        
        Args:
            name_query: Name to search for (searches both first and last name)
            
        Returns:
            List of users matching the name query
        """
        try:
            return self.db.query(User).filter(
                or_(
                    User.first_name.ilike(f"%{name_query}%"),
                    User.last_name.ilike(f"%{name_query}%")
                )
            ).all()
        except Exception as e:
            logger.error(f"Error searching users by name {name_query}: {e}")
            raise
    
    def get_by_full_name(self, first_name: str, last_name: str) -> Optional[User]:
        """
        Get user by exact first and last name match.
        
        Args:
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            User instance or None if not found
        """
        try:
            return self.db.query(User).filter(
                User.first_name == first_name,
                User.last_name == last_name
            ).first()
        except Exception as e:
            logger.error(f"Error getting user by full name {first_name} {last_name}: {e}")
            raise
    
    def user_exists_by_name(self, first_name: str, last_name: str) -> bool:
        """
        Check if a user exists with the given first and last name.
        
        Args:
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            True if user exists, False otherwise
        """
        try:
            return self.db.query(User).filter(
                User.first_name == first_name,
                User.last_name == last_name
            ).first() is not None
        except Exception as e:
            logger.error(f"Error checking user existence by name {first_name} {last_name}: {e}")
            raise 