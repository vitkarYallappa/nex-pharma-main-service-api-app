"""
FastAPI main application.
Entry point for the NexPharma API application.
"""
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
from app.utils.logging_config import setup_logging, get_logger

# Setup simple logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting NexPharma API - Environment: {settings.env}")
    
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
    """Handle Pydantic validation errors."""
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
    """Handle ValueError exceptions."""
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
    """Handle general exceptions."""
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
    """Root endpoint."""
    logger.info("Root endpoint accessed")
    
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


# Health check endpoint
@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    logger.info("Health check endpoint accessed")
    
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
    
    logger.info(f"Starting uvicorn server on 0.0.0.0:8000")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.effective_log_level.lower()
    ) 