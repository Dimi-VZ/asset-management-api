# Architecture Documentation

## System Overview

The Asset Management API is a RESTful service built with FastAPI, following a layered architecture pattern.

## Architecture Layers

```
┌─────────────────────────────────────┐
│         API Routes Layer            │
│    (Request/Response Handling)       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Business Logic Layer         │
│         (CRUD Operations)            │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Data Access Layer            │
│      (SQLAlchemy Models)             │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Database (PostgreSQL)        │
└─────────────────────────────────────┘
```

## Component Diagram

```
                    ┌─────────┐
                    │ Client  │
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │ FastAPI │
                    │   API   │
                    └────┬────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
   │PostgreSQL│     │  Redis  │     │ OpenAI  │
   │          │     │  Cache  │     │   API   │
   └──────────┘     └─────────┘     └─────────┘
        │
   ┌────▼────┐
   │  SMTP   │
   │ Server  │
   └─────────┘
```

## Database Schema

### Users Table
- `id` (UUID, PK)
- `email` (String, Unique)
- `hashed_password` (String)
- `is_active` (Boolean)
- `is_superuser` (Boolean)
- `is_verified` (Boolean)
- `last_login_ip` (String)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Assets Table
- `id` (UUID, PK)
- `name` (String)
- `asset_type` (String)
- `serial_number` (String, Unique)
- `status` (String)
- `assigned_to` (String, Nullable)
- `purchase_date` (Date, Nullable)
- `purchase_price` (Decimal, Nullable)
- `description` (Text, Nullable)
- `created_at` (DateTime)
- `updated_at` (DateTime)

## Authentication Flow

```
1. User registers → POST /auth/register
2. User logs in → POST /auth/login
   ├─ Extract IP address
   ├─ Compare with last_login_ip
   ├─ Send email if IP changed
   └─ Return JWT token
3. Client includes token in requests
4. API validates token
5. Request processed if valid
```

## Caching Strategy

### Cache Keys
- `assets:list:skip:{skip}:limit:{limit}` - Paginated asset lists
- TTL: 60 seconds

### Invalidation
- On asset create: Invalidate all `assets:list*` keys
- On asset update: Invalidate list and specific asset cache
- On asset delete: Invalidate list and specific asset cache

## Request Flow

### Asset Creation Flow
```
Client Request
    ↓
Authentication Middleware (JWT validation)
    ↓
Route Handler
    ↓
CRUD Layer
    ↓
Database (PostgreSQL)
    ↓
Cache Invalidation (Redis)
    ↓
Response
```

### Asset Listing Flow
```
Client Request
    ↓
Authentication Middleware
    ↓
Route Handler
    ↓
Cache Check (Redis)
    ├─ Cache Hit → Return cached data
    └─ Cache Miss → Query Database → Cache result → Return data
```

## Service Interactions

### Email Service
- Triggered on login IP change
- Uses SMTP for delivery
- Non-blocking (doesn't fail request if email fails)

### AI Service
- Triggered on image upload
- Calls OpenAI GPT-4 Vision API
- Updates asset description field
- Handles API errors gracefully

## Security

- JWT tokens with configurable expiration
- Password hashing with bcrypt
- IP tracking for security monitoring
- Email alerts for suspicious activity
- All asset endpoints protected by authentication

## Scalability Considerations

- Stateless API design (JWT tokens)
- Redis caching reduces database load
- Database connection pooling
- Horizontal scaling ready (stateless services)
