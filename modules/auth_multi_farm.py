"""
Multi-farm support functions
Функции для работы с множественными хозяйствами пользователя
"""
import streamlit as st
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from modules.database import UserFarm, Farm, SessionLocal
from modules.auth import get_current_user, is_admin


def get_user_farms(user_id: int, db: Session = None) -> List[Dict]:
    """
    Получить все хозяйства пользователя

    Args:
        user_id: ID пользователя
        db: Сессия БД (опционально)

    Returns:
        Список хозяйств с ролями пользователя
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        # Админ видит все хозяйства
        user = get_current_user()
        if user and user.get("role") == "admin":
            farms = db.query(Farm).all()
            return [{
                "farm_id": f.id,
                "farm_name": f.name,
                "farm_bin": f.bin,
                "role": "admin",
                "is_primary": False
            } for f in farms]

        # Обычный пользователь - хозяйства из user_farms
        user_farm_records = db.query(
            UserFarm, Farm
        ).join(
            Farm, UserFarm.farm_id == Farm.id
        ).filter(
            UserFarm.user_id == user_id
        ).all()

        result = []
        for uf, farm in user_farm_records:
            result.append({
                "farm_id": farm.id,
                "farm_name": farm.name,
                "farm_bin": farm.bin,
                "role": uf.role,
                "is_primary": uf.is_primary
            })

        return result
    finally:
        if close_db:
            db.close()


def get_primary_farm_id(user_id: int, db: Session = None) -> Optional[int]:
    """
    Получить ID основного хозяйства пользователя

    Args:
        user_id: ID пользователя
        db: Сессия БД

    Returns:
        ID основного хозяйства или None
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        primary = db.query(UserFarm).filter(
            UserFarm.user_id == user_id,
            UserFarm.is_primary == True
        ).first()

        if primary:
            return primary.farm_id

        # Если нет основного - вернуть первое доступное
        first_farm = db.query(UserFarm).filter(
            UserFarm.user_id == user_id
        ).first()

        return first_farm.farm_id if first_farm else None
    finally:
        if close_db:
            db.close()


def get_selected_farm_id() -> Optional[int]:
    """
    Получить ID текущего выбранного хозяйства из session_state

    Returns:
        ID выбранного хозяйства или None
    """
    user = get_current_user()
    if not user:
        return None

    # Проверяем, есть ли выбранное хозяйство в session_state
    if "selected_farm_id" in st.session_state:
        return st.session_state.selected_farm_id

    # Если нет - пытаемся получить основное хозяйство
    user_id = user.get("id")
    if user_id:
        primary_farm_id = get_primary_farm_id(user_id)
        if primary_farm_id:
            st.session_state.selected_farm_id = primary_farm_id
            return primary_farm_id

    # Fallback на legacy farm_id из user
    legacy_farm_id = user.get("farm_id")
    if legacy_farm_id:
        st.session_state.selected_farm_id = legacy_farm_id
        return legacy_farm_id

    return None


def set_selected_farm_id(farm_id: int):
    """
    Установить выбранное хозяйство в session_state

    Args:
        farm_id: ID хозяйства
    """
    st.session_state.selected_farm_id = farm_id
    # Обновляем также в user session для совместимости
    if "user" in st.session_state:
        st.session_state.user["farm_id"] = farm_id


def render_farm_selector():
    """
    Отобразить селектор хозяйств в интерфейсе
    Должен быть вызван на каждой странице для переключения между хозяйствами
    """
    user = get_current_user()
    if not user:
        return

    user_id = user.get("id")
    if not user_id:
        return

    # Получаем список хозяйств пользователя
    farms = get_user_farms(user_id)

    if not farms:
        st.warning("⚠️ У вас нет доступа ни к одному хозяйству")
        return

    # Если только одно хозяйство - просто показываем его название
    if len(farms) == 1:
        farm = farms[0]
        st.info(f"🏢 **{farm['farm_name']}** ({farm['farm_bin']})")
        set_selected_farm_id(farm['farm_id'])
        return

    # Если несколько хозяйств - показываем селектор
    current_farm_id = get_selected_farm_id()

    # Найти текущее хозяйство в списке
    current_index = 0
    farm_options = []
    for i, farm in enumerate(farms):
        label = f"{farm['farm_name']} ({farm['farm_bin']})"
        if farm['is_primary']:
            label += " ⭐"
        farm_options.append(label)
        if farm['farm_id'] == current_farm_id:
            current_index = i

    selected_label = st.selectbox(
        "🏢 Выберите хозяйство:",
        options=farm_options,
        index=current_index,
        key="farm_selector"
    )

    # Обновить выбранное хозяйство
    selected_index = farm_options.index(selected_label)
    selected_farm_id = farms[selected_index]['farm_id']

    if selected_farm_id != current_farm_id:
        set_selected_farm_id(selected_farm_id)
        st.rerun()
