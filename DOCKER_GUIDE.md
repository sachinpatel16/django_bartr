# Docker Image Creation Guide for Django Bartr

## Overview
This guide provides step-by-step instructions for creating and managing Docker images for the Django Bartr application.

## Prerequisites
- Docker Desktop installed and running
- Git repository cloned locally
- All project files present

## Step-by-Step Process

### Step 1: Verify Docker Installation
```bash
docker --version
docker ps
```

### Step 2: Navigate to Project Directory
```bash
cd /path/to/django_bartr
```

### Step 3: Create .dockerignore File (Optional but Recommended)
A `.dockerignore` file has been created to exclude unnecessary files from the build context.

### Step 4: Build Docker Image

#### Option A: Using docker-compose (Recommended)
```bash
docker-compose build
```

#### Option B: Using Docker directly
```bash
docker build -t django-bartr:latest .
```

### Step 5: Verify Built Images
```bash
docker images django-bartr
```

### Step 6: Tag Your Image (Optional)
```bash
docker tag <image-id> django-bartr:latest
docker tag <image-id> django-bartr:v1.0.0
```

### Step 7: Run Your Application

#### Using docker-compose (Recommended for development)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

#### Using Docker directly
```bash
# Run the web application
docker run -d -p 8080:8080 --name django-bartr-web django-bartr:latest

# Run with environment variables
docker run -d -p 8080:8080 \
  -e DJANGO_SETTINGS_MODULE=config.settings.production \
  -e DB_HOST=your-db-host \
  --name django-bartr-web \
  django-bartr:latest
```

## Docker Compose Services

The application includes the following services:

1. **web** - Django application server (Gunicorn)
2. **db** - PostgreSQL database
3. **redis** - Redis for Celery
4. **celery** - Celery worker
5. **celery-beat** - Celery beat scheduler
6. **nginx** - Reverse proxy

## Useful Commands

### View Running Containers
```bash
docker-compose ps
docker ps
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web
docker-compose logs db

# Follow logs
docker-compose logs -f web
```

### Execute Commands in Running Container
```bash
# Django management commands
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic

# Shell access
docker-compose exec web bash
```

### Stop and Remove
```bash
# Stop services
docker-compose stop

# Stop and remove containers, networks
docker-compose down

# Stop and remove everything including volumes
docker-compose down -v
```

## Image Management

### List Images
```bash
docker images
docker images django-bartr
```

### Remove Images
```bash
# Remove specific image
docker rmi django-bartr:latest

# Remove all unused images
docker image prune -a
```

### Push to Registry (Optional)
```bash
# Tag for registry
docker tag django-bartr:latest your-registry/django-bartr:latest

# Push to registry
docker push your-registry/django-bartr:latest
```

## Environment Variables

Create a `.env` file in your project root with the following variables:

```env
# Django Settings
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-secret-key
DEBUG=False

# Database
DB_HOST=db
DB_PORT=5432
DB_NAME=bartr
DB_USER=postgres
DB_PASSWORD=dwij9143

# Redis/Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# AWS S3 (if using)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=your-region
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using the port
   netstat -ano | findstr :8080
   
   # Kill the process or change port in docker-compose.yml
   ```

2. **Permission denied**
   ```bash
   # Run Docker commands with administrator privileges
   ```

3. **Build fails**
   ```bash
   # Clean build cache
   docker-compose build --no-cache
   ```

4. **Database connection issues**
   ```bash
   # Check if database is running
   docker-compose ps db
   
   # Check database logs
   docker-compose logs db
   ```

### Health Checks
The application includes health checks. Check status with:
```bash
docker-compose ps
```

## Production Deployment

For production deployment:

1. Use production settings
2. Set up proper environment variables
3. Use external database and Redis
4. Configure SSL/TLS
5. Set up monitoring and logging
6. Use Docker Swarm or Kubernetes for orchestration

## File Structure
```
django_bartr/
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Multi-service orchestration
├── .dockerignore          # Files to exclude from build
├── requirements.txt       # Python dependencies
├── config/               # Django settings
├── freelancing/          # Django apps
├── manage.py            # Django management
└── nginx.conf           # Nginx configuration
```

## Next Steps

1. Set up CI/CD pipeline
2. Configure monitoring and logging
3. Set up backup strategies
4. Implement security best practices
5. Configure auto-scaling

---

**Note**: This guide assumes you're running on Windows. Commands may vary slightly on other operating systems. 