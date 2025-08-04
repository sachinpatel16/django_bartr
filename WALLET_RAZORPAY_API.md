# Wallet Razorpay API Documentation

## Overview

This API allows users to add points to their wallet using Razorpay payment gateway. The wallet balance represents points directly (1 rupee = 1 point).

## API Endpoints

### 1. Create Razorpay Order

**POST** `/api/custom_auth/v1/wallet/razorpay/create-order/`

Creates a Razorpay order for wallet recharge.

**Request Body:**

```json
{
  "amount": 100.0,
  "currency": "INR",
  "description": "Wallet recharge",
  "receipt": "optional_receipt_id",
  "notes": {
    "additional_info": "any additional data"
  }
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

### 2. Verify Payment and Add Points

**POST** `/api/custom_auth/v1/wallet/razorpay/verify-payment/`

Verifies the Razorpay payment and adds points to the user's wallet.

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

### 3. List Razorpay Transactions

**GET** `/api/custom_auth/v1/wallet/razorpay/transactions/`

Lists all Razorpay transactions for the authenticated user.

**Query Parameters:**

- `status`: Filter by transaction status (pending, success, failed, cancelled)
- `currency`: Filter by currency
- `ordering`: Sort by create_time or amount

**Response:**

```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_name": "John Doe",
      "user_email": "john@example.com",
      "wallet": 1,
      "razorpay_order_id": "order_ABC123",
      "razorpay_payment_id": "pay_XYZ789",
      "razorpay_signature": "signature",
      "amount": 100.0,
      "points_to_add": 100.0,
      "currency": "INR",
      "status": "success",
      "description": "Wallet recharge",
      "receipt": "receipt_id",
      "notes": {},
      "error_code": null,
      "error_description": null,
      "create_time": "2024-01-01T12:00:00Z",
      "update_time": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### 4. Get Wallet Balance

**GET** `/api/custom_auth/v1/wallet/`

Get the current wallet balance (points).

**Response:**

```json
{
  "id": 1,
  "user": 1,
  "balance": 150.0,
  "is_active": true,
  "create_time": "2024-01-01T12:00:00Z",
  "update_time": "2024-01-01T12:00:00Z"
}
```

### 5. Get Wallet History

**GET** `/api/custom_auth/v1/wallet/history/`

Get transaction history for the wallet.

**Query Parameters:**

- `transaction_type`: Filter by transaction type (credit, debit)
- `reference_note`: Filter by reference note
- `reference_id`: Filter by reference ID
- `ordering`: Sort by create_time or amount

**Response:**

```json
{
  "count": 1,
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
      "create_time": "2024-01-01T12:00:00Z"
    }
  ]
}
```

## Authentication

All endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Environment Variables

Add these to your `.env` file:

```
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

## Integration Flow

1. Frontend calls `/create-order/` with amount
2. Frontend receives order_id and initiates Razorpay payment
3. After successful payment, frontend calls `/verify-payment/` with payment details
4. Points are automatically added to user's wallet
5. Frontend can check wallet balance using `/wallet/` endpoint

## Error Handling

All endpoints return appropriate HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request (validation errors)
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

Error responses include:

```json
{
  "success": false,
  "error": "Error message"
}
```
