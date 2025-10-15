# 🔐 Настройка системы авторизации

**Версия:** 2.0.0
**Дата:** 15 октября 2025

---

## 📋 Обзор

Система авторизации добавляет многопользовательский режим работы с разграничением доступа по ролям.

### Роли пользователей:

| Роль | Иконка | Описание | Доступ |
|------|--------|----------|--------|
| **Admin** | 👑 | Администратор | Полный доступ + управление пользователями |
| **Farmer** | 👨‍🌾 | Фермер | Доступ только к своему хозяйству |
| **Viewer** | 👁️ | Наблюдатель | Только просмотр (консультанты, агрономы) |

---

## 🚀 Первоначальная настройка

### Шаг 1: Обновить зависимости

```bash
pip install -r requirements.txt
```

Новые зависимости:
- `streamlit-authenticator>=0.3.1`
- `bcrypt>=4.0.0`

### Шаг 2: Обновить базу данных

При первом запуске приложения после обновления база данных автоматически создаст новые таблицы:
- `users` - пользователи системы
- `audit_logs` - журнал действий

```bash
streamlit run app.py
```

### Шаг 3: Создать первого администратора

Запустите utility script для создания админа:

```bash
python create_admin.py
```

**Пример:**
```
Username: admin
Email: admin@agrodata.kz
Full Name: System Administrator
Password: ******* (минимум 6 символов)
```

✅ Готово! Теперь вы можете войти в систему.

---

## 🔑 Использование системы

### Вход в систему

1. Откройте приложение: `http://localhost:8501`
2. Перейдите на страницу **🔐 Login** (в боковом меню внизу)
3. Введите username и пароль
4. Нажмите **🔓 Войти**

### Регистрация нового пользователя

**Способ 1: Самостоятельная регистрация**
1. Перейдите на страницу **🔐 Login**
2. Откройте вкладку **📝 Регистрация**
3. Заполните форму
4. Нажмите **📝 Зарегистрироваться**

⚠️ После регистрации администратор должен:
- Активировать аккаунт (по умолчанию активен)
- Привязать к хозяйству
- Назначить правильную роль

**Способ 2: Создание через админ-панель**
1. Войдите как администратор
2. Перейдите на страницу **⚙️ Admin**
3. Откройте вкладку **➕ Создать пользователя**
4. Заполните форму и создайте пользователя

---

## ⚙️ Админ-панель

Доступна только для пользователей с ролью **admin**.

### Путь: `pages/98_⚙️_Admin.py`

### Функции:

**1. Управление пользователями**
- Просмотр всех пользователей
- Фильтрация по роли, статусу, хозяйству
- Редактирование пользователей
- Изменение пароля
- Активация/деактивация
- Удаление пользователей

**2. Создание пользователей**
- Быстрое создание новых аккаунтов
- Автоматическая привязка к хозяйству
- Назначение ролей

**3. Журнал действий**
- Просмотр последних 100 действий
- Кто, когда, что сделал
- Экспорт в CSV

**4. Настройки** (в разработке)
- Резервное копирование
- Системные логи
- Настройки безопасности

---

## 🔒 Безопасность

### Хеширование паролей

Пароли хешируются с использованием **bcrypt** с автоматической генерацией соли.

```python
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')
```

### Сессии

Авторизационные данные хранятся в `st.session_state`:
- Не сохраняются между перезапусками браузера
- Очищаются при выходе
- Защищены от XSS

### Аудит

Все действия пользователей логируются в таблицу `audit_logs`:
- Login/Logout
- Create/Update/Delete операции
- Timestamp и IP (будущее)

---

## 💻 Интеграция в существующие страницы

### Добавление виджета авторизации

В любую страницу добавьте:

```python
from modules.auth_widget import show_auth_widget

# В sidebar
with st.sidebar:
    show_auth_widget()
```

### Требование авторизации

**Простая проверка:**
```python
from modules.auth import require_auth

require_auth()  # Остановит выполнение если не авторизован
```

**Проверка роли:**
```python
from modules.auth import require_admin, require_role

require_admin()  # Только для админов

require_role("farmer", "admin")  # Для фермеров и админов
```

**Проверка доступа к хозяйству:**
```python
from modules.auth import has_farm_access

if not has_farm_access(farm_id):
    st.error("❌ Нет доступа к этому хозяйству")
    st.stop()
```

### Получение текущего пользователя

```python
from modules.auth import get_current_user, is_authenticated

if is_authenticated():
    user = get_current_user()
    print(user['username'])
    print(user['role'])
    print(user['farm_id'])
```

---

## 📊 Структура базы данных

### Таблица `users`

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Primary key |
| username | String(50) | Уникальное имя пользователя |
| email | String(100) | Уникальный email |
| hashed_password | String(255) | Хеш пароля (bcrypt) |
| full_name | String(200) | Полное имя |
| role | String(20) | admin / farmer / viewer |
| is_active | Boolean | Активен ли аккаунт |
| farm_id | Integer | FK к таблице farms (nullable) |
| created_at | DateTime | Дата создания |
| updated_at | DateTime | Дата обновления |
| last_login | DateTime | Последний вход |

### Таблица `audit_logs`

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Primary key |
| user_id | Integer | FK к users |
| action | String(100) | Тип действия |
| entity_type | String(50) | Тип сущности |
| entity_id | Integer | ID сущности |
| details | Text | JSON с деталями |
| ip_address | String(50) | IP адрес |
| created_at | DateTime | Timestamp |

---

## 🔧 API Reference

### modules/auth.py

**Основные функции:**

```python
# Хеширование и проверка
hash_password(password: str) -> str
verify_password(password: str, hashed: str) -> bool

# Управление пользователями
create_user(db, username, email, password, full_name, role, farm_id) -> User
authenticate_user(db, username, password) -> User | None

# Сессии
login_user(user: User)
logout_user()
get_current_user() -> dict | None

# Проверки
is_authenticated() -> bool
is_admin() -> bool
is_farmer() -> bool
is_viewer() -> bool
has_farm_access(farm_id: int) -> bool

# Декораторы/проверки
require_auth()
require_admin()
require_role(*roles)

# Аудит
log_action(db, user_id, action, entity_type, entity_id, details)

# Helpers
get_user_display_name() -> str
get_user_role_display() -> str
```

### modules/auth_widget.py

```python
# Виджет для sidebar
show_auth_widget()

# Статус в контенте
show_auth_status()

# Проверка с кастомным сообщением
require_auth_with_message(custom_message: str)
```

---

## 🆘 Troubleshooting

### Проблема: Не могу войти

**Решение:**
1. Проверьте правильность username и пароля
2. Убедитесь, что пользователь активен (`is_active = True`)
3. Проверьте, создан ли пользователь: `python create_admin.py`

### Проблема: Забыл пароль админа

**Решение:**
Создайте нового администратора или измените пароль напрямую в базе:

```python
from modules.database import SessionLocal, User
from modules.auth import hash_password

db = SessionLocal()
admin = db.query(User).filter(User.username == "admin").first()
admin.hashed_password = hash_password("new_password")
db.commit()
```

### Проблема: Нет доступа к хозяйству

**Решение:**
Администратор должен привязать пользователя к хозяйству:
1. Админ-панель → Управление пользователями
2. Выбрать пользователя → Редактировать
3. Выбрать хозяйство → Сохранить

### Проблема: Таблицы users не существует

**Решение:**
Пересоздайте базу данных:

```bash
rm farm_data.db
python -c "from modules.database import init_db; init_db()"
python create_admin.py
```

---

## 📈 Roadmap

### v2.1 (планируется)
- [ ] Двухфакторная аутентификация (2FA)
- [ ] Восстановление пароля по email
- [ ] История входов
- [ ] Ограничение попыток входа

### v2.2 (планируется)
- [ ] OAuth интеграция (Google, Microsoft)
- [ ] API токены для внешних систем
- [ ] Детальные права доступа (RBAC+)
- [ ] Multi-tenancy для организаций

---

## 📚 Дополнительные ресурсы

- [bcrypt Documentation](https://github.com/pyca/bcrypt/)
- [Streamlit Authentication](https://docs.streamlit.io/library/advanced-features/session-state)
- [Security Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

**Версия документа:** 1.0
**Последнее обновление:** 15 октября 2025
