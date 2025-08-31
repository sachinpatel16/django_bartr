# Merchant-to-Merchant Deal System API Documentation

## Overview

This system allows merchants to create deals and match with other merchants through a Tinder-like swiping interface. Merchants can exchange wallet points for business deals.

## Core Features

- **Deal Creation**: Merchants create deals with points requirements
- **Deal Discovery**: Tinder-like interface to browse other merchants' deals
- **Swipe System**: Right swipe (interested) or Left swipe (not interested)
- **Matching**: Mutual interest creates a match
- **Points Transfer**: Automatic points transfer when deals are completed
- **Notifications**: Real-time notifications for matches and actions

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
  "points_required": 2000.0,
  "deal_value": 2500.0,
  "category": 1,
  "expiry_date": "2024-12-31T23:59:59Z",
  "min_points": 1500.0,
  "max_points": 2500.0,
  "preferred_cities": ["Mumbai", "Delhi"],
  "preferred_categories": [1, 2],
  "terms_conditions": "Valid for 30 days",
  "is_negotiable": true
}
```

#### Get My Deals

```
GET /api/v1/merchant-deals/
```

#### Activate/Deactivate Deal

```
POST /api/v1/merchant-deals/{id}/activate/
POST /api/v1/merchant-deals/{id}/deactivate/
```

### 2. Deal Discovery (Tinder Interface)

#### Get Available Deals

```
GET /api/v1/deal-discovery/
```

**Query Parameters:**

- `category`: Filter by category ID
- `min_points`: Minimum points required
- `max_points`: Maximum points required
- `city`: Filter by city
- `search_query`: Search in title, description, or business name
- `page`: Page number for pagination
- `page_size`: Items per page

#### Get Random Deal for Swiping

```
GET /api/v1/deal-discovery/random_deal/
```

### 3. Merchant Swiping

#### Swipe on a Deal

```
POST /api/v1/merchant-swipes/
```

**Request Body:**

```json
{
  "deal": 1,
  "swipe_type": "right", // "right" or "left"
  "notes": "Great deal!",
  "counter_offer": 1800.0 // Optional counter offer
}
```

#### Get My Swipes

```
GET /api/v1/merchant-swipes/
```

### 4. Merchant Matches

#### Get My Matches

```
GET /api/v1/merchant-matches/
```

#### Accept Match

```
POST /api/v1/merchant-matches/{id}/accept/
```

**Request Body:**

```json
{
  "notes": "Looking forward to the deal!",
  "agreed_points": 2000.0
}
```

#### Reject Match

```
POST /api/v1/merchant-matches/{id}/reject/
```

#### Complete Match

```
POST /api/v1/merchant-matches/{id}/complete/
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
  "total_matches": 8,
  "successful_deals": 4,
  "total_points_transferred": 8000.0,
  "points_sent": 4000.0,
  "points_received": 4000.0
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
    "points_required": 1500.00,
    "deal_value": 2000.00,
    "category": 1
}
```

**Samsung Merchant:**

```json
POST /api/v1/merchant-deals/
{
    "title": "Electronics Exchange",
    "description": "Exchange electronics for 2000 points",
    "points_required": 2000.00,
    "deal_value": 2500.00,
    "category": 1
}
```

### Step 2: Discovery & Swiping

**Apple swipes right on Samsung's deal:**

```json
POST /api/v1/merchant-swipes/
{
    "deal": 2,
    "swipe_type": "right",
    "notes": "Great electronics deal!"
}
```

**Samsung swipes right on Apple's deal:**

```json
POST /api/v1/merchant-swipes/
{
    "deal": 1,
    "swipe_type": "right",
    "notes": "Mobile accessories needed!"
}
```

### Step 3: Match Created

System automatically creates a match and sends notifications to both merchants.

### Step 4: Accept Match

**Samsung accepts the match:**

```json
POST /api/v1/merchant-matches/{match_id}/accept/
{
    "agreed_points": 2000.00
}
```

### Step 5: Complete Deal

**Either merchant completes the deal:**

```json
POST /api/v1/merchant-matches/{match_id}/complete/
```

System automatically transfers 2000 points from Samsung to Apple and marks the match as completed.

## Data Models

### MerchantDeal

- `merchant`: ForeignKey to MerchantProfile
- `title`: Deal title
- `description`: Deal description
- `points_required`: Points needed for deal
- `deal_value`: Actual value of deal
- `category`: Deal category
- `status`: Active/Inactive/Expired/Completed
- `expiry_date`: When deal expires
- `min_points`/`max_points`: Point range
- `preferred_cities`: Preferred cities for deal
- `preferred_categories`: Preferred business categories
- `terms_conditions`: Deal terms
- `is_negotiable`: Whether points are negotiable

### MerchantSwipe

- `merchant`: Merchant who swiped
- `deal`: Deal being swiped on
- `swipe_type`: Right (interested) or Left (not interested)
- `swipe_time`: When swipe occurred
- `notes`: Additional notes
- `counter_offer`: Optional counter offer points

### MerchantMatch

- `deal`: The deal being matched
- `merchant1`: Deal creator
- `merchant2`: Merchant who swiped right
- `status`: Pending/Accepted/Rejected/Expired/Completed
- `agreed_points`: Final agreed points
- `deal_terms`: Agreed terms
- `merchant1_notes`/`merchant2_notes`: Communication notes

### MerchantNotification

- `merchant`: Merchant receiving notification
- `notification_type`: Type of notification
- `title`: Notification title
- `message`: Notification message
- `deal`/`match`: Related objects
- `is_read`: Read status
- `action_url`: URL for action

### MerchantPointsTransfer

- `match`: Related match
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
- Swipe operations are limited to prevent spam
- Deal creation is limited per merchant

## Webhook Notifications

For real-time updates, webhooks can be configured for:

- New matches
- Match status changes
- Points transfers
- Deal expirations

## Testing

Use the provided test data and endpoints to test the complete flow:

1. Create test merchants
2. Create test deals
3. Test swiping functionality
4. Verify matching system
5. Test points transfer
6. Verify notifications

## Support

For technical support or questions about the API, contact the development team.
