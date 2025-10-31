"""
Authentication Widget for Sidebar
"""
import streamlit as st
from modules.auth import (
    get_current_user, is_authenticated, get_user_display_name,
    get_user_role_display, logout_user
)


def show_auth_widget():
    """
    Показывает виджет авторизации в боковом меню
    """
    st.sidebar.markdown("---")

    if is_authenticated():
        # Пользователь авторизован
        user = get_current_user()

        st.sidebar.markdown("### 👤 Профиль")

        # Информация о пользователе
        st.sidebar.success(f"**{get_user_display_name()}**")
        st.sidebar.info(f"{get_user_role_display()}")

        if user.get('farm_id'):
            st.sidebar.caption(f"🏢 Хозяйство ID: {user['farm_id']}")

        # Кнопки управления
        col1, col2 = st.sidebar.columns(2)

        with col1:
            if st.button("👤 Профиль", key="sidebar_profile", use_container_width=True):
                st.switch_page("pages/99_🔐_Вход.py")

        with col2:
            if st.button("🚪 Выход", key="sidebar_logout", use_container_width=True):
                logout_user()
                st.rerun()

        # Админ-панель для администраторов
        if user.get('role') == 'admin':
            st.sidebar.markdown("---")
            if st.sidebar.button("⚙️ Админ-панель", key="sidebar_admin", use_container_width=True, type="primary"):
                st.switch_page("pages/98_⚙️_Администрирование.py")

    else:
        # Пользователь не авторизован
        st.sidebar.markdown("### 🔐 Авторизация")
        st.sidebar.warning("Вы не авторизованы")

        if st.sidebar.button("🔑 Войти", key="sidebar_login", use_container_width=True, type="primary"):
            st.switch_page("pages/99_🔐_Вход.py")

        st.sidebar.caption("💡 Войдите для полного доступа")


def show_auth_status():
    """
    Показывает краткий статус авторизации (для использования в основном контенте)
    """
    if is_authenticated():
        user = get_current_user()
        st.success(f"✅ Вы вошли как **{get_user_display_name()}** ({get_user_role_display()})")
    else:
        st.warning("⚠️ Вы не авторизованы. [Войти →](pages/99_🔐_Login.py)")


def require_auth_with_message(custom_message: str = None):
    """
    Проверка авторизации с кастомным сообщением
    """
    if not is_authenticated():
        st.error("❌ Доступ запрещен")

        if custom_message:
            st.warning(custom_message)
        else:
            st.warning("Для доступа к этой странице необходимо войти в систему.")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔑 Перейти к странице входа", type="primary", use_container_width=True):
                st.switch_page("pages/99_🔐_Вход.py")

        st.stop()
