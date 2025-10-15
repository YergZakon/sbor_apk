# 🔐 Правильный формат Streamlit Secrets

## ⚠️ Важно!

В Streamlit Cloud Secrets нужно использовать **точный** формат из Supabase.

---

## 📝 Как получить правильную строку подключения

### В Supabase Dashboard:

1. Откройте ваш проект
2. Перейдите в **Settings** (иконка шестеренки слева внизу)
3. Выберите **Database**
4. Прокрутите вниз до секции **Connection string**
5. В выпадающем списке выберите **URI** (не PSQL!)
6. В другом выпадающем списке выберите **Transaction** (порт 6543)
7. Скопируйте строку

---

## ✅ Правильный формат в Streamlit Secrets

Откройте Streamlit Cloud → Settings → Secrets

И вставьте **ТОЧНО В ТАКОМ ФОРМАТЕ**:

```toml
DATABASE_URL = "postgresql://postgres.xxxxxxxxxxxxx:your_password_here@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
```

### Важные моменты:

1. ✅ **Должны быть кавычки** вокруг URL
2. ✅ **Замените пароль** - вместо `your_password_here` вставьте реальный пароль
3. ✅ **Порт 6543** (Transaction mode, с pooler)
4. ✅ **Не должно быть пробелов** вокруг `=`
5. ✅ **Одна строка** (без переносов)

---

## 🔍 Примеры (НЕ копируйте, используйте СВОЮ строку!)

### ❌ НЕПРАВИЛЬНО:

```toml
# Без кавычек - НЕ РАБОТАЕТ
DATABASE_URL = postgresql://...

# Пробелы вокруг = - НЕ РАБОТАЕТ  
DATABASE_URL = "postgresql://..."

# Не заменили пароль - НЕ РАБОТАЕТ
DATABASE_URL = "postgresql://postgres.xxx:[YOUR_PASSWORD]@..."

# Неправильный порт 5432 без pooler - МОЖЕТ НЕ РАБОТАТЬ
DATABASE_URL = "postgresql://...@db.xxx.supabase.co:5432/postgres"
```

### ✅ ПРАВИЛЬНО:

```toml
DATABASE_URL = "postgresql://postgres.abcdefghijklmnop:SuperSecret123@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
```

---

## 🔄 Пошаговая инструкция исправления

### 1. Получите правильную строку в Supabase

1. Зайдите на https://supabase.com
2. Откройте ваш проект `farm-data-system`
3. Settings → Database
4. Connection string → **URI** → **Transaction** (порт 6543)
5. Скопируйте строку ПОЛНОСТЬЮ

### 2. Найдите ваш пароль

Если забыли пароль:
1. В Supabase Settings → Database
2. Нажмите **Reset database password**
3. Создайте новый пароль (запишите его!)
4. Замените `[YOUR_PASSWORD]` в строке подключения на новый пароль

### 3. Обновите Streamlit Secrets

1. Откройте https://share.streamlit.io/
2. Найдите приложение `sbor-apk`
3. Три точки (⋮) → **Settings** → **Secrets**
4. **УДАЛИТЕ** старое содержимое
5. Вставьте новое:
   ```toml
   DATABASE_URL = "postgresql://postgres.xxxxx:ваш_пароль@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
   ```
6. Нажмите **Save**

### 4. Перезапустите приложение

1. В Streamlit Cloud: три точки (⋮) → **Reboot app**
2. Дождитесь перезапуска (~1-2 минуты)
3. Проверьте логи

---

## 🧪 Тестирование локально (опционально)

Если хотите проверить строку подключения локально:

```bash
cd farm_data_system

# Создайте файл .env
echo 'DATABASE_URL="postgresql://postgres.xxx:password@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"' > .env

# Запустите приложение
streamlit run app.py
```

Если запустилось без ошибок - строка правильная! ✅

---

## 📋 Чеклист проверки

Перед сохранением Secrets проверьте:

- [ ] Формат: `DATABASE_URL = "postgresql://..."`
- [ ] Кавычки есть вокруг URL
- [ ] Пароль заменен (нет `[YOUR_PASSWORD]`)
- [ ] Порт 6543 (с pooler)
- [ ] Хост содержит `.pooler.supabase.com`
- [ ] Нет лишних пробелов
- [ ] Строка не разорвана (на одной линии)

---

## 🆘 Если всё равно не работает

1. **Скопируйте ТОЧНОЕ содержимое Streamlit Secrets** (замените пароль на `***`)
2. **Скопируйте текст ошибки** из логов
3. **Покажите мне** - я помогу найти проблему

---

## ✅ После исправления

После сохранения правильного DATABASE_URL:

1. Перезапустите приложение
2. Проверьте логи - должно быть:
   ```
   Database initialized successfully
   ✓ Connected to PostgreSQL
   ```
3. Откройте приложение
4. Зарегистрируйте хозяйство
5. Проверьте в Supabase Table Editor - запись должна появиться!

---

**Удачи!** 🚀
