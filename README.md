# 🌾 АгроДанные КЗ - Farm Management System

Modern full-stack application for Kazakhstan farm management.

**Version 2.0 - Full-Stack Architecture**

---

## 🏗️ Architecture

### Tech Stack

**Backend:**
- FastAPI 0.104+ (async Python)
- PostgreSQL (Supabase)
- SQLAlchemy 2.0 ORM  
- JWT Authentication
- Redis (caching)

**Frontend:**
- Next.js 14 (React 18)
- TypeScript
- Tailwind CSS + shadcn/ui
- TanStack Query
- Zustand

---

## 📂 Project Structure

```
farm_data_system/
├── backend/          # FastAPI backend
├── frontend/         # Next.js frontend  
├── shared/           # JSON catalogs, migrations
├── streamlit_app/    # Legacy v1.0
└── docs/             # Documentation
```

---

## 🚀 Quick Start

```bash
# Start with Docker
docker-compose up -d

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/v1/docs
```

---

## 📚 Documentation

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)  
- [MODERNIZATION_PLAN.md](MODERNIZATION_PLAN.md)
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 📊 Status

| Component | Status |
|-----------|--------|
| Backend API | ✅ Initial setup |
| Frontend | ✅ Initial setup |
| Auth | ⏳ In progress |
| Deployment | ⏳ Pending |

---

**GitHub:** https://github.com/YergZakon/sbor_apk

_Version 2.0 - October 2025_ 🚀
