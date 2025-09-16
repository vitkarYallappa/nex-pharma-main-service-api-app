#!/usr/bin/env python3
"""
Test script to demonstrate structured JSON logging functionality.
Run this script to see examples of all logging features.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.logging_config import (
    setup_logging, 
    get_logger, 
    set_correlation_id, 
    clear_correlation_id,
    log_exception
)
from app.config.settings import settings


def test_basic_logging():
    """Test basic logging functionality."""
    logger = get_logger(__name__)
    
    print("=== Testing Basic Logging ===")
    
    # Test different log levels
    logger.debug("This is a debug message", extra={'test_type': 'basic_logging'})
    logger.info("This is an info message", extra={'test_type': 'basic_logging'})
    logger.warning("This is a warning message", extra={'test_type': 'basic_logging'})
    logger.error("This is an error message", extra={'test_type': 'basic_logging'})
    
    # Test structured logging with extra fields
    logger.info(
        "User action performed",
        extra={
            'test_type': 'structured_logging',
            'user_id': 12345,
            'action': 'login',
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Test Browser)'
        }
    )


def test_correlation_id():
    """Test correlation ID functionality."""
    logger = get_logger(__name__)
    
    print("\n=== Testing Correlation ID ===")
    
    # Set correlation ID
    correlation_id = "test-correlation-123"
    set_correlation_id(correlation_id)
    
    logger.info(
        "Request started",
        extra={
            'test_type': 'correlation_test',
            'event': 'request_start'
        }
    )
    
    logger.info(
        "Processing request",
        extra={
            'test_type': 'correlation_test',
            'event': 'request_processing',
            'step': 'validation'
        }
    )
    
    logger.info(
        "Request completed",
        extra={
            'test_type': 'correlation_test',
            'event': 'request_end'
        }
    )
    
    # Clear correlation ID
    clear_correlation_id()
    
    logger.info(
        "Next request without correlation ID",
        extra={'test_type': 'correlation_test'}
    )


def test_exception_logging():
    """Test exception logging functionality."""
    logger = get_logger(__name__)
    
    print("\n=== Testing Exception Logging ===")
    
    try:
        # Simulate an error
        result = 10 / 0
    except ZeroDivisionError as e:
        log_exception(
            logger,
            "Division by zero error occurred",
            e,
            test_type='exception_logging',
            operation='division',
            numerator=10,
            denominator=0
        )
    
    try:
        # Simulate another error
        data = {"key": "value"}
        result = data["nonexistent_key"]
    except KeyError as e:
        log_exception(
            logger,
            "Key not found in data",
            e,
            test_type='exception_logging',
            operation='key_access',
            available_keys=list(data.keys()),
            requested_key='nonexistent_key'
        )


def test_performance_logging():
    """Test performance and timing logging."""
    import time
    
    logger = get_logger(__name__)
    
    print("\n=== Testing Performance Logging ===")
    
    # Simulate a timed operation
    start_time = time.time()
    
    logger.info(
        "Starting database operation",
        extra={
            'test_type': 'performance_logging',
            'operation': 'database_query',
            'query_type': 'SELECT',
            'table': 'users'
        }
    )
    
    # Simulate work
    time.sleep(0.1)
    
    end_time = time.time()
    duration = end_time - start_time
    
    logger.info(
        "Database operation completed",
        extra={
            'test_type': 'performance_logging',
            'operation': 'database_query',
            'duration_seconds': round(duration, 4),
            'records_processed': 150,
            'cache_hit': True
        }
    )


def test_business_logic_logging():
    """Test business logic logging."""
    logger = get_logger(__name__)
    
    print("\n=== Testing Business Logic Logging ===")
    
    # Simulate business events
    logger.info(
        "User registration initiated",
        extra={
            'test_type': 'business_logic',
            'event': 'user_registration_start',
            'user_email': 'test@example.com',
            'registration_source': 'web_form'
        }
    )
    
    logger.info(
        "Email validation completed",
        extra={
            'test_type': 'business_logic',
            'event': 'email_validation',
            'validation_result': 'success',
            'email_provider': 'example.com'
        }
    )
    
    logger.warning(
        "Password strength below recommended",
        extra={
            'test_type': 'business_logic',
            'event': 'password_validation',
            'strength_score': 3,
            'min_required_score': 4,
            'recommendations': ['add_numbers', 'add_special_chars']
        }
    )
    
    logger.info(
        "User registration completed",
        extra={
            'test_type': 'business_logic',
            'event': 'user_registration_success',
            'user_id': 67890,
            'account_type': 'standard',
            'verification_email_sent': True
        }
    )


def main():
    """Main test function."""
    print(f"Starting logging tests...")
    print(f"Environment: {settings.env}")
    print(f"Debug mode: {settings.debug}")
    print(f"Log level: {settings.effective_log_level}")
    print(f"Log directory: {settings.log_dir}")
    print(f"Log files will be created in: {os.path.abspath(settings.log_dir)}")
    
    # Setup logging
    setup_logging()
    
    # Run tests
    test_basic_logging()
    test_correlation_id()
    test_exception_logging()
    test_performance_logging()
    test_business_logic_logging()
    
    print(f"\n=== Test Complete ===")
    print(f"Check the following log files:")
    print(f"  - {os.path.abspath(settings.log_dir)}/app.log (size-based rotation)")
    print(f"  - {os.path.abspath(settings.log_dir)}/app_timed.log (time-based rotation)")
    print(f"  - {os.path.abspath(settings.log_dir)}/error.log (errors only)")
    print(f"Console output also shows structured JSON logs.")


if __name__ == "__main__":
    main() 