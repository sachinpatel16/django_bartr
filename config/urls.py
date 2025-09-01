from rest_framework import permissions
from rest_framework.permissions import AllowAny
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


from drf_yasg import openapi  # type: ignore
from drf_yasg.views import get_schema_view  # type: ignore
from rest_framework_simplejwt.authentication import JWTAuthentication  # type: ignore

# For swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Bartr API",
        default_version='v1',
        description="""
        # 🚀 Bartr - Complete Voucher Management Platform API
        
        ## Overview
        Bartr is a comprehensive voucher management platform that enables merchants to create and manage vouchers, 
        users to discover and purchase vouchers, and provides gift card sharing via WhatsApp with multi-user claiming.
        
        ## Key Features
        - **Voucher Management**: Complete CRUD operations for merchants
        - **Gift Card Sharing**: WhatsApp integration with multi-user claiming
        - **Wallet Integration**: Point-based voucher purchases
        - **Merchant Scanning**: QR code-based voucher redemption
        - **Location-based Advertising**: City/state targeting for promotions
        - **WhatsApp Contact Management**: Bulk contact validation and synchronization
        
        ## Authentication
        All API endpoints require JWT token authentication. Include the token in the Authorization header:
        ```
        Authorization: Bearer <your_jwt_token>
        ```
        
        ## Base URLs
        - **Production**: https://bartrlatest-8l446.sevalla.app/api/
        - **Development**: http://localhost:8000/api/
        
        ## API Categories
        1. **Authentication & User Management** - User registration, login, profile management
        2. **Merchant Management** - Merchant profiles, business information
        3. **Voucher System** - Voucher creation, management, and analytics
        4. **Wallet & Payments** - Point management, Razorpay integration
        5. **Gift Card Sharing** - WhatsApp integration, multi-user claiming
        6. **Advertisement Management** - Location-based promotion
        7. **Merchant Scanning** - Voucher redemption workflow
        
        ## Getting Started
        1. Authenticate using `/api/custom_auth/v1/auth/classic/`
        2. Use the returned JWT token for subsequent requests
        3. Explore the API endpoints below
        
        For detailed documentation, visit: [API_README.md](https://github.com/your-repo/API_README.md)
        """,
        terms_of_service="https://bartr.club/terms/",
        contact=openapi.Contact(
            name="Bartr Support",
            email="support@bartr.club",
            url="https://bartr.club"
        ),
        license=openapi.License(
            name="Commercial License",
            url="https://bartr.club/license/"
        ),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('api/', include([
            path('custom_auth/', include('freelancing.custom_auth.api_urls')),
            path('voucher/', include('freelancing.voucher.api_urls')),
        ])),
    ],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', csrf_exempt(lambda request: JsonResponse({'status': 'healthy', 'message': 'Django application is running'})), name='health-check'),
    path('cors-test/', csrf_exempt(lambda request: JsonResponse({'cors': 'working', 'origin': request.META.get('HTTP_ORIGIN', 'unknown')})), name='cors-test'),
    # Swagger Documentation URLs
    path('swagger/', login_required(schema_view.with_ui('swagger', cache_timeout=0)), name='schema-swagger-ui'),
    path('redoc/', login_required(schema_view.with_ui('redoc', cache_timeout=0)), name='schema-redoc'),
    path('swagger.json', login_required(schema_view.without_ui(cache_timeout=0)), name='schema-json'),
    path('accounts/login/', lambda request: redirect(f'/admin/login/?next=/swagger/')),  # Redirect to admin login with next parameter
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include([
        # path('registration/', include('freelancing.registrations.api_urls')),
        path('custom_auth/', include('freelancing.custom_auth.api_urls')),
        path('voucher/', include('freelancing.voucher.api_urls')),
    ])),
    path('i18n/', include('django.conf.urls.i18n')),  # Enable language switching
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
