# 🚀 План модернизации: Streamlit → Modern Full-Stack

**Дата:** 25 октября 2025
**Цель:** Создание современного full-stack приложения на базе существующей системы

---

## 📋 Оглавление

1. [Выбор технологического стека](#технологический-стек)
2. [Архитектура системы](#архитектура)
3. [Структура проекта](#структура-проекта)
4. [Этапы миграции](#этапы-миграции)
5. [База данных](#база-данных)
6. [API Design](#api-design)
7. [Frontend компоненты](#frontend-компоненты)
8. [Аутентификация и авторизация](#аутентификация)
9. [Deployment](#deployment)
10. [Timeline](#timeline)

---

## 🛠️ Технологический стек

### Backend (API)

**Framework:** FastAPI 0.104+
- ✅ Современный async Python framework
- ✅ Автоматическая OpenAPI документация
- ✅ Pydantic для валидации
- ✅ Высокая производительность
- ✅ WebSocket поддержка

**ORM:** SQLAlchemy 2.0 (уже используется)
- ✅ Сохраняем существующие модели
- ✅ Async SQLAlchemy для производительности

**Database:** PostgreSQL (Supabase)
- ✅ Сохраняем текущую БД
- ✅ Используем существующие миграции
- ✅ Supabase Row Level Security (RLS)

**Authentication:**
- FastAPI-Users или custom JWT
- Supabase Auth (опционально)
- OAuth2 + JWT tokens

**Additional:**
- Alembic - миграции БД
- Redis - кэширование и sessions
- Celery - фоновые задачи (импорт Excel)
- pytest - тестирование

### Frontend

**Framework:** Next.js 14+ (React 18+)
- ✅ SSR/SSG для SEO
- ✅ App Router (новая архитектура)
- ✅ Server Components
- ✅ Built-in API routes

**UI Library:**
- **Shadcn/ui** + Tailwind CSS
  - Современные компоненты
  - Полностью кастомизируемые
  - Темная/светлая тема
- **Radix UI** - headless компоненты
- **Lucide React** - иконки

**State Management:**
- React Query (TanStack Query) - server state
- Zustand - client state (легковесная альтернатива Redux)

**Forms:**
- React Hook Form + Zod - валидация форм
- Сохраняем логику валидации из validators.py

**Charts/Maps:**
- Recharts - графики
- React Leaflet - карты полей
- Plotly React (опционально)

**Data Tables:**
- TanStack Table - мощные таблицы с сортировкой, фильтрами

**TypeScript:** ✅ Полная типизация

### DevOps

**Backend Deployment:**
- Railway / Render / DigitalOcean App Platform
- Docker container
- Gunicorn + Uvicorn workers

**Frontend Deployment:**
- Vercel (рекомендуется для Next.js)
- Netlify (альтернатива)

**Database:**
- Supabase (текущая)
- Миграции через Alembic

**CI/CD:**
- GitHub Actions
- Автоматическое тестирование
- Автоматический деплой

---

## 🏗️ Архитектура

### High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                   CLIENT LAYER                      │
│  Next.js 14 + React 18 + TypeScript + Tailwind     │
│              (Deployed on Vercel)                   │
└────────────────┬────────────────────────────────────┘
                 │
                 │ HTTPS/REST API
                 │ WebSocket (real-time)
                 │
┌────────────────▼────────────────────────────────────┐
│                   API LAYER                         │
│        FastAPI + SQLAlchemy + Pydantic             │
│           (Deployed on Railway)                     │
└────────────────┬────────────────────────────────────┘
                 │
                 │ PostgreSQL Protocol
                 │
┌────────────────▼────────────────────────────────────┐
│                DATABASE LAYER                       │
│      PostgreSQL 15 + PostGIS (Supabase)            │
│           + Redis (Caching)                         │
└─────────────────────────────────────────────────────┘
```

### Backend Architecture (FastAPI)

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Settings (Pydantic)
│   │
│   ├── api/
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py      # /api/v1/auth/*
│   │   │   ├── farms.py     # /api/v1/farms/*
│   │   │   ├── fields.py    # /api/v1/fields/*
│   │   │   ├── operations.py
│   │   │   ├── equipment.py
│   │   │   ├── references.py
│   │   │   └── ...
│   │   └── deps.py          # Dependencies (DB session, auth)
│   │
│   ├── models/              # SQLAlchemy models (from existing)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── farm.py
│   │   ├── field.py
│   │   ├── operation.py
│   │   └── ...
│   │
│   ├── schemas/             # Pydantic schemas (API contracts)
│   │   ├── __init__.py
│   │   ├── user.py          # UserCreate, UserRead, UserUpdate
│   │   ├── farm.py
│   │   ├── field.py
│   │   └── ...
│   │
│   ├── crud/                # Database operations
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── farm.py
│   │   └── ...
│   │
│   ├── core/
│   │   ├── security.py      # JWT, password hashing
│   │   ├── permissions.py   # RBAC logic
│   │   └── config.py        # Settings
│   │
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── farm_service.py
│   │   └── ...
│   │
│   └── utils/
│       ├── validators.py    # Port from existing
│       └── formatters.py
│
├── tests/
├── alembic/                 # DB migrations
├── requirements.txt
└── Dockerfile
```

### Frontend Architecture (Next.js 14)

```
frontend/
├── app/                     # Next.js 14 App Router
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Home page
│   ├── (auth)/
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/
│   │   ├── layout.tsx       # Dashboard layout
│   │   ├── page.tsx         # Dashboard home
│   │   ├── farms/
│   │   ├── fields/
│   │   ├── operations/
│   │   ├── equipment/
│   │   ├── references/
│   │   └── settings/
│   │
├── components/
│   ├── ui/                  # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── select.tsx
│   │   ├── table.tsx
│   │   └── ...
│   ├── forms/               # Reusable forms
│   │   ├── field-form.tsx
│   │   ├── operation-form.tsx
│   │   └── ...
│   ├── tables/              # Data tables
│   ├── maps/                # Map components
│   ├── charts/              # Chart components
│   └── layouts/
│
├── lib/
│   ├── api/                 # API client
│   │   ├── client.ts        # Axios/Fetch wrapper
│   │   ├── farms.ts
│   │   ├── fields.ts
│   │   └── ...
│   ├── hooks/               # Custom React hooks
│   ├── utils/
│   └── validations/         # Zod schemas
│
├── stores/                  # Zustand stores
│   ├── auth.ts
│   └── ui.ts
│
├── types/                   # TypeScript types
│   ├── api.ts
│   ├── models.ts
│   └── ...
│
├── public/
├── styles/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

---

## 📂 Структура проекта

### Новая структура репозитория

```
farm_data_system/           # Root
│
├── streamlit_app/          # Существующее Streamlit приложение
│   ├── app.py
│   ├── pages/
│   ├── modules/
│   └── ...
│
├── backend/                # NEW: FastAPI backend
│   ├── app/
│   ├── tests/
│   ├── alembic/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
│
├── frontend/               # NEW: Next.js frontend
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   ├── package.json
│   └── README.md
│
├── shared/                 # Shared resources
│   ├── data/               # JSON references (symlinked)
│   └── migrations/         # DB migrations (shared)
│
├── docs/                   # Documentation
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── DEVELOPMENT.md
│
├── docker-compose.yml      # Local development
├── .github/
│   └── workflows/
│       ├── backend-ci.yml
│       └── frontend-ci.yml
│
└── README.md
```

---

## 🎯 Этапы миграции

### Phase 1: Подготовка и setup (2-3 дня)

**1.1 Создание новой ветки**
```bash
git checkout -b feature/modern-stack
```

**1.2 Структура проекта**
- Создать папки backend/, frontend/, shared/
- Переместить streamlit в streamlit_app/
- Настроить .gitignore

**1.3 Backend setup**
- Инициализировать FastAPI проект
- Портировать SQLAlchemy модели
- Настроить Alembic
- Создать базовые endpoints

**1.4 Frontend setup**
- Инициализировать Next.js проект
- Настроить TypeScript
- Установить shadcn/ui
- Создать базовую структуру

### Phase 2: Backend API (1 неделя)

**2.1 Authentication (Day 1-2)**
- JWT authentication
- User registration/login
- Password reset
- Role-based access control

**2.2 Core APIs (Day 3-5)**
- Farms API (CRUD)
- Fields API (CRUD + maps)
- Users API (multi-farm assignments)
- References API (JSON catalogs)

**2.3 Operations APIs (Day 6-7)**
- Sowing operations
- Fertilizer operations
- Pesticide operations
- Harvest operations
- Other operations (tillage, irrigation, etc.)

**2.4 Equipment APIs**
- Machinery CRUD
- Implements CRUD
- Equipment assignment to operations

**2.5 Analytics APIs**
- Dashboard metrics
- Journal/logs with filters
- Export endpoints (CSV, Excel)

### Phase 3: Frontend Development (1.5 недели)

**3.1 Core UI (Day 1-3)**
- Authentication pages (login, register)
- Dashboard layout with sidebar
- Dashboard home with metrics
- Farm selector (multi-farm support)

**3.2 Farm Management (Day 4-5)**
- Farm list/detail pages
- Field CRUD with map integration
- Field list with data table

**3.3 Operations (Day 6-9)**
- Operation forms (reusable components)
- Sowing page
- Fertilizer page
- Pesticide page
- Harvest page
- Other operations pages

**3.4 Equipment & References (Day 10-11)**
- Equipment management
- References editor (16 catalogs)
- Import/export functionality

### Phase 4: Advanced Features (3-4 дня)

**4.1 Real-time features**
- WebSocket для уведомлений
- Live updates на dashboard

**4.2 Maps Integration**
- React Leaflet интеграция
- Field boundary drawing
- GPS координаты

**4.3 Charts & Analytics**
- Recharts интеграция
- Dashboard charts
- Field fertility maps

**4.4 Import/Export**
- Excel import (background jobs)
- CSV/Excel export
- Progress tracking

### Phase 5: Testing & Polish (2-3 дня)

**5.1 Backend Testing**
- pytest unit tests
- API integration tests
- Load testing

**5.2 Frontend Testing**
- Jest + React Testing Library
- E2E tests (Playwright)

**5.3 UI/UX Polish**
- Responsive design
- Dark/light theme
- Loading states
- Error handling

### Phase 6: Deployment (2 дня)

**6.1 Backend Deployment**
- Docker image
- Railway deployment
- Environment variables
- CI/CD pipeline

**6.2 Frontend Deployment**
- Vercel deployment
- Environment variables
- CI/CD pipeline

**6.3 Database**
- Supabase connection
- Apply migrations
- RLS policies

---

## 🗄️ База данных

### Стратегия

**✅ Сохраняем существующую БД Supabase**
- Используем те же таблицы
- Применяем существующие миграции 002-005
- Добавляем Row Level Security (RLS) для безопасности

### Новые улучшения

**Supabase RLS Policies:**

```sql
-- Example: Fields table policy
CREATE POLICY "Users can view fields of their farms"
ON fields FOR SELECT
USING (
  farm_id IN (
    SELECT farm_id FROM user_farms WHERE user_id = auth.uid()
  )
);

CREATE POLICY "Users can insert fields in their farms"
ON fields FOR INSERT
WITH CHECK (
  farm_id IN (
    SELECT farm_id FROM user_farms
    WHERE user_id = auth.uid()
    AND role IN ('admin', 'manager')
  )
);
```

**Indexes для производительности:**

```sql
CREATE INDEX idx_operations_farm_date ON operations(farm_id, operation_date DESC);
CREATE INDEX idx_fields_farm ON fields(farm_id);
CREATE INDEX idx_user_farms_user ON user_farms(user_id);
```

---

## 🔌 API Design

### REST API Structure

**Base URL:** `https://api.agrodannye.kz/v1`

### Authentication Endpoints

```
POST   /auth/register        # Регистрация
POST   /auth/login           # Вход (получить JWT)
POST   /auth/logout          # Выход
POST   /auth/refresh         # Обновить токен
POST   /auth/reset-password  # Сброс пароля
GET    /auth/me              # Текущий пользователь
```

### Farms Endpoints

```
GET    /farms                # Список хозяйств пользователя
POST   /farms                # Создать хозяйство
GET    /farms/{id}           # Детали хозяйства
PUT    /farms/{id}           # Обновить хозяйство
DELETE /farms/{id}           # Удалить хозяйство
GET    /farms/{id}/users     # Пользователи хозяйства
POST   /farms/{id}/users     # Добавить пользователя
```

### Fields Endpoints

```
GET    /farms/{farm_id}/fields            # Список полей
POST   /farms/{farm_id}/fields            # Создать поле
GET    /fields/{id}                       # Детали поля
PUT    /fields/{id}                       # Обновить поле
DELETE /fields/{id}                       # Удалить поле
GET    /fields/{id}/operations            # Операции на поле
```

### Operations Endpoints

```
GET    /operations                        # Все операции (с фильтрами)
POST   /operations                        # Создать операцию
GET    /operations/{id}                   # Детали операции
PUT    /operations/{id}                   # Обновить операцию
DELETE /operations/{id}                   # Удалить операцию

# Specific operation types
POST   /operations/sowing                 # Создать посев
POST   /operations/fertilizing            # Внесение удобрений
POST   /operations/spraying               # Обработка СЗР
POST   /operations/harvest                # Уборка
```

### Equipment Endpoints

```
GET    /equipment/machinery               # Список техники
POST   /equipment/machinery               # Добавить технику
GET    /equipment/machinery/{id}          # Детали техники
PUT    /equipment/machinery/{id}          # Обновить технику
DELETE /equipment/machinery/{id}          # Удалить технику

GET    /equipment/implements              # Список агрегатов
POST   /equipment/implements              # Добавить агрегат
...
```

### References Endpoints

```
GET    /references                        # Список всех справочников
GET    /references/{type}                 # Конкретный справочник
POST   /references/{type}                 # Добавить запись
PUT    /references/{type}/{name}          # Обновить запись
DELETE /references/{type}/{name}          # Удалить запись
```

### Analytics Endpoints

```
GET    /analytics/dashboard               # Метрики dashboard
GET    /analytics/fields/fertility        # Карта плодородия
GET    /analytics/operations/summary      # Сводка операций
```

### Example Response Format

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Поле №1",
    "area_ha": 150.5,
    "farm_id": 7
  },
  "meta": {
    "timestamp": "2025-10-25T10:30:00Z"
  }
}
```

**Error Response:**

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Area must be greater than 0",
    "details": {
      "field": "area_ha",
      "value": -10
    }
  }
}
```

---

## 🎨 Frontend Компоненты

### Key Components

**1. Authentication**
- LoginForm
- RegisterForm
- ResetPasswordForm

**2. Dashboard**
- DashboardLayout (sidebar, header)
- MetricsCard
- RecentOperations
- FarmSelector

**3. Forms**
- FieldForm
- SowingForm
- FertilizerForm
- PesticideForm
- HarvestForm
- EquipmentForm

**4. Tables**
- FieldsTable (sortable, filterable)
- OperationsTable
- EquipmentTable

**5. Maps**
- FieldMap (React Leaflet)
- FieldBoundaryDrawer
- FertilityHeatmap

**6. Charts**
- OperationsChart (timeline)
- YieldChart
- CropDistribution

### UI/UX Features

- **Dark/Light theme** - системная и ручная
- **Responsive** - mobile, tablet, desktop
- **Keyboard shortcuts** - для power users
- **Loading states** - скелетоны
- **Error boundaries** - graceful errors
- **Toast notifications** - success/error feedback

---

## 🔐 Аутентификация

### Strategy

**JWT Tokens:**
- Access token (15 min expiry)
- Refresh token (7 days expiry)
- HttpOnly cookies для безопасности

**Permissions:**
```typescript
enum Permission {
  VIEW_FARM = 'view_farm',
  EDIT_FARM = 'edit_farm',
  DELETE_FARM = 'delete_farm',
  MANAGE_USERS = 'manage_users',
  // ... etc
}

// Backend checks
@require_permission(Permission.EDIT_FARM)
async def update_farm(farm_id: int):
    ...

// Frontend checks
{hasPermission(Permission.EDIT_FARM) && <EditButton />}
```

---

## 🚀 Deployment

### Backend (Railway)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Environment Variables:**
```
DATABASE_URL=postgresql://...
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
```

### Frontend (Vercel)

**next.config.js:**
```javascript
module.exports = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
}
```

---

## ⏱️ Timeline

### Optimistic Timeline (3-4 недели full-time)

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1: Setup | 2-3 дня | Project structure, basic skeleton |
| Phase 2: Backend | 1 неделя | Full REST API working |
| Phase 3: Frontend | 1.5 недели | Complete UI implementation |
| Phase 4: Advanced | 3-4 дня | Maps, charts, real-time |
| Phase 5: Testing | 2-3 дня | Tests, bug fixes |
| Phase 6: Deployment | 2 дня | Production ready |

**Total: ~3-4 weeks**

### Realistic Timeline (part-time, 2-3 hours/day)

**Total: ~8-10 weeks**

---

## 🎯 MVP Features (First Release)

### Must Have
- ✅ Authentication (login, register)
- ✅ Farm management
- ✅ Field CRUD with maps
- ✅ Basic operations (sowing, harvest)
- ✅ Dashboard with metrics
- ✅ Responsive UI

### Nice to Have (v1.1)
- Import/Export
- All 9 operation types
- Equipment management
- Advanced analytics
- Real-time updates

### Future (v2.0)
- Mobile app (React Native)
- Offline support (PWA)
- ML predictions
- Weather integration
- Satellite imagery

---

## 💰 Cost Estimate

### Free Tier (Development & Small Scale)

- **Supabase:** Free tier (500 MB storage, 50k rows)
- **Vercel:** Free tier (100 GB bandwidth)
- **Railway:** $5/month (500 hours)
- **Total:** ~$5/month

### Production Scale

- **Supabase:** Pro plan $25/month (8 GB storage)
- **Vercel:** Pro $20/month (1 TB bandwidth)
- **Railway:** ~$20/month
- **Total:** ~$65/month

---

## ✅ Преимущества новой архитектуры

1. **Performance** - 10-100x faster than Streamlit
2. **Scalability** - can handle thousands of concurrent users
3. **Mobile-friendly** - responsive design, mobile apps later
4. **Developer Experience** - modern tools, TypeScript safety
5. **SEO** - Next.js SSR for better indexing
6. **Offline-capable** - PWA support
7. **API-first** - можно создать мобильное приложение позже
8. **Professional UI** - современный дизайн
9. **Better UX** - faster interactions, real-time updates
10. **Maintainability** - чистая архитектура, тесты

---

## 🚦 Готовы начать?

**Следующие шаги:**

1. Создать ветку `feature/modern-stack`
2. Создать структуру папок
3. Инициализировать backend (FastAPI)
4. Инициализировать frontend (Next.js)
5. Портировать первые модели и endpoints
6. Создать базовый UI

**Подтвердите и мы начинаем!** 🚀
