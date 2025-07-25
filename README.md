# Media Generation API

A robust, asynchronous microservice for media generation using the Replicate API. This project demonstrates best practices in Python backend architecture with FastAPI, Celery, and async processing.

## 🏗️ Architecture Overview

- **FastAPI**: High-performance async web framework for API endpoints
- **Celery**: Distributed task queue for background media generation
- **Redis**: Message broker and result backend for Celery
- **Postgres**: Primary database for job metadata and persistence
- **Tortoise ORM**: Async ORM for database operations
- **Docker**: Containerized deployment with docker-compose

## 📋 Features

### Core Functionality
- ✅ **Async Media Generation**: POST `/api/v1/generate` endpoint for job creation
- ✅ **Job Status Tracking**: GET `/api/v1/status/{job_id}` for real-time status updates
- ✅ **Retry Logic**: Exponential backoff with configurable retry attempts
- ✅ **Error Handling**: Comprehensive error tracking and recovery
- ✅ **Storage Options**: Support for local filesystem and S3-compatible storage

### Technical Excellence
- ✅ **Clean Architecture**: Separation of concerns with services, models, and routers
- ✅ **Typed Pydantic Models**: Full request/response validation
- ✅ **Async Everything**: All I/O operations are async-compatible
- ✅ **Docker Support**: Complete containerized setup
- ✅ **Health Monitoring**: Built-in health checks and Celery monitoring
- ✅ **Configuration Management**: Environment-based configuration

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- Replicate API token (optional, mock implementation available)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd media-generation-api

# Quick setup with Makefile
make setup

# Or manual setup
cp .env-example .env
mkdir -p storage/media

# Edit .env and add your Replicate API token
# REPLICATE_API_TOKEN=r8_your_token_here
```

### 2. Docker Deployment (Recommended)
```bash
# Start all services
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f celery_worker
```

### 3. Local Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start Postgres and Redis (via Docker)
docker-compose up -d postgres redis

# Initialize database
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"

# Start FastAPI application
python scripts/run_dev.py

# In another terminal, start Celery worker
python scripts/start_worker.py
```

## 📊 API Usage

### Generate Media
```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over mountains",
    "parameters": {
      "width": 1024,
      "height": 1024,
      "num_inference_steps": 50
    }
  }'
```

**Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "pending",
  "message": "Job created successfully. Use job ID 123e4567-e89b-12d3-a456-426614174000 to check status."
}
```

### Check Job Status
```bash
curl "http://localhost:8000/api/v1/status/123e4567-e89b-12d3-a456-426614174000"
```

**Response (Completed):**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "result_url": "/media/123e4567-e89b-12d3-a456-426614174000.jpg",
  "created_at": "2023-12-01T12:00:00Z",
  "updated_at": "2023-12-01T12:01:30Z",
  "retry_count": 0
}
```

### Get Detailed Job Information
```bash
curl "http://localhost:8000/api/v1/jobs/123e4567-e89b-12d3-a456-426614174000"
```

## 🔧 Configuration

All configuration is managed through environment variables. See `.env-example` for a complete reference.

### Quick Setup
```bash
# Copy example file and customize
cp .env-example .env
# Edit .env with your actual values, especially REPLICATE_API_TOKEN
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | Postgres connection string | `postgres://postgres:password@localhost:5432/media_generation` | Yes |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` | Yes |
| `REPLICATE_API_TOKEN` | Replicate API token | `` | No (uses mock) |
| `STORAGE_TYPE` | Storage backend (`local` or `s3`) | `local` | Yes |
| `LOCAL_STORAGE_PATH` | Local file storage path | `./storage/media` | If local storage |
| `AWS_ACCESS_KEY_ID` | AWS access key | `` | If S3 storage |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | `` | If S3 storage |
| `S3_BUCKET_NAME` | S3 bucket name | `media-generation-bucket` | If S3 storage |
| `MAX_RETRIES` | Maximum retry attempts | `3` | No |
| `RETRY_DELAY` | Base retry delay (seconds) | `60` | No |

### Job Status Flow
```
PENDING → PROCESSING → COMPLETED
    ↓         ↓           ↑
    ↓     RETRYING ──────┘
    ↓         ↓
    └─────→ FAILED
```

## 🏛️ Project Structure

```
├── app/
│   ├── models/           # Database models (Tortoise ORM)
│   ├── schemas/          # Pydantic models for validation
│   ├── services/         # Business logic layer
│   ├── tasks/            # Celery tasks
│   ├── routers/          # FastAPI route handlers
│   ├── utils/            # Utility functions
│   ├── config.py         # Configuration management
│   ├── database.py       # Database initialization
│   └── main.py           # FastAPI application
├── alembic/              # Database migrations
├── scripts/              # Development and deployment scripts
├── docker-compose.yml    # Multi-service Docker setup
├── Dockerfile           # Application container
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔄 Development Workflow

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Monitoring and Debugging

#### Celery Monitoring with Flower
Access Celery task monitoring at: http://localhost:5555

#### API Documentation
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### Health Checks
```bash
# API health
curl http://localhost:8000/api/v1/health

# Celery worker health
celery -A app.tasks.celery_app inspect ping
```

## 🚦 Production Considerations

### Security
- [ ] Configure CORS origins appropriately
- [ ] Set up API authentication/authorization
- [ ] Use secrets management for sensitive configuration
- [ ] Enable HTTPS with proper SSL certificates

### Scaling
- [ ] Configure horizontal scaling for Celery workers
- [ ] Set up load balancing for API instances
- [ ] Implement connection pooling for database
- [ ] Add Redis clustering for high availability

### Monitoring
- [ ] Integrate with APM tools (e.g., Sentry, New Relic)
- [ ] Set up logging aggregation
- [ ] Configure metrics collection and alerting
- [ ] Implement distributed tracing

### Performance
- [ ] Tune Celery worker concurrency
- [ ] Optimize database queries and indexing
- [ ] Implement caching strategies
- [ ] Configure media CDN for static assets

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check if Postgres is running
   docker-compose ps postgres
   
   # Check logs
   docker-compose logs postgres
   ```

2. **Celery Worker Not Processing Tasks**
   ```bash
   # Check worker status
   celery -A app.tasks.celery_app inspect active
   
   # Restart worker
   docker-compose restart celery_worker
   ```

3. **Storage Permission Issues**
   ```bash
   # Fix local storage permissions
   sudo chown -R $USER:$USER ./storage
   chmod -R 755 ./storage
   ```

### Debug Mode
Set `DEBUG=true` in `.env` for verbose logging and auto-reload.

## 📝 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/generate` | Create media generation job |
| GET | `/api/v1/status/{job_id}` | Get job status |
| GET | `/api/v1/jobs/{job_id}` | Get detailed job information |
| GET | `/api/v1/health` | Health check |
| GET | `/docs` | Interactive API documentation |

### Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ using FastAPI, Celery, and modern Python async patterns.** 