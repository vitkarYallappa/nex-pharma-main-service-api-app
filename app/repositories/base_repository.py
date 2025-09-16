"""
Base repository pattern implementation.
Provides generic CRUD operations for all models.
"""
import logging
from typing import Generic, TypeVar, Type, List, Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.config.database import Base

# Type variable for model classes
ModelType = TypeVar("ModelType", bound=Base)

logger = logging.getLogger(__name__)


class BaseRepository(Generic[ModelType]):
    """
    Base repository class providing generic CRUD operations.
    
    Args:
        model: SQLAlchemy model class
        db: Database session
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize repository with model and database session.
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
    
    def get_by_id(self, id_value: Any) -> Optional[ModelType]:
        """
        Get a single record by its primary key.
        
        Args:
            id_value: Primary key value
            
        Returns:
            Model instance or None if not found
        """
        try:
            return self.db.query(self.model).filter(
                self.model.__table__.primary_key.columns[0] == id_value
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} by ID {id_value}: {e}")
            raise
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Get all records with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of model instances
        """
        try:
            return self.db.query(self.model).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all {self.model.__name__}: {e}")
            raise
    
    def create(self, obj_data: Dict[str, Any]) -> ModelType:
        """
        Create a new record.
        
        Args:
            obj_data: Dictionary of field values
            
        Returns:
            Created model instance
        """
        try:
            db_obj = self.model(**obj_data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            logger.info(f"Created {self.model.__name__} with data: {obj_data}")
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            self.db.rollback()
            raise
    
    def update(self, id_value: Any, obj_data: Dict[str, Any]) -> Optional[ModelType]:
        """
        Update an existing record.
        
        Args:
            id_value: Primary key value
            obj_data: Dictionary of field values to update
            
        Returns:
            Updated model instance or None if not found
        """
        try:
            db_obj = self.get_by_id(id_value)
            if not db_obj:
                return None
            
            for field, value in obj_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            self.db.commit()
            self.db.refresh(db_obj)
            logger.info(f"Updated {self.model.__name__} {id_value} with data: {obj_data}")
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error updating {self.model.__name__} {id_value}: {e}")
            self.db.rollback()
            raise
    
    def delete(self, id_value: Any) -> bool:
        """
        Delete a record by its primary key.
        
        Args:
            id_value: Primary key value
            
        Returns:
            True if deleted, False if not found
        """
        try:
            db_obj = self.get_by_id(id_value)
            if not db_obj:
                return False
            
            self.db.delete(db_obj)
            self.db.commit()
            logger.info(f"Deleted {self.model.__name__} {id_value}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting {self.model.__name__} {id_value}: {e}")
            self.db.rollback()
            raise
    
    def count(self) -> int:
        """
        Get total count of records.
        
        Returns:
            Total number of records
        """
        try:
            return self.db.query(self.model).count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {e}")
            raise
    
    def exists(self, id_value: Any) -> bool:
        """
        Check if a record exists by its primary key.
        
        Args:
            id_value: Primary key value
            
        Returns:
            True if exists, False otherwise
        """
        try:
            return self.db.query(self.model).filter(
                self.model.__table__.primary_key.columns[0] == id_value
            ).first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model.__name__} {id_value}: {e}")
            raise 