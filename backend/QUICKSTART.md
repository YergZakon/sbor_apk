# 🚀 Backend Quick Start Guide

## Запуск локально (для разработки)

### 1. Установка зависимостей

```bash
cd backend

# Создать виртуальное окружение
python -m venv venv

# Активировать
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
```

### 2. Настройка окружения

Создать файл `.env`:

```bash
cp .env.example .env
```

Отредактировать `.env`:

```env
# Для локальной разработки с SQLite:
DATABASE_URL=sqlite:///./farm_data.db

# Или для Supabase:
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres

# Секретный ключ (генерировать новый!)
SECRET_KEY=your-super-secret-key-min-32-characters-long-please-change-this

# Остальное можно оставить по умолчанию
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
ENVIRONMENT=development
```

### 3. Запуск сервера

```bash
# Запуск с авто-перезагрузкой
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Сервер запустится на http://localhost:8000

### 4. Проверка API

Откройте в браузере:
- **Swagger UI:** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc
- **Health check:** http://localhost:8000/health

## 📝 Тестирование API через Swagger

### 1. Регистрация пользователя

1. Откройте http://localhost:8000/api/v1/docs
2. Найдите `POST /api/v1/auth/register`
3. Нажмите "Try it out"
4. Введите данные:

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "full_name": "Test User"
}
```

5. Нажмите "Execute"

### 2. Вход (получение токена)

1. Найдите `POST /api/v1/auth/login`
2. Нажмите "Try it out"
3. Введите:
   - username: `testuser`
   - password: `password123`
4. Нажмите "Execute"
5. Скопируйте `access_token` из ответа

### 3. Авторизация в Swagger

1. Нажмите кнопку "Authorize" вверху страницы
2. Вставьте токен в поле (формат: просто токен, без "Bearer")
3. Нажмите "Authorize"

Теперь все endpoints требующие авторизации будут работать!

### 4. Создание фермы

1. Найдите `POST /api/v1/farms/`
2. Нажмите "Try it out"
3. Введите данные:

```json
{
  "bin": "123456789012",
  "name": "Тестовое хозяйство",
  "region": "Акмолинская область",
  "district": "Аршалынский район",
  "total_area_ha": 5000,
  "arable_area_ha": 4500
}
```

4. Нажмите "Execute"
5. Запомните `id` созданной фермы

### 5. Создание поля

1. Найдите `POST /api/v1/fields/`
2. Введите данные (используйте farm_id из предыдущего шага):

```json
{
  "farm_id": 1,
  "area_ha": 150.5,
  "name": "Поле №1",
  "soil_type": "Чернозем обыкновенный"
}
```

### 6. Просмотр данных

- `GET /api/v1/farms/` - список ваших ферм
- `GET /api/v1/farms/{farm_id}` - детали фермы со статистикой
- `GET /api/v1/fields/` - список полей
- `GET /api/v1/fields/{field_id}` - детали поля со статистикой

## 🔧 Полезные команды

```bash
# Запуск в production режиме
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Проверка типов
mypy app/

# Форматирование кода
black app/

# Линтинг
flake8 app/
```

## 🐛 Troubleshooting

### Ошибка: "No module named 'app'"

Убедитесь что вы находитесь в папке `backend/` и виртуальное окружение активировано.

### Ошибка подключения к БД

Проверьте `DATABASE_URL` в `.env` файле.

Для тестов можно использовать SQLite:
```env
DATABASE_URL=sqlite:///./farm_data.db
```

### Порт 8000 занят

Запустите на другом порту:
```bash
uvicorn app.main:app --reload --port 8001
```

## 📊 Структура API

```
/api/v1/
├── /auth/
│   ├── POST   /register      # Регистрация
│   ├── POST   /login          # Вход
│   ├── POST   /refresh        # Обновить токен
│   ├── GET    /me             # Текущий пользователь
│   ├── POST   /change-password
│   └── POST   /logout
│
├── /farms/
│   ├── GET    /               # Список ферм
│   ├── POST   /               # Создать ферму
│   ├── GET    /{id}           # Детали фермы
│   ├── PUT    /{id}           # Обновить ферму
│   └── DELETE /{id}           # Удалить ферму
│
└── /fields/
    ├── GET    /               # Список полей
    ├── POST   /               # Создать поле
    ├── GET    /{id}           # Детали поля
    ├── PUT    /{id}           # Обновить поле
    └── DELETE /{id}           # Удалить поле
```

## ✅ Готово!

Backend API работает и готов к использованию! 🎉

Следующий шаг: подключение frontend.
