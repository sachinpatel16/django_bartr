# WhatsApp Gift Card Sharing API Documentation

## Overview

This document describes the WhatsApp Gift Card Sharing API endpoints for the Bartr platform. The system allows users to share gift card vouchers with their WhatsApp contacts through a comprehensive contact management and sharing system.

## Table of Contents

1. [Authentication](#authentication)
2. [Contact Management APIs](#contact-management-apis)
3. [Gift Card Sharing APIs](#gift-card-sharing-apis)
4. [WhatsApp Integration](#whatsapp-integration)
5. [Error Handling](#error-handling)
6. [Examples](#examples)

## Authentication

All API endpoints require:

- **JWT Token**: For user-specific operations
- **API Key**: Required for all endpoints to identify the application

### Headers Required

```http
Authorization: Bearer <JWT_TOKEN>
X-API-Key: <YOUR_API_KEY>
Content-Type: application/json
```

---

## Contact Management APIs

### 1. Sync Phone Contacts

Synchronizes user's phone contacts and checks WhatsApp availability.

#### Endpoint

```http
POST /api/v1/whatsapp-contacts/sync-contacts/
```

#### Request Body

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

#### Response

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

#### Status Codes

- `200 OK`: Contacts synced successfully
- `400 Bad Request`: No contacts provided
- `500 Internal Server Error`: Sync failed

---

### 2. Get WhatsApp Contacts

Retrieves only contacts that are available on WhatsApp.

#### Endpoint

```http
GET /api/v1/whatsapp-contacts/whatsapp-contacts/
```

#### Response

```json
[
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
```

#### Status Codes

- `200 OK`: Contacts retrieved successfully
- `500 Internal Server Error`: Failed to fetch contacts

---

## Gift Card Sharing APIs

### 1. Share Gift Card via WhatsApp

Shares a gift card voucher with multiple WhatsApp contacts.

#### Endpoint

```http
POST /api/v1/vouchers/{voucher_id}/share-gift-card/
```

#### Request Body

```json
{
  "phone_numbers": ["+919876543210", "+919876543211", "+919876543212"]
}
```

#### Response

```json
{
  "message": "Gift card shared successfully to 2 contacts",
  "success_count": 2,
  "failed_numbers": ["+919876543212"]
}
```

#### Status Codes

- `200 OK`: Gift card shared successfully
- `400 Bad Request`: Voucher is not a gift card or no valid WhatsApp contacts found
- `500 Internal Server Error`: Sharing process failed

---

### 2. Get Voucher QR Code

Retrieves QR code data for a specific purchased voucher that can be shared.

#### Endpoint

```http
GET /api/v1/user-vouchers/{redemption_id}/qr-code/
```

#### Response

```json
{
  "message": "Voucher QR code data",
  "voucher_details": {
    "id": 123,
    "title": "50% Off Coffee",
    "merchant_name": "Coffee Shop",
    "voucher_type": "percentage",
    "voucher_value": "50% off (min bill: ₹100)",
    "user_name": "John Doe",
    "user_phone": "+919876543210",
    "purchased_at": "2024-01-15T10:30:00Z",
    "expiry_date": "2025-01-15T10:30:00Z",
    "remaining_redemptions": 1,
    "purchase_reference": "VCH-12345678",
    "redemption_id": 456
  },
  "qr_code_data": {
    "purchase_reference": "VCH-12345678",
    "redemption_id": 456,
    "voucher_uuid": "550e8400-e29b-41d4-a716-446655440000"
  },
  "redemption_instructions": "Show this QR code to the merchant for redemption. The merchant will scan it to process your voucher."
}
```

#### Status Codes

- `200 OK`: QR code data retrieved successfully
- `400 Bad Request`: Voucher expired or already redeemed
- `404 Not Found`: Voucher not found or not owned by user
- `500 Internal Server Error`: Unexpected error occurred

---

## WhatsApp Integration

### WhatsApp Business API Integration

The system currently has a placeholder for WhatsApp API integration. Here are the recommended implementations:

#### Option 1: WhatsApp Business API (Meta)

```python
def send_whatsapp_gift_card(self, phone_number, voucher):
    try:
        api_url = "https://graph.facebook.com/v17.0/YOUR_PHONE_NUMBER_ID/messages"
        headers = {
            "Authorization": f"Bearer {YOUR_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        message_data = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": "gift_card_share",
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "header",
                        "parameters": [
                            {
                                "type": "image",
                                "image": {
                                    "link": voucher.get_display_image().url if voucher.get_display_image() else ""
                                }
                            }
                        ]
                    },
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": voucher.title},
                            {"type": "text", "text": voucher.merchant.business_name},
                            {"type": "text", "text": voucher.message}
                        ]
                    },
                    {
                        "type": "button",
                        "sub_type": "url",
                        "index": 0,
                        "parameters": [
                            {
                                "type": "text",
                                "text": f"https://yourdomain.com/voucher/{voucher.uuid}"
                            }
                        ]
                    }
                ]
            }
        }

        response = requests.post(api_url, json=message_data, headers=headers)
        return response.status_code == 200

    except Exception:
        return False
```

#### Option 2: Twilio WhatsApp API

```python
def send_whatsapp_gift_card(self, phone_number, voucher):
    try:
        from twilio.rest import Client

        client = Client(ACCOUNT_SID, AUTH_TOKEN)

        # Create rich message with image and text
        message_body = f"""
🎁 *Gift Card: {voucher.title}*

{voucher.message}

🏪 *Merchant:* {voucher.merchant.business_name}
📍 *Location:* {voucher.merchant.city}, {voucher.merchant.state}

💳 *Voucher Type:* {voucher.voucher_type.name}
💰 *Value:* {self.get_voucher_value(voucher)}

⏰ *Valid Until:* {voucher.expiry_date.strftime('%B %d, %Y')}

Scan the QR code or visit: https://yourdomain.com/voucher/{voucher.uuid}
        """

        message = client.messages.create(
            from_=f'whatsapp:+{YOUR_TWILIO_NUMBER}',
            body=message_body,
            to=f'whatsapp:+{phone_number}'
        )

        return message.sid is not None

    except Exception:
        return False
```

#### Option 3: MessageBird WhatsApp API

```python
def send_whatsapp_gift_card(self, phone_number, voucher):
    try:
        import messagebird

        client = messagebird.Client(YOUR_ACCESS_KEY)

        message_data = {
            'to': phone_number,
            'from': YOUR_CHANNEL_ID,
            'type': 'text',
            'content': {
                'text': f"""
🎁 Gift Card: {voucher.title}

{voucher.message}

Merchant: {voucher.merchant.business_name}
Location: {voucher.merchant.city}, {voucher.merchant.state}

Voucher Type: {voucher.voucher_type.name}
Value: {self.get_voucher_value(voucher)}

Valid Until: {voucher.expiry_date.strftime('%B %d, %Y')}

Visit: https://yourdomain.com/voucher/{voucher.uuid}
                """
            }
        }

        response = client.conversation_send(message_data)
        return response.id is not None

    except Exception:
        return False
```

---

## Error Handling

### Common Error Responses

#### 1. Authentication Errors

```json
{
  "error": "Authentication required. Please provide a valid JWT token.",
  "status": 401
}
```

#### 2. Validation Errors

```json
{
  "error": "Only gift cards can be shared",
  "status": 400
}
```

#### 3. Contact Not Found

```json
{
  "error": "No valid WhatsApp contacts found",
  "status": 400
}
```

#### 4. Voucher Not Found

```json
{
  "error": "Voucher not found or inactive",
  "status": 404
}
```

#### 5. Server Errors

```json
{
  "error": "Failed to share gift card",
  "status": 500
}
```

---

## Examples

### Complete Gift Card Sharing Flow

#### Step 1: Sync Contacts

```bash
curl -X POST "https://yourdomain.com/api/v1/whatsapp-contacts/sync-contacts/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contacts": [
        {"name": "John Doe", "phone_number": "+919876543210"},
        {"name": "Jane Smith", "phone_number": "+919876543211"}
    ]
}'
```

#### Step 2: Share Gift Card

```bash
curl -X POST "https://yourdomain.com/api/v1/vouchers/123/share-gift-card/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_numbers": ["+919876543210", "+919876543211"]
}'
```

#### Step 3: Get WhatsApp Contacts

```bash
curl -X GET "https://yourdomain.com/api/v1/whatsapp-contacts/whatsapp-contacts/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "X-API-Key: YOUR_API_KEY"
```

### Python Client Example

```python
import requests

class WhatsAppClient:
    def __init__(self, base_url, jwt_token, api_key):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {jwt_token}',
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }

    def sync_contacts(self, contacts):
        url = f"{self.base_url}/api/v1/whatsapp-contacts/sync-contacts/"
        response = requests.post(url, json={'contacts': contacts}, headers=self.headers)
        return response.json()

    def share_gift_card(self, voucher_id, phone_numbers):
        url = f"{self.base_url}/api/v1/vouchers/{voucher_id}/share-gift-card/"
        response = requests.post(url, json={'phone_numbers': phone_numbers}, headers=self.headers)
        return response.json()

    def get_whatsapp_contacts(self):
        url = f"{self.base_url}/api/v1/whatsapp-contacts/whatsapp-contacts/"
        response = requests.get(url, headers=self.headers)
        return response.json()

# Usage
client = WhatsAppClient(
    base_url="https://yourdomain.com",
    jwt_token="YOUR_JWT_TOKEN",
    api_key="YOUR_API_KEY"
)

# Sync contacts
contacts = [
    {"name": "John Doe", "phone_number": "+919876543210"},
    {"name": "Jane Smith", "phone_number": "+919876543211"}
]
result = client.sync_contacts(contacts)
print(f"Synced {len(result['whatsapp_contacts'])} WhatsApp contacts")

# Share gift card
share_result = client.share_gift_card(123, ["+919876543210", "+919876543211"])
print(f"Shared successfully to {share_result['success_count']} contacts")
```

---

## Configuration

### Environment Variables Required

```bash
# WhatsApp Business API (Meta)
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id

# Twilio WhatsApp API
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=your_twilio_whatsapp_number

# MessageBird WhatsApp API
MESSAGEBIRD_ACCESS_KEY=your_access_key
MESSAGEBIRD_CHANNEL_ID=your_channel_id
```

### Site Settings

The following settings can be configured via the admin panel:

- `whatsapp_api_provider`: Choose between 'meta', 'twilio', 'messagebird'
- `whatsapp_message_template`: Custom message template for gift cards
- `whatsapp_share_limit`: Maximum number of contacts per share (default: 50)

---

## Rate Limiting

- **Contact Sync**: Maximum 100 contacts per request
- **Gift Card Sharing**: Maximum 50 phone numbers per request
- **API Calls**: 100 requests per minute per user

---

## Testing

### Test Endpoints

For development and testing, use these test endpoints:

```http
# Test contact sync
POST /api/v1/whatsapp-contacts/sync-contacts/test/

# Test gift card sharing
POST /api/v1/vouchers/test/share-gift-card/

# Test WhatsApp status check
POST /api/v1/whatsapp-contacts/test-status/
```

### Test Data

```json
{
  "test_contacts": [
    { "name": "Test User 1", "phone_number": "+919876543210" },
    { "name": "Test User 2", "phone_number": "+919876543211" }
  ],
  "test_voucher_id": 999,
  "test_phone_numbers": ["+919876543210", "+919876543211"]
}
```

---

## Support

For technical support or questions about the WhatsApp API integration:

- **Email**: support@yourdomain.com
- **Documentation**: https://docs.yourdomain.com/whatsapp-api
- **API Status**: https://status.yourdomain.com

---

## Changelog

### Version 1.0.0 (Current)

- Initial WhatsApp contact management
- Gift card sharing functionality
- Contact synchronization
- WhatsApp status checking

### Planned Features

- Rich media message support
- Message templates
- Delivery status tracking
- Analytics and reporting
- Bulk messaging capabilities
