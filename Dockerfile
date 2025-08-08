# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production
ENV ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,*

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        libjpeg-dev \
        libpng-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev \
        pkg-config \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media

# Collect static files
# RUN python manage.py collectstatic --noinput --settings=config.settings.production

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Create a startup script to run migrations and start the application
RUN echo '#!/bin/bash\n\
echo "Running database migrations..."\n\
python manage.py migrate --settings=config.settings.production --noinput\n\
echo "Starting Gunicorn..."\n\
exec gunicorn --bind 0.0.0.0:8080 --workers 3 --timeout 120 config.wsgi:application\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health/ || exit 1

# Default command
CMD ["/app/start.sh"] 