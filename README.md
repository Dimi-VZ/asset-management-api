# Asset Management API

FastAPI-based REST API for managing company digital assets with authentication, caching, and AI-powered image analysis.

## Features

- **Asset Management**: Full CRUD operations for digital assets (laptops, monitors, phones, etc.)
- **Authentication**: JWT-based authentication with FastAPI Users
- **Caching**: Redis caching with automatic invalidation for improved performance
- **Security**: IP-based login tracking with email alerts for suspicious activity
- **AI Integration**: Automatic asset description generation from images using OpenAI

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis
- **Migrations**: Alembic
- **Authentication**: FastAPI Users with JWT
- **Testing**: Pytest
- **Containerization**: Docker & Docker Compose
- **Dependency Management**: Poetry

## Quick Start

```bash
docker-compose up --build
```

API will be available at `http://localhost:8001`

Interactive API documentation: `http://localhost:8001/docs`

## Project Structure

```
asset-management/
├── app/
│   ├── api/routes/     # API endpoints
│   ├── crud/           # Database operations
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic (email, AI)
│   ├── auth.py         # Authentication setup
│   ├── cache.py        # Redis caching
│   ├── config.py       # Configuration
│   ├── database.py     # Database connection
│   └── main.py         # Application entry point
├── alembic/            # Database migrations
├── tests/              # Test suite
├── docker-compose.yml  # Docker services
└── Dockerfile          # Application container
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and receive JWT token

### Assets (Protected)
- `POST /assets` - Create asset
- `GET /assets` - List all assets (cached)
- `GET /assets/{id}` - Get asset by ID
- `PUT /assets/{id}` - Update asset
- `DELETE /assets/{id}` - Delete asset
- `POST /assets/{id}/upload-image` - Upload image and generate AI description

## Testing

Run the test suite:

```bash
docker-compose exec api pytest -v
```

Run with coverage:

```bash
docker-compose exec api pytest --cov=app --cov-report=term-missing
```

## Documentation

- [Setup Guide](SETUP.md) - Installation and configuration
- [API Documentation](API.md) - Complete API reference
- [Architecture](ARCHITECTURE.md) - System design and architecture

## Environment Variables

Configure environment variables in `.env` file:

```bash
# Copy example file
cp .env.example .env

# Edit .env with your credentials:
# - OPENAI_API_KEY (required for image uploads)
# - SMTP_USER and SMTP_PASSWORD (required for email alerts)
# - JWT_SECRET (required for authentication)
```
### Email configuration (tests vs runtime)

Email-related tests are intentionally configured to send emails to
dedicated test inboxes (e.g. AI or asset-related test addresses).

This is done to:
- Prevent accidental emails being sent to real users
- Keep test behaviour predictable and isolated
- Allow reviewers to substitute their own test inboxes if desired

Test email addresses are currently hardcoded for safety and clarity,
but can be easily externalised via environment variables if required.

See [Setup Guide](SETUP.md) for detailed configuration instructions.
