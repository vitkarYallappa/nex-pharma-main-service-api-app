"""
User model definition.
Defines the users table with UUID primary key and required name fields.
"""
import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.config.database import Base


class User(Base):
    """
    User model representing the users table.
    
    Fields:
        uuid: Primary key (string UUID, auto-generated)
        first_name: User's first name (required)
        last_name: User's last name (required)
    """
    
    __tablename__ = "users"
    
    uuid = Column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
        doc="Unique identifier for the user"
    )
    
    first_name = Column(
        String(100),
        nullable=False,
        doc="User's first name"
    )
    
    last_name = Column(
        String(100),
        nullable=False,
        doc="User's last name"
    )
    
    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User(uuid='{self.uuid}', name='{self.first_name} {self.last_name}')>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self) -> str:
        """Get the user's full name."""
        return f"{self.first_name} {self.last_name}" 