"""
CRUD operations for Farm model
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.farm import Farm
from app.models.field import Field
from app.models.operation import Operation
from app.schemas.farm import FarmCreate, FarmUpdate


def get_farm(db: Session, farm_id: int) -> Optional[Farm]:
    """Get farm by ID"""
    return db.query(Farm).filter(Farm.id == farm_id).first()


def get_farm_by_bin(db: Session, bin: str) -> Optional[Farm]:
    """Get farm by BIN"""
    return db.query(Farm).filter(Farm.bin == bin).first()


def get_farms(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Farm]:
    """Get list of farms with pagination"""
    return db.query(Farm).offset(skip).limit(limit).all()


def get_user_farms(db: Session, user_id: int) -> List[Farm]:
    """Get all farms accessible to a user"""
    from app.models.user import UserFarm

    # Admin sees all farms
    from app.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.role == "admin":
        return db.query(Farm).all()

    # Regular users see only their farms
    farm_ids = db.query(UserFarm.farm_id).filter(
        UserFarm.user_id == user_id
    ).subquery()

    return db.query(Farm).filter(Farm.id.in_(farm_ids)).all()


def create_farm(db: Session, farm: FarmCreate, creator_id: Optional[int] = None) -> Farm:
    """Create new farm"""
    db_farm = Farm(**farm.model_dump())

    db.add(db_farm)
    db.commit()
    db.refresh(db_farm)

    # If creator_id provided, add creator as admin of the farm
    if creator_id:
        from app.crud.user import add_user_to_farm
        add_user_to_farm(
            db=db,
            user_id=creator_id,
            farm_id=db_farm.id,
            role="admin",
            is_primary=True
        )

    return db_farm


def update_farm(db: Session, farm_id: int, farm_update: FarmUpdate) -> Optional[Farm]:
    """Update farm"""
    db_farm = get_farm(db, farm_id)
    if not db_farm:
        return None

    update_data = farm_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_farm, field, value)

    db.commit()
    db.refresh(db_farm)
    return db_farm


def delete_farm(db: Session, farm_id: int) -> bool:
    """Delete farm"""
    db_farm = get_farm(db, farm_id)
    if not db_farm:
        return False

    db.delete(db_farm)
    db.commit()
    return True


def get_farm_stats(db: Session, farm_id: int) -> dict:
    """Get farm statistics"""
    fields_count = db.query(func.count(Field.id)).filter(
        Field.farm_id == farm_id
    ).scalar() or 0

    total_field_area = db.query(func.sum(Field.area_ha)).filter(
        Field.farm_id == farm_id
    ).scalar() or 0.0

    operations_count = db.query(func.count(Operation.id)).filter(
        Operation.farm_id == farm_id
    ).scalar() or 0

    return {
        "fields_count": fields_count,
        "total_field_area": float(total_field_area),
        "operations_count": operations_count
    }
