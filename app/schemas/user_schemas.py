"""
User Pydantic schemas for request/response validation.
Defines data structures for user operations.
"""
from typing import Optional
from pydantic import BaseModel, Field, validator


class UserCreateSchema(BaseModel):
    """
    Schema for creating a new user.
    
    Fields:
        first_name: User's first name (required)
        last_name: User's last name (required)
    """
    
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User's first name"
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User's last name"
    )
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        """Validate that names are not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError('Name cannot be empty or just whitespace')
        return v.strip()
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe"
            }
        }


class UserOutSchema(BaseModel):
    """
    Schema for user output/response.
    
    Fields:
        uuid: User's unique identifier
        first_name: User's first name
        last_name: User's last name
    """
    
    uuid: str = Field(..., description="User's unique identifier")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "uuid": "123e4567-e89b-12d3-a456-426614174000",
                "first_name": "John",
                "last_name": "Doe"
            }
        }


class UserUpdateSchema(BaseModel):
    """
    Schema for updating user information.
    All fields are optional for partial updates.
    
    Fields:
        first_name: User's first name (optional)
        last_name: User's last name (optional)
    """
    
    first_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="User's first name"
    )
    last_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="User's last name"
    )
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        """Validate that names are not empty or just whitespace if provided."""
        if v is not None and (not v or not v.strip()):
            raise ValueError('Name cannot be empty or just whitespace')
        return v.strip() if v else v
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "first_name": "Jane",
                "last_name": "Smith"
            }
        }


class UserSearchSchema(BaseModel):
    """
    Schema for user search parameters.
    
    Fields:
        query: Search query for name
        first_name: Filter by first name
        last_name: Filter by last name
    """
    
    query: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Search query for user names"
    )
    first_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Filter by first name"
    )
    last_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Filter by last name"
    )
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "query": "John",
                "first_name": "John",
                "last_name": "Doe"
            }
        } 