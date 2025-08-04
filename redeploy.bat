@echo off
echo === Fixing JWT ImportError Issue ===
echo This script will help you redeploy with the fixed requirements.txt

REM Stop any running containers
echo Stopping existing containers...
docker-compose down

REM Remove old images to ensure clean rebuild
echo Removing old images...
docker-compose down --rmi all

REM Rebuild with new requirements
echo Rebuilding with fixed requirements...
docker-compose build --no-cache

REM Start the services
echo Starting services...
docker-compose up -d

echo === Deployment Complete ===
echo Check the logs with: docker-compose logs -f
pause 