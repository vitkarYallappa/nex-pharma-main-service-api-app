"""
User service layer implementation.
Contains business logic and validation for user operations.
"""
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schemas import UserCreateSchema, UserUpdateSchema

logger = logging.getLogger(__name__)


class UserService:
    """
    User service containing business logic and validation.
    Handles user operations with proper validation and error handling.
    """
    
    def __init__(self, db: Session):
        """
        Initialize user service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.user_repository = UserRepository(db)
    
    def create_user(self, user_data: UserCreateSchema) -> User:
        """
        Create a new user with validation.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user instance
            
        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate business rules
            self._validate_user_data(user_data.first_name, user_data.last_name)
            
            # Check if user already exists with same name
            if self.user_repository.user_exists_by_name(user_data.first_name, user_data.last_name):
                raise ValueError(f"User with name '{user_data.first_name} {user_data.last_name}' already exists")
            
            # Create user
            user_dict = {
                "first_name": user_data.first_name,
                "last_name": user_data.last_name
            }
            
            user = self.user_repository.create(user_dict)
            logger.info(f"Created user: {user.uuid} - {user.full_name}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def get_user_by_uuid(self, uuid: str) -> Optional[User]:
        """
        Get user by UUID.
        
        Args:
            uuid: User UUID
            
        Returns:
            User instance or None if not found
        """
        try:
            if not uuid or not uuid.strip():
                raise ValueError("UUID cannot be empty")
            
            return self.user_repository.get_by_uuid(uuid.strip())
        except Exception as e:
            logger.error(f"Error getting user by UUID {uuid}: {e}")
            raise
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of users
        """
        try:
            if skip < 0:
                skip = 0
            if limit <= 0 or limit > 1000:
                limit = 100
                
            return self.user_repository.get_all(skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            raise
    
    def update_user(self, uuid: str, user_data: UserUpdateSchema) -> Optional[User]:
        """
        Update user information.
        
        Args:
            uuid: User UUID
            user_data: User update data
            
        Returns:
            Updated user instance or None if not found
            
        Raises:
            ValueError: If validation fails
        """
        try:
            if not uuid or not uuid.strip():
                raise ValueError("UUID cannot be empty")
            
            # Get existing user
            existing_user = self.user_repository.get_by_uuid(uuid.strip())
            if not existing_user:
                return None
            
            # Prepare update data
            update_dict = {}
            if user_data.first_name is not None:
                update_dict["first_name"] = user_data.first_name
            if user_data.last_name is not None:
                update_dict["last_name"] = user_data.last_name
            
            # If no updates provided, return existing user
            if not update_dict:
                return existing_user
            
            # Validate business rules for updated data
            first_name = update_dict.get("first_name", existing_user.first_name)
            last_name = update_dict.get("last_name", existing_user.last_name)
            self._validate_user_data(first_name, last_name)
            
            # Check if another user exists with the new name combination
            if (first_name != existing_user.first_name or last_name != existing_user.last_name):
                existing_with_name = self.user_repository.get_by_full_name(first_name, last_name)
                if existing_with_name and existing_with_name.uuid != uuid:
                    raise ValueError(f"Another user with name '{first_name} {last_name}' already exists")
            
            # Update user
            updated_user = self.user_repository.update(uuid, update_dict)
            if updated_user:
                logger.info(f"Updated user: {updated_user.uuid} - {updated_user.full_name}")
            
            return updated_user
            
        except Exception as e:
            logger.error(f"Error updating user {uuid}: {e}")
            raise
    
    def delete_user(self, uuid: str) -> bool:
        """
        Delete user by UUID.
        
        Args:
            uuid: User UUID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            if not uuid or not uuid.strip():
                raise ValueError("UUID cannot be empty")
            
            result = self.user_repository.delete(uuid.strip())
            if result:
                logger.info(f"Deleted user: {uuid}")
            
            return result
        except Exception as e:
            logger.error(f"Error deleting user {uuid}: {e}")
            raise
    
    def search_users(self, query: str) -> List[User]:
        """
        Search users by name.
        
        Args:
            query: Search query
            
        Returns:
            List of matching users
        """
        try:
            if not query or not query.strip():
                return []
            
            return self.user_repository.search_by_name(query.strip())
        except Exception as e:
            logger.error(f"Error searching users with query '{query}': {e}")
            raise
    
    def get_users_by_first_name(self, first_name: str) -> List[User]:
        """
        Get users by first name.
        
        Args:
            first_name: First name to search for
            
        Returns:
            List of users with matching first name
        """
        try:
            if not first_name or not first_name.strip():
                return []
            
            return self.user_repository.get_by_first_name(first_name.strip())
        except Exception as e:
            logger.error(f"Error getting users by first name '{first_name}': {e}")
            raise
    
    def get_users_by_last_name(self, last_name: str) -> List[User]:
        """
        Get users by last name.
        
        Args:
            last_name: Last name to search for
            
        Returns:
            List of users with matching last name
        """
        try:
            if not last_name or not last_name.strip():
                return []
            
            return self.user_repository.get_by_last_name(last_name.strip())
        except Exception as e:
            logger.error(f"Error getting users by last name '{last_name}': {e}")
            raise
    
    def get_user_count(self) -> int:
        """
        Get total number of users.
        
        Returns:
            Total user count
        """
        try:
            return self.user_repository.count()
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            raise
    
    def _validate_user_data(self, first_name: str, last_name: str) -> None:
        """
        Validate user data according to business rules.
        
        Args:
            first_name: User's first name
            last_name: User's last name
            
        Raises:
            ValueError: If validation fails
        """
        if not first_name or not first_name.strip():
            raise ValueError("First name cannot be empty")
        
        if not last_name or not last_name.strip():
            raise ValueError("Last name cannot be empty")
        
        if len(first_name.strip()) > 100:
            raise ValueError("First name cannot exceed 100 characters")
        
        if len(last_name.strip()) > 100:
            raise ValueError("Last name cannot exceed 100 characters") 