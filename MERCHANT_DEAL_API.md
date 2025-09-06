# 🏪 Merchant-to-Merchant Deal System API Documentation

## Overview

This system allows merchants to create deals with points and request deals from other merchants. When a deal is created, points are deducted from the merchant's wallet. Merchants can only use deal points between each other for exchanges and discounts.

## Base URL

```
http://localhost:8000/api/custom-auth/
```

## Authentication

All endpoints require JWT authentication:

```json
{
  "Authorization": "Bearer YOUR_JWT_TOKEN"
}
```

## Core Features

- **Deal Creation**: Merchants create deals with points (deducted from wallet)
- **Deal Discovery**: Browse other merchants' deals with point-based filtering
- **Request System**: Request deals instead of swiping
- **Deal Confirmation**: Accept/reject deal requests
- **Points Transfer**: Automatic points transfer when deals are completed
- **Usage Tracking**: Complete audit trail of how deal points are used
- **Notifications**: Real-time notifications for all actions

---

## 🎯 1. Merchant Deals Management

### 1.1 Create a Deal

**URL:** `POST /api/custom-auth/v1/merchant-deals/`

**Headers:**

```json
{
  "Authorization": "Bearer YOUR_JWT_TOKEN",
  "Content-Type": "application/json"
}
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

**Response (201 Created):**

```json
{
  "id": 1,
  "merchant": 1,
  "merchant_name": "Tech Store",
  "merchant_logo": "http://localhost:8000/media/merchant/logo/tech_logo.jpg",
  "title": "Electronics Exchange Deal",
  "description": "Exchange electronics for 2000 points",
  "points_offered": 2000.0,
  "points_used": 0.0,
  "points_remaining": 2000.0,
  "deal_value": 2500.0,
  "category": 1,
  "category_name": "Electronics",
  "status": "active",
  "expiry_date": "2024-12-31T23:59:59Z",
  "is_expired": false,
  "preferred_cities": ["Mumbai", "Delhi"],
  "preferred_categories": [1, 2],
  "terms_conditions": "Valid for 30 days",
  "is_negotiable": true,
  "request_count": 0,
  "confirmation_count": 0,
  "create_time": "2024-01-15T10:30:00Z"
}
```

**Note:** Points are automatically deducted from merchant's wallet when deal is created.

### 1.2 Get My Deals List

**URL:** `GET /api/custom-auth/v1/merchant-deals/`

**Query Parameters:**

- `status`: Filter by status (active, inactive, expired, completed, cancelled)
- `category`: Filter by category ID
- `points_offered`: Filter by points offered
- `search`: Search in title or description
- `ordering`: Order by field (create_time, points_offered, etc.)

**Example:**

```
GET /api/custom-auth/v1/merchant-deals/?status=active&category=1&ordering=-create_time
```

**Response (200 OK):**

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "merchant": 1,
      "merchant_name": "Tech Store",
      "merchant_logo": "http://localhost:8000/media/merchant/logo/tech_logo.jpg",
      "title": "Electronics Exchange Deal",
      "description": "Exchange electronics for 2000 points",
      "points_offered": 2000.0,
      "points_used": 500.0,
      "points_remaining": 1500.0,
      "deal_value": 2500.0,
      "category": 1,
      "category_name": "Electronics",
      "status": "active",
      "expiry_date": "2024-12-31T23:59:59Z",
      "is_expired": false,
      "preferred_cities": ["Mumbai", "Delhi"],
      "preferred_categories": [1, 2],
      "terms_conditions": "Valid for 30 days",
      "is_negotiable": true,
      "request_count": 2,
      "confirmation_count": 1,
      "create_time": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 1.3 Get Single Deal

**URL:** `GET /api/custom-auth/v1/merchant-deals/{id}/`

**Response (200 OK):**

```json
{
  "id": 1,
  "merchant": 1,
  "merchant_name": "Tech Store",
  "merchant_logo": "http://localhost:8000/media/merchant/logo/tech_logo.jpg",
  "title": "Electronics Exchange Deal",
  "description": "Exchange electronics for 2000 points",
  "points_offered": 2000.0,
  "points_used": 500.0,
  "points_remaining": 1500.0,
  "deal_value": 2500.0,
  "category": 1,
  "category_name": "Electronics",
  "status": "active",
  "expiry_date": "2024-12-31T23:59:59Z",
  "is_expired": false,
  "preferred_cities": ["Mumbai", "Delhi"],
  "preferred_categories": [1, 2],
  "terms_conditions": "Valid for 30 days",
  "is_negotiable": true,
  "request_count": 2,
  "confirmation_count": 1,
  "create_time": "2024-01-15T10:30:00Z"
}
```

### 1.4 Update Deal

**URL:** `PUT /api/custom-auth/v1/merchant-deals/{id}/` or `PATCH /api/custom-auth/v1/merchant-deals/{id}/`

**Request Body (PATCH):**

```json
{
  "title": "Updated Electronics Exchange Deal",
  "description": "Updated description",
  "points_offered": 2500.0,
  "deal_value": 3000.0,
  "is_negotiable": false
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "merchant": 1,
  "merchant_name": "Tech Store",
  "title": "Updated Electronics Exchange Deal",
  "description": "Updated description",
  "points_offered": 2500.0,
  "points_used": 500.0,
  "points_remaining": 2000.0,
  "deal_value": 3000.0,
  "status": "active",
  "is_negotiable": false,
  "create_time": "2024-01-15T10:30:00Z"
}
```

### 1.5 Delete Deal

**URL:** `DELETE /api/custom-auth/v1/merchant-deals/{id}/`

**Response (204 No Content):**

```
No content
```

### 1.6 Activate Deal

**URL:** `POST /api/custom-auth/v1/merchant-deals/{id}/activate/`

**Response (200 OK):**

```json
{
  "message": "Deal activated successfully"
}
```

### 1.7 Deactivate Deal

**URL:** `POST /api/custom-auth/v1/merchant-deals/{id}/deactivate/`

**Response (200 OK):**

```json
{
  "message": "Deal deactivated successfully"
}
```

### 1.8 Get Deal Usage History

**URL:** `GET /api/custom-auth/v1/merchant-deals/{id}/usage-history/`

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "deal": 1,
    "deal_title": "Electronics Exchange Deal",
    "confirmation": 1,
    "from_merchant": 1,
    "from_merchant_name": "Tech Store",
    "to_merchant": 2,
    "to_merchant_name": "Gadget Hub",
    "usage_type": "exchange",
    "points_used": 500.0,
    "usage_description": "Point exchange between Tech Store and Gadget Hub",
    "transaction_id": "DEAL_USAGE_A1B2C3D4",
    "create_time": "2024-01-15T12:00:00Z"
  }
]
```

---

## 🔍 2. Deal Discovery

### 2.1 Discover Available Deals

**URL:** `GET /api/custom-auth/v1/deal-discovery/`

**Query Parameters:**

- `category`: Filter by category ID
- `points_offered`: Filter by points offered
- `merchant__city`: Filter by city
- `search`: Search in title, description, or business name
- `min_points`: Minimum points filter
- `max_points`: Maximum points filter
- `ordering`: Order by field

**Example:**

```
GET /api/custom-auth/v1/deal-discovery/?category=1&min_points=1000&max_points=3000&search=electronics&ordering=-create_time
```

**Response (200 OK):**

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 2,
      "merchant": 2,
      "merchant_name": "Gadget Hub",
      "merchant_logo": "http://localhost:8000/media/merchant/logo/gadget_logo.jpg",
      "title": "Mobile Accessories Deal",
      "description": "Get mobile accessories for 1500 points",
      "points_offered": 1500.0,
      "points_remaining": 1500.0,
      "deal_value": 2000.0,
      "category": 1,
      "category_name": "Electronics",
      "status": "active",
      "is_expired": false,
      "preferred_cities": ["Mumbai"],
      "preferred_categories": [1],
      "terms_conditions": "Valid for 15 days",
      "is_negotiable": true,
      "request_count": 3,
      "confirmation_count": 1,
      "create_time": "2024-01-14T15:20:00Z"
    }
  ]
}
```

### 2.2 Get Deals by Specific Points

**URL:** `GET /api/custom-auth/v1/deal-discovery/by-points/?points=2000`

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "merchant": 1,
    "merchant_name": "Tech Store",
    "merchant_logo": "http://localhost:8000/media/merchant/logo/tech_logo.jpg",
    "title": "Electronics Exchange Deal",
    "description": "Exchange electronics for 2000 points",
    "points_offered": 2000.0,
    "points_remaining": 2000.0,
    "deal_value": 2500.0,
    "category": 1,
    "category_name": "Electronics",
    "status": "active",
    "is_expired": false,
    "request_count": 0,
    "confirmation_count": 0,
    "create_time": "2024-01-15T10:30:00Z"
  }
]
```

---

## 🤝 3. Deal Requests

### 3.1 Create Deal Request

**URL:** `POST /api/custom-auth/v1/deal-requests/`

**Request Body:**

```json
{
  "deal": 2,
  "points_requested": 1500.0,
  "message": "I'm interested in this mobile accessories deal. Can we discuss terms?",
  "counter_offer": 1200.0
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "requesting_merchant": 1,
  "requesting_merchant_name": "Tech Store",
  "deal": 2,
  "deal_title": "Mobile Accessories Deal",
  "deal_merchant": "Gadget Hub",
  "status": "pending",
  "request_time": "2024-01-15T11:00:00Z",
  "message": "I'm interested in this mobile accessories deal. Can we discuss terms?",
  "points_requested": 1500.0,
  "counter_offer": 1200.0
}
```

### 3.2 Get My Deal Requests

**URL:** `GET /api/custom-auth/v1/deal-requests/`

**Query Parameters:**

- `status`: Filter by status (pending, accepted, rejected, cancelled)
- `deal__category`: Filter by deal category
- `points_requested`: Filter by points requested
- `ordering`: Order by field

**Response (200 OK):**

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "requesting_merchant": 1,
      "requesting_merchant_name": "Tech Store",
      "deal": 2,
      "deal_title": "Mobile Accessories Deal",
      "deal_merchant": "Gadget Hub",
      "status": "pending",
      "request_time": "2024-01-15T11:00:00Z",
      "message": "I'm interested in this mobile accessories deal. Can we discuss terms?",
      "points_requested": 1500.0,
      "counter_offer": 1200.0
    }
  ]
}
```

### 3.3 Get Single Deal Request

**URL:** `GET /api/custom-auth/v1/deal-requests/{id}/`

**Response (200 OK):**

```json
{
  "id": 1,
  "requesting_merchant": 1,
  "requesting_merchant_name": "Tech Store",
  "deal": 2,
  "deal_title": "Mobile Accessories Deal",
  "deal_merchant": "Gadget Hub",
  "status": "pending",
  "request_time": "2024-01-15T11:00:00Z",
  "message": "I'm interested in this mobile accessories deal. Can we discuss terms?",
  "points_requested": 1500.0,
  "counter_offer": 1200.0
}
```

### 3.4 Update Deal Request

**URL:** `PUT /api/custom-auth/v1/deal-requests/{id}/` or `PATCH /api/custom-auth/v1/deal-requests/{id}/`

**Request Body (PATCH):**

```json
{
  "message": "Updated message with new terms",
  "counter_offer": 1300.0
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "requesting_merchant": 1,
  "requesting_merchant_name": "Tech Store",
  "deal": 2,
  "deal_title": "Mobile Accessories Deal",
  "deal_merchant": "Gadget Hub",
  "status": "pending",
  "request_time": "2024-01-15T11:00:00Z",
  "message": "Updated message with new terms",
  "points_requested": 1500.0,
  "counter_offer": 1300.0
}
```

### 3.5 Delete Deal Request

**URL:** `DELETE /api/custom-auth/v1/deal-requests/{id}/`

**Response (204 No Content):**

```
No content
```

### 3.6 Accept Deal Request

**URL:** `POST /api/custom-auth/v1/deal-requests/{id}/accept/`

**Response (200 OK):**

```json
{
  "message": "Deal request accepted successfully"
}
```

### 3.7 Reject Deal Request

**URL:** `POST /api/custom-auth/v1/deal-requests/{id}/reject/`

**Response (200 OK):**

```json
{
  "message": "Deal request rejected successfully"
}
```

---

## ✅ 4. Deal Confirmations

### 4.1 Get My Deal Confirmations

**URL:** `GET /api/custom-auth/v1/deal-confirmations/`

**Query Parameters:**

- `status`: Filter by status (pending, confirmed, cancelled, completed)
- `points_exchanged`: Filter by points exchanged
- `ordering`: Order by field

**Response (200 OK):**

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "deal": 2,
      "deal_title": "Mobile Accessories Deal",
      "merchant1": 2,
      "merchant1_name": "Gadget Hub",
      "merchant1_logo": "http://localhost:8000/media/merchant/logo/gadget_logo.jpg",
      "merchant2": 1,
      "merchant2_name": "Tech Store",
      "merchant2_logo": "http://localhost:8000/media/merchant/logo/tech_logo.jpg",
      "status": "confirmed",
      "confirmation_time": "2024-01-15T12:00:00Z",
      "completed_time": null,
      "points_exchanged": 1500.0,
      "deal_terms": "Exchange mobile accessories for 1500 points",
      "merchant1_notes": "Ready to proceed",
      "merchant2_notes": "Looking forward to collaboration"
    }
  ]
}
```

### 4.2 Get Single Deal Confirmation

**URL:** `GET /api/custom-auth/v1/deal-confirmations/{id}/`

**Response (200 OK):**

```json
{
  "id": 1,
  "deal": 2,
  "deal_title": "Mobile Accessories Deal",
  "merchant1": 2,
  "merchant1_name": "Gadget Hub",
  "merchant1_logo": "http://localhost:8000/media/merchant/logo/gadget_logo.jpg",
  "merchant2": 1,
  "merchant2_name": "Tech Store",
  "merchant2_logo": "http://localhost:8000/media/merchant/logo/tech_logo.jpg",
  "status": "confirmed",
  "confirmation_time": "2024-01-15T12:00:00Z",
  "completed_time": null,
  "points_exchanged": 1500.0,
  "deal_terms": "Exchange mobile accessories for 1500 points",
  "merchant1_notes": "Ready to proceed",
  "merchant2_notes": "Looking forward to collaboration"
}
```

### 4.3 Update Deal Confirmation

**URL:** `PUT /api/custom-auth/v1/deal-confirmations/{id}/` or `PATCH /api/custom-auth/v1/deal-confirmations/{id}/`

**Request Body (PATCH):**

```json
{
  "deal_terms": "Updated terms and conditions",
  "merchant1_notes": "Updated notes from merchant 1",
  "merchant2_notes": "Updated notes from merchant 2"
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "deal": 2,
  "deal_title": "Mobile Accessories Deal",
  "merchant1": 2,
  "merchant1_name": "Gadget Hub",
  "merchant2": 1,
  "merchant2_name": "Tech Store",
  "status": "confirmed",
  "confirmation_time": "2024-01-15T12:00:00Z",
  "points_exchanged": 1500.0,
  "deal_terms": "Updated terms and conditions",
  "merchant1_notes": "Updated notes from merchant 1",
  "merchant2_notes": "Updated notes from merchant 2"
}
```

### 4.4 Complete Deal

**URL:** `POST /api/custom-auth/v1/deal-confirmations/{id}/complete/`

**Response (200 OK):**

```json
{
  "message": "Deal completed and points transferred successfully"
}
```

### 4.5 Get Deal Confirmation Usage History

**URL:** `GET /api/custom-auth/v1/deal-confirmations/{id}/usage-history/`

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "deal": 2,
    "deal_title": "Mobile Accessories Deal",
    "confirmation": 1,
    "from_merchant": 2,
    "from_merchant_name": "Gadget Hub",
    "to_merchant": 1,
    "to_merchant_name": "Tech Store",
    "usage_type": "exchange",
    "points_used": 1500.0,
    "usage_description": "Point exchange between Gadget Hub and Tech Store",
    "transaction_id": "DEAL_USAGE_B2C3D4E5",
    "create_time": "2024-01-15T13:00:00Z"
  }
]
```

---

## 🔔 5. Notifications

### 5.1 Get Notifications

**URL:** `GET /api/custom-auth/v1/merchant-notifications/`

**Query Parameters:**

- `notification_type`: Filter by type (deal_request, deal_accepted, deal_rejected, deal_expired, points_transfer, system)
- `is_read`: Filter by read status (true/false)
- `ordering`: Order by field

**Response (200 OK):**

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "notification_type": "deal_request",
      "title": "New Deal Request!",
      "message": "Tech Store requested your deal \"Mobile Accessories Deal\"",
      "deal": 2,
      "is_read": false,
      "read_time": null,
      "action_url": "/merchant/deal-requests/1/",
      "action_data": {},
      "create_time": "2024-01-15T11:00:00Z"
    },
    {
      "id": 2,
      "notification_type": "points_transfer",
      "title": "Points Received",
      "message": "You received 1500.00 points from Gadget Hub",
      "deal": 2,
      "is_read": true,
      "read_time": "2024-01-15T13:30:00Z",
      "action_url": "/merchant/deal-confirmations/1/",
      "action_data": {},
      "create_time": "2024-01-15T13:00:00Z"
    }
  ]
}
```

### 5.2 Get Single Notification

**URL:** `GET /api/custom-auth/v1/merchant-notifications/{id}/`

**Response (200 OK):**

```json
{
  "id": 1,
  "notification_type": "deal_request",
  "title": "New Deal Request!",
  "message": "Tech Store requested your deal \"Mobile Accessories Deal\"",
  "deal": 2,
  "is_read": false,
  "read_time": null,
  "action_url": "/merchant/deal-requests/1/",
  "action_data": {},
  "create_time": "2024-01-15T11:00:00Z"
}
```

### 5.3 Update Notification

**URL:** `PUT /api/custom-auth/v1/merchant-notifications/{id}/` or `PATCH /api/custom-auth/v1/merchant-notifications/{id}/`

**Request Body (PATCH):**

```json
{
  "is_read": true
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "notification_type": "deal_request",
  "title": "New Deal Request!",
  "message": "Tech Store requested your deal \"Mobile Accessories Deal\"",
  "deal": 2,
  "is_read": true,
  "read_time": "2024-01-15T14:00:00Z",
  "action_url": "/merchant/deal-requests/1/",
  "action_data": {},
  "create_time": "2024-01-15T11:00:00Z"
}
```

### 5.4 Delete Notification

**URL:** `DELETE /api/custom-auth/v1/merchant-notifications/{id}/`

**Response (204 No Content):**

```
No content
```

### 5.5 Mark Notification as Read

**URL:** `POST /api/custom-auth/v1/merchant-notifications/{id}/mark-read/`

**Response (200 OK):**

```json
{
  "message": "Notification marked as read"
}
```

### 5.6 Mark All Notifications as Read

**URL:** `POST /api/custom-auth/v1/merchant-notifications/mark-all-read/`

**Response (200 OK):**

```json
{
  "message": "All notifications marked as read"
}
```

### 5.7 Get Unread Count

**URL:** `GET /api/custom-auth/v1/merchant-notifications/unread-count/`

**Response (200 OK):**

```json
{
  "unread_count": 3
}
```

---

## 📊 6. Statistics

### 6.1 Get Deal Statistics

**URL:** `GET /api/custom-auth/v1/deal-stats/`

**Response (200 OK):**

```json
{
  "total_deals": 5,
  "active_deals": 3,
  "total_requests": 8,
  "successful_deals": 4,
  "total_points_offered": 10000.0,
  "total_points_used": 6000.0
}
```

---

## 🏪 7. Additional Merchant Endpoints

### 7.1 Get Merchant Profile

**URL:** `GET /api/custom-auth/v1/merchant_profile/me/`

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "user": 1,
    "category": 1,
    "business_name": "Tech Store",
    "owner_name": "John Doe",
    "email": "john@techstore.com",
    "phone": "+1234567890",
    "gender": "male",
    "gst_number": "22AAAAA0000A1Z5",
    "fssai_number": "12345678901234",
    "address": "123 Tech Street, Mumbai",
    "area": "Bandra",
    "pin": "400050",
    "city": "Mumbai",
    "state": "Maharashtra",
    "latitude": 19.076,
    "longitude": 72.8777,
    "logo": "http://localhost:8000/media/merchant/logo/tech_logo.jpg",
    "banner_image": "http://localhost:8000/media/merchant/banner/tech_banner.jpg"
  }
}
```

### 7.2 Update Merchant Profile

**URL:** `PUT /api/custom-auth/v1/merchant_profile/me/` or `PATCH /api/custom-auth/v1/merchant_profile/me/`

**Request Body (PATCH):**

```json
{
  "business_name": "Updated Tech Store",
  "owner_name": "John Smith",
  "email": "johnsmith@techstore.com",
  "address": "456 Updated Street, Mumbai"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "business_name": "Updated Tech Store",
    "owner_name": "John Smith",
    "email": "johnsmith@techstore.com",
    "address": "456 Updated Street, Mumbai"
  }
}
```

### 7.3 Get Wallet Balance

**URL:** `GET /api/custom-auth/v1/wallet/`

**Response (200 OK):**

```json
{
  "id": 1,
  "user": 1,
  "balance": 5000.0,
  "is_active": true,
  "create_time": "2024-01-01T00:00:00Z",
  "update_time": "2024-01-15T10:30:00Z"
}
```

### 7.4 Get Wallet History

**URL:** `GET /api/custom-auth/v1/wallet/history/`

**Query Parameters:**

- `transaction_type`: Filter by type (credit, debit)
- `reference_note`: Filter by reference note
- `reference_id`: Filter by reference ID
- `ordering`: Order by field

**Response (200 OK):**

```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "transaction_type": "credit",
      "amount": 1000.0,
      "reference_note": "Razorpay payment - order_123",
      "reference_id": "order_123",
      "meta": null,
      "create_time": "2024-01-15T10:00:00Z"
    },
    {
      "id": 2,
      "transaction_type": "debit",
      "amount": 2000.0,
      "reference_note": "Deal created: Electronics Exchange Deal",
      "reference_id": "DEAL_A1B2C3D4",
      "meta": null,
      "create_time": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 7.5 Get Wallet Summary

**URL:** `GET /api/custom-auth/v1/wallet/summary/`

**Response (200 OK):**

```json
{
  "balance": 5000.0,
  "recent_transactions": [
    {
      "id": 1,
      "transaction_type": "credit",
      "amount": 1000.0,
      "reference_note": "Razorpay payment - order_123",
      "reference_id": "order_123",
      "create_time": "2024-01-15T10:00:00Z"
    },
    {
      "id": 2,
      "transaction_type": "debit",
      "amount": 2000.0,
      "reference_note": "Deal created: Electronics Exchange Deal",
      "reference_id": "DEAL_A1B2C3D4",
      "create_time": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

## 🏷️ 8. Categories

### 8.1 Get Categories

**URL:** `GET /api/custom-auth/v1/category/`

**Response (200 OK):**

```json
{
  "results": [
    {
      "id": 1,
      "name": "Electronics",
      "description": "Electronic devices and accessories",
      "image": "http://localhost:8000/media/categories/electronics.jpg",
      "image_url": "http://localhost:8000/media/categories/electronics.jpg",
      "is_active": true,
      "create_time": "2024-01-01T00:00:00Z",
      "update_time": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "Fashion",
      "description": "Clothing and fashion accessories",
      "image": "http://localhost:8000/media/categories/fashion.jpg",
      "image_url": "http://localhost:8000/media/categories/fashion.jpg",
      "is_active": true,
      "create_time": "2024-01-01T00:00:00Z",
      "update_time": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

## 🏪 9. Merchant Listing

### 9.1 Get All Merchants

**URL:** `GET /api/custom-auth/v1/merchants/list/`

**Query Parameters:**

- `category`: Filter by category ID
- `city`: Filter by city
- `state`: Filter by state
- `has_vouchers`: Filter by voucher availability (true/false)
- `order_by`: Order by field (vouchers_desc, vouchers_asc)
- `latitude`: User latitude for distance calculation
- `longitude`: User longitude for distance calculation

**Example:**

```
GET /api/custom-auth/v1/merchants/list/?category=1&city=Mumbai&has_vouchers=true&latitude=19.0760&longitude=72.8777
```

**Response (200 OK):**

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_name": "John Doe",
      "user_email": "john@techstore.com",
      "user_phone": "+1234567890",
      "category": 1,
      "category_name": "Electronics",
      "category_image": "http://localhost:8000/media/categories/electronics.jpg",
      "business_name": "Tech Store",
      "owner_name": "John Doe",
      "email": "john@techstore.com",
      "phone": "+1234567890",
      "gender": "male",
      "gst_number": "22AAAAA0000A1Z5",
      "fssai_number": "12345678901234",
      "address": "123 Tech Street, Mumbai",
      "area": "Bandra",
      "pin": "400050",
      "city": "Mumbai",
      "state": "Maharashtra",
      "latitude": 19.076,
      "longitude": 72.8777,
      "logo": "http://localhost:8000/media/merchant/logo/tech_logo.jpg",
      "logo_url": "http://localhost:8000/media/merchant/logo/tech_logo.jpg",
      "banner_image": "http://localhost:8000/media/merchant/banner/tech_banner.jpg",
      "banner_url": "http://localhost:8000/media/merchant/banner/tech_banner.jpg",
      "distance": 0.5,
      "available_vouchers_count": 3,
      "is_active": true,
      "create_time": "2024-01-01T00:00:00Z",
      "update_time": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

## 🚀 Complete Flow Example

### Step 1: Create Deals

**Apple Merchant:**

```bash
POST /api/custom-auth/v1/merchant-deals/
{
    "title": "Mobile Accessories Deal",
    "description": "Get mobile accessories for 1500 points",
    "points_offered": 1500.00,
    "deal_value": 2000.00,
    "category": 1
}
```

_Note: 1500 points deducted from Apple's wallet_

**Samsung Merchant:**

```bash
POST /api/custom-auth/v1/merchant-deals/
{
    "title": "Electronics Exchange",
    "description": "Exchange electronics for 2000 points",
    "points_offered": 2000.00,
    "deal_value": 2500.00,
    "category": 1
}
```

_Note: 2000 points deducted from Samsung's wallet_

### Step 2: Discovery & Request

**Apple discovers Samsung's deal:**

```bash
GET /api/custom-auth/v1/deal-discovery/by-points/?points=2000
```

**Apple requests Samsung's deal:**

```bash
POST /api/custom-auth/v1/deal-requests/
{
    "deal": 2,
    "points_requested": 2000.00,
    "message": "Great electronics deal! I'm interested."
}
```

### Step 3: Deal Confirmation

**Samsung accepts the request:**

```bash
POST /api/custom-auth/v1/deal-requests/{request_id}/accept/
```

_System creates deal confirmation and marks 2000 points as used in Samsung's deal_

### Step 4: Complete Deal

**Either merchant completes the deal:**

```bash
POST /api/custom-auth/v1/deal-confirmations/{confirmation_id}/complete/
```

_System transfers 2000 points from Samsung to Apple and tracks usage_

---

## 📋 Data Models

### MerchantDeal

- `merchant`: ForeignKey to MerchantProfile
- `title`: Deal title
- `description`: Deal description
- `points_offered`: Points offered by merchant (deducted from wallet)
- `points_used`: Points used from this deal
- `points_remaining`: Remaining points available
- `deal_value`: Actual value of deal
- `category`: Deal category
- `status`: Active/Inactive/Expired/Completed/Cancelled
- `expiry_date`: When deal expires
- `preferred_cities`: Preferred cities for deal
- `preferred_categories`: Preferred business categories
- `terms_conditions`: Deal terms
- `is_negotiable`: Whether points are negotiable

### MerchantDealRequest

- `requesting_merchant`: Merchant requesting the deal
- `deal`: Deal being requested
- `status`: Pending/Accepted/Rejected/Cancelled
- `request_time`: When request was made
- `message`: Request message
- `points_requested`: Points requested
- `counter_offer`: Optional counter offer points

### MerchantDealConfirmation

- `deal_request`: Related deal request
- `deal`: The deal being confirmed
- `merchant1`: Deal creator
- `merchant2`: Merchant who requested
- `status`: Pending Confirmation/Confirmed/Cancelled/Completed
- `points_exchanged`: Points exchanged
- `deal_terms`: Agreed terms
- `merchant1_notes`/`merchant2_notes`: Communication notes

### DealPointUsage

- `deal`: Related deal
- `confirmation`: Related confirmation
- `from_merchant`/`to_merchant`: Usage parties
- `usage_type`: Exchange/Discount/Transfer
- `points_used`: Points used
- `usage_description`: Description of usage
- `transaction_id`: Unique transaction ID

### MerchantNotification

- `merchant`: Merchant receiving notification
- `notification_type`: Deal Request/Accepted/Rejected/Points Transfer/System
- `title`: Notification title
- `message`: Notification message
- `deal`/`confirmation`: Related objects
- `is_read`: Read status
- `action_url`: URL for action

### MerchantPointsTransfer

- `confirmation`: Related deal confirmation
- `from_merchant`/`to_merchant`: Transfer parties
- `points_amount`: Points being transferred
- `transfer_fee`: Transfer fees
- `net_amount`: Net amount after fees
- `status`: Transfer status
- `transaction_id`: Unique transaction ID

---

## 🔐 Authentication

All endpoints require JWT authentication. Use the standard authentication headers:

```
Authorization: Bearer <your_jwt_token>
```

---

## ⚠️ Error Handling

Standard HTTP status codes are used:

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

---

## 🚦 Rate Limiting

- Standard rate limiting applies
- Deal request operations are limited to prevent spam
- Deal creation is limited per merchant

---

## 🔗 Webhook Notifications

For real-time updates, webhooks can be configured for:

- New deal requests
- Deal confirmations
- Points transfers
- Deal expirations

---

## 🧪 Testing

Use the provided test data and endpoints to test the complete flow:

1. Create test merchants
2. Create test deals (verify points deduction)
3. Test deal discovery and filtering
4. Test deal request system
5. Test deal confirmation and completion
6. Verify points transfer and usage tracking
7. Verify notifications

---

## 📞 Support

For technical support or questions about the API, contact the development team.

---

**Made with ❤️ for the merchant community**

_Transform your business networking with the power of smart matching and points exchange!_
