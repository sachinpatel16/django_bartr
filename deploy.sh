#!/bin/bash

# 🚀 Django Bartr Deployment Script
# This script helps you push your Docker image and deploy it

set -e  # Exit on any error

echo "🚀 Starting Django Bartr Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="sachinpatel016/django_bartr"
TAG=${1:-latest}
VERSION=${2:-v1.0.0}

echo -e "${BLUE}📋 Configuration:${NC}"
echo "  Image: $IMAGE_NAME"
echo "  Tag: $TAG"
echo "  Version: $VERSION"
echo ""

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: Build the image
print_status "Building Docker image..."
docker-compose build

# Step 2: Tag the image
print_status "Tagging Docker image..."
docker tag django-bartr:latest $IMAGE_NAME:$TAG
docker tag django-bartr:latest $IMAGE_NAME:$VERSION

# Step 3: Login to Docker Hub
print_status "Logging in to Docker Hub..."
docker login

# Step 4: Push the image
print_status "Pushing image to Docker Hub..."
docker push $IMAGE_NAME:$TAG
docker push $IMAGE_NAME:$VERSION

print_status "Image pushed successfully!"

# Step 5: Show deployment options
echo ""
echo -e "${BLUE}🎯 Deployment Options:${NC}"
echo ""
echo "1. ${GREEN}Local Docker Compose:${NC}"
echo "   docker-compose up -d"
echo ""
echo "2. ${GREEN}Production Docker Compose:${NC}"
echo "   docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "3. ${GREEN}Direct Docker Run:${NC}"
echo "   docker run -d -p 8080:8080 --name django-bartr $IMAGE_NAME:$TAG"
echo ""
echo "4. ${GREEN}Kubernetes:${NC}"
echo "   kubectl apply -f k8s/"
echo ""
echo "5. ${GREEN}AWS ECS:${NC}"
echo "   aws ecs register-task-definition --cli-input-json file://task-definition.json"
echo ""
echo "6. ${GREEN}Google Cloud Run:${NC}"
echo "   gcloud run deploy django-bartr --image $IMAGE_NAME:$TAG --platform managed"
echo ""
echo "7. ${GREEN}Azure Container Instances:${NC}"
echo "   az container create --resource-group django-bartr-rg --name django-bartr --image $IMAGE_NAME:$TAG"
echo ""
echo "8. ${GREEN}DigitalOcean App Platform:${NC}"
echo "   doctl apps create --spec app.yaml"
echo ""
echo "9. ${GREEN}Heroku:${NC}"
echo "   heroku container:push web"
echo ""
echo "10. ${GREEN}Railway:${NC}"
echo "    railway up"
echo ""
echo "11. ${GREEN}Render:${NC}"
echo "    Deploy via Render Dashboard"
echo ""

# Step 6: Environment variables reminder
echo -e "${BLUE}🔧 Required Environment Variables:${NC}"
echo ""
echo "DJANGO_SETTINGS_MODULE=config.settings.production"
echo "SECRET_KEY=your-production-secret-key"
echo "DEBUG=False"
echo "ALLOWED_HOSTS=your-domain.com,localhost"
echo "DB_HOST=your-db-host"
echo "DB_NAME=your-db-name"
echo "DB_USER=your-db-user"
echo "DB_PASSWORD=your-db-password"
echo "CELERY_BROKER_URL=redis://your-redis-host:6379/0"
echo "CELERY_RESULT_BACKEND=redis://your-redis-host:6379/0"
echo ""

# Step 7: Health check
echo -e "${BLUE}🏥 Health Check:${NC}"
echo ""
echo "After deployment, check your application health:"
echo "curl -f http://your-domain.com/health/"
echo ""

print_status "Deployment script completed!"
echo ""
echo -e "${BLUE}📚 For detailed instructions, see: DEPLOYMENT_GUIDE.md${NC}"
echo -e "${BLUE}🐳 Your image is available at: https://hub.docker.com/r/$IMAGE_NAME${NC}"
echo ""

# Optional: Ask user what they want to do next
echo -e "${YELLOW}What would you like to do next?${NC}"
echo "1. Deploy locally with docker-compose"
echo "2. Deploy to a cloud platform"
echo "3. View deployment guide"
echo "4. Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        print_status "Starting local deployment..."
        docker-compose up -d
        print_status "Local deployment completed!"
        echo "Your application is running at: http://localhost:8080"
        ;;
    2)
        print_warning "Please refer to DEPLOYMENT_GUIDE.md for cloud deployment instructions"
        ;;
    3)
        print_status "Opening deployment guide..."
        if command -v xdg-open &> /dev/null; then
            xdg-open DEPLOYMENT_GUIDE.md
        elif command -v open &> /dev/null; then
            open DEPLOYMENT_GUIDE.md
        else
            echo "Please open DEPLOYMENT_GUIDE.md manually"
        fi
        ;;
    4)
        print_status "Goodbye!"
        exit 0
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac 