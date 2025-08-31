# Merchant-to-Merchant Deal System

## 🎯 Overview

A revolutionary system that allows merchants to create deals and match with other merchants through a Tinder-like swiping interface. Merchants can exchange wallet points for business deals, creating a new way of business networking and collaboration.

## 🚀 Key Features

### ✨ Core Functionality

- **Deal Creation**: Merchants create deals with points requirements
- **Tinder-like Interface**: Swipe right (interested) or left (not interested)
- **Smart Matching**: Mutual interest automatically creates matches
- **Points Transfer**: Automatic wallet points transfer when deals complete
- **Real-time Notifications**: Instant updates on matches and actions
- **Business Analytics**: Comprehensive statistics and insights

### 🔄 Complete Workflow

1. **Create Deal** → Merchant posts a deal with points requirement
2. **Discover Deals** → Browse other merchants' deals
3. **Swipe** → Right swipe = interested, Left swipe = not interested
4. **Match** → Mutual interest creates a match
5. **Accept** → Both parties agree to the deal
6. **Complete** → Points transfer and deal completion

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

```json
POST /api/v1/merchant-deals/
{
    "title": "Electronics Exchange Deal",
    "description": "Exchange electronics for 2000 points",
    "points_required": 2000.00,
    "deal_value": 2500.00,
    "category": 1,
    "expiry_date": "2024-12-31T23:59:59Z",
    "min_points": 1500.00,
    "max_points": 2500.00,
    "preferred_cities": ["Mumbai", "Delhi"],
    "terms_conditions": "Valid for 30 days",
    "is_negotiable": true
}
```

#### 2. Discover Other Deals

```bash
GET /api/v1/deal-discovery/
```

#### 3. Swipe on Deals

```json
POST /api/v1/merchant-swipes/
{
    "deal": 1,
    "swipe_type": "right",  // "right" or "left"
    "notes": "Great deal!",
    "counter_offer": 1800.00
}
```

#### 4. Manage Matches

```bash
# Get your matches
GET /api/v1/merchant-matches/

# Accept a match
POST /api/v1/merchant-matches/{id}/accept/

# Complete a deal
POST /api/v1/merchant-matches/{id}/complete/
```

#### 5. Check Notifications

```bash
# Get notifications
GET /api/v1/merchant-notifications/

# Mark as read
POST /api/v1/merchant-notifications/{id}/mark_read/
```

### For Developers

#### API Endpoints Overview

- **Deals**: `/api/v1/merchant-deals/`
- **Discovery**: `/api/v1/deal-discovery/`
- **Swipes**: `/api/v1/merchant-swipes/`
- **Matches**: `/api/v1/merchant-matches/`
- **Notifications**: `/api/v1/merchant-notifications/`
- **Statistics**: `/api/v1/deal-stats/`

#### Testing the System

```bash
# Run the test script
python test_merchant_deal_system.py

# Or test individual endpoints
curl -X GET "http://localhost:8000/api/v1/deal-discovery/" \
     -H "Authorization: Token YOUR_TOKEN"
```

## 💡 Real-World Example

### Scenario: Apple Store & Samsung Store Collaboration

#### Step 1: Create Deals

**Apple Store creates:**

- Title: "Mobile Accessories Deal"
- Points: 1500
- Value: ₹2000

**Samsung Store creates:**

- Title: "Electronics Exchange"
- Points: 2000
- Value: ₹2500

#### Step 2: Discovery & Swiping

- Apple swipes RIGHT on Samsung's deal
- Samsung swipes RIGHT on Apple's deal
- **MATCH CREATED!** 🎉

#### Step 3: Deal Completion

- Both merchants agree to terms
- 2000 points transferred from Samsung to Apple
- Both businesses benefit from cross-promotion

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
- **Match Expiry**: Set in `MerchantMatch` model
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

- All deals and matches
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
curl -X GET "http://localhost:8000/api/v1/deal-stats/" \
     -H "Authorization: Token YOUR_TOKEN"
```

#### 3. Points Transfer Failures

- Check wallet balance
- Verify match status
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
POST /merchant-deals/

# Discover deals
GET /deal-discovery/

# Swipe on deal
POST /merchant-swipes/

# Get matches
GET /merchant-matches/

# Complete deal
POST /merchant-matches/{id}/complete/
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
