# 🚀 Django Bartr Deployment Guide

## 📋 Table of Contents
1. [Push to Docker Hub](#push-to-docker-hub)
2. [Deploy on Docker Hub](#deploy-on-docker-hub)
3. [Deploy on AWS](#deploy-on-aws)
4. [Deploy on Google Cloud](#deploy-on-google-cloud)
5. [Deploy on Azure](#deploy-on-azure)
6. [Deploy on DigitalOcean](#deploy-on-digitalocean)
7. [Deploy on Heroku](#deploy-on-heroku)
8. [Deploy on Railway](#deploy-on-railway)
9. [Deploy on Render](#deploy-on-render)

---

## 1. Push to Docker Hub

### Step 1: Tag your image
```bash
docker tag django-bartr:latest sachinpatel016/django_bartr:latest
docker tag django-bartr:latest sachinpatel016/django_bartr:v1.0.0
```

### Step 2: Login to Docker Hub
```bash
docker login
# Enter your username: sachinpatel016
# Enter your password
```

### Step 3: Push the image
```bash
# Push latest tag
docker push sachinpatel016/django_bartr:latest

# Push version tag
docker push sachinpatel016/django_bartr:v1.0.0
```

### Step 4: Verify on Docker Hub
Visit: https://hub.docker.com/r/sachinpatel016/django_bartr

---

## 2. Deploy on Docker Hub

### Using Docker Compose with your image
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  web:
    image: sachinpatel016/django_bartr:latest
    ports:
      - "8080:8080"
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - SECRET_KEY=your-production-secret-key
      - DEBUG=False
      - ALLOWED_HOSTS=your-domain.com,localhost
      - DB_HOST=your-db-host
      - DB_NAME=your-db-name
      - DB_USER=your-db-user
      - DB_PASSWORD=your-db-password
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=your-db-name
      - POSTGRES_USER=your-db-user
      - POSTGRES_PASSWORD=your-db-password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  postgres_data:
```

### Deploy command
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 3. Deploy on AWS

### Option A: AWS ECS (Elastic Container Service)

#### Create ECS Task Definition
```json
{
  "family": "django-bartr",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "django-bartr",
      "image": "sachinpatel016/django_bartr:latest",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DJANGO_SETTINGS_MODULE",
          "value": "config.settings.production"
        },
        {
          "name": "SECRET_KEY",
          "value": "your-production-secret-key"
        },
        {
          "name": "DEBUG",
          "value": "False"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/django-bartr",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Deploy using AWS CLI
```bash
# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster your-cluster \
  --service-name django-bartr \
  --task-definition django-bartr:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

### Option B: AWS EC2 with Docker

#### Launch EC2 instance and install Docker
```bash
# Connect to your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Docker
sudo apt update
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker $USER

# Pull and run your image
docker pull sachinpatel016/django_bartr:latest
docker run -d -p 80:8080 --name django-bartr sachinpatel016/django_bartr:latest
```

---

## 4. Deploy on Google Cloud

### Option A: Google Cloud Run

#### Deploy using gcloud CLI
```bash
# Deploy to Cloud Run
gcloud run deploy django-bartr \
  --image sachinpatel016/django_bartr:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars DJANGO_SETTINGS_MODULE=config.settings.production,SECRET_KEY=your-secret-key,DEBUG=False
```

### Option B: Google Kubernetes Engine (GKE)

#### Create deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-bartr
spec:
  replicas: 3
  selector:
    matchLabels:
      app: django-bartr
  template:
    metadata:
      labels:
        app: django-bartr
    spec:
      containers:
      - name: django-bartr
        image: sachinpatel016/django_bartr:latest
        ports:
        - containerPort: 8080
        env:
        - name: DJANGO_SETTINGS_MODULE
          value: "config.settings.production"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: django-secrets
              key: secret-key
---
apiVersion: v1
kind: Service
metadata:
  name: django-bartr-service
spec:
  selector:
    app: django-bartr
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

#### Deploy to GKE
```bash
# Create cluster
gcloud container clusters create django-bartr-cluster --num-nodes=3

# Deploy
kubectl apply -f deployment.yaml
```

---

## 5. Deploy on Azure

### Option A: Azure Container Instances

#### Deploy using Azure CLI
```bash
# Create resource group
az group create --name django-bartr-rg --location eastus

# Deploy container
az container create \
  --resource-group django-bartr-rg \
  --name django-bartr \
  --image sachinpatel016/django_bartr:latest \
  --dns-name-label django-bartr \
  --ports 8080 \
  --environment-variables DJANGO_SETTINGS_MODULE=config.settings.production SECRET_KEY=your-secret-key DEBUG=False
```

### Option B: Azure Kubernetes Service (AKS)

#### Deploy to AKS
```bash
# Create AKS cluster
az aks create --resource-group django-bartr-rg --name django-bartr-aks --node-count 3

# Deploy using the same Kubernetes manifests as GKE
kubectl apply -f deployment.yaml
```

---

## 6. Deploy on DigitalOcean

### Option A: DigitalOcean App Platform

#### Create app.yaml
```yaml
name: django-bartr
services:
- name: web
  source_dir: /
  dockerfile_path: Dockerfile
  http_port: 8080
  instance_count: 2
  instance_size_slug: basic-xxs
  envs:
  - key: DJANGO_SETTINGS_MODULE
    value: config.settings.production
  - key: SECRET_KEY
    value: your-secret-key
  - key: DEBUG
    value: "False"
```

#### Deploy using doctl
```bash
doctl apps create --spec app.yaml
```

### Option B: DigitalOcean Droplets

#### Deploy on Droplet
```bash
# Connect to your droplet
ssh root@your-droplet-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Pull and run your image
docker pull sachinpatel016/django_bartr:latest
docker run -d -p 80:8080 --name django-bartr sachinpatel016/django_bartr:latest
```

---

## 7. Deploy on Heroku

### Option A: Heroku Container Registry

#### Deploy using Heroku CLI
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-django-bartr-app

# Login to Heroku Container Registry
heroku container:login

# Build and push
heroku container:push web

# Release
heroku container:release web

# Set environment variables
heroku config:set DJANGO_SETTINGS_MODULE=config.settings.production
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
```

### Option B: Heroku with Dockerfile
```bash
# Create heroku.yml
echo "build:
  docker:
    web: Dockerfile" > heroku.yml

# Deploy
git add heroku.yml
git commit -m "Add Heroku deployment"
git push heroku main
```

---

## 8. Deploy on Railway

### Deploy using Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Set environment variables
railway variables set DJANGO_SETTINGS_MODULE=config.settings.production
railway variables set SECRET_KEY=your-secret-key
railway variables set DEBUG=False
```

---

## 9. Deploy on Render

### Create render.yaml
```yaml
services:
  - type: web
    name: django-bartr
    env: docker
    dockerfilePath: ./Dockerfile
    dockerCommand: gunicorn --bind 0.0.0.0:$PORT --workers 3 --timeout 120 config.wsgi:application
    envVars:
      - key: DJANGO_SETTINGS_MODULE
        value: config.settings.production
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
```

### Deploy using Render Dashboard
1. Go to https://render.com
2. Connect your GitHub repository
3. Select "Web Service"
4. Choose your repository
5. Set environment variables
6. Deploy

---

## 🔧 Environment Variables

### Required Environment Variables
```bash
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,localhost
ENGINE=django.db.backends.postgresql
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
CELERY_BROKER_URL=redis://your-redis-host:6379/0
CELERY_RESULT_BACKEND=redis://your-redis-host:6379/0
```

### Optional Environment Variables
```bash
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
SERVER_EMAIL_SIGNATURE=Bartr
USE_CLOUDFRONT=False
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_CUSTOM_DOMAIN=your-cloudfront-domain
API_KEY_SECRET=your-api-key-secret
ADMINS=[["Admin", "admin@example.com"]]
```

---

## 📊 Monitoring and Logs

### View Logs
```bash
# Docker
docker logs container-name

# Kubernetes
kubectl logs deployment/django-bartr

# AWS ECS
aws logs describe-log-groups --log-group-name-prefix /ecs/django-bartr

# Google Cloud Run
gcloud logging read "resource.type=cloud_run_revision"
```

### Health Checks
```bash
# Check application health
curl -f http://your-domain.com/health/

# Check container status
docker ps
kubectl get pods
```

---

## 🔒 Security Best Practices

1. **Use strong SECRET_KEY**
2. **Set DEBUG=False in production**
3. **Use HTTPS everywhere**
4. **Configure proper ALLOWED_HOSTS**
5. **Use environment variables for secrets**
6. **Regular security updates**
7. **Backup your database**
8. **Monitor application logs**

---

## 📈 Scaling

### Horizontal Scaling
```bash
# Docker Swarm
docker service scale django_bartr=5

# Kubernetes
kubectl scale deployment django-bartr --replicas=5

# AWS ECS
aws ecs update-service --cluster your-cluster --service django-bartr --desired-count 5
```

### Vertical Scaling
- Increase CPU and memory limits
- Use larger instance types
- Optimize application performance

---

## 🆘 Troubleshooting

### Common Issues
1. **Port conflicts**: Change port mappings
2. **Database connection**: Check connection strings
3. **Memory issues**: Increase container memory
4. **Startup timeouts**: Increase health check timeouts
5. **Static files**: Ensure proper static file configuration

### Debug Commands
```bash
# Check container status
docker ps -a

# View logs
docker logs container-name

# Execute commands in container
docker exec -it container-name bash

# Check resource usage
docker stats
```

---

## 📞 Support

For issues and questions:
- Check application logs
- Review environment variables
- Verify network connectivity
- Test locally first
- Use health check endpoints

---

**Happy Deploying! 🚀** 