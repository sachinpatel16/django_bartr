# 🎫 Complete Voucher Management System API Documentation

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Authentication & Headers](#authentication--headers)
3. [Complete Flow Diagram](#complete-flow-diagram)
4. [Merchant Voucher Management APIs](#merchant-voucher-management-apis)
5. [Public Voucher Discovery APIs](#public-voucher-discovery-apis)
6. [User Voucher Purchase & Management APIs](#user-voucher-purchase--management-apis)
7. [WhatsApp Contact Management APIs](#whatsapp-contact-management-apis)
8. [Gift Card Sharing & Claiming APIs](#gift-card-sharing--claiming-apis)
9. [Merchant Voucher Scanning & Redemption APIs](#merchant-voucher-scanning--redemption-apis)
10. [Advertisement Management APIs](#advertisement-management-apis)
11. [Error Handling](#error-handling)
12. [Testing Examples](#testing-examples)

## 🎯 System Overview

The Bartr Voucher Management System is a comprehensive platform that enables:

- **Merchants** to create, manage, and promote vouchers
- **Users** to discover, purchase, and redeem vouchers
- **Gift Card Sharing** via WhatsApp with multi-user claiming
- **Merchant Scanning** for voucher redemption
- **Advertisement Management** for location-based promotion

### 🔑 Key Features

- **Multi-User Gift Cards**: One gift card can be shared with multiple users
- **WhatsApp Integration**: Direct gift card sharing via WhatsApp
- **Merchant Scanning**: QR code-based voucher redemption
- **Wallet Integration**: Point-based voucher purchases
- **Location Targeting**: City/state-based advertisement management

## 🔐 Authentication & Headers

### Required Headers

```http
Authorization: Bearer <JWT_TOKEN>
X-API-Key: <API_KEY>
Content-Type: application/json
```

### Authentication Types

- **JWT Token**: Required for user-specific operations
- **API Key**: Required for all endpoints to identify the application
- **Merchant Profile**: Required for merchant-specific operations

---

## 🔄 Complete Flow Diagram

```
1. MERCHANT CREATES VOUCHER
   ↓
2. USER DISCOVERS VOUCHER (Public APIs)
   ↓
3. USER PURCHASES VOUCHER (Wallet Points)
   ↓
4. USER SHARES GIFT CARD (WhatsApp)
   ↓
5. RECIPIENTS CLAIM GIFT CARD
   ↓
6. MERCHANT SCANS & REDEEMS VOUCHER
   ↓
7. SYSTEM TRACKS REDEMPTION
```

---

## 🏪 Merchant Voucher Management APIs

### 1. Create Voucher

**Endpoint:** `POST /api/voucher/vouchers/`

**Request Body:**

```json
{
  "title": "50% Off Coffee",
  "message": "Get 50% off on any coffee",
  "terms_conditions": "Valid only on weekdays",
  "count": 100,
  "image": "<file_upload>",
  "voucher_type": 1,
  "percentage_value": 50.0,
  "percentage_min_bill": 100.0,
  "is_gift_card": false,
  "is_active": true
}
```

**Response:**

```json
{
  "id": 1,
  "title": "50% Off Coffee",
  "message": "Get 50% off on any coffee",
  "voucher_type": 1,
  "percentage_value": "50.00",
  "percentage_min_bill": "100.00",
  "is_gift_card": false,
  "is_active": true,
  "merchant": 1,
  "category": null
}
```

### 2. Get Voucher Statistics

**Endpoint:** `GET /api/voucher/vouchers/statistics/`

**Response:**

```json
{
  "total_vouchers": 25,
  "total_purchases": 150,
  "total_redemptions": 120,
  "redemption_rate": 80.0,
  "recent_activity": {
    "purchases_last_30_days": 45,
    "redemptions_last_30_days": 38
  },
  "top_performing_vouchers": [
    {
      "id": 1,
      "title": "50% Off Coffee",
      "purchase_count": 25,
      "redemption_count": 20,
      "popularity_score": 70
    }
  ]
}
```

### 3. Share Gift Card via WhatsApp

**Endpoint:** `POST /api/voucher/vouchers/{id}/share-gift-card/`

**Request Body:**

```json
{
  "phone_numbers": ["+919876543210", "+919876543211"]
}
```

**Response:**

```json
{
  "message": "Gift card shared successfully to 2 contacts",
  "success_count": 2,
  "failed_numbers": [],
  "shares_created": [
    {
      "phone_number": "+919876543210",
      "claim_reference": "GFT-12345678",
      "share_id": 1
    },
    {
      "phone_number": "+919876543211",
      "claim_reference": "GFT-87654321",
      "share_id": 2
    }
  ],
  "note": "Each recipient can claim and use the gift card independently"
}
```

### 4. Get Popular Vouchers

**Endpoint:** `GET /api/voucher/vouchers/popular/`

**Response:**

```json
{
  "popular_vouchers": [
    {
      "id": 1,
      "title": "50% Off Coffee",
      "merchant": "Coffee Shop",
      "purchase_count": 25,
      "redemption_count": 20,
      "popularity_score": 70,
      "voucher_type": "percentage",
      "category": "Food & Beverage",
      "image": "http://example.com/image.jpg"
    }
  ],
  "total_count": 10,
  "message": "Popular vouchers based on purchase and redemption activity"
}
```

---

## 🌐 Public Voucher Discovery APIs

### 1. Browse Vouchers

**Endpoint:** `GET /api/voucher/public-vouchers/`

**Query Parameters:**

- `category`: Filter by category ID
- `merchant`: Filter by merchant ID
- `voucher_type`: Filter by voucher type
- `search`: Search by title/message/merchant

**Response:**

```json
{
  "count": 50,
  "next": "http://api.example.com/public-vouchers/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "50% Off Coffee",
      "message": "Get 50% off on any coffee",
      "merchant_name": "Coffee Shop",
      "voucher_type_name": "percentage",
      "voucher_value": "50% off (min bill: ₹100)",
      "purchase_cost": "10 points",
      "is_purchased": false,
      "can_purchase": true
    }
  ]
}
```

### 2. Get Featured Vouchers

**Endpoint:** `GET /api/voucher/public-vouchers/featured/`

**Response:**

```json
{
    "featured_vouchers": [...],
    "total_count": 10,
    "message": "Featured vouchers based on popularity"
}
```

### 3. Get Trending Vouchers

**Endpoint:** `GET /api/voucher/public-vouchers/trending/`

**Response:**

```json
{
    "trending_vouchers": [...],
    "total_count": 10,
    "period": "Last 7 days",
    "message": "Trending vouchers based on recent purchase activity"
}
```

---

## 🛒 User Voucher Purchase & Management APIs

### 1. Purchase Voucher

**Endpoint:** `POST /api/voucher/voucher-purchase/purchase/`

**Request Body:**

```json
{
  "voucher_id": 123
}
```

**Response:**

```json
{
  "message": "Voucher purchased successfully",
  "voucher_id": 123,
  "voucher_title": "50% Off Coffee",
  "purchase_cost": 10.0,
  "remaining_balance": 90.0,
  "redemption_id": 456,
  "purchase_reference": "VCH-12345678",
  "expiry_date": "2024-12-31T23:59:59Z",
  "transaction_id": "WT-789-20241201120000"
}
```

### 2. Cancel Purchase

**Endpoint:** `POST /api/voucher/voucher-purchase/cancel/`

**Request Body:**

```json
{
  "redemption_id": 456,
  "reason": "Changed my mind"
}
```

**Response:**

```json
{
  "message": "Voucher purchase cancelled successfully",
  "voucher_title": "50% Off Coffee",
  "purchase_reference": "VCH-12345678",
  "purchase_status": "cancelled",
  "transaction_id": "WT-789-20241201120000"
}
```

### 3. Refund Purchase

**Endpoint:** `POST /api/v1/voucher-purchase/refund/`

**Request Body:**

```json
{
  "redemption_id": 456,
  "reason": "Not satisfied with service"
}
```

**Response:**

```json
{
  "message": "Voucher purchase refunded successfully",
  "voucher_title": "50% Off Coffee",
  "purchase_reference": "VCH-12345678",
  "refund_amount": 10.0,
  "remaining_balance": 100.0,
  "purchase_status": "refunded",
  "transaction_id": "WT-789-20241201120000"
}
```

### 4. Get User Vouchers

**Endpoint:** `GET /api/v1/user-vouchers/`

**Query Parameters:**

- `purchase_status`: Filter by status (purchased, redeemed, expired, cancelled, refunded)
- `is_gift_voucher`: Filter gift vouchers

**Response:**

```json
{
  "count": 15,
  "results": [
    {
      "id": 456,
      "voucher_title": "50% Off Coffee",
      "merchant_name": "Coffee Shop",
      "voucher_type": "percentage",
      "voucher_value": "50% off (min bill: ₹100)",
      "purchased_at": "2024-01-01T10:00:00Z",
      "expiry_date": "2024-12-31T23:59:59Z",
      "purchase_status": "purchased",
      "can_redeem": true,
      "remaining_redemptions": 1
    }
  ]
}
```

### 5. Get Voucher QR Code

**Endpoint:** `GET /api/v1/user-vouchers/{id}/qr-code/`

**Response:**

```json
{
  "message": "Voucher QR code data",
  "voucher_details": {
    "id": 1,
    "title": "50% Off Coffee",
    "merchant_name": "Coffee Shop",
    "voucher_type": "percentage",
    "voucher_value": "50% off (min bill: ₹100)",
    "purchased_at": "2024-01-01T10:00:00Z",
    "expiry_date": "2024-12-31T23:59:59Z",
    "remaining_redemptions": 1
  },
  "qr_code_data": {
    "purchase_reference": "VCH-12345678",
    "redemption_id": 456,
    "voucher_uuid": "550e8400-e29b-41d4-a716-446655440000"
  },
  "redemption_instructions": "Show this QR code to the merchant for redemption"
}
```

---

## 📱 WhatsApp Contact Management APIs

### 1. Sync Phone Contacts

**Endpoint:** `POST /api/v1/whatsapp-contacts/sync-contacts/`

**Request Body:**

```json
{
  "contacts": [
    {
      "name": "John Doe",
      "phone_number": "+919876543210"
    },
    {
      "name": "Jane Smith",
      "phone_number": "+919876543211"
    }
  ]
}
```

**Response:**

```json
{
  "message": "Synced 2 contacts, 2 on WhatsApp",
  "whatsapp_contacts": [
    {
      "id": 1,
      "name": "John Doe",
      "phone_number": "+919876543210",
      "is_on_whatsapp": true
    },
    {
      "id": 2,
      "name": "Jane Smith",
      "phone_number": "+919876543211",
      "is_on_whatsapp": true
    }
  ]
}
```

### 2. Get WhatsApp Contacts

**Endpoint:** `GET /api/v1/whatsapp-contacts/whatsapp-contacts/`

**Response:**

```json
[
  {
    "id": 1,
    "name": "John Doe",
    "phone_number": "+919876543210",
    "is_on_whatsapp": true
  }
]
```

---

## 🎁 Gift Card Sharing & Claiming APIs

### 1. Claim Gift Card

**Endpoint:** `POST /api/v1/gift-card-claim/claim/`

**Request Body:**

```json
{
  "claim_reference": "GFT-12345678"
}
```

**Response:**

```json
{
  "message": "Gift card claimed successfully!",
  "gift_card_details": {
    "id": 789,
    "title": "Free Coffee Gift Card",
    "merchant": "Coffee Shop",
    "voucher_type": "product",
    "voucher_value": "Free Coffee (min bill: ₹0)",
    "expiry_date": "2024-12-31T23:59:59Z",
    "purchase_reference": "GFT-12345678",
    "claim_reference": "GFT-12345678"
  },
  "redemption_instructions": "You can now use this gift card at the merchant location"
}
```

### 2. Get My Gift Cards

**Endpoint:** `GET /api/v1/gift-card-claim/my-gift-cards/`

**Response:**

```json
{
  "gift_cards": [
    {
      "id": 789,
      "title": "Free Coffee Gift Card",
      "merchant": "Coffee Shop",
      "voucher_type": "product",
      "voucher_value": "Free Coffee (min bill: ₹0)",
      "purchased_at": "2024-01-01T12:00:00Z",
      "expiry_date": "2024-12-31T23:59:59Z",
      "purchase_reference": "GFT-12345678",
      "purchase_status": "purchased",
      "can_redeem": true,
      "remaining_redemptions": 1
    }
  ],
  "total_count": 1,
  "message": "Your claimed gift cards"
}
```

### 3. Get Shared by Me

**Endpoint:** `GET /api/v1/gift-card-claim/shared-by-me/`

**Response:**

```json
{
  "shares": [
    {
      "share_id": 1,
      "recipient_phone": "+919876543210",
      "recipient_name": "John Doe",
      "voucher_title": "Free Coffee Gift Card",
      "shared_via": "whatsapp",
      "shared_at": "2024-01-01T10:00:00Z",
      "is_claimed": true,
      "claimed_at": "2024-01-01T12:00:00Z",
      "claim_reference": "GFT-12345678"
    }
  ],
  "total_count": 1,
  "message": "Gift cards shared by you"
}
```

---

## 📱 Merchant Voucher Scanning & Redemption APIs

### 1. Scan Voucher

**Endpoint:** `POST /api/v1/merchant/scan/scan/`

**Request Body:**

```json
{
  "qr_data": "VCH-12345678"
}
```

**Response:**

```json
{
  "message": "Voucher found and eligible for redemption",
  "voucher_details": {
    "id": 1,
    "title": "50% Off Coffee",
    "voucher_type": "percentage",
    "voucher_value": "50% off (min bill: ₹100)",
    "user_info": {
      "name": "John Doe",
      "phone": "+919876543210",
      "is_original_purchaser": true
    },
    "purchased_at": "2024-01-01T10:00:00Z",
    "expiry_date": "2024-12-31T23:59:59Z",
    "remaining_redemptions": 1,
    "purchase_reference": "VCH-12345678",
    "redemption_id": 456,
    "is_gift_card": false
  },
  "can_redeem": true
}
```

### 2. Redeem Voucher

**Endpoint:** `POST /api/v1/merchant/scan/redeem/`

**Request Body:**

```json
{
  "redemption_id": 456,
  "location": "Main Store",
  "notes": "Customer was very happy",
  "quantity": 1
}
```

**Response:**

```json
{
  "message": "Voucher redeemed successfully",
  "voucher_title": "50% Off Coffee",
  "user_name": "John Doe",
  "redeemed_at": "2024-01-01T15:00:00Z",
  "redemption_location": "Main Store",
  "purchase_reference": "VCH-12345678",
  "quantity_redeemed": 1,
  "remaining_redemptions": 0,
  "merchant_name": "Coffee Shop",
  "transaction_id": "WT-789-20241201120000"
}
```

---

## 📢 Advertisement Management APIs

### 1. Create Advertisement

**Endpoint:** `POST /api/v1/advertisements/`

**Request Body:**

```json
{
  "voucher": 1,
  "banner_image": "<file_upload>",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "city": "Mumbai",
  "state": "Maharashtra"
}
```

**Response:**

```json
{
  "message": "Advertisement created successfully",
  "advertisement_id": 1,
  "voucher_title": "50% Off Coffee",
  "cost_deducted": 10.0,
  "remaining_balance": 90.0,
  "transaction_note": "Advertisement Creation: 50% Off Coffee"
}
```

### 2. Get Active Advertisements

**Endpoint:** `GET /api/v1/advertisements/active/`

**Response:**

```json
[
  {
    "id": 1,
    "voucher_title": "50% Off Coffee",
    "merchant_name": "Coffee Shop",
    "banner_image": "http://example.com/banner.jpg",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "city": "Mumbai",
    "state": "Maharashtra"
  }
]
```

### 3. Get Advertisements by Location

**Endpoint:** `GET /api/v1/advertisements/by-location/?city=Mumbai&state=Maharashtra`

**Response:**

```json
{
    "advertisements": [...],
    "total_count": 5,
    "location": "Mumbai, Maharashtra",
    "message": "Advertisements available in Mumbai, Maharashtra"
}
```

---

## 🚨 Error Handling

### Common Error Responses

#### 400 Bad Request

```json
{
  "error": "Voucher not found or invalid QR code",
  "debug_info": {
    "qr_data_received": "INVALID-123",
    "qr_data_type": "string",
    "message": "Please check if the voucher exists and the QR code is valid"
  }
}
```

#### 401 Unauthorized

```json
{
  "error": "Authentication required. Please provide a valid JWT token."
}
```

#### 403 Forbidden

```json
{
  "error": "Access denied. You can only scan vouchers from your own business.",
  "debug_info": {
    "voucher_merchant": "Coffee Shop",
    "current_merchant": "Different Shop"
  }
}
```

#### 500 Internal Server Error

```json
{
  "error": "An unexpected error occurred. Please try again.",
  "debug_info": {
    "error_type": "ValidationError",
    "error_message": "Voucher has expired",
    "traceback": "Traceback hidden in production"
  }
}
```

---

## 🧪 Testing Examples

### Complete Gift Card Flow Test

#### Step 1: Create Gift Card Voucher

```bash
curl -X POST "http://localhost:8000/api/v1/vouchers/" \
  -H "Authorization: Bearer <MERCHANT_JWT>" \
  -H "X-API-Key: <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Free Coffee Gift Card",
    "message": "Enjoy a free coffee on us!",
    "voucher_type": 3,
    "product_name": "Coffee",
    "is_gift_card": true,
    "is_active": true
  }'
```

#### Step 2: User Purchases Gift Card

```bash
curl -X POST "http://localhost:8000/api/v1/voucher-purchase/purchase/" \
  -H "Authorization: Bearer <USER_JWT>" \
  -H "X-API-Key: <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"voucher_id": 1}'
```

#### Step 3: User Shares Gift Card

```bash
curl -X POST "http://localhost:8000/api/v1/vouchers/1/share-gift-card/" \
  -H "Authorization: Bearer <USER_JWT>" \
  -H "X-API-Key: <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"phone_numbers": ["+919876543210"]}'
```

#### Step 4: Recipient Claims Gift Card

```bash
curl -X POST "http://localhost:8000/api/v1/gift-card-claim/claim/" \
  -H "Authorization: Bearer <RECIPIENT_JWT>" \
  -H "X-API-Key: <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"claim_reference": "GFT-12345678"}'
```

#### Step 5: Merchant Scans Gift Card

```bash
curl -X POST "http://localhost:8000/api/v1/merchant/scan/scan/" \
  -H "Authorization: Bearer <MERCHANT_JWT>" \
  -H "X-API-Key: <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"qr_data": "GFT-12345678"}'
```

#### Step 6: Merchant Redeems Gift Card

```bash
curl -X POST "http://localhost:8000/api/v1/merchant/scan/redeem/" \
  -H "Authorization: Bearer <MERCHANT_JWT>" \
  -H "X-API-Key: <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "redemption_id": 789,
    "location": "Main Store",
    "notes": "Gift card redeemed successfully",
    "quantity": 1
  }'
```

---

## 📊 Database Models Summary

### Core Models

- **Voucher**: Main voucher entity with type-specific fields
- **UserVoucherRedemption**: Tracks user purchases and redemptions
- **GiftCardShare**: Manages gift card sharing and claiming
- **WhatsAppContact**: User contacts for WhatsApp sharing
- **Advertisement**: Location-based voucher promotion

### Key Relationships

- One Voucher can have many UserVoucherRedemptions
- One UserVoucherRedemption can have many GiftCardShares
- Each GiftCardShare creates a new UserVoucherRedemption for recipient
- Merchants can only scan vouchers from their own business

---

## 🔧 Configuration

### Environment Variables

```bash
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# WhatsApp Integration (configure based on your provider)
WHATSAPP_API_KEY=your-whatsapp-api-key
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id

# File Storage
MEDIA_URL=/media/
MEDIA_ROOT=/path/to/media/
```

### Site Settings

```python
# Configurable via Django Admin
voucher_cost = 10  # Points required to purchase voucher
advertisement_cost = 10  # Points required to create advertisement
advertisement_extension_cost_per_day = 1  # Points per day for extension
```

---

## 📝 Notes

1. **Multi-User Gift Cards**: The system allows one gift card to be shared with multiple users, each getting their own redemption record
2. **WhatsApp Integration**: Gift cards are automatically sent via WhatsApp when shared
3. **Merchant Security**: Merchants can only scan and redeem vouchers from their own business
4. **Atomic Transactions**: All critical operations use database transactions for data consistency
5. **QR Code Formats**: Supports multiple QR code formats (VCH-XXXXXXXX, GFT-XXXXXXXX, redemption ID, UUID)
6. **Wallet Integration**: Vouchers are purchased using wallet points, with configurable costs

This API system provides a complete voucher management solution with gift card sharing capabilities, merchant scanning, and comprehensive user management.
