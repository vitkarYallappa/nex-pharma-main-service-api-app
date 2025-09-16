"""
User controller implementation.
Handles HTTP requests for user operations.
"""
import logging
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.services.user_service import UserService
from app.schemas.user_schemas import UserCreateSchema, UserUpdateSchema, UserOutSchema
from app.utils.response import (
    success_response, error_response, created_response, 
    not_found_response, validation_error_response
)

logger = logging.getLogger(__name__)


class UserController:
    """
    User controller handling HTTP requests for user operations.
    Provides endpoints for creating, retrieving, updating, and deleting users.
    """
    
    def __init__(self, db: Session):
        """
        Initialize user controller.
        
        Args:
            db: Database session
        """
        self.db = db
        self.user_service = UserService(db)
    
    def create_user(self, user_data: UserCreateSchema) -> Dict[str, Any]:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            Response dictionary with created user data
        """
        try:
            # Create user through service
            user = self.user_service.create_user(user_data)
            
            # Convert to output schema
            user_out = UserOutSchema.from_orm(user)
            
            return created_response(
                message="User created successfully",
                data=user_out.dict()
            )
            
        except ValueError as e:
            logger.warning(f"Validation error creating user: {e}")
            return validation_error_response(
                message=str(e)
            )
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return error_response(
                message="Failed to create user",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_user_by_uuid(self, uuid: str) -> Dict[str, Any]:
        """
        Get user by UUID.
        
        Args:
            uuid: User UUID
            
        Returns:
            Response dictionary with user data or not found
        """
        try:
            # Get user through service
            user = self.user_service.get_user_by_uuid(uuid)
            
            if not user:
                return not_found_response(
                    message=f"User with UUID '{uuid}' not found"
                )
            
            # Convert to output schema
            user_out = UserOutSchema.from_orm(user)
            
            return success_response(
                message="User retrieved successfully",
                data=user_out.dict()
            )
            
        except ValueError as e:
            logger.warning(f"Validation error getting user: {e}")
            return validation_error_response(
                message=str(e)
            )
        except Exception as e:
            logger.error(f"Error getting user by UUID {uuid}: {e}")
            return error_response(
                message="Failed to retrieve user",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def list_users(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """
        List users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Response dictionary with list of users
        """
        try:
            # Get users through service
            users = self.user_service.get_all_users(skip=skip, limit=limit)
            total_count = self.user_service.get_user_count()
            
            # Convert to output schemas
            users_out = [UserOutSchema.from_orm(user).dict() for user in users]
            
            return success_response(
                message="Users retrieved successfully",
                data={
                    "users": users_out,
                    "total": total_count,
                    "skip": skip,
                    "limit": limit,
                    "count": len(users_out)
                }
            )
            
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return error_response(
                message="Failed to retrieve users",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update_user(self, uuid: str, user_data: UserUpdateSchema) -> Dict[str, Any]:
        """
        Update user information.
        
        Args:
            uuid: User UUID
            user_data: User update data
            
        Returns:
            Response dictionary with updated user data
        """
        try:
            # Update user through service
            user = self.user_service.update_user(uuid, user_data)
            
            if not user:
                return not_found_response(
                    message=f"User with UUID '{uuid}' not found"
                )
            
            # Convert to output schema
            user_out = UserOutSchema.from_orm(user)
            
            return success_response(
                message="User updated successfully",
                data=user_out.dict()
            )
            
        except ValueError as e:
            logger.warning(f"Validation error updating user: {e}")
            return validation_error_response(
                message=str(e)
            )
        except Exception as e:
            logger.error(f"Error updating user {uuid}: {e}")
            return error_response(
                message="Failed to update user",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete_user(self, uuid: str) -> Dict[str, Any]:
        """
        Delete user by UUID.
        
        Args:
            uuid: User UUID
            
        Returns:
            Response dictionary confirming deletion
        """
        try:
            # Delete user through service
            deleted = self.user_service.delete_user(uuid)
            
            if not deleted:
                return not_found_response(
                    message=f"User with UUID '{uuid}' not found"
                )
            
            return success_response(
                message="User deleted successfully",
                data={"uuid": uuid}
            )
            
        except ValueError as e:
            logger.warning(f"Validation error deleting user: {e}")
            return validation_error_response(
                message=str(e)
            )
        except Exception as e:
            logger.error(f"Error deleting user {uuid}: {e}")
            return error_response(
                message="Failed to delete user",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def search_users(self, query: Optional[str] = None, first_name: Optional[str] = None, 
                    last_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Search users by name.
        
        Args:
            query: General search query
            first_name: Filter by first name
            last_name: Filter by last name
            
        Returns:
            Response dictionary with matching users
        """
        try:
            users = []
            
            if query:
                users = self.user_service.search_users(query)
            elif first_name:
                users = self.user_service.get_users_by_first_name(first_name)
            elif last_name:
                users = self.user_service.get_users_by_last_name(last_name)
            else:
                return validation_error_response(
                    message="At least one search parameter (query, first_name, or last_name) is required"
                )
            
            # Convert to output schemas
            users_out = [UserOutSchema.from_orm(user).dict() for user in users]
            
            return success_response(
                message="User search completed successfully",
                data={
                    "users": users_out,
                    "count": len(users_out),
                    "query": query,
                    "first_name": first_name,
                    "last_name": last_name
                }
            )
            
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return error_response(
                message="Failed to search users",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 