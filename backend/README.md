# 🚀 АгроДанные КЗ - Backend API

FastAPI backend for farm management system.

## 🛠️ Tech Stack

- **Framework:** FastAPI 0.104+
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Authentication:** JWT tokens
- **Validation:** Pydantic v2
- **Testing:** pytest
- **Code Quality:** black, flake8, mypy

## 📦 Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your values
```

## 🚀 Running

### Development

```bash
# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI:** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc
- **OpenAPI JSON:** http://localhost:8000/api/v1/openapi.json

## 🗄️ Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry
│   ├── core/
│   │   ├── config.py        # Settings
│   │   ├── security.py      # JWT, passwords
│   │   └── database.py      # DB connection
│   ├── api/
│   │   └── v1/              # API routes
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── crud/                # Database operations
│   ├── services/            # Business logic
│   └── utils/               # Utilities
├── tests/                   # Test files
├── alembic/                 # Database migrations
├── requirements.txt
└── .env.example
```

## 🔐 Authentication

API uses JWT tokens for authentication:

```bash
# Login
POST /api/v1/auth/login
{
  "username": "user@example.com",
  "password": "password"
}

# Response
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}

# Use token in requests
Authorization: Bearer eyJ...
```

## 🌐 Environment Variables

See `.env.example` for all available variables.

Required:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key (32+ characters)

## 📝 Development

```bash
# Format code
black app/

# Lint
flake8 app/

# Type checking
mypy app/
```

## 🚀 Deployment

See [../docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md) for deployment instructions.

## 📞 Support

GitHub: https://github.com/YergZakon/sbor_apk
