# Merchant-to-Merchant Deal System API Documentation

## Overview

This system allows merchants to create deals with points and request deals from other merchants. When a deal is created, points are deducted from the merchant's wallet. Merchants can only use deal points between each other for exchanges and discounts.

## Core Features

- **Deal Creation**: Merchants create deals with points (deducted from wallet)
- **Deal Discovery**: Browse other merchants' deals with point-based filtering
- **Request System**: Request deals instead of swiping
- **Deal Confirmation**: Accept/reject deal requests
- **Points Transfer**: Automatic points transfer when deals are completed
- **Usage Tracking**: Complete audit trail of how deal points are used
- **Notifications**: Real-time notifications for all actions

## API Endpoints

### 1. Merchant Deals

#### Create a Deal

```
POST /api/v1/merchant-deals/
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

**Note:** Points are automatically deducted from merchant's wallet when deal is created.

#### Get My Deals

```
GET /api/v1/merchant-deals/
```

#### Get Deal Usage History

```
GET /api/v1/merchant-deals/{id}/usage-history/
```

#### Activate/Deactivate Deal

```
POST /api/v1/merchant-deals/{id}/activate/
POST /api/v1/merchant-deals/{id}/deactivate/
```

### 2. Deal Discovery

#### Get Available Deals

```
GET /api/v1/deal-discovery/
```

**Query Parameters:**

- `category`: Filter by category ID
- `points_offered`: Filter by points offered
- `merchant__city`: Filter by city
- `search`: Search in title, description, or business name

#### Get Deals by Points

```
GET /api/v1/deal-discovery/by-points/?points=2000
```

**Note:** Only shows deals with remaining points available.

### 3. Deal Requests

#### Request a Deal

```
POST /api/v1/deal-requests/
```

**Request Body:**

```json
{
  "deal": 1,
  "points_requested": 2000.0,
  "message": "I'm interested in this deal",
  "counter_offer": 1800.0 // Optional counter offer
}
```

#### Get My Requests

```
GET /api/v1/deal-requests/
```

#### Accept Request

```
POST /api/v1/deal-requests/{id}/accept/
```

#### Reject Request

```
POST /api/v1/deal-requests/{id}/reject/
```

### 4. Deal Confirmations

#### Get My Confirmations

```
GET /api/v1/deal-confirmations/
```

#### Complete Deal

```
POST /api/v1/deal-confirmations/{id}/complete/
```

#### Get Usage History

```
GET /api/v1/deal-confirmations/{id}/usage-history/
```

### 5. Notifications

#### Get Notifications

```
GET /api/v1/merchant-notifications/
```

#### Mark as Read

```
POST /api/v1/merchant-notifications/{id}/mark_read/
```

#### Mark All as Read

```
POST /api/v1/merchant-notifications/mark_all_read/
```

#### Get Unread Count

```
GET /api/v1/merchant-notifications/unread_count/
```

### 6. Statistics

#### Get Deal Statistics

```
GET /api/v1/deal-stats/
```

**Response:**

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

## Complete Flow Example

### Step 1: Create Deals

**Apple Merchant:**

```json
POST /api/v1/merchant-deals/
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

```json
POST /api/v1/merchant-deals/
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
GET /api/v1/deal-discovery/by-points/?points=2000
```

**Apple requests Samsung's deal:**

```json
POST /api/v1/deal-requests/
{
    "deal": 2,
    "points_requested": 2000.00,
    "message": "Great electronics deal! I'm interested."
}
```

### Step 3: Deal Confirmation

**Samsung accepts the request:**

```json
POST /api/v1/deal-requests/{request_id}/accept/
```

_System creates deal confirmation and marks 2000 points as used in Samsung's deal_

### Step 4: Complete Deal

**Either merchant completes the deal:**

```json
POST /api/v1/deal-confirmations/{confirmation_id}/complete/
```

_System transfers 2000 points from Samsung to Apple and tracks usage_

## Data Models

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

## Authentication

All endpoints require authentication. Use the standard authentication headers:

```
Authorization: Token <your_token>
```

## Error Handling

Standard HTTP status codes are used:

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `500`: Internal Server Error

## Rate Limiting

- Standard rate limiting applies
- Deal request operations are limited to prevent spam
- Deal creation is limited per merchant

## Webhook Notifications

For real-time updates, webhooks can be configured for:

- New deal requests
- Deal confirmations
- Points transfers
- Deal expirations

## Testing

Use the provided test data and endpoints to test the complete flow:

1. Create test merchants
2. Create test deals (verify points deduction)
3. Test deal discovery and filtering
4. Test deal request system
5. Test deal confirmation and completion
6. Verify points transfer and usage tracking
7. Verify notifications

## Support

For technical support or questions about the API, contact the development team.
