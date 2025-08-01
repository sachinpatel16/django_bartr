from .base import * # NOQA

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Configure ALLOWED_HOSTS with fallback
try:
    ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
except:
    # Fallback for missing environment variable
    ALLOWED_HOSTS = [
        'bartr-t2shu.sevalla.app',
        'localhost',
        '127.0.0.1',
        '0.0.0.0',
        '*'
    ]

# ADMINS
try:
    ADMINS = env.json('ADMINS')
except:
    ADMINS = (
        ('Admin', 'admin@example.com'),
    )

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

INSTALLED_APPS += ["storages"]

# Try to use PostgreSQL, fallback to SQLite if not available
try:
    import psycopg2
    DATABASES = {
        'default': {
            'ENGINE': env('ENGINE', default='django.db.backends.postgresql'),
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST'),
            'PORT': env('PORT', default='5432'),
        }
    }
except ImportError:
    # Fallback to SQLite if PostgreSQL is not available
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# E-mail settings
# -----------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
try:
    EMAIL_HOST_USER = env('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = SERVER_EMAIL = env('SERVER_EMAIL_SIGNATURE') + ' <%s>' % env('SERVER_EMAIL')
except:
    # Fallback for missing email settings
    EMAIL_HOST_USER = 'noreply@example.com'
    EMAIL_HOST_PASSWORD = ''
    DEFAULT_FROM_EMAIL = SERVER_EMAIL = 'noreply@example.com'


# Storage configurations
# --------------------------------------------------------------------------
try:
    USE_CLOUDFRONT = env.bool('USE_CLOUDFRONT', default=False)
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_AUTO_CREATE_BUCKET = True
    AWS_DEFAULT_ACL = 'public-read'
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_SECURE_URLS = True

    if USE_CLOUDFRONT:
        AWS_S3_CUSTOM_DOMAIN = env('AWS_S3_CUSTOM_DOMAIN')
    else:
        AWS_S3_CUSTOM_DOMAIN = '{}.s3.amazonaws.com'.format(AWS_STORAGE_BUCKET_NAME)

    STATIC_URL = '//{}/static/'.format(AWS_S3_CUSTOM_DOMAIN)
    MEDIA_URL = '//{}/media/'.format(AWS_S3_CUSTOM_DOMAIN)

    DEFAULT_FILE_STORAGE = 'config.settings.s3utils.MediaRootS3BotoStorage'
    STATICFILES_STORAGE = 'config.settings.s3utils.StaticRootS3BotoStorage'

    AWS_PRELOAD_METADATA = False
except:
    # Fallback for missing AWS settings - use local storage
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    MEDIA_ROOT = BASE_DIR / 'media'


