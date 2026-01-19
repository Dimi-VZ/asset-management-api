# Setup Guide

## Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose)
- Git

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd asset-management
```

### 2. Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and configure:

**Required:**
- `JWT_SECRET` - Generate with: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`

**Optional (for full functionality):**
- `SMTP_USER` and `SMTP_PASSWORD` - For email alerts
- `OPENAI_API_KEY` - For AI image descriptions

### 3. Start Services

```bash
docker-compose up --build
```

This starts:
- PostgreSQL database (port 5433)
- Redis cache (port 6380)
- FastAPI application (port 8001)

### 4. Verify Installation

Check health endpoint:

```bash
curl http://localhost:8001/health
```

Access API documentation:

```
http://localhost:8001/docs
```

## Database Migrations

Migrations run automatically on container startup. To run manually:

```bash
docker-compose exec api alembic upgrade head
```

## SMTP Configuration (Email Alerts)

### Gmail Setup

1. Enable 2-Step Verification: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Update `.env`:
   ```env
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   ```
4. Restart: `docker-compose restart api`

### Testing Email

```bash
curl -X POST "http://localhost:8001/test-email" \
  -H "Content-Type: application/json" \
  -d '{"to_email": "your-email@gmail.com"}'
```

## OpenAI Configuration (AI Descriptions)

1. Get API key: https://platform.openai.com/api-keys
2. Update `.env`:
   ```env
   OPENAI_API_KEY=sk-your-key-here
   ```
3. Restart: `docker-compose restart api`

## Troubleshooting

### Port Conflicts

If ports are in use, modify `docker-compose.yml`:
- API: Change `8001:8000` to another port
- PostgreSQL: Change `5433:5432`
- Redis: Change `6380:6379`

### Database Connection Issues

Ensure PostgreSQL container is healthy:
```bash
docker-compose ps
```

Check logs:
```bash
docker-compose logs postgres
```

### Cache Issues

Clear Redis cache:
```bash
docker-compose exec redis redis-cli FLUSHALL
```

### Reset Everything

```bash
docker-compose down -v
docker-compose up --build
```

## Development

### Running Tests

```bash
docker-compose exec api pytest -v
```

### Viewing Logs

```bash
docker-compose logs -f api
```

### Database Access

```bash
docker-compose exec postgres psql -U assetuser -d assetdb
```

### Redis Access

```bash
docker-compose exec redis redis-cli
```
