# 🏪 Merchant-to-Merchant Deal System

## 🎯 Overview

A revolutionary B2B platform that allows merchants to create deals using wallet points and exchange them with other merchants. The system enables business-to-business networking through a points-based deal exchange mechanism.

## 🚀 Key Features

### ✨ Core Functionality

- **Deal Creation**: Merchants create deals with points (automatically deducted from wallet)
- **Deal Discovery**: Browse and filter deals from other merchants
- **Request System**: Request deals with custom messages and counter offers
- **Deal Confirmation**: Accept/reject deal requests with terms negotiation
- **Points Transfer**: Automatic wallet points transfer when deals complete
- **Usage Tracking**: Complete audit trail of all point transactions
- **Real-time Notifications**: Instant updates on all deal activities
- **Business Analytics**: Comprehensive statistics and insights

### 🔄 Complete Workflow

1. **Create Deal** → Points deducted from merchant's wallet
2. **Discover Deals** → Browse other merchants' available deals
3. **Request Deal** → Send request with message and counter offer
4. **Accept/Reject** → Deal creator accepts or rejects request
5. **Complete Deal** → Points transfer and deal completion
6. **Track Usage** → Complete audit trail of all transactions

## 🛠️ Installation & Setup

### Prerequisites

- Django 3.2+
- Python 3.8+
- PostgreSQL/MySQL database
- Redis (for caching)

### 1. Database Migrations

```bash
python manage.py makemigrations custom_auth
python manage.py migrate
```

### 2. Create Superuser

```bash
python manage.py createsuperuser
```

### 3. Run Development Server

```bash
python manage.py runserver
```

## 📱 How to Use

### For Merchants

#### 1. Create Your First Deal

```bash
POST /api/custom-auth/v1/merchant-deals/
```

**Request Body:**

```json
{
  "title": "Electronics Exchange Deal",
  "description": "Exchange electronics for 2000 points",
  "points_offered": 2000.0,
  "deal_value": 2500.0,
  "category": 1,
  "expiry_date": "2024-12-31T23:59:59Z",
  "preferred_cities": ["Mumbai", "Delhi"],
  "preferred_categories": [1, 2],
  "terms_conditions": "Valid for 30 days",
  "is_negotiable": true
}
```

**Response:**

```json
{
  "id": 1,
  "merchant": 1,
  "merchant_name": "Tech Store",
  "title": "Electronics Exchange Deal",
  "points_offered": 2000.0,
  "points_remaining": 2000.0,
  "deal_value": 2500.0,
  "status": "active",
  "create_time": "2024-01-15T10:30:00Z"
}
```

**Note:** 2000 points are automatically deducted from your wallet when the deal is created.

#### 2. Discover Other Deals

```bash
GET /api/custom-auth/v1/deal-discovery/
```

**Query Parameters:**

- `category`: Filter by category ID
- `min_points`: Minimum points filter
- `max_points`: Maximum points filter
- `search`: Search in title, description, or business name
- `merchant__city`: Filter by city

**Example:**

```
GET /api/custom-auth/v1/deal-discovery/?category=1&min_points=1000&max_points=3000&search=electronics
```

#### 3. Request a Deal

```bash
POST /api/custom-auth/v1/deal-requests/
```

**Request Body:**

```json
{
  "deal": 2,
  "points_requested": 1500.0,
  "message": "I'm interested in this mobile accessories deal. Can we discuss terms?",
  "counter_offer": 1200.0
}
```

#### 4. Manage Deal Requests

```bash
# Get my requests
GET /api/custom-auth/v1/deal-requests/

# Accept a request
POST /api/custom-auth/v1/deal-requests/{id}/accept/

# Reject a request
POST /api/custom-auth/v1/deal-requests/{id}/reject/
```

#### 5. Complete Deals

```bash
# Get my confirmations
GET /api/custom-auth/v1/deal-confirmations/

# Complete a deal
POST /api/custom-auth/v1/deal-confirmations/{id}/complete/
```

#### 6. Check Notifications

```bash
# Get notifications
GET /api/custom-auth/v1/merchant-notifications/

# Mark as read
POST /api/custom-auth/v1/merchant-notifications/{id}/mark-read/

# Mark all as read
POST /api/custom-auth/v1/merchant-notifications/mark-all-read/

# Get unread count
GET /api/custom-auth/v1/merchant-notifications/unread-count/
```

## 💡 Real-World Example

### Scenario: Apple Store & Samsung Store Collaboration

#### Step 1: Create Deals

**Apple Store creates deal:**

```json
POST /api/custom-auth/v1/merchant-deals/
{
  "title": "Mobile Accessories Deal",
  "description": "Get mobile accessories for 1500 points",
  "points_offered": 1500.00,
  "deal_value": 2000.00,
  "category": 1
}
```

_Result: 1500 points deducted from Apple's wallet_

**Samsung Store creates deal:**

```json
POST /api/custom-auth/v1/merchant-deals/
{
  "title": "Electronics Exchange",
  "description": "Exchange electronics for 2000 points",
  "points_offered": 2000.00,
  "deal_value": 2500.00,
  "category": 1
}
```

_Result: 2000 points deducted from Samsung's wallet_

#### Step 2: Discovery & Request

**Apple discovers Samsung's deal:**

```bash
GET /api/custom-auth/v1/deal-discovery/by-points/?points=2000
```

**Apple requests Samsung's deal:**

```json
POST /api/custom-auth/v1/deal-requests/
{
  "deal": 2,
  "points_requested": 2000.00,
  "message": "Great electronics deal! I'm interested."
}
```

#### Step 3: Deal Confirmation

**Samsung accepts the request:**

```bash
POST /api/custom-auth/v1/deal-requests/1/accept/
```

_Result: Deal confirmation created, 2000 points marked as used in Samsung's deal_

#### Step 4: Complete Deal

**Either merchant completes the deal:**

```bash
POST /api/custom-auth/v1/deal-confirmations/1/complete/
```

_Result: 2000 points transferred from Samsung to Apple, usage tracked_

## 🔧 Key Features Explained

### 1. **Points System**

- 1 Rupee = 10 Points
- Points stored in user's wallet
- Automatic deduction when creating deals
- Automatic transfer when completing deals

### 2. **Deal Lifecycle**

- **Created** → Points deducted from creator's wallet
- **Requested** → Other merchants can request the deal
- **Accepted** → Deal confirmation created
- **Completed** → Points transferred, usage tracked

### 3. **Security & Validation**

- Only deal creator can accept/reject requests
- Points validation before deal creation
- Transaction tracking for all operations
- Real-time notifications for all actions

### 4. **Usage Tracking**

- Complete audit trail of point usage
- Transaction IDs for all operations
- Detailed usage descriptions
- Merchant-to-merchant transfer records

## 📊 API Endpoints Overview

### Core Endpoints

- **Deals**: `/api/custom-auth/v1/merchant-deals/`
- **Discovery**: `/api/custom-auth/v1/deal-discovery/`
- **Requests**: `/api/custom-auth/v1/deal-requests/`
- **Confirmations**: `/api/custom-auth/v1/deal-confirmations/`
- **Notifications**: `/api/custom-auth/v1/merchant-notifications/`
- **Statistics**: `/api/custom-auth/v1/deal-stats/`

### Additional Endpoints

- **Merchant Profile**: `/api/custom-auth/v1/merchant_profile/`
- **Wallet**: `/api/custom-auth/v1/wallet/`
- **Categories**: `/api/custom-auth/v1/category/`
- **Merchant Listing**: `/api/custom-auth/v1/merchants/list/`

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Redis
REDIS_URL=redis://localhost:6379

# API Settings
API_VERSION=v1
DEBUG=True
```

### Customization Options

- **Transfer Fees**: Configure in `MerchantPointsTransfer` model
- **Deal Expiry**: Set in `MerchantDeal` model
- **Notification Types**: Extend in `MerchantNotification` model
- **Deal Categories**: Manage through Django admin

## 📊 Monitoring & Analytics

### Dashboard Metrics

- Total deals created
- Active deals count
- Match success rate
- Points transferred
- Popular deal categories
- Merchant engagement

### Admin Panel

Access `/admin/` to manage:

- All deals and confirmations
- Merchant profiles
- Points transfers
- System notifications

## 🚨 Troubleshooting

### Common Issues

#### 1. Migration Errors

```bash
# Reset migrations
python manage.py migrate custom_auth zero
python manage.py makemigrations custom_auth
python manage.py migrate
```

#### 2. API Authentication

```bash
# Check token validity
curl -X GET "http://localhost:8000/api/custom-auth/v1/deal-stats/" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 3. Points Transfer Failures

- Check wallet balance
- Verify deal confirmation status
- Review transaction logs

### Debug Mode

```python
# In settings.py
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'custom_auth': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 🔮 Future Enhancements

### Planned Features

- **AI-Powered Matching**: Smart deal recommendations
- **Video Calls**: Built-in communication
- **Escrow System**: Secure points holding
- **Multi-Currency**: Support for different point systems
- **Mobile App**: Native iOS/Android applications
- **Webhooks**: Real-time external integrations

### API Extensions

- **GraphQL Support**: Flexible data queries
- **WebSocket**: Real-time updates
- **Rate Limiting**: Advanced API protection
- **OAuth2**: Enhanced authentication

## 📚 API Documentation

Complete API documentation is available in `MERCHANT_DEAL_API.md`

### Quick Reference

```bash
# Create deal
POST /api/custom-auth/v1/merchant-deals/

# Discover deals
GET /api/custom-auth/v1/deal-discovery/

# Request deal
POST /api/custom-auth/v1/deal-requests/

# Get confirmations
GET /api/custom-auth/v1/deal-confirmations/

# Complete deal
POST /api/custom-auth/v1/deal-confirmations/{id}/complete/
```

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

### Code Standards

- Follow PEP 8
- Add docstrings
- Write unit tests
- Update documentation

## 📞 Support

### Getting Help

- **Documentation**: Check this README and API docs
- **Issues**: Report bugs on GitHub
- **Discussions**: Join community discussions
- **Email**: Contact development team

### Community

- **GitHub**: Repository and issues
- **Discord**: Community chat
- **Blog**: Latest updates and tutorials

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django community for the excellent framework
- Contributors and beta testers
- Business partners for real-world feedback

---

**Made with ❤️ for the merchant community**

_Transform your business networking with the power of smart matching and points exchange!_
