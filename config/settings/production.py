from .base import * # NOQA

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost','127.0.0.1','0.0.0.0','bartrlatest-8l446.sevalla.app','api.bartr.club']

CSRF_TRUSTED_ORIGINS = [
    'https://*.kinsta.app',
    'https://*.sevalla.app',
    'https://bartrlatest-8l446.sevalla.app',
    'https://api.bartr.club'
]

# CORS Configuration for Production
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    'https://bartrlatest-8l446.sevalla.app',
    'https://api.bartr.club',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://\w+\.sevalla\.app$",
    r"^https://\w+\.kinsta\.app$",
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]


# ADMINS
ADMINS = env.json('ADMINS')

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

INSTALLED_APPS += ["storages"]

DATABASES = {
    'default': {
        'ENGINE': env('ENGINE'),
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}

# E-mail settings
# -----------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = SERVER_EMAIL = env('SERVER_EMAIL_SIGNATURE') + ' <%s>' % env('SERVER_EMAIL')


# Storage configurations
# --------------------------------------------------------------------------
USE_CLOUDFRONT= env.bool('USE_CLOUDFRONT', default=False)
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_AUTO_CREATE_BUCKET = True
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False
AWS_S3_SECURE_URLS = True
AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL') 

if USE_CLOUDFRONT:
    AWS_S3_CUSTOM_DOMAIN = env('AWS_S3_CUSTOM_DOMAIN')
else:
    AWS_S3_CUSTOM_DOMAIN = '{}.s3.amazonaws.com'.format(AWS_STORAGE_BUCKET_NAME)

STATIC_URL = '//{}/static/'.format(AWS_S3_CUSTOM_DOMAIN)
MEDIA_URL = '//{}/media/'.format(AWS_S3_CUSTOM_DOMAIN)

# STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/freelancing/static/"
# MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/freelancing/media/"


DEFAULT_FILE_STORAGE = 'config.settings.s3utils.MediaRootS3BotoStorage'
STATICFILES_STORAGE = 'config.settings.s3utils.StaticRootS3BotoStorage'

AWS_PRELOAD_METADATA = False


