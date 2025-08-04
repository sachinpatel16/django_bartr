# Production Deployment Guide

## Database Connection Fix

The error you're getting is because Django is trying to connect to `127.0.0.1:5432` (localhost) instead of your production database.

## Environment Variables for Production

Set these environment variables in your production platform (Sevalla, Heroku, etc.):

```bash
# Django Settings
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=django-insecure-your-secret-key-here-change-this-in-production
DEBUG=False

# Database Configuration - IMPORTANT!
# Replace 'your-production-db-host' with your actual database host
DB_NAME=bartr
DB_USER=postgres
DB_PASSWORD=dwij9143
DB_HOST=your-production-db-host  # ⚠️ CHANGE THIS!
DB_PORT=5432
DB_SSL=false

# Alternative: Use DATABASE_URL (recommended for cloud platforms)
# DATABASE_URL=postgres://postgres:dwij9143@your-production-db-host:5432/bartr

# Email Settings
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
SERVER_EMAIL_SIGNATURE=Bartr
SERVER_EMAIL=noreply@bartr.com

# AWS S3 Settings
USE_CLOUDFRONT=False
AWS_STORAGE_BUCKET_NAME=djangobartr
AWS_ACCESS_KEY_ID=AKIA6L6AERXVRPJVIEEL
AWS_SECRET_ACCESS_KEY=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
AWS_S3_CUSTOM_DOMAIN=djangobartr.s3.amazonaws.com

# API Key
API_KEY_SECRET=gAAAAABnLZyXV33WOqXmf-dmKviuREu7WKDqIcNAUYLUZDX0L2-KDUO_wzEbaiiaMlf003f_Ny7wjYpLUEW4SgLRJ5TSSl7rSg==

# Admins
ADMINS=[["Admin", "admin@example.com"]]

# Allowed Hosts
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,*,bartrlatest-8l446.sevalla.app,api.bartr.club
```

## Database Options

### Option 1: Use External Database (AWS RDS, DigitalOcean, etc.)
Set `DB_HOST` to your database server's IP address or domain.

### Option 2: Use Cloud Platform's Database Service
If your platform provides a database service, use their provided `DATABASE_URL`.

### Option 3: Use Docker Database (if using Docker in production)
Set `DB_HOST=db` (as in your docker-compose.yml).

## Quick Fix for Testing

If you want to test quickly, you can temporarily use SQLite:

```python
# In config/settings/production.py, replace the DATABASES configuration with:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## Deployment Steps

1. **Set the correct `DB_HOST`** in your production environment variables
2. **Deploy your updated code** with the new production settings
3. **Run migrations** if needed:
   ```bash
   python manage.py migrate --settings=config.settings.production
   ```

## Common Database Hosts

- **AWS RDS**: `your-db-name.region.rds.amazonaws.com`
- **DigitalOcean**: `your-db-host.digitaloceanspaces.com`
- **Google Cloud SQL**: `your-project:region:instance`
- **Local/Development**: `127.0.0.1` or `localhost`
- **Docker**: `db` (service name)

## Troubleshooting

1. **Check if database is accessible** from your production server
2. **Verify firewall settings** allow connections on port 5432
3. **Test connection** using:
   ```bash
   psql -h your-db-host -U postgres -d bartr
   ```

The main issue is that `DB_HOST` needs to point to your actual production database server, not `127.0.0.1`.

## CSRF Fix

The CSRF verification failed error (403 Forbidden) has been fixed by:

1. **Adding CSRF exemption** to API endpoints that need it
2. **Creating custom CSRF middleware** that skips CSRF verification for `/api/` endpoints
3. **Configuring proper CSRF settings** for production

### What was changed:

- Added `@method_decorator(csrf_exempt, name='dispatch')` to API views
- Created `CustomCsrfMiddleware` to handle API endpoints
- Updated production settings with proper CSRF configuration
- Set `DEBUG=False` for production security

The API endpoints should now work without CSRF errors while maintaining security for non-API endpoints. 