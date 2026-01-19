# API Documentation

## Authentication

All asset endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Register User

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false,
  "created_at": "2024-01-18T12:00:00Z"
}
```

### Login

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword123
```

**Response:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

## Asset Endpoints

### Create Asset

```http
POST /assets
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "MacBook Pro 16",
  "asset_type": "laptop",
  "serial_number": "SN123456",
  "status": "active",
  "assigned_to": "John Doe",
  "purchase_date": "2024-01-15",
  "purchase_price": 2499.99,
  "description": "16-inch MacBook Pro with M3 chip"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "name": "MacBook Pro 16",
  "asset_type": "laptop",
  "serial_number": "SN123456",
  "status": "active",
  "assigned_to": "John Doe",
  "purchase_date": "2024-01-15",
  "purchase_price": 2499.99,
  "description": "16-inch MacBook Pro with M3 chip",
  "created_at": "2024-01-18T12:00:00Z",
  "updated_at": "2024-01-18T12:00:00Z"
}
```

### List Assets

```http
GET /assets?skip=0&limit=100
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "MacBook Pro 16",
    "asset_type": "laptop",
    "serial_number": "SN123456",
    "status": "active",
    ...
  }
]
```

**Note:** Results are cached for 60 seconds.

### Get Asset by ID

```http
GET /assets/{asset_id}
Authorization: Bearer <token>
```

**Response:** `200 OK` (asset object) or `404 Not Found`

### Update Asset

```http
PUT /assets/{asset_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "maintenance",
  "assigned_to": "Jane Smith"
}
```

**Response:** `200 OK` (updated asset object)

All fields are optional - only provided fields will be updated.

### Delete Asset

```http
DELETE /assets/{asset_id}
Authorization: Bearer <token>
```

**Response:** `204 No Content` or `404 Not Found`

### Upload Image and Generate Description

```http
POST /assets/{asset_id}/upload-image
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <image-file>
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "MacBook Pro",
  ...
  "description": "A silver MacBook Pro laptop. The device appears to be in good condition with stickers on the lid."
}
```

**Constraints:**
- File must be an image (JPEG, PNG)
- Maximum file size: 10MB
- Requires OpenAI API key configured

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "User account is inactive"
}
```

### 404 Not Found
```json
{
  "detail": "Asset with id {id} not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

## Rate Limiting

No rate limiting currently implemented.

## Caching

- Asset listing is cached for 60 seconds
- Cache is automatically invalidated on create, update, or delete operations
