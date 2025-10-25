"""
CRUD operations for User model
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.user import User, UserFarm
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[User]:
    """Get list of users with pagination"""
    query = db.query(User)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    return query.offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """Create new user"""
    hashed_password = get_password_hash(user.password)

    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role,
        is_active=True
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def update_password(db: Session, user_id: int, new_password: str) -> Optional[User]:
    """Update user password"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    db_user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user by username/email and password"""
    # Try username first
    user = get_user_by_username(db, username)

    # If not found, try email
    if not user:
        user = get_user_by_email(db, username)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def update_last_login(db: Session, user_id: int) -> None:
    """Update user's last login timestamp"""
    db_user = get_user(db, user_id)
    if db_user:
        db_user.last_login = datetime.utcnow()
        db.commit()


# UserFarm CRUD operations
def get_user_farms(db: Session, user_id: int) -> List[UserFarm]:
    """Get all farms for a user"""
    return db.query(UserFarm).filter(UserFarm.user_id == user_id).all()


def get_primary_farm(db: Session, user_id: int) -> Optional[UserFarm]:
    """Get user's primary farm"""
    return db.query(UserFarm).filter(
        UserFarm.user_id == user_id,
        UserFarm.is_primary == True
    ).first()


def add_user_to_farm(
    db: Session,
    user_id: int,
    farm_id: int,
    role: str = "viewer",
    is_primary: bool = False
) -> UserFarm:
    """Add user to farm with specific role"""
    # If setting as primary, unset other primary farms for this user
    if is_primary:
        db.query(UserFarm).filter(
            UserFarm.user_id == user_id,
            UserFarm.is_primary == True
        ).update({"is_primary": False})

    user_farm = UserFarm(
        user_id=user_id,
        farm_id=farm_id,
        role=role,
        is_primary=is_primary
    )

    db.add(user_farm)
    db.commit()
    db.refresh(user_farm)
    return user_farm


def remove_user_from_farm(db: Session, user_id: int, farm_id: int) -> bool:
    """Remove user from farm"""
    user_farm = db.query(UserFarm).filter(
        UserFarm.user_id == user_id,
        UserFarm.farm_id == farm_id
    ).first()

    if not user_farm:
        return False

    db.delete(user_farm)
    db.commit()
    return True


def update_user_farm_role(
    db: Session,
    user_id: int,
    farm_id: int,
    role: Optional[str] = None,
    is_primary: Optional[bool] = None
) -> Optional[UserFarm]:
    """Update user's role in a farm"""
    user_farm = db.query(UserFarm).filter(
        UserFarm.user_id == user_id,
        UserFarm.farm_id == farm_id
    ).first()

    if not user_farm:
        return None

    if role is not None:
        user_farm.role = role

    if is_primary is not None:
        if is_primary:
            # Unset other primary farms
            db.query(UserFarm).filter(
                UserFarm.user_id == user_id,
                UserFarm.is_primary == True
            ).update({"is_primary": False})
        user_farm.is_primary = is_primary

    db.commit()
    db.refresh(user_farm)
    return user_farm
