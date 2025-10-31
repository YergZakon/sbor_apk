"""
Login & Registration Page
"""
import streamlit as st
from modules.database import SessionLocal, User
from modules.auth import authenticate_user, login_user, logout_user, get_current_user, create_user
import re

st.set_page_config(page_title="Вход в систему", page_icon="🔐", layout="centered")

# Инициализация session state
if "user" not in st.session_state:
    st.session_state["user"] = None

db = SessionLocal()

try:
    current_user = get_current_user()

    # Если пользователь уже авторизован
    if current_user:
        st.title("👋 Вы уже вошли в систему")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.success(f"**Пользователь:** {current_user['full_name'] or current_user['username']}")
            st.info(f"**Роль:** {current_user['role']}")
            if current_user['farm_id']:
                st.info(f"**Хозяйство ID:** {current_user['farm_id']}")

        with col2:
            if st.button("🚪 Выйти", use_container_width=True, type="primary"):
                logout_user()
                st.rerun()

        st.markdown("---")
        st.markdown("### 🔗 Быстрые ссылки")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🏠 Dashboard", use_container_width=True):
                st.switch_page("pages/1_🏠_Панель_управления.py")

        with col2:
            if st.button("🌱 Поля", use_container_width=True):
                st.switch_page("pages/2_🌱_Поля.py")

        with col3:
            if current_user['role'] == 'admin':
                if st.button("⚙️ Админка", use_container_width=True):
                    st.switch_page("pages/98_⚙️_Администрирование.py")

    else:
        # Страница входа
        st.title("🔐 Вход в систему")
        st.markdown("Система сбора сельскохозяйственных данных")

        tabs = st.tabs(["🔑 Вход", "📝 Регистрация"])

        # ========================
        # ВКЛАДКА ВХОДА
        # ========================
        with tabs[0]:
            st.markdown("### Войти в систему")

            with st.form("login_form"):
                username = st.text_input(
                    "Имя пользователя",
                    placeholder="Введите ваш username",
                    help="Используйте имя пользователя, которое вы указали при регистрации"
                )

                password = st.text_input(
                    "Пароль",
                    type="password",
                    placeholder="Введите пароль",
                    help="Пароль чувствителен к регистру"
                )

                submitted = st.form_submit_button("🔓 Войти", use_container_width=True, type="primary")

                if submitted:
                    if not username or not password:
                        st.error("❌ Заполните все поля")
                    else:
                        with st.spinner("Проверка учетных данных..."):
                            user = authenticate_user(db, username, password)

                            if user:
                                login_user(user)
                                st.success(f"✅ Добро пожаловать, {user.full_name or user.username}!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Неверное имя пользователя или пароль")

            st.markdown("---")
            st.info("💡 **Первый раз здесь?** Зарегистрируйтесь на вкладке 'Регистрация'")

        # ========================
        # ВКЛАДКА РЕГИСТРАЦИИ
        # ========================
        with tabs[1]:
            st.markdown("### Создать новый аккаунт")

            st.info("ℹ️ **После регистрации** вы сможете создать свое хозяйство и начать работу с системой.")

            with st.form("registration_form"):
                col1, col2 = st.columns(2)

                with col1:
                    reg_username = st.text_input(
                        "Имя пользователя *",
                        placeholder="username",
                        help="Уникальное имя для входа (только латиница, цифры, _)"
                    )

                    reg_email = st.text_input(
                        "Email *",
                        placeholder="user@example.com",
                        help="Ваш email адрес"
                    )

                with col2:
                    reg_full_name = st.text_input(
                        "Полное имя *",
                        placeholder="Иванов Иван Иванович",
                        help="Ваше полное имя"
                    )

                    reg_password = st.text_input(
                        "Пароль *",
                        type="password",
                        placeholder="Минимум 6 символов",
                        help="Используйте надежный пароль"
                    )

                reg_password_confirm = st.text_input(
                    "Подтвердите пароль *",
                    type="password",
                    placeholder="Введите пароль еще раз"
                )

                st.markdown("---")

                reg_submitted = st.form_submit_button("📝 Зарегистрироваться", use_container_width=True, type="primary")

                if reg_submitted:
                    errors = []

                    # Валидация
                    if not reg_username or not reg_email or not reg_full_name or not reg_password:
                        errors.append("Заполните все обязательные поля")

                    if reg_username and not re.match(r'^[a-zA-Z0-9_]{3,20}$', reg_username):
                        errors.append("Имя пользователя: 3-20 символов, только латиница, цифры и _")

                    if reg_email and not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', reg_email):
                        errors.append("Неверный формат email")

                    if reg_password and len(reg_password) < 6:
                        errors.append("Пароль должен быть минимум 6 символов")

                    if reg_password != reg_password_confirm:
                        errors.append("Пароли не совпадают")

                    # Проверка уникальности
                    if reg_username:
                        existing_user = db.query(User).filter(User.username == reg_username).first()
                        if existing_user:
                            errors.append("Пользователь с таким именем уже существует")

                    if reg_email:
                        existing_email = db.query(User).filter(User.email == reg_email).first()
                        if existing_email:
                            errors.append("Пользователь с таким email уже существует")

                    if errors:
                        for error in errors:
                            st.error(f"❌ {error}")
                    else:
                        try:
                            # Создаем пользователя с ролью farmer по умолчанию
                            new_user = create_user(
                                db=db,
                                username=reg_username,
                                email=reg_email,
                                password=reg_password,
                                full_name=reg_full_name,
                                role="farmer",
                                farm_id=None
                            )

                            st.success(f"✅ Аккаунт успешно создан!")
                            st.info("💡 Сейчас вы будете перенаправлены на создание хозяйства")
                            st.balloons()

                            # Автоматический вход после регистрации
                            login_user(new_user)

                            # Перенаправление на Farm Setup для создания хозяйства
                            import time
                            time.sleep(2)
                            st.switch_page("pages/0_🏢_Регистрация_хозяйства.py")

                        except Exception as e:
                            st.error(f"❌ Ошибка при регистрации: {str(e)}")

            st.markdown("---")
            st.info("💡 **Уже есть аккаунт?** Войдите на вкладке 'Вход'")

finally:
    db.close()

# Sidebar info
with st.sidebar:
    st.markdown("### ℹ️ Информация")
    st.markdown("""
    **Роли пользователей:**
    - 👑 **Admin** - полный доступ + управление пользователями
    - 👨‍🌾 **Farmer** - доступ к своему хозяйству
    - 👁️ **Viewer** - только просмотр

    **Безопасность:**
    - Пароли хешируются (bcrypt)
    - Сессии защищены
    - Аудит всех действий
    """)

    st.markdown("---")
    st.markdown("**Нужна помощь?**")
    st.markdown("Обратитесь к администратору системы")
