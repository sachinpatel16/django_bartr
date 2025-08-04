@echo off
setlocal enabledelayedexpansion

echo 🚀 Starting deployment of Django Bartr application...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo ❌ .env file not found in the project root.
    echo Please create a .env file with your configuration values.
    echo See README.md for required environment variables.
    pause
    exit /b 1
)
echo ✅ Using existing .env file for configuration.

REM Stop any running containers
echo 🛑 Stopping any running containers...
docker-compose down

REM Build and start services
echo 🔨 Building and starting services...
docker-compose up -d --build

REM Wait for database to be ready
echo ⏳ Waiting for database to be ready...
timeout /t 30 /nobreak >nul

REM Run database migrations
echo 🗄️ Running database migrations...
docker-compose exec web python manage.py migrate --settings=config.settings.production

REM Create superuser if it doesn't exist
echo 👤 Creating superuser ^(if not exists^)...
docker-compose exec web python manage.py shell --settings=config.settings.production -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(is_superuser=True).exists() else None"

REM Collect static files
echo 📦 Collecting static files...
docker-compose exec web python manage.py collectstatic --noinput --settings=config.settings.production

REM Check if services are healthy
echo 🏥 Checking service health...
timeout /t 10 /nobreak >nul

REM Test health endpoint
curl -f http://localhost:8080/health/ >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Health check failed. Please check the logs:
    docker-compose logs web
) else (
    echo ✅ Application is healthy and running!
    echo 🌐 Access your application at: http://localhost:8080
    echo 🔧 Admin interface: http://localhost:8080/admin
    echo 📚 API Documentation: http://localhost:8080/swagger/
    echo 👤 Admin credentials: admin / admin123
)

echo 🎉 Deployment completed!
echo.
echo 📋 Useful commands:
echo   View logs: docker-compose logs -f
echo   Stop services: docker-compose down
echo   Restart services: docker-compose restart
echo   Access Django shell: docker-compose exec web python manage.py shell
echo   Run management commands: docker-compose exec web python manage.py [command]

pause 