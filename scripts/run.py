#!/usr/bin/env python3
"""
Application runner script.
Runs the FastAPI application locally or in production based on environment.
"""
import os
import sys
import argparse
import logging
import uvicorn

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_local():
    """Run application in local development mode."""
    logger.info("Starting application in LOCAL mode")
    logger.info(f"Database URL: {settings.database_url}")
    logger.info(f"Debug mode: {settings.debug}")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info" if settings.debug else "warning",
        access_log=True
    )


def run_production():
    """Run application in production mode."""
    logger.info("Starting application in PRODUCTION mode")
    logger.info(f"Database URL: {settings.database_url}")
    logger.info(f"Debug mode: {settings.debug}")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=False,
        log_level="warning",
        access_log=False,
        workers=int(os.getenv("WORKERS", "4"))
    )


def main():
    """Main function to parse arguments and run application."""
    parser = argparse.ArgumentParser(description="Run FastAPI application")
    parser.add_argument(
        "--env",
        choices=["local", "production"],
        default="local",
        help="Environment to run in (default: local)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of worker processes for production (default: 4)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload (development only)"
    )
    
    args = parser.parse_args()
    
    # Set environment variable
    os.environ["ENV"] = args.env
    
    # Import app after setting environment
    from app.main import app
    
    logger.info(f"Running FastAPI application")
    logger.info(f"Environment: {args.env}")
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    
    if args.env == "production":
        logger.info(f"Workers: {args.workers}")
        uvicorn.run(
            "app.main:app",
            host=args.host,
            port=args.port,
            reload=False,
            log_level="warning",
            access_log=False,
            workers=args.workers
        )
    else:
        logger.info(f"Reload: {args.reload}")
        uvicorn.run(
            "app.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info",
            access_log=True
        )


if __name__ == "__main__":
    main() 