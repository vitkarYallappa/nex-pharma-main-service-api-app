"""
Response utilities for consistent API responses.
Provides standardized JSON response format.
"""
from typing import Any, Dict, Optional, Union
from fastapi import status
from fastapi.responses import JSONResponse


def create_response(
    success: bool,
    message: str,
    data: Optional[Any] = None,
    errors: Optional[Dict[str, Any]] = None,
    status_code: int = status.HTTP_200_OK
) -> Dict[str, Any]:
    """
    Create a standardized response dictionary.
    
    Args:
        success: Whether the operation was successful
        message: Response message
        data: Response data (optional)
        errors: Error details (optional)
        status_code: HTTP status code
        
    Returns:
        Standardized response dictionary
    """
    response = {
        "success": success,
        "message": message,
        "status_code": status_code
    }
    
    if data is not None:
        response["data"] = data
    
    if errors is not None:
        response["errors"] = errors
    
    return response


def success_response(
    message: str,
    data: Optional[Any] = None,
    status_code: int = status.HTTP_200_OK
) -> Dict[str, Any]:
    """
    Create a success response.
    
    Args:
        message: Success message
        data: Response data (optional)
        status_code: HTTP status code
        
    Returns:
        Success response dictionary
    """
    return create_response(
        success=True,
        message=message,
        data=data,
        status_code=status_code
    )


def error_response(
    message: str,
    errors: Optional[Dict[str, Any]] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> Dict[str, Any]:
    """
    Create an error response.
    
    Args:
        message: Error message
        errors: Error details (optional)
        status_code: HTTP status code
        
    Returns:
        Error response dictionary
    """
    return create_response(
        success=False,
        message=message,
        errors=errors,
        status_code=status_code
    )


def created_response(
    message: str,
    data: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Create a resource created response.
    
    Args:
        message: Success message
        data: Created resource data
        
    Returns:
        Created response dictionary
    """
    return success_response(
        message=message,
        data=data,
        status_code=status.HTTP_201_CREATED
    )


def not_found_response(
    message: str = "Resource not found"
) -> Dict[str, Any]:
    """
    Create a not found response.
    
    Args:
        message: Not found message
        
    Returns:
        Not found response dictionary
    """
    return error_response(
        message=message,
        status_code=status.HTTP_404_NOT_FOUND
    )


def validation_error_response(
    message: str = "Validation error",
    errors: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a validation error response.
    
    Args:
        message: Validation error message
        errors: Validation error details
        
    Returns:
        Validation error response dictionary
    """
    return error_response(
        message=message,
        errors=errors,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


def internal_error_response(
    message: str = "Internal server error"
) -> Dict[str, Any]:
    """
    Create an internal server error response.
    
    Args:
        message: Error message
        
    Returns:
        Internal error response dictionary
    """
    return error_response(
        message=message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def json_response(
    success: bool,
    message: str,
    data: Optional[Any] = None,
    errors: Optional[Dict[str, Any]] = None,
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """
    Create a FastAPI JSONResponse with standardized format.
    
    Args:
        success: Whether the operation was successful
        message: Response message
        data: Response data (optional)
        errors: Error details (optional)
        status_code: HTTP status code
        
    Returns:
        FastAPI JSONResponse
    """
    response_data = create_response(
        success=success,
        message=message,
        data=data,
        errors=errors,
        status_code=status_code
    )
    
    return JSONResponse(
        content=response_data,
        status_code=status_code
    ) 