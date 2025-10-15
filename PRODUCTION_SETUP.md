# 🚀 Настройка Production окружения (Streamlit Cloud)

**Дата:** 15 октября 2025
**Версия:** 2.0.0

---

## 📋 Чеклист деплоя с авторизацией

### ✅ Уже сделано:

- [x] Код запушен в GitHub (коммит `2877ef6`)
- [x] requirements.txt обновлен (bcrypt, streamlit-authenticator)
- [x] База данных PostgreSQL на Supabase
- [x] DATABASE_URL настроен в Streamlit Secrets

### 🔄 Нужно сделать после деплоя:

1. **Дождаться автоматического деплоя**
   - Streamlit Cloud автоматически развернет новую версию
   - URL: https://sbor-apk.streamlit.app
   - Время деплоя: 2-5 минут

2. **Создать первого администратора**
   - ⚠️ **ВАЖНО:** Нельзя запустить `create_admin.py` на Streamlit Cloud напрямую
   - Используем альтернативный метод (см. ниже)

3. **Протестировать авторизацию**
   - Войти под админом
   - Создать тестового пользователя
   - Проверить разграничение доступа

---

## 🔐 Создание первого админа на Production

### Способ 1: Через консоль PostgreSQL (Supabase)

1. **Зайти в Supabase Dashboard:**
   - https://supabase.com
   - Выбрать ваш проект
   - Table Editor → users

2. **Вручную создать запись:**

**Сначала сгенерируйте хеш пароля локально:**

```bash
# Локально на вашем компьютере
python
>>> import bcrypt
>>> password = "ваш_пароль_здесь"  # ЗАМЕНИТЕ!
>>> salt = bcrypt.gensalt()
>>> hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
>>> print(hashed.decode('utf-8'))
# Скопируйте полученный хеш
```

**Затем вставьте в Supabase:**

```sql
INSERT INTO users (
    username,
    email,
    hashed_password,
    full_name,
    role,
    is_active,
    created_at,
    updated_at
) VALUES (
    'admin',
    'admin@agrodata.kz',
    '$2b$12$ВАШ_ХЕШ_ЗДЕСЬ',  -- ЗАМЕНИТЕ на сгенерированный хеш!
    'System Administrator',
    'admin',
    true,
    NOW(),
    NOW()
);
```

### Способ 2: Через страницу регистрации + SQL

1. **Зарегистрируйтесь на сайте:**
   - Перейдите на https://sbor-apk.streamlit.app
   - Откройте страницу 🔐 Login
   - Вкладка "Регистрация"
   - Создайте аккаунт (будет роль "farmer")

2. **Обновите роль в Supabase:**

```sql
UPDATE users
SET role = 'admin'
WHERE username = 'ваш_username';
```

### Способ 3: Через Python скрипт (если есть доступ к БД)

Создайте локальный скрипт `create_prod_admin.py`:

```python
import psycopg2
import bcrypt

# ЗАМЕНИТЕ на ваш DATABASE_URL из Supabase
DATABASE_URL = "postgresql://postgres.xxxxx:password@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"

# Данные админа
username = "admin"
email = "admin@agrodata.kz"
password = "ваш_пароль"  # ЗАМЕНИТЕ!
full_name = "System Administrator"

# Хешируем пароль
salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# Подключаемся к БД
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Создаем админа
cursor.execute("""
    INSERT INTO users (username, email, hashed_password, full_name, role, is_active, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
""", (username, email, hashed_password, full_name, 'admin', True))

conn.commit()
print(f"✅ Admin user '{username}' created successfully!")

cursor.close()
conn.close()
```

Запустите:
```bash
pip install psycopg2-binary bcrypt
python create_prod_admin.py
```

---

## 🧪 Проверка после деплоя

### 1. Проверка развертывания

```
✅ Приложение доступно: https://sbor-apk.streamlit.app
✅ Нет ошибок при запуске
✅ База данных подключена
✅ Видна страница 🔐 Login в меню
✅ Видна страница ⚙️ Admin (после входа под админом)
```

### 2. Проверка авторизации

**Тест 1: Вход под админом**
1. Перейти на страницу 🔐 Login
2. Ввести admin credentials
3. Успешный вход ✅
4. В sidebar отображается: "👤 System Administrator" + "👑 Администратор"

**Тест 2: Админ-панель**
1. Нажать "⚙️ Админ-панель" в sidebar
2. Открывается страница с управлением пользователями ✅
3. Статистика показывает: "Всего пользователей: 1" ✅

**Тест 3: Создание пользователя**
1. Админ-панель → вкладка "➕ Создать пользователя"
2. Заполнить форму:
   - Username: testuser
   - Email: test@example.com
   - ФИО: Test User
   - Пароль: test123
   - Роль: farmer
3. Нажать "Создать пользователя" ✅
4. Пользователь создан

**Тест 4: Вход под фермером**
1. Выйти (кнопка 🚪 Выход)
2. Войти как testuser / test123
3. Успешный вход ✅
4. В sidebar: "👤 Test User" + "👨‍🌾 Фермер"
5. НЕ видна кнопка "⚙️ Админ-панель" ✅

**Тест 5: Разграничение доступа**
1. Попытаться открыть админ-панель напрямую
2. Должна быть ошибка "❌ Доступ запрещен" ✅

### 3. Проверка работы с данными

**Тест 6: Создание хозяйства**
1. Войти под farmer
2. Перейти на страницу 🏢 Farm Setup
3. Создать хозяйство
4. В админ-панели (под админом) привязать farmer к этому хозяйству

**Тест 7: Аудит**
1. Войти под админом
2. Админ-панель → вкладка "📜 Журнал действий"
3. Видны записи о входах и создании пользователей ✅

---

## ⚙️ Streamlit Cloud настройки

### Secrets (если еще не настроены):

```toml
# .streamlit/secrets.toml на Streamlit Cloud

# PostgreSQL Connection
DATABASE_URL = "postgresql://postgres.xxxxx:password@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"

# Опционально: дополнительные секреты
# JWT_SECRET = "случайная_строка_для_токенов"
# SESSION_TIMEOUT = 3600
```

### Requirements (уже в репозитории):

```txt
streamlit>=1.32.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
bcrypt>=4.0.0
streamlit-authenticator>=0.3.1
# ... остальные зависимости
```

---

## 🐛 Troubleshooting

### Проблема: "ModuleNotFoundError: No module named 'bcrypt'"

**Решение:**
- Проверьте, что `requirements.txt` включает `bcrypt>=4.0.0`
- Streamlit Cloud должен автоматически установить

### Проблема: "relation 'users' does not exist"

**Решение:**
1. Убедитесь, что DATABASE_URL правильный
2. База данных должна автоматически создать таблицы при первом запуске
3. Если нет - пересоздайте БД:
   - Локально запустите: `python -c "from modules.database import init_db; init_db()"`
   - Или в Supabase вручную выполните SQL для создания таблиц

### Проблема: "Не могу войти под админом"

**Решение:**
1. Проверьте правильность username и password
2. В Supabase проверьте таблицу users:
   ```sql
   SELECT username, email, role, is_active FROM users;
   ```
3. Убедитесь, что `is_active = true`
4. Пересоздайте админа если нужно

### Проблема: "Пароли не работают"

**Решение:**
- Убедитесь, что хеш пароля был создан правильно с bcrypt
- НЕ вставляйте plain text пароли в БД!
- Всегда используйте bcrypt для хеширования

---

## 📊 Мониторинг

### Логи Streamlit Cloud:

1. Перейдите в Streamlit Cloud Dashboard
2. Выберите приложение "sbor_apk"
3. Нажмите "Manage app" (правый нижний угол)
4. Смотрите логи в реальном времени

### Метрики для отслеживания:

- Количество пользователей
- Количество входов
- Количество ошибок авторизации
- Активность в админ-панели

---

## 🎉 Готово!

После выполнения всех шагов система с авторизацией полностью развернута на Streamlit Cloud!

**Следующие шаги:**
1. Создайте пользователей для реальных фермеров
2. Привяжите каждого фермера к своему хозяйству
3. Обучите пользователей работе с системой
4. Мониторьте логи и аудит

---

**Версия документа:** 1.0
**Последнее обновление:** 15 октября 2025
