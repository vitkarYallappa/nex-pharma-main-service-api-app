"""
FastAPI main application.
Entry point for the NexPharma API application.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.config.settings import settings
from app.config.database import create_tables
from app.routes.api import api_router
from app.utils.response import error_response, validation_error_response

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting NexPharma API application")
    logger.info(f"Environment: {settings.env}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Create database tables if they don't exist
    try:
        create_tables()
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down NexPharma API application")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FastAPI application for NexPharma with user management, AI integration, and storage services",
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors.
    
    Args:
        request: FastAPI request object
        exc: Validation error exception
        
    Returns:
        JSON response with validation error details
    """
    logger.warning(f"Validation error on {request.url}: {exc}")
    
    errors = {}
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors[field] = error["msg"]
    
    response_data = validation_error_response(
        message="Request validation failed",
        errors=errors
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_data
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """
    Handle ValueError exceptions.
    
    Args:
        request: FastAPI request object
        exc: ValueError exception
        
    Returns:
        JSON response with error details
    """
    logger.warning(f"Value error on {request.url}: {exc}")
    
    response_data = error_response(
        message=str(exc),
        status_code=status.HTTP_400_BAD_REQUEST
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=response_data
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general exceptions.
    
    Args:
        request: FastAPI request object
        exc: Exception
        
    Returns:
        JSON response with error details
    """
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    
    response_data = error_response(
        message="Internal server error" if not settings.debug else str(exc),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_data
    )


# Include API routes
app.include_router(api_router, prefix="/api")


# Root endpoint
@app.get("/", tags=["root"])
def read_root():
    """
    Root endpoint.
    
    Returns:
        Welcome message and API information
    """
    return {
        "success": True,
        "message": f"Welcome to {settings.app_name}",
        "data": {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.env,
            "debug": settings.debug,
            "docs_url": "/docs" if settings.debug else "disabled",
            "api_endpoints": {
                "health": "/api/health",
                "info": "/api/info",
                "users": "/api/users"
            }
        },
        "status_code": 200
    }


# Health check endpoint (also available at root level)
@app.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status response
    """
    return {
        "success": True,
        "message": "API is healthy",
        "data": {
            "status": "healthy",
            "environment": settings.env,
            "version": settings.app_version
        },
        "status_code": 200
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    ) 