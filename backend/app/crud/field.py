"""
CRUD operations for Field model
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.field import Field
from app.models.operation import Operation
from app.schemas.field import FieldCreate, FieldUpdate


def get_field(db: Session, field_id: int) -> Optional[Field]:
    """Get field by ID"""
    return db.query(Field).filter(Field.id == field_id).first()


def get_field_by_code(db: Session, field_code: str) -> Optional[Field]:
    """Get field by field_code"""
    return db.query(Field).filter(Field.field_code == field_code).first()


def get_fields(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    farm_id: Optional[int] = None
) -> List[Field]:
    """Get list of fields with pagination"""
    query = db.query(Field)

    if farm_id is not None:
        query = query.filter(Field.farm_id == farm_id)

    return query.offset(skip).limit(limit).all()


def get_farm_fields(db: Session, farm_id: int) -> List[Field]:
    """Get all fields for a farm"""
    return db.query(Field).filter(Field.farm_id == farm_id).all()


def create_field(db: Session, field: FieldCreate) -> Field:
    """Create new field"""
    # Generate field_code
    field_code = generate_field_code(db, field.farm_id)

    db_field = Field(
        **field.model_dump(),
        field_code=field_code
    )

    db.add(db_field)
    db.commit()
    db.refresh(db_field)
    return db_field


def update_field(db: Session, field_id: int, field_update: FieldUpdate) -> Optional[Field]:
    """Update field"""
    db_field = get_field(db, field_id)
    if not db_field:
        return None

    update_data = field_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_field, field, value)

    db.commit()
    db.refresh(db_field)
    return db_field


def delete_field(db: Session, field_id: int) -> bool:
    """Delete field"""
    db_field = get_field(db, field_id)
    if not db_field:
        return False

    # Check if field has operations
    operations_count = db.query(func.count(Operation.id)).filter(
        Operation.field_id == field_id
    ).scalar()

    if operations_count and operations_count > 0:
        return False  # Cannot delete field with operations

    db.delete(db_field)
    db.commit()
    return True


def generate_field_code(db: Session, farm_id: int) -> str:
    """Generate unique field code for a farm"""
    # Get all existing field codes for this farm
    existing_codes = db.query(Field.field_code).filter(
        Field.field_code.like('field_%')
    ).all()

    # Extract numbers and find max
    max_number = 0
    for (code,) in existing_codes:
        try:
            number = int(code.split('_')[1])
            max_number = max(max_number, number)
        except (ValueError, IndexError):
            continue

    # Generate new code
    new_number = max_number + 1
    return f"field_{new_number:03d}"


def get_field_stats(db: Session, field_id: int) -> dict:
    """Get field statistics"""
    operations_count = db.query(func.count(Operation.id)).filter(
        Operation.field_id == field_id
    ).scalar() or 0

    last_operation = db.query(Operation).filter(
        Operation.field_id == field_id
    ).order_by(Operation.operation_date.desc()).first()

    return {
        "operations_count": operations_count,
        "last_operation_date": last_operation.operation_date if last_operation else None
    }
