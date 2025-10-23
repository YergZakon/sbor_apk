"""
Admin Panel - User Management
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from modules.database import SessionLocal, User, Farm, AuditLog, UserFarm
from modules.auth import (
    require_admin, get_current_user, create_user, hash_password,
    get_user_display_name, log_action
)

st.set_page_config(page_title="Админ-панель", page_icon="⚙️", layout="wide")

# Проверка прав администратора
require_admin()

st.title("⚙️ Админ-панель")
st.markdown("Управление пользователями и системой")

db = SessionLocal()
current_user = get_current_user()

try:
    # Статистика в шапке
    st.markdown("### 📊 Статистика системы")

    col1, col2, col3, col4 = st.columns(4)

    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_farms = db.query(Farm).count()
    recent_logins = db.query(User).filter(User.last_login.isnot(None)).count()

    with col1:
        st.metric("Всего пользователей", total_users)
    with col2:
        st.metric("Активных", active_users, delta=f"{active_users}/{total_users}")
    with col3:
        st.metric("Хозяйств", total_farms)
    with col4:
        st.metric("Входили в систему", recent_logins)

    st.markdown("---")

    # Вкладки админки
    tabs = st.tabs(["👥 Пользователи", "➕ Создать пользователя", "🏢 Назначение на хозяйства", "📜 Журнал действий", "⚙️ Настройки"])

    # ============================================================================
    # ВКЛАДКА: УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ
    # ============================================================================
    with tabs[0]:
        st.markdown("### 👥 Управление пользователями")

        # Фильтры
        col1, col2, col3 = st.columns(3)

        with col1:
            filter_role = st.selectbox("Роль", ["Все", "admin", "farmer", "viewer"])

        with col2:
            filter_status = st.selectbox("Статус", ["Все", "Активные", "Неактивные"])

        with col3:
            filter_farm = st.selectbox(
                "Хозяйство",
                ["Все"] + [f"{f.bin} - {f.name}" for f in db.query(Farm).all()]
            )

        # Получение пользователей с фильтрами
        query = db.query(User, Farm).outerjoin(Farm, User.farm_id == Farm.id)

        if filter_role != "Все":
            query = query.filter(User.role == filter_role)

        if filter_status == "Активные":
            query = query.filter(User.is_active == True)
        elif filter_status == "Неактивные":
            query = query.filter(User.is_active == False)

        if filter_farm != "Все":
            farm_bin = filter_farm.split(" - ")[0]
            query = query.filter(Farm.bin == farm_bin)

        users = query.all()

        if users:
            st.markdown(f"**Найдено пользователей:** {len(users)}")

            # Таблица пользователей
            data = []
            for user, farm in users:
                data.append({
                    "ID": user.id,
                    "Username": user.username,
                    "ФИО": user.full_name or "-",
                    "Email": user.email,
                    "Роль": user.role,
                    "Хозяйство": farm.name if farm else "Не привязан",
                    "Активен": "✅" if user.is_active else "❌",
                    "Последний вход": user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Никогда"
                })

            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Редактирование пользователя
            st.markdown("---")
            st.markdown("### ✏️ Редактировать пользователя")

            selected_username = st.selectbox(
                "Выберите пользователя",
                [user.username for user, _ in users]
            )

            if selected_username:
                selected_user = next((u for u, _ in users if u.username == selected_username), None)

                if selected_user:
                    with st.form("edit_user_form"):
                        st.markdown(f"**Редактирование:** {selected_user.username}")

                        col1, col2 = st.columns(2)

                        with col1:
                            edit_full_name = st.text_input("ФИО", value=selected_user.full_name or "")
                            edit_email = st.text_input("Email", value=selected_user.email)
                            edit_role = st.selectbox(
                                "Роль",
                                ["admin", "farmer", "viewer"],
                                index=["admin", "farmer", "viewer"].index(selected_user.role)
                            )

                        with col2:
                            farms = db.query(Farm).all()
                            farm_options = ["Не привязан"] + [f"{f.id} - {f.name}" for f in farms]

                            current_farm_index = 0
                            if selected_user.farm_id:
                                for idx, f in enumerate(farms, start=1):
                                    if f.id == selected_user.farm_id:
                                        current_farm_index = idx
                                        break

                            edit_farm = st.selectbox("Хозяйство", farm_options, index=current_farm_index)

                            edit_is_active = st.checkbox("Активен", value=selected_user.is_active)

                            edit_new_password = st.text_input(
                                "Новый пароль (оставьте пустым, чтобы не менять)",
                                type="password"
                            )

                        col1, col2 = st.columns(2)

                        with col1:
                            update_submitted = st.form_submit_button("💾 Сохранить изменения", type="primary", use_container_width=True)

                        with col2:
                            if selected_user.id != current_user['id']:  # Нельзя удалить себя
                                delete_submitted = st.form_submit_button("🗑️ Удалить пользователя", use_container_width=True)
                            else:
                                delete_submitted = False
                                st.info("Нельзя удалить себя")

                        if update_submitted:
                            try:
                                selected_user.full_name = edit_full_name
                                selected_user.email = edit_email
                                selected_user.role = edit_role
                                selected_user.is_active = edit_is_active

                                if edit_farm != "Не привязан":
                                    farm_id = int(edit_farm.split(" - ")[0])
                                    selected_user.farm_id = farm_id
                                else:
                                    selected_user.farm_id = None

                                if edit_new_password:
                                    selected_user.hashed_password = hash_password(edit_new_password)

                                selected_user.updated_at = datetime.now()

                                db.commit()

                                # Если редактируем текущего пользователя, обновляем session_state
                                if selected_user.id == current_user['id']:
                                    st.session_state["user"]["full_name"] = selected_user.full_name
                                    st.session_state["user"]["email"] = selected_user.email
                                    st.session_state["user"]["role"] = selected_user.role
                                    st.session_state["user"]["farm_id"] = selected_user.farm_id

                                # Логируем действие
                                log_action(
                                    db, current_user['id'], "update", "user", selected_user.id,
                                    f"Updated user: {selected_user.username}"
                                )

                                st.success(f"✅ Пользователь {selected_user.username} обновлен!")
                                st.rerun()

                            except Exception as e:
                                db.rollback()
                                st.error(f"❌ Ошибка: {str(e)}")

                        if delete_submitted:
                            try:
                                username_to_delete = selected_user.username
                                db.delete(selected_user)
                                db.commit()

                                log_action(
                                    db, current_user['id'], "delete", "user", selected_user.id,
                                    f"Deleted user: {username_to_delete}"
                                )

                                st.success(f"✅ Пользователь {username_to_delete} удален!")
                                st.rerun()

                            except Exception as e:
                                db.rollback()
                                st.error(f"❌ Ошибка: {str(e)}")

        else:
            st.info("👤 Пользователей не найдено")

    # ============================================================================
    # ВКЛАДКА: СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ
    # ============================================================================
    with tabs[1]:
        st.markdown("### ➕ Создать нового пользователя")

        with st.form("create_user_form"):
            col1, col2 = st.columns(2)

            with col1:
                new_username = st.text_input("Username *", placeholder="username")
                new_email = st.text_input("Email *", placeholder="user@example.com")
                new_full_name = st.text_input("ФИО *", placeholder="Иванов Иван Иванович")

            with col2:
                new_password = st.text_input("Пароль *", type="password", placeholder="Минимум 6 символов")
                new_role = st.selectbox("Роль *", ["farmer", "admin", "viewer"])

                farms = db.query(Farm).all()
                farm_options = ["Не привязан"] + [f"{f.id} - {f.name}" for f in farms]
                new_farm = st.selectbox("Хозяйство", farm_options)

            create_submitted = st.form_submit_button("➕ Создать пользователя", type="primary", use_container_width=True)

            if create_submitted:
                errors = []

                if not new_username or not new_email or not new_full_name or not new_password:
                    errors.append("Заполните все обязательные поля")

                if len(new_password) < 6:
                    errors.append("Пароль должен быть минимум 6 символов")

                # Проверка уникальности
                if db.query(User).filter(User.username == new_username).first():
                    errors.append("Пользователь с таким username уже существует")

                if db.query(User).filter(User.email == new_email).first():
                    errors.append("Пользователь с таким email уже существует")

                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    try:
                        farm_id = None
                        if new_farm != "Не привязан":
                            farm_id = int(new_farm.split(" - ")[0])

                        new_user = create_user(
                            db=db,
                            username=new_username,
                            email=new_email,
                            password=new_password,
                            full_name=new_full_name,
                            role=new_role,
                            farm_id=farm_id
                        )

                        log_action(
                            db, current_user['id'], "create", "user", new_user.id,
                            f"Created user: {new_user.username}"
                        )

                        st.success(f"✅ Пользователь {new_user.username} создан!")
                        st.balloons()

                    except Exception as e:
                        st.error(f"❌ Ошибка: {str(e)}")

    # ============================================================================
    # ВКЛАДКА: НАЗНАЧЕНИЕ НА ХОЗЯЙСТВА (MULTI-FARM)
    # ============================================================================
    with tabs[2]:
        st.markdown("### 🏢 Управление доступом к хозяйствам")
        st.info("💡 **Multi-Farm**: Назначьте пользователю доступ к нескольким хозяйствам с разными ролями")

        # Выбор пользователя
        all_users = db.query(User).filter(User.role != 'admin').all()  # Админам не нужно назначение

        if not all_users:
            st.warning("👤 Нет пользователей для назначения (только админы)")
        else:
            selected_user_for_farms = st.selectbox(
                "Выберите пользователя",
                options=[u.username for u in all_users],
                key="user_farms_select"
            )

            if selected_user_for_farms:
                user_obj = next((u for u in all_users if u.username == selected_user_for_farms), None)

                if user_obj:
                    st.markdown(f"#### Пользователь: **{user_obj.full_name or user_obj.username}** ({user_obj.email})")

                    # Показать текущие назначения
                    current_assignments = db.query(
                        UserFarm, Farm
                    ).join(
                        Farm, UserFarm.farm_id == Farm.id
                    ).filter(
                        UserFarm.user_id == user_obj.id
                    ).all()

                    st.markdown("##### 📋 Текущие назначения:")

                    if current_assignments:
                        for uf, farm in current_assignments:
                            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

                            with col1:
                                primary_star = "⭐ " if uf.is_primary else ""
                                st.write(f"{primary_star}**{farm.name}** ({farm.bin})")

                            with col2:
                                role_display = {
                                    "admin": "👑 Администратор",
                                    "manager": "👔 Менеджер",
                                    "viewer": "👁️ Наблюдатель"
                                }.get(uf.role, uf.role)
                                st.write(role_display)

                            with col3:
                                if uf.is_primary:
                                    st.success("Основное")
                                else:
                                    if st.button("Сделать основным", key=f"primary_{uf.id}"):
                                        # Убрать is_primary у всех других
                                        db.query(UserFarm).filter(
                                            UserFarm.user_id == user_obj.id
                                        ).update({"is_primary": False})

                                        # Установить для текущего
                                        uf.is_primary = True
                                        db.commit()

                                        st.success("✅ Установлено как основное")
                                        st.rerun()

                            with col4:
                                if st.button("🗑️", key=f"delete_uf_{uf.id}"):
                                    db.delete(uf)
                                    db.commit()
                                    st.success("✅ Удалено")
                                    st.rerun()

                        st.markdown("---")
                    else:
                        st.warning("⚠️ Пользователь не назначен ни на одно хозяйство")
                        st.info("💡 Используйте форму ниже для добавления")

                    # Форма добавления нового назначения
                    st.markdown("##### ➕ Добавить доступ к хозяйству")

                    with st.form("add_user_farm_form"):
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            all_farms = db.query(Farm).all()

                            # Исключить уже назначенные хозяйства
                            assigned_farm_ids = [uf.farm_id for uf, _ in current_assignments]
                            available_farms = [f for f in all_farms if f.id not in assigned_farm_ids]

                            if not available_farms:
                                st.warning("Все хозяйства уже назначены")
                                farm_to_add = None
                            else:
                                farm_options = [f"{f.id} - {f.name} ({f.bin})" for f in available_farms]
                                selected_farm_option = st.selectbox("Хозяйство", farm_options)

                                if selected_farm_option:
                                    farm_id_to_add = int(selected_farm_option.split(" - ")[0])
                                    farm_to_add = next((f for f in available_farms if f.id == farm_id_to_add), None)
                                else:
                                    farm_to_add = None

                        with col2:
                            role_to_add = st.selectbox(
                                "Роль в хозяйстве",
                                options=["viewer", "manager", "admin"],
                                format_func=lambda x: {
                                    "admin": "👑 Администратор (полный доступ)",
                                    "manager": "👔 Менеджер (редактирование)",
                                    "viewer": "👁️ Наблюдатель (только просмотр)"
                                }[x]
                            )

                        with col3:
                            set_as_primary = st.checkbox(
                                "Сделать основным",
                                value=len(current_assignments) == 0,  # Первое назначение всегда основное
                                help="Основное хозяйство показывается по умолчанию"
                            )

                        add_farm_submitted = st.form_submit_button(
                            "➕ Добавить доступ",
                            type="primary",
                            use_container_width=True
                        )

                        if add_farm_submitted and farm_to_add:
                            try:
                                # Если устанавливаем как основное - убираем is_primary у других
                                if set_as_primary:
                                    db.query(UserFarm).filter(
                                        UserFarm.user_id == user_obj.id
                                    ).update({"is_primary": False})

                                # Создаем новое назначение
                                new_uf = UserFarm(
                                    user_id=user_obj.id,
                                    farm_id=farm_to_add.id,
                                    role=role_to_add,
                                    is_primary=set_as_primary
                                )

                                db.add(new_uf)
                                db.commit()

                                log_action(
                                    db, current_user['id'], "create", "user_farm", new_uf.id,
                                    f"Assigned {user_obj.username} to {farm_to_add.name} as {role_to_add}"
                                )

                                st.success(f"✅ Пользователь {user_obj.username} добавлен в {farm_to_add.name}")
                                st.rerun()

                            except Exception as e:
                                db.rollback()
                                st.error(f"❌ Ошибка: {str(e)}")

    # ============================================================================
    # ВКЛАДКА: ЖУРНАЛ ДЕЙСТВИЙ
    # ============================================================================
    with tabs[3]:
        st.markdown("### 📜 Журнал действий пользователей")

        logs = db.query(AuditLog, User).join(User).order_by(AuditLog.created_at.desc()).limit(100).all()

        if logs:
            data = []
            for log, user in logs:
                data.append({
                    "Дата": log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "Пользователь": user.username,
                    "Действие": log.action,
                    "Тип": log.entity_type or "-",
                    "ID": log.entity_id or "-",
                    "Детали": log.details or "-"
                })

            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Экспорт
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "📥 Скачать журнал (CSV)",
                csv,
                "audit_log.csv",
                "text/csv"
            )
        else:
            st.info("📭 Журнал пуст")

    # ============================================================================
    # ВКЛАДКА: НАСТРОЙКИ
    # ============================================================================
    with tabs[4]:
        st.markdown("### ⚙️ Системные настройки")

        st.info("🚧 Раздел в разработке")

        st.markdown("**Планируется:**")
        st.markdown("- Резервное копирование базы данных")
        st.markdown("- Экспорт всех данных")
        st.markdown("- Настройки безопасности")
        st.markdown("- Системные логи")

finally:
    db.close()

# Sidebar
with st.sidebar:
    st.markdown(f"### 👤 {get_user_display_name()}")
    st.markdown(f"**Роль:** {current_user['role']}")

    st.markdown("---")
    st.markdown("### 📊 Быстрая статистика")
    st.metric("Пользователей", total_users)
    st.metric("Хозяйств", total_farms)
