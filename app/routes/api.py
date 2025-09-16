"""
Main API router.
Includes all route modules and provides API versioning.
"""
from fastapi import APIRouter

from app.routes.user_routes import router as user_router

# Create main API router
api_router = APIRouter()

# Include route modules
api_router.include_router(user_router)

# Health check endpoint
@api_router.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status response
    """
    return {
        "success": True,
        "message": "API is healthy",
        "status_code": 200
    }


# API info endpoint
@api_router.get("/info", tags=["info"])
def api_info():
    """
    API information endpoint.
    
    Returns:
        API information
    """
    return {
        "success": True,
        "message": "NexPharma API",
        "data": {
            "name": "NexPharma API",
            "version": "1.0.0",
            "description": "FastAPI application for NexPharma with user management",
            "endpoints": {
                "users": "/api/users",
                "health": "/api/health",
                "info": "/api/info"
            }
        },
        "status_code": 200
    } 