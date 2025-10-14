# 🗄️ Настройка постоянного хранения данных с Supabase

## ⚠️ Проблема
На бесплатном Streamlit Cloud SQLite база данных **НЕ сохраняется**:
- При каждом деплое данные удаляются
- После перезапуска данные пропадают
- После сна (7 дней) данные теряются

## ✅ Решение: Supabase PostgreSQL

### Преимущества
- ✅ **Бесплатно** (500 MB БД)
- ✅ **PostgreSQL** (надежнее SQLite)
- ✅ **Данные сохраняются навсегда**
- ✅ **Легко настроить** (5 минут)
- ✅ **Код уже готов!**

---

## 📝 Пошаговая инструкция

### Шаг 1: Создайте аккаунт Supabase

1. Откройте: https://supabase.com
2. Нажмите "Start your project"
3. Войдите через GitHub (используйте аккаунт YergZakon)

### Шаг 2: Создайте новый проект

1. Нажмите "New Project"
2. Выберите организацию (или создайте новую)
3. Заполните форму:
   - **Name**: `farm-data-system` (или любое имя)
   - **Database Password**: придумайте надежный пароль (сохраните его!)
   - **Region**: Europe West (recommended) или ближайший к Казахстану
   - **Pricing Plan**: Free
4. Нажмите "Create new project"
5. Дождитесь создания (~2 минуты)

### Шаг 3: Получите строку подключения

1. В Supabase Dashboard откройте:
   - **Settings** (иконка шестеренки внизу слева)
   - **Database**
2. Прокрутите до секции "Connection string"
3. Выберите режим: **URI**
4. Скопируйте строку подключения
   
   Она будет выглядеть так:
   ```
   postgresql://postgres.[PROJECT_REF]:[YOUR_PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
   ```

5. **ВАЖНО:** Замените `[YOUR_PASSWORD]` на реальный пароль, который вы создали

### Шаг 4: Добавьте DATABASE_URL в Streamlit Cloud

1. Откройте: https://share.streamlit.io/
2. Найдите приложение `sbor-apk`
3. Нажмите на три точки (⋮) → **Settings**
4. Перейдите в **Secrets**
5. Вставьте в поле:

```toml
DATABASE_URL = "postgresql://postgres.[PROJECT_REF]:[YOUR_PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
```

**Замените** на вашу реальную строку подключения!

6. Нажмите **Save**

### Шаг 5: Перезапустите приложение

1. В Streamlit Cloud нажмите **Reboot app**
2. Дождитесь перезапуска (~1-2 минуты)
3. Готово! 🎉

---

## ✅ Проверка

После настройки:

1. **Откройте приложение**: https://sbor-apk.streamlit.app
2. **Зарегистрируйте хозяйство**
3. **Добавьте поле**
4. **Создайте операцию**
5. **Закройте вкладку и откройте снова**

Если данные остались - всё работает! ✅

---

## 🔍 Как это работает

### Локально (на вашем компьютере):
```python
DATABASE_URL = "sqlite:///./farm_data.db"  # Файл
```

### На Streamlit Cloud (с Supabase):
```python
DATABASE_URL = "postgresql://postgres:...@supabase.com:6543/postgres"  # Внешняя БД
```

Код автоматически определяет, какую БД использовать:
- Если есть переменная `DATABASE_URL` → использует её
- Если нет → использует SQLite локально

---

## 📊 Мониторинг Supabase

### Посмотреть данные:

1. Откройте Supabase Dashboard
2. Перейдите в **Table Editor**
3. Выберите таблицу (farms, fields, operations и т.д.)
4. Просмотрите/отредактируйте данные

### Посмотреть SQL запросы:

1. Откройте **SQL Editor**
2. Напишите запрос, например:
```sql
SELECT * FROM farms;
```

### Посмотреть размер БД:

1. Откройте **Settings** → **Database**
2. Смотрите "Database size"

---

## 🆘 Troubleshooting

### Ошибка: "password authentication failed"
- Проверьте, что заменили `[YOUR_PASSWORD]` на реальный пароль
- Убедитесь, что в пароле нет спецсимволов, требующих экранирования

### Ошибка: "could not connect to server"
- Проверьте, что скопировали полную строку подключения
- Убедитесь, что выбрали режим "URI" (не "PSQL")

### Ошибка: "relation 'farms' does not exist"
- Это нормально при первом запуске
- База данных автоматически создаст таблицы при первом обращении

### Приложение не запускается
1. Проверьте логи в Streamlit Cloud Dashboard
2. Убедитесь, что в Secrets правильный формат (TOML)
3. Проверьте, что добавили `psycopg2-binary` в requirements.txt

---

## 💰 Лимиты бесплатного плана Supabase

- **Database**: 500 MB
- **Bandwidth**: 5 GB/месяц
- **Storage**: 1 GB
- **Requests**: Unlimited

Для MVP этого более чем достаточно!

---

## 🔐 Безопасность

**ВАЖНО:**
- ❌ НЕ коммитьте DATABASE_URL в Git
- ❌ НЕ публикуйте пароль публично
- ✅ Используйте только Streamlit Secrets
- ✅ Используйте сильный пароль

---

## 🎯 Альтернативы Supabase

Если по какой-то причине Supabase не подходит:

### Railway
- https://railway.app
- $5 кредит/месяц
- PostgreSQL + Redis

### ElephantSQL
- https://www.elephantsql.com
- 20 MB бесплатно
- Только PostgreSQL

### Neon
- https://neon.tech
- 10 GB бесплатно
- Serverless PostgreSQL

---

## ✅ Готово!

После настройки:
- ✅ Данные сохраняются навсегда
- ✅ Работает при перезапусках
- ✅ Не удаляется при деплоях
- ✅ Доступ из любого места

**Статус**: Готово к production 🚀
