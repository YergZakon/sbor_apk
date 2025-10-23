"""
Authentication and authorization utilities
"""
import bcrypt
import streamlit as st
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from modules.database import User, Farm, AuditLog, UserFarm, SessionLocal


def hash_password(password: str) -> str:
    """Хеширование пароля"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    full_name: str,
    role: str = "farmer",
    farm_id: Optional[int] = None
) -> User:
    """Создание нового пользователя"""
    hashed_pwd = hash_password(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_pwd,
        full_name=full_name,
        role=role,
        farm_id=farm_id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Аутентификация пользователя"""
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return None

    if not user.is_active:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    # Обновляем время последнего входа
    user.last_login = datetime.now()
    db.commit()

    return user


def get_current_user() -> Optional[dict]:
    """Получение текущего пользователя из session_state"""
    if "user" in st.session_state:
        return st.session_state["user"]
    return None


def is_authenticated() -> bool:
    """Проверка, авторизован ли пользователь"""
    return "user" in st.session_state and st.session_state["user"] is not None


def is_admin() -> bool:
    """Проверка, является ли пользователь администратором"""
    user = get_current_user()
    return user is not None and user.get("role") == "admin"


def is_farmer() -> bool:
    """Проверка, является ли пользователь фермером"""
    user = get_current_user()
    return user is not None and user.get("role") == "farmer"


def is_viewer() -> bool:
    """Проверка, является ли пользователь просмотрщиком"""
    user = get_current_user()
    return user is not None and user.get("role") == "viewer"


def has_farm_access(farm_id: int) -> bool:
    """Проверка доступа к хозяйству"""
    user = get_current_user()

    if not user:
        return False

    # Админ имеет доступ ко всем хозяйствам
    if user.get("role") == "admin":
        return True

    # Проверяем, привязан ли пользователь к этому хозяйству
    return user.get("farm_id") == farm_id


def require_auth(redirect_to_login: bool = True):
    """Декоратор/проверка авторизации"""
    if not is_authenticated():
        st.error("❌ Требуется авторизация")
        if redirect_to_login:
            st.info("👉 Пожалуйста, войдите в систему через боковое меню")
        st.stop()


def require_admin():
    """Проверка прав администратора"""
    require_auth()
    if not is_admin():
        st.error("❌ Доступ запрещен. Требуются права администратора.")
        st.stop()


def require_role(*roles):
    """Проверка наличия одной из указанных ролей"""
    require_auth()
    user = get_current_user()

    if user.get("role") not in roles:
        st.error(f"❌ Доступ запрещен. Требуется одна из ролей: {', '.join(roles)}")
        st.stop()


def login_user(user: User):
    """Вход пользователя в систему"""
    st.session_state["user"] = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "farm_id": user.farm_id
    }


def logout_user():
    """Выход пользователя из системы"""
    if "user" in st.session_state:
        del st.session_state["user"]


def log_action(
    db: Session,
    user_id: int,
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    details: Optional[str] = None
):
    """Логирование действий пользователя"""
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )
    db.add(log)
    db.commit()


def get_user_display_name() -> str:
    """Получение отображаемого имени пользователя"""
    user = get_current_user()
    if not user:
        return "Гость"

    return user.get("full_name") or user.get("username") or "Пользователь"


def get_user_role_display() -> str:
    """Получение отображаемого названия роли"""
    user = get_current_user()
    if not user:
        return ""

    role_map = {
        "admin": "👑 Администратор",
        "farmer": "👨‍🌾 Фермер",
        "viewer": "👁️ Наблюдатель"
    }

    return role_map.get(user.get("role"), user.get("role"))


def get_user_farm_id() -> Optional[int]:
    """Получение ID хозяйства текущего пользователя"""
    user = get_current_user()
    if not user:
        return None
    return user.get("farm_id")


def filter_query_by_farm(query, model):
    """
    Фильтрация запроса по хозяйству в зависимости от роли пользователя

    Args:
        query: SQLAlchemy query
        model: Модель с полем farm_id

    Returns:
        Отфильтрованный query
    """
    user = get_current_user()

    if not user:
        # Если не авторизован - пустой результат
        return query.filter(False)

    # Админ видит всё
    if user.get("role") == "admin":
        return query

    # Фермер и Viewer видят только данные своего хозяйства
    farm_id = user.get("farm_id")

    if not farm_id:
        # Если не привязан к хозяйству - пустой результат
        return query.filter(False)

    # Фильтруем по farm_id
    if hasattr(model, 'farm_id'):
        return query.filter(model.farm_id == farm_id)
    else:
        # Если у модели нет farm_id напрямую, возвращаем как есть
        return query


def can_edit_data() -> bool:
    """Проверка, может ли пользователь редактировать данные"""
    user = get_current_user()
    if not user:
        return False

    # Admin и Farmer могут редактировать
    return user.get("role") in ["admin", "farmer"]


def can_delete_data() -> bool:
    """Проверка, может ли пользователь удалять данные"""
    user = get_current_user()
    if not user:
        return False

    # Только Admin может удалять
    return user.get("role") == "admin"


def require_farm_binding():
    """Проверка, что пользователь привязан к хозяйству"""
    require_auth()

    user = get_current_user()

    # Админ может работать без привязки
    if user.get("role") == "admin":
        return

    # Для остальных обязательна привязка
    if not user.get("farm_id"):
        st.error("❌ Ваш аккаунт не привязан к хозяйству")
        st.warning("Обратитесь к администратору для привязки вашего аккаунта к хозяйству.")

        st.info("**Контакты администратора:**\nEmail: admin@agrodata.kz")
        st.stop()
