# NexPharma FastAPI Application

A complete FastAPI project with user management, AI integration (AWS Bedrock), and unified storage (MinIO/S3). Built with clean architecture patterns and production-ready configurations.

## 🏗️ Project Architecture

```
fastapi-app/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config/
│   │   ├── settings.py         # Pydantic settings with environment detection
│   │   └── database.py         # SQLAlchemy configuration
│   ├── models/
│   │   └── user.py            # User model with UUID primary key
│   ├── repositories/
│   │   ├── base_repository.py  # Generic CRUD repository
│   │   └── user_repository.py  # User-specific queries
│   ├── services/
│   │   ├── user_service.py     # User business logic
│   │   ├── bedrock_service.py  # AWS Bedrock AI integration
│   │   └── storage_service.py  # MinIO/S3 unified storage
│   ├── controllers/
│   │   └── user_controller.py  # HTTP request handlers
│   ├── routes/
│   │   ├── api.py             # Main API router
│   │   └── user_routes.py     # User endpoints
│   ├── schemas/
│   │   └── user_schemas.py    # Pydantic request/response models
│   ├── utils/
│   │   ├── response.py        # Standardized JSON responses
│   │   └── storage_config.py  # Storage utilities
│   ├── core/
│   │   └── dependencies.py    # FastAPI dependencies
│   └── seeders/
│       ├── base_seeder.py     # Base seeder class
│       └── user_seeder.py     # User data seeder
├── migrations/                 # Alembic database migrations
├── environments/
│   ├── .env.local             # Local development config
│   └── .env.production        # Production config
├── scripts/
│   ├── run.py                 # Application runner
│   ├── migrate.py             # Database migration manager
│   └── seed.py                # Database seeder
├── docker-compose.local.yml   # Local development stack
└── requirements.txt           # Python dependencies
```

## 🚀 Features

### Core Features
- **User Management**: Complete CRUD operations with UUID primary keys
- **Clean Architecture**: Repository pattern, service layer, and dependency injection
- **Database Migrations**: Alembic integration with environment-specific configs
- **Data Seeding**: Automated database seeding with sample data
- **Standardized Responses**: Consistent JSON response format across all endpoints

### AI Integration
- **AWS Bedrock**: Text generation, embeddings, and sentiment analysis
- **Automatic Credentials**: EC2 IAM role detection for production
- **Multiple Models**: Support for Claude, Titan, and other Bedrock models

### Storage Services
- **Unified Interface**: Single API for both MinIO (local) and S3 (production)
- **File Operations**: Upload, download, delete, and list files
- **Presigned URLs**: Secure file access with expiration
- **Environment Detection**: Automatic MinIO/S3 switching

### Production Ready
- **Environment Configuration**: Separate configs for local/production
- **Docker Support**: Complete containerization with docker-compose
- **Error Handling**: Comprehensive exception handling and logging
- **Health Checks**: Built-in health monitoring endpoints
- **CORS Support**: Configurable cross-origin resource sharing

## 🛠️ Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL
- Docker & Docker Compose (optional)

### Local Development

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd fastapi-app
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb nex_pharma
   
   # Run migrations
   python3 scripts/migrate.py --env local init
   python3 scripts/migrate.py --env local upgrade
   
   # Seed sample data
   python3 scripts/seed.py --env local run user
   ```

3. **Run Application**
   ```bash
   python3 scripts/run.py --env local --reload
   ```

4. **Access API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Docker Development

1. **Start Services**
   ```bash
   docker-compose -f docker-compose.local.yml up -d
   ```

2. **Run Migrations**
   ```bash
   docker-compose -f docker-compose.local.yml exec app python3 scripts/migrate.py --env local init
   docker-compose -f docker-compose.local.yml exec app python3 scripts/migrate.py --env local upgrade
   ```

3. **Seed Data**
   ```bash
   docker-compose -f docker-compose.local.yml exec app python3 scripts/seed.py --env local run user
   ```

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    uuid VARCHAR PRIMARY KEY,  -- Auto-generated UUID
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL
);
```

## 🔌 API Endpoints

### User Management
- `POST /api/users` - Create user
- `GET /api/users` - List users (paginated)
- `GET /api/users/{uuid}` - Get user by UUID
- `PUT /api/users/{uuid}` - Update user
- `DELETE /api/users/{uuid}` - Delete user
- `GET /api/users/search/` - Search users by name

### System
- `GET /` - Root endpoint with API info
- `GET /health` - Health check
- `GET /api/health` - API health check
- `GET /api/info` - API information

### Response Format
All endpoints return standardized JSON responses:
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {...},
  "status_code": 200
}
```

## 🔧 Configuration

### Environment Variables

#### Local Development (.env.local)
```env
ENV=local
DEBUG=true
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nex_pharma
DB_USER=postgres
DB_PASSWORD=postgres
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
STORAGE_BUCKET=nexpharma-storage
```

#### Production (.env.production)
```env
ENV=production
DEBUG=false
DB_HOST=your-rds-endpoint.amazonaws.com
DB_NAME=nex_pharma
DB_USER=postgres
DB_PASSWORD=your_secure_password
AWS_REGION=us-east-1
STORAGE_BUCKET=nexpharma-production-storage
```

## 🚀 Production Deployment

### EC2 Deployment
1. **Setup Environment**
   ```bash
   # Install dependencies
   sudo apt update
   sudo apt install python3-pip postgresql-client
   pip3 install -r requirements.txt
   
   # Configure environment
   export ENV=production
   ```

2. **Database Setup**
   ```bash
   # Run migrations
   python3 scripts/migrate.py --env production upgrade
   
   # Seed initial data
   python3 scripts/seed.py --env production run user
   ```

3. **Run Application**
   ```bash
   python3 scripts/run.py --env production --workers 4
   ```

### AWS Services Integration
- **RDS PostgreSQL**: Managed database service
- **EC2 IAM Roles**: Automatic credential detection
- **S3**: Production file storage
- **Bedrock**: AI/ML services

## 🧪 Scripts Usage

### Application Runner
```bash
# Local development with auto-reload
python3 scripts/run.py --env local --reload

# Production with multiple workers
python3 scripts/run.py --env production --workers 4
```

### Database Migrations
```bash
# Create initial migration
python3 scripts/migrate.py --env local init

# Create new migration
python3 scripts/migrate.py --env local create "Add new table"

# Apply migrations
python3 scripts/migrate.py --env local upgrade

# Rollback migration
python3 scripts/migrate.py --env local downgrade -1
```

### Database Seeding
```bash
# List available seeders
python3 scripts/seed.py list

# Run specific seeder
python3 scripts/seed.py --env local run user

# Run all seeders
python3 scripts/seed.py --env local all

# Clear and reseed
python3 scripts/seed.py --env local --clear run user
```

## 🔍 Development Tools

### API Documentation
- **Swagger UI**: `/docs` (development only)
- **ReDoc**: `/redoc` (development only)

### Database Tools
- **Alembic**: Database migrations and versioning
- **SQLAlchemy**: ORM with async support

### Code Quality
- **Type Hints**: Full type annotation coverage
- **Docstrings**: Comprehensive documentation
- **Error Handling**: Structured exception management
- **Logging**: Configurable logging levels

## 🏢 Architecture Patterns

### Repository Pattern
- **BaseRepository**: Generic CRUD operations
- **UserRepository**: User-specific queries
- **Type Safety**: Generic type support

### Service Layer
- **Business Logic**: Centralized validation and rules
- **Error Handling**: Consistent error management
- **Dependency Injection**: Clean service composition

### Response Standardization
- **Unified Format**: Consistent JSON responses
- **Error Details**: Structured error information
- **Status Codes**: Proper HTTP status usage

## 🔒 Security Features

- **Input Validation**: Pydantic schema validation
- **SQL Injection Protection**: SQLAlchemy ORM
- **CORS Configuration**: Environment-specific settings
- **Error Sanitization**: Production error masking

## 📈 Monitoring & Health

### Health Checks
- **Database Connectivity**: Connection verification
- **Service Availability**: Component status checks
- **Environment Information**: Runtime details

### Logging
- **Structured Logging**: JSON-formatted logs
- **Log Levels**: Environment-specific verbosity
- **Error Tracking**: Exception logging with context

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the logs for error details

---

**Built with ❤️ using FastAPI, SQLAlchemy, and modern Python practices.**
