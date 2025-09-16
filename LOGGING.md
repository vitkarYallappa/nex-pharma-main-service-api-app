# Structured JSON Logging System

This document describes the comprehensive structured JSON logging system implemented in the NexPharma FastAPI application.

## Features

✅ **Structured JSON Logging** - All logs are formatted as JSON with consistent fields  
✅ **Environment-based Log Levels** - DEBUG for development, INFO for production  
✅ **Dual File Rotation** - Both time-based (hourly) and size-based (5MB) rotation  
✅ **Correlation ID Tracking** - Unique IDs for tracing requests across the application  
✅ **Exception Handling** - Structured logging of unhandled exceptions with stack traces  
✅ **Request/Response Middleware** - Automatic logging of HTTP requests and responses  
✅ **Multiple Log Outputs** - Console and rotating file handlers  
✅ **Retention Policy** - Configurable backup file limits  
✅ **Security** - Automatic redaction of sensitive fields  

## Architecture

### Core Components

1. **`app/utils/logging_config.py`** - Main logging configuration and utilities
2. **`app/utils/middleware.py`** - Request/response logging middleware
3. **`app/config/settings.py`** - Logging configuration settings
4. **`logs/`** - Directory for log files (auto-created)

### Log Files

- **`logs/app.log`** - Main application logs with size-based rotation (5MB)
- **`logs/app_timed.log`** - Time-based rotation logs (hourly)
- **`logs/error.log`** - Error-level logs only
- **Console output** - All logs also output to console in JSON format

## Configuration

### Environment Variables

```bash
# Logging Configuration
LOG_LEVEL=DEBUG              # Log level (DEBUG, INFO, WARNING, ERROR)
LOG_DIR=logs                 # Directory for log files
LOG_MAX_FILE_SIZE_MB=5       # Max file size before rotation (MB)
LOG_MAX_BACKUP_COUNT=10      # Number of backup files to keep
LOG_ROTATION_HOURS=1         # Hours between time-based rotation
```

### Environment-based Defaults

- **Development** (`ENV=local`): DEBUG level logging
- **Production** (`ENV=production`): INFO level logging

## Usage

### Basic Logging

```python
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Basic log levels
logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
```

### Structured Logging

```python
# Add structured data to logs
logger.info(
    "User login successful",
    extra={
        'user_id': 12345,
        'ip_address': '192.168.1.100',
        'login_method': 'email',
        'session_id': 'abc123'
    }
)
```

### Exception Logging

```python
from app.utils.logging_config import log_exception

try:
    # Some operation
    pass
except Exception as e:
    log_exception(
        logger,
        "Operation failed",
        e,
        user_id=12345,
        operation='data_processing'
    )
```

### Correlation ID Tracking

```python
from app.utils.logging_config import set_correlation_id, clear_correlation_id

# Set correlation ID for request tracking
correlation_id = "req-123-456"
set_correlation_id(correlation_id)

logger.info("Processing request")  # Will include correlation_id

# Clear when done
clear_correlation_id()
```

## Log Format

All logs follow this JSON structure:

```json
{
  "timestamp": "2023-12-07T10:30:45.123Z",
  "level": "INFO",
  "logger": "app.controllers.user_controller",
  "message": "User created successfully",
  "module": "user_controller",
  "function": "create_user",
  "line_number": 45,
  "process_id": 1234,
  "thread_id": 5678,
  "correlation_id": "req-abc-123",
  "user_id": 12345,
  "operation": "user_creation"
}
```

### Exception Logs Include

```json
{
  "timestamp": "2023-12-07T10:30:45.123Z",
  "level": "ERROR",
  "logger": "app.controllers.user_controller",
  "message": "Database connection failed",
  "exception": {
    "type": "ConnectionError",
    "message": "Unable to connect to database",
    "traceback": ["...", "..."]
  },
  "correlation_id": "req-abc-123"
}
```

## Middleware Features

### Request Logging

Automatically logs:
- HTTP method and URL
- Headers (sensitive headers redacted)
- Query parameters
- Request body (sensitive fields redacted)
- Client IP and port
- Processing time

### Response Logging

Automatically logs:
- Status code
- Response headers
- Content type and length
- Processing time

### Correlation ID Headers

Each response includes an `X-Correlation-ID` header for client-side tracking.

## Security Features

### Automatic Redaction

Sensitive fields are automatically redacted in logs:
- `password`
- `token`
- `secret`
- `key`
- `authorization`
- `credit_card`
- `ssn`
- `api_key`

### Header Redaction

Sensitive headers are redacted:
- `authorization`
- `cookie`
- `x-api-key`

## File Rotation

### Size-based Rotation
- Rotates when files reach 5MB (configurable)
- Keeps 10 backup files (configurable)
- Format: `app.log`, `app.log.1`, `app.log.2`, etc.

### Time-based Rotation
- Rotates every hour (configurable)
- Keeps 240 backup files (10 days × 24 hours)
- Format: `app_timed.log.2023-12-07_14`

## Testing

Run the logging test script to see all features in action:

```bash
python scripts/test_logging.py
```

This will demonstrate:
- Basic logging at different levels
- Structured logging with extra fields
- Correlation ID tracking
- Exception logging with stack traces
- Performance timing logs
- Business logic event logging

## Integration

### In Controllers

```python
from app.utils.logging_config import get_logger, log_exception

logger = get_logger(__name__)

class UserController:
    async def create_user(self, user_data: dict):
        logger.info(
            "Creating new user",
            extra={
                'operation': 'user_creation',
                'email': user_data.get('email'),
                'registration_source': 'api'
            }
        )
        
        try:
            # Create user logic
            user = await self.user_service.create(user_data)
            
            logger.info(
                "User created successfully",
                extra={
                    'user_id': user.id,
                    'operation': 'user_creation'
                }
            )
            
            return user
            
        except Exception as e:
            log_exception(
                logger,
                "Failed to create user",
                e,
                operation='user_creation',
                email=user_data.get('email')
            )
            raise
```

### In Services

```python
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

class UserService:
    async def authenticate(self, email: str, password: str):
        logger.info(
            "Authentication attempt",
            extra={
                'operation': 'authentication',
                'email': email,
                'method': 'email_password'
            }
        )
        
        # Authentication logic
        
        if success:
            logger.info(
                "Authentication successful",
                extra={
                    'operation': 'authentication',
                    'user_id': user.id,
                    'email': email
                }
            )
        else:
            logger.warning(
                "Authentication failed",
                extra={
                    'operation': 'authentication',
                    'email': email,
                    'reason': 'invalid_credentials'
                }
            )
```

## Monitoring and Alerting

The structured JSON format makes it easy to:

1. **Parse logs** with tools like ELK Stack, Fluentd, or Logstash
2. **Create alerts** based on error rates or specific events
3. **Build dashboards** for application monitoring
4. **Trace requests** using correlation IDs
5. **Analyze performance** using timing data

## Best Practices

1. **Use appropriate log levels**
   - DEBUG: Detailed debugging information
   - INFO: General application flow
   - WARNING: Unusual but handled situations
   - ERROR: Error conditions

2. **Include context in extra fields**
   - User IDs, operation names, relevant data
   - Use consistent field names across the application

3. **Use correlation IDs for request tracing**
   - Set at the beginning of request processing
   - Include in all related log entries

4. **Log business events**
   - User registrations, logins, important actions
   - Include relevant business context

5. **Don't log sensitive data**
   - The system automatically redacts known sensitive fields
   - Be careful with custom fields that might contain sensitive data

## Troubleshooting

### Log Files Not Created

- Check that the `logs/` directory exists and is writable
- Verify LOG_DIR setting in environment variables
- Check file system permissions

### Logs Not Rotating

- Verify LOG_MAX_FILE_SIZE_MB and LOG_ROTATION_HOURS settings
- Check disk space availability
- Ensure proper file permissions for rotation

### Missing Correlation IDs

- Ensure LoggingMiddleware is properly configured
- Check that correlation IDs are set in request processing
- Verify middleware order in main.py

### Performance Impact

- Structured logging has minimal performance impact
- File I/O is handled asynchronously where possible
- Consider adjusting log levels in production if needed 