"""
Base seeder class for database seeding.
Provides common functionality for all seeders.
"""
import logging
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

from app.config.database import SessionLocal

logger = logging.getLogger(__name__)


class BaseSeeder(ABC):
    """
    Abstract base class for database seeders.
    Provides common functionality and interface for all seeders.
    """
    
    def __init__(self):
        """Initialize base seeder."""
        self.db: Session = None
    
    def get_db_session(self) -> Session:
        """
        Get database session.
        
        Returns:
            Database session
        """
        if not self.db:
            self.db = SessionLocal()
        return self.db
    
    def close_db_session(self) -> None:
        """Close database session."""
        if self.db:
            self.db.close()
            self.db = None
    
    @abstractmethod
    def seed(self) -> None:
        """
        Abstract method to implement seeding logic.
        Must be implemented by concrete seeder classes.
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """
        Abstract method to implement clearing logic.
        Must be implemented by concrete seeder classes.
        """
        pass
    
    def run(self, clear_first: bool = False) -> None:
        """
        Run the seeder.
        
        Args:
            clear_first: Whether to clear existing data first
        """
        try:
            self.get_db_session()
            
            if clear_first:
                logger.info(f"Clearing data for {self.__class__.__name__}")
                self.clear()
            
            logger.info(f"Running seeder: {self.__class__.__name__}")
            self.seed()
            
            logger.info(f"Seeder {self.__class__.__name__} completed successfully")
            
        except Exception as e:
            logger.error(f"Error running seeder {self.__class__.__name__}: {e}")
            if self.db:
                self.db.rollback()
            raise
        finally:
            self.close_db_session()
    
    def log_info(self, message: str) -> None:
        """
        Log info message with seeder name.
        
        Args:
            message: Message to log
        """
        logger.info(f"[{self.__class__.__name__}] {message}")
    
    def log_warning(self, message: str) -> None:
        """
        Log warning message with seeder name.
        
        Args:
            message: Message to log
        """
        logger.warning(f"[{self.__class__.__name__}] {message}")
    
    def log_error(self, message: str) -> None:
        """
        Log error message with seeder name.
        
        Args:
            message: Message to log
        """
        logger.error(f"[{self.__class__.__name__}] {message}")
    
    def record_exists(self, model_class, **filters) -> bool:
        """
        Check if a record exists with given filters.
        
        Args:
            model_class: SQLAlchemy model class
            **filters: Filter conditions
            
        Returns:
            True if record exists, False otherwise
        """
        try:
            return self.db.query(model_class).filter_by(**filters).first() is not None
        except Exception as e:
            self.log_error(f"Error checking record existence: {e}")
            return False
    
    def count_records(self, model_class) -> int:
        """
        Count records in a table.
        
        Args:
            model_class: SQLAlchemy model class
            
        Returns:
            Number of records
        """
        try:
            return self.db.query(model_class).count()
        except Exception as e:
            self.log_error(f"Error counting records: {e}")
            return 0 