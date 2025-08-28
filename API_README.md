# 🚀 Bartr API Documentation

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL](#base-url)
4. [API Endpoints](#api-endpoints)
   - [Authentication APIs](#authentication-apis)
   - [User Management APIs](#user-management-apis)
   - [Merchant Profile APIs](#merchant-profile-apis)
   - [Wallet APIs](#wallet-apis)
   - [Voucher Management APIs](#voucher-management-apis)
   - [Voucher Purchase APIs](#voucher-purchase-apis)
   - [User Voucher APIs](#user-voucher-apis)
   - [WhatsApp Contact APIs](#whatsapp-contact-apis)
   - [Gift Card APIs](#gift-card-apis)
   - [Advertisement APIs](#advertisement-apis)
   - [Category APIs](#category-apis)
5. [Error Handling](#error-handling)
6. [Testing Examples](#testing-examples)

## 🎯 Overview

Bartr is a comprehensive voucher management platform that enables:

- **Merchants** to create, manage, and promote vouchers
- **Users** to discover, purchase, and redeem vouchers
- **Gift Card Sharing** via WhatsApp with multi-user claiming
- **Wallet Integration** for point-based purchases
- **Merchant Scanning** for voucher redemption
- **Location-based Advertisement** management

## 🔐 Authentication

All API endpoints require JWT token authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

### Getting JWT Token

```http
POST /api/custom_auth/v1/auth/classic/
```

**Request Body:**

```json
{
  "phone": "+919876543210"
}
```

**Response:**

```json
{
  "message": "Login Successful",
  "data": {
    "id": 1,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "phone": "+919876543210",
    "fullname": "John Doe",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "success": "true"
}
```

## 🌐 Base URL

```
Base URL: http://localhost:8000/api/
Swagger UI: http://localhost:8000/swagger/
```

---

## 🔑 Authentication APIs

### 1. User Authentication

**Endpoint:** `POST /api/custom_auth/v1/auth/classic/`

**Description:** Authenticate user using phone number and return JWT tokens.

**Request Body:**

```json
{
  "phone": "+919876543210"
}
```

**Response:**

```json
{
  "message": "Login Successful",
  "data": {
    "id": 1,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "phone": "+919876543210",
    "fullname": "John Doe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "photo": null,
    "gender": "male",
    "is_merchant": false,
    "merchant_id": null,
    "address": "123 Main St",
    "area": "Downtown",
    "pin": "400001",
    "city": "Mumbai",
    "state": "Maharashtra",
    "is_active": true,
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "success": "true"
}
```

---

## 👤 User Management APIs

### 1. Get User Profile

**Endpoint:** `GET /api/custom_auth/v1/users/me/`

**Description:** Get current user's profile information.

**Headers:**

```http
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "id": 1,
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "phone": "+919876543210",
  "fullname": "John Doe",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "photo": null,
  "gender": "male",
  "is_merchant": false,
  "merchant_id": null,
  "address": "123 Main St",
  "area": "Downtown",
  "pin": "400001",
  "city": "Mumbai",
  "state": "Maharashtra",
  "is_active": true
}
```

### 2. Update User Profile

**Endpoint:** `PUT /api/custom_auth/v1/users/me/`

**Description:** Update current user's profile information.

**Request Body:**

```json
{
  "fullname": "John Smith",
  "email": "johnsmith@example.com",
  "address": "456 New St",
  "city": "Pune",
  "state": "Maharashtra"
}
```

**Response:** Updated user profile data

### 3. Update User Photo

**Endpoint:** `POST /api/custom_auth/v1/users/{id}/photos/update_or_create/`

**Description:** Update or create user profile photo.

**Request Body:** Form data with photo file

**Response:** Updated user data with photo URL

---

## 🏪 Merchant Profile APIs

### 1. Create Merchant Profile

**Endpoint:** `POST /api/custom_auth/v1/merchant_profile/`

**Description:** Create a new merchant profile for the authenticated user.

**Request Body:**

```json
{
  "business_name": "Coffee Shop",
  "business_type": "Restaurant",
  "description": "Best coffee in town",
  "address": "123 Coffee St",
  "city": "Mumbai",
  "state": "Maharashtra",
  "pin": "400001",
  "phone": "+919876543210",
  "email": "coffee@example.com",
  "logo": "<file_upload>",
  "banner_image": "<file_upload>"
}
```

**Response:**

```json
{
  "id": 1,
  "business_name": "Coffee Shop",
  "business_type": "Restaurant",
  "description": "Best coffee in town",
  "address": "123 Coffee St",
  "city": "Mumbai",
  "state": "Maharashtra",
  "pin": "400001",
  "phone": "+919876543210",
  "email": "coffee@example.com",
  "logo": "http://localhost:8000/media/merchant/logo/logo.jpg",
  "banner_image": "http://localhost:8000/media/merchant/banner/banner.jpg",
  "is_active": true,
  "create_time": "2024-01-01T10:00:00Z"
}
```

### 2. Get Merchant Profile

**Endpoint:** `GET /api/custom_auth/v1/merchant_profile/{id}/`

**Description:** Get merchant profile details.

**Response:** Merchant profile data

### 3. Update Merchant Profile

**Endpoint:** `PUT /api/custom_auth/v1/merchant_profile/{id}/`

**Description:** Update merchant profile information.

**Request Body:** Partial merchant profile data

**Response:** Updated merchant profile data

### 4. List Merchants

**Endpoint:** `GET /api/custom_auth/v1/merchants/list/`

**Description:** Get list of all active merchants.

**Query Parameters:**

- `search`: Search by business name
- `city`: Filter by city
- `state`: Filter by state
- `business_type`: Filter by business type

**Response:**

```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "business_name": "Coffee Shop",
      "business_type": "Restaurant",
      "city": "Mumbai",
      "state": "Maharashtra",
      "logo": "http://localhost:8000/media/merchant/logo/logo.jpg"
    }
  ]
}
```

---

## 💰 Wallet APIs

### 1. Get Wallet Balance

**Endpoint:** `GET /api/custom_auth/v1/wallet/`

**Description:** Get current user's wallet balance.

**Response:**

```json
{
  "id": 1,
  "user": 1,
  "balance": 150.0,
  "is_active": true,
  "create_time": "2024-01-01T10:00:00Z",
  "update_time": "2024-01-01T10:00:00Z"
}
```

### 2. Get Wallet History

**Endpoint:** `GET /api/custom_auth/v1/wallet/history/`

**Description:** Get wallet transaction history.

**Query Parameters:**

- `transaction_type`: Filter by type (credit, debit)
- `reference_note`: Filter by reference note
- `ordering`: Sort by create_time or amount

**Response:**

```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "transaction_type": "credit",
      "amount": 100.0,
      "reference_note": "Razorpay payment - order_ABC123",
      "reference_id": "order_ABC123",
      "meta": {
        "points_added": 100.0,
        "transaction_type": "points_credit"
      },
      "create_time": "2024-01-01T10:00:00Z"
    }
  ]
}
```

### 3. Get Wallet Summary

**Endpoint:** `GET /api/custom_auth/v1/wallet/summary/`

**Description:** Get wallet summary statistics.

**Response:**

```json
{
  "total_balance": 150.0,
  "total_credits": 200.0,
  "total_debits": 50.0,
  "recent_transactions": 5,
  "last_transaction": "2024-01-01T10:00:00Z"
}
```

### 4. Razorpay Wallet Integration

#### Create Razorpay Order

**Endpoint:** `POST /api/custom_auth/v1/wallet/razorpay/create-order/`

**Description:** Create Razorpay order for wallet recharge.

**Request Body:**

```json
{
  "amount": 100.0,
  "currency": "INR",
  "description": "Wallet recharge",
  "receipt": "optional_receipt_id"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "order_id": "order_ABC123",
    "amount": 100.0,
    "currency": "INR",
    "receipt": "wallet_recharge_123_1234567890",
    "transaction_id": 1
  }
}
```

#### Verify Payment

**Endpoint:** `POST /api/custom_auth/v1/wallet/razorpay/verify-payment/`

**Description:** Verify Razorpay payment and add points to wallet.

**Request Body:**

```json
{
  "razorpay_order_id": "order_ABC123",
  "razorpay_payment_id": "pay_XYZ789",
  "razorpay_signature": "generated_signature"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "transaction_id": 1,
    "amount": 100.0,
    "points_added": 100.0,
    "wallet_balance": 150.0,
    "payment_id": "pay_XYZ789"
  }
}
```

#### List Razorpay Transactions

**Endpoint:** `GET /api/custom_auth/v1/wallet/razorpay/transactions/`

**Description:** List all Razorpay transactions for the user.

**Response:**

```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "razorpay_order_id": "order_ABC123",
      "razorpay_payment_id": "pay_XYZ789",
      "amount": 100.0,
      "points_to_add": 100.0,
      "currency": "INR",
      "status": "success",
      "create_time": "2024-01-01T10:00:00Z"
    }
  ]
}
```

---

## 🎫 Voucher Management APIs

### 1. Create Voucher

**Endpoint:** `POST /api/voucher/v1/voucher/`

**Description:** Create a new voucher (merchant only).

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
  "category": 1
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
  "category": 1
}
```

### 2. Get Voucher Statistics

**Endpoint:** `GET /api/voucher/v1/voucher/statistics/`

**Description:** Get voucher statistics for merchant.

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

**Endpoint:** `POST /api/voucher/v1/voucher/{id}/share-gift-card/`

**Description:** Share gift card voucher with WhatsApp contacts.

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
    }
  ]
}
```

### 4. Get Popular Vouchers

**Endpoint:** `GET /api/voucher/v1/voucher/popular/`

**Description:** Get popular vouchers based on activity.

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
      "popularity_score": 70
    }
  ]
}
```

---

## 🌐 Public Voucher Discovery APIs

### 1. Browse Vouchers

**Endpoint:** `GET /api/voucher/v1/public/vouchers/`

**Description:** Browse public vouchers (no authentication required).

**Query Parameters:**

- `category`: Filter by category ID
- `merchant`: Filter by merchant ID
- `voucher_type`: Filter by voucher type
- `search`: Search by title/message/merchant

**Response:**

```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "title": "50% Off Coffee",
      "message": "Get 50% off on any coffee",
      "merchant_name": "Coffee Shop",
      "voucher_type_name": "percentage",
      "voucher_value": "50% off",
      "purchase_cost": "10 points",
      "is_purchased": false,
      "can_purchase": true
    }
  ]
}
```

### 2. Get Featured Vouchers

**Endpoint:** `GET /api/voucher/v1/public/vouchers/featured/`

**Description:** Get featured vouchers based on popularity.

**Response:** List of featured vouchers

### 3. Get Trending Vouchers

**Endpoint:** `GET /api/voucher/v1/public/vouchers/trending/`

**Description:** Get trending vouchers based on recent activity.

**Response:** List of trending vouchers

---

## 🛒 Voucher Purchase APIs

### 1. Purchase Voucher

**Endpoint:** `POST /api/voucher/v1/purchase/purchase/`

**Description:** Purchase a voucher using wallet points.

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
  "expiry_date": "2024-12-31T23:59:59Z"
}
```

### 2. Cancel Purchase

**Endpoint:** `POST /api/voucher/v1/purchase/cancel/`

**Description:** Cancel a voucher purchase.

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
  "purchase_status": "cancelled"
}
```

### 3. Refund Purchase

**Endpoint:** `POST /api/voucher/v1/purchase/refund/`

**Description:** Refund a voucher purchase.

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
  "refund_amount": 10.0,
  "remaining_balance": 100.0,
  "purchase_status": "refunded"
}
```

---

## 📱 User Voucher APIs

### 1. Get User Vouchers

**Endpoint:** `GET /api/voucher/v1/my-vouchers/`

**Description:** Get current user's purchased vouchers.

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

### 2. Get Voucher QR Code

**Endpoint:** `GET /api/voucher/v1/my-vouchers/{id}/qr-code/`

**Description:** Get QR code data for voucher redemption.

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
  }
}
```

---

## 📞 WhatsApp Contact APIs

### 1. Sync Phone Contacts

**Endpoint:** `POST /api/voucher/v1/whatsapp-contacts/sync-contacts/`

**Description:** Synchronize user's phone contacts and check WhatsApp availability.

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
    }
  ]
}
```

### 2. Get WhatsApp Contacts

**Endpoint:** `GET /api/voucher/v1/whatsapp-contacts/whatsapp-contacts/`

**Description:** Get contacts that are available on WhatsApp.

**Response:** List of WhatsApp contacts

---

## 🎁 Gift Card APIs

### 1. Claim Gift Card

**Endpoint:** `POST /api/voucher/v1/gift-card-claim/claim/`

**Description:** Claim a shared gift card.

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
  }
}
```

### 2. Get My Gift Cards

**Endpoint:** `GET /api/voucher/v1/gift-card-claim/my-gift-cards/`

**Description:** Get user's claimed gift cards.

**Response:** List of claimed gift cards

### 3. Get Shared by Me

**Endpoint:** `GET /api/voucher/v1/gift-card-claim/shared-by-me/`

**Description:** Get gift cards shared by the current user.

**Response:** List of shared gift cards

---

## 📢 Advertisement APIs

### 1. Create Advertisement

**Endpoint:** `POST /api/voucher/v1/advertisements/`

**Description:** Create advertisement for voucher promotion.

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
  "remaining_balance": 90.0
}
```

### 2. Get Active Advertisements

**Endpoint:** `GET /api/voucher/v1/advertisements/active/`

**Description:** Get active advertisements.

**Response:** List of active advertisements

### 3. Get Advertisements by Location

**Endpoint:** `GET /api/voucher/v1/advertisements/by-location/?city=Mumbai&state=Maharashtra`

**Description:** Get advertisements by location.

**Response:** List of advertisements in specified location

---

## 🏷️ Category APIs

### 1. List Categories

**Endpoint:** `GET /api/custom_auth/v1/category/`

**Description:** Get list of all categories.

**Response:**

```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "Food & Beverage",
      "image": "http://localhost:8000/media/category/food.jpg",
      "is_active": true
    }
  ]
}
```

### 2. Create Category

**Endpoint:** `POST /api/custom_auth/v1/category/`

**Description:** Create a new category (admin only).

**Request Body:**

```json
{
  "name": "Food & Beverage",
  "image": "<file_upload>"
}
```

**Response:** Created category data

---

## 🚨 Error Handling

### Common Error Responses

#### 400 Bad Request

```json
{
  "error": "Validation error",
  "detail": "Field 'phone' is required"
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
  "error": "Access denied. You don't have permission to perform this action."
}
```

#### 404 Not Found

```json
{
  "error": "Resource not found"
}
```

#### 500 Internal Server Error

```json
{
  "error": "An unexpected error occurred. Please try again."
}
```

---

## 🧪 Testing Examples

### Complete Voucher Flow Test

#### Step 1: User Authentication

```bash
curl -X POST "http://localhost:8000/api/custom_auth/v1/auth/classic/" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'
```

#### Step 2: Create Merchant Profile

```bash
curl -X POST "http://localhost:8000/api/custom_auth/v1/merchant_profile/" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "Coffee Shop",
    "business_type": "Restaurant",
    "description": "Best coffee in town",
    "city": "Mumbai",
    "state": "Maharashtra"
  }'
```

#### Step 3: Create Voucher

```bash
curl -X POST "http://localhost:8000/api/voucher/v1/voucher/" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "50% Off Coffee",
    "message": "Get 50% off on any coffee",
    "voucher_type": 1,
    "percentage_value": 50.0,
    "percentage_min_bill": 100.0
  }'
```

#### Step 4: Purchase Voucher

```bash
curl -X POST "http://localhost:8000/api/voucher/v1/purchase/purchase/" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"voucher_id": 1}'
```

#### Step 5: Share Gift Card

```bash
curl -X POST "http://localhost:8000/api/voucher/v1/voucher/1/share-gift-card/" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"phone_numbers": ["+919876543210"]}'
```

---

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

```python
# Configurable via Django Admin
voucher_cost = 10  # Points required to purchase voucher
gift_card_cost = 10  # Points required to purchase gift card
advertisement_cost = 10  # Points required to create advertisement
```

---

## 📊 Database Models Summary

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

### Key Relationships

- One User can have one Wallet
- One User can have one MerchantProfile
- One MerchantProfile can have many Vouchers
- One Voucher can have many UserVoucherRedemptions
- One UserVoucherRedemption can have many GiftCardShares

---

## 📝 Notes

1. **Multi-User Gift Cards**: The system allows one gift card to be shared with multiple users
2. **WhatsApp Integration**: Gift cards are automatically sent via WhatsApp when shared
3. **Merchant Security**: Merchants can only manage their own vouchers and scan their own vouchers
4. **Atomic Transactions**: All critical operations use database transactions for data consistency
5. **Wallet Integration**: Vouchers are purchased using wallet points, with configurable costs
6. **Location Targeting**: Advertisements support city/state-based targeting

This API system provides a complete voucher management solution with gift card sharing capabilities, merchant scanning, and comprehensive user management.
