"""
Custom middleware for logging requests, responses, and handling exceptions.
Provides correlation ID tracking and structured logging.
"""
import time
import uuid
import json
import traceback
from typing import Callable, Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.logging_config import (
    get_logger, 
    set_correlation_id, 
    clear_correlation_id,
    log_exception
)
from app.config.settings import settings


logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses with correlation IDs.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process HTTP request and response with logging.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler
            
        Returns:
            HTTP response
        """
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        set_correlation_id(correlation_id)
        
        # Start timing
        start_time = time.time()
        
        # Extract request information
        request_info = await self._extract_request_info(request)
        
        # Log incoming request
        logger.info(
            "Incoming request",
            extra={
                'correlation_id': correlation_id,
                'request_info': request_info,
                'event_type': 'request_start'
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Extract response information
            response_info = self._extract_response_info(response, process_time)
            
            # Log outgoing response
            logger.info(
                "Outgoing response",
                extra={
                    'correlation_id': correlation_id,
                    'request_info': request_info,
                    'response_info': response_info,
                    'event_type': 'request_end',
                    'processing_time_seconds': process_time
                }
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as exc:
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log exception with structured information
            log_exception(
                logger,
                "Unhandled exception in request processing",
                exc,
                correlation_id=correlation_id,
                request_info=request_info,
                processing_time_seconds=process_time,
                event_type='request_error'
            )
            
            # Create error response
            error_response = self._create_error_response(exc, correlation_id)
            return error_response
            
        finally:
            # Clear correlation ID from context
            clear_correlation_id()
    
    async def _extract_request_info(self, request: Request) -> Dict[str, Any]:
        """
        Extract relevant information from the request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Dictionary with request information
        """
        # Get client info
        client_host = request.client.host if request.client else "unknown"
        client_port = request.client.port if request.client else 0
        
        # Get headers (excluding sensitive ones)
        headers = dict(request.headers)
        sensitive_headers = ['authorization', 'cookie', 'x-api-key']
        for header in sensitive_headers:
            if header in headers:
                headers[header] = "[REDACTED]"
        
        # Get query parameters
        query_params = dict(request.query_params)
        
        # Get path parameters
        path_params = dict(request.path_params)
        
        # Try to get request body for non-GET requests
        body = None
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    # Try to parse as JSON, fallback to string
                    try:
                        body = json.loads(body_bytes.decode('utf-8'))
                        # Redact sensitive fields
                        if isinstance(body, dict):
                            body = self._redact_sensitive_fields(body)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        body = f"[BINARY_DATA_{len(body_bytes)}_BYTES]"
            except Exception:
                body = "[BODY_READ_ERROR]"
        
        return {
            'method': request.method,
            'url': str(request.url),
            'path': request.url.path,
            'query_params': query_params,
            'path_params': path_params,
            'headers': headers,
            'client': {
                'host': client_host,
                'port': client_port
            },
            'body': body,
            'content_type': request.headers.get('content-type'),
            'user_agent': request.headers.get('user-agent')
        }
    
    def _extract_response_info(self, response: Response, process_time: float) -> Dict[str, Any]:
        """
        Extract relevant information from the response.
        
        Args:
            response: FastAPI response object
            process_time: Request processing time in seconds
            
        Returns:
            Dictionary with response information
        """
        # Get response headers
        headers = dict(response.headers)
        
        return {
            'status_code': response.status_code,
            'headers': headers,
            'content_type': response.headers.get('content-type'),
            'content_length': response.headers.get('content-length'),
            'processing_time_seconds': round(process_time, 4)
        }
    
    def _redact_sensitive_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redact sensitive fields from request/response data.
        
        Args:
            data: Dictionary to redact
            
        Returns:
            Dictionary with sensitive fields redacted
        """
        sensitive_fields = [
            'password', 'token', 'secret', 'key', 'authorization',
            'credit_card', 'ssn', 'social_security', 'api_key'
        ]
        
        redacted_data = data.copy()
        for field in sensitive_fields:
            if field in redacted_data:
                redacted_data[field] = "[REDACTED]"
        
        return redacted_data
    
    def _create_error_response(self, exc: Exception, correlation_id: str) -> JSONResponse:
        """
        Create a standardized error response.
        
        Args:
            exc: Exception that occurred
            correlation_id: Request correlation ID
            
        Returns:
            JSON error response
        """
        error_detail = {
            'success': False,
            'message': 'Internal server error',
            'correlation_id': correlation_id,
            'status_code': 500
        }
        
        # Include exception details in debug mode
        if settings.debug:
            error_detail['debug'] = {
                'exception_type': type(exc).__name__,
                'exception_message': str(exc),
                'traceback': traceback.format_exc().split('\n')
            }
        
        return JSONResponse(
            status_code=500,
            content=error_detail,
            headers={'X-Correlation-ID': correlation_id}
        )


class ExceptionLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware specifically for logging unhandled exceptions with structured stack traces.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with exception logging.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler
            
        Returns:
            HTTP response
        """
        try:
            return await call_next(request)
        except Exception as exc:
            # Get correlation ID if available
            correlation_id = getattr(request.state, 'correlation_id', 'unknown')
            
            # Log the exception with full context
            log_exception(
                logger,
                f"Unhandled exception in {request.method} {request.url.path}",
                exc,
                correlation_id=correlation_id,
                request_method=request.method,
                request_path=request.url.path,
                request_query=str(request.query_params),
                client_host=request.client.host if request.client else 'unknown',
                event_type='unhandled_exception'
            )
            
            # Re-raise the exception to be handled by other middleware or handlers
            raise 