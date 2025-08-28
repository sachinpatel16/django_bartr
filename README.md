# 🚀 Bartr - Voucher Management Platform

## 📋 Overview

Bartr is a comprehensive voucher management platform that enables merchants to create, manage, and promote vouchers while allowing users to discover, purchase, and redeem them. The platform features gift card sharing via WhatsApp, wallet integration, and location-based advertisement management.

## ✨ Key Features

- **Voucher Management**: Create, manage, and track voucher performance
- **Gift Card Sharing**: Share gift cards via WhatsApp with multi-user claiming
- **Wallet Integration**: Point-based voucher purchases with Razorpay integration
- **Merchant Scanning**: QR code-based voucher redemption
- **Location Targeting**: City/state-based advertisement management
- **WhatsApp Integration**: Direct gift card sharing via WhatsApp
- **Multi-User Support**: One gift card can be shared with multiple users

## 🏗️ Architecture

- **Backend**: Django REST Framework with JWT authentication
- **Database**: PostgreSQL with Django ORM
- **Payment Gateway**: Razorpay integration for wallet recharge
- **File Storage**: Local media storage with configurable paths
- **API Documentation**: Swagger/OpenAPI with drf-yasg

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (for Celery)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd django_bartr
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run migrations**

   ```bash
   python manage.py migrate
   ```

5. **Create superuser**

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 📚 API Documentation

### 📖 Complete API Reference

- **[API_README.md](API_README.md)** - Comprehensive API documentation with all endpoints, request/response examples, and testing instructions

### 🔗 API Endpoints Overview

#### Authentication & User Management

- `POST /api/custom_auth/v1/auth/classic/` - User authentication
- `GET /api/custom_auth/v1/users/me/` - Get user profile
- `PUT /api/custom_auth/v1/users/me/` - Update user profile

#### Merchant Management

- `POST /api/custom_auth/v1/merchant_profile/` - Create merchant profile
- `GET /api/custom_auth/v1/merchants/list/` - List all merchants

#### Wallet & Payments

- `GET /api/custom_auth/v1/wallet/` - Get wallet balance
- `POST /api/custom_auth/v1/wallet/razorpay/create-order/` - Create payment order
- `POST /api/custom_auth/v1/wallet/razorpay/verify-payment/` - Verify payment

#### Voucher Management

- `POST /api/voucher/v1/voucher/` - Create voucher (merchant)
- `GET /api/voucher/v1/voucher/statistics/` - Get voucher statistics
- `POST /api/voucher/v1/voucher/{id}/share-gift-card/` - Share gift card

#### Public Voucher Discovery

- `GET /api/voucher/v1/public/vouchers/` - Browse public vouchers
- `GET /api/voucher/v1/public/vouchers/featured/` - Get featured vouchers
- `GET /api/voucher/v1/public/vouchers/trending/` - Get trending vouchers

#### Voucher Purchase & Management

- `POST /api/voucher/v1/purchase/purchase/` - Purchase voucher
- `POST /api/voucher/v1/purchase/cancel/` - Cancel purchase
- `POST /api/voucher/v1/purchase/refund/` - Refund purchase

#### User Vouchers

- `GET /api/voucher/v1/my-vouchers/` - Get user's vouchers
- `GET /api/voucher/v1/my-vouchers/{id}/qr-code/` - Get voucher QR code

#### WhatsApp Integration

- `POST /api/voucher/v1/whatsapp-contacts/sync-contacts/` - Sync contacts
- `GET /api/voucher/v1/whatsapp-contacts/whatsapp-contacts/` - Get WhatsApp contacts

#### Gift Card Management

- `POST /api/voucher/v1/gift-card-claim/claim/` - Claim gift card
- `GET /api/voucher/v1/gift-card-claim/my-gift-cards/` - Get claimed gift cards
- `GET /api/voucher/v1/gift-card-claim/shared-by-me/` - Get shared gift cards

#### Advertisement Management

- `POST /api/voucher/v1/advertisements/` - Create advertisement
- `GET /api/voucher/v1/advertisements/active/` - Get active advertisements
- `GET /api/voucher/v1/advertisements/by-location/` - Get ads by location

#### Categories

- `GET /api/custom_auth/v1/category/` - List categories
- `POST /api/custom_auth/v1/category/` - Create category

## 🔐 Authentication

The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

## 🧪 Testing

### Swagger UI

Access the interactive API documentation at: `http://localhost:8000/swagger/`

### Health Check

```bash
curl http://localhost:8000/health/
```

### Complete Testing Examples

See [API_README.md](API_README.md#testing-examples) for comprehensive testing examples including the complete voucher flow.

## 🔧 Configuration

### Environment Variables

```bash
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Razorpay Integration
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

# WhatsApp Integration
WHATSAPP_API_KEY=your_whatsapp_api_key
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# File Storage
MEDIA_URL=/media/
MEDIA_ROOT=/path/to/media/
```

### Site Settings

Configurable via Django Admin:

- `voucher_cost`: Points required to purchase voucher (default: 10)
- `gift_card_cost`: Points required to purchase gift card (default: 10)
- `advertisement_cost`: Points required to create advertisement (default: 10)

## 📊 Database Models

### Core Models

- **ApplicationUser**: User authentication and profile
- **MerchantProfile**: Merchant business information
- **Wallet**: User wallet for points management
- **Voucher**: Voucher definitions and types
- **UserVoucherRedemption**: User purchases and redemptions
- **GiftCardShare**: Gift card sharing and claiming
- **WhatsAppContact**: User contacts for WhatsApp sharing
- **Advertisement**: Location-based voucher promotion
- **Category**: Voucher categorization

## 🚀 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or use the deployment scripts
./deploy.sh  # Linux/Mac
deploy.bat   # Windows
```

### Manual Deployment

```bash
# Collect static files
python manage.py collectstatic

# Run with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## 📁 Project Structure

```
django_bartr/
├── config/                 # Django settings and configuration
├── freelancing/           # Main application modules
│   ├── custom_auth/      # Authentication and user management
│   ├── voucher/          # Voucher management system
│   ├── registrations/    # User registration
│   └── utils/            # Utility functions and helpers
├── media/                # User uploaded files
├── static/               # Static files
├── requirements.txt      # Python dependencies
├── docker-compose.yml   # Docker configuration
└── API_README.md        # Complete API documentation
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the BSD License - see the LICENSE file for details.

## 🆘 Support

For technical support or questions:

- **Email**: support@yourdomain.com
- **Documentation**: [API_README.md](API_README.md)
- **Swagger UI**: http://localhost:8000/swagger/

## 📝 Changelog

### Version 1.0.0

- Initial release with complete voucher management system
- WhatsApp gift card sharing integration
- Razorpay wallet integration
- Merchant scanning and redemption system
- Location-based advertisement management

---

**Happy coding! 🎉**
