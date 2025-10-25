"""
Fields API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.crud import field as crud_field, farm as crud_farm
from app.schemas.field import FieldCreate, FieldUpdate, FieldRead, FieldWithStats
from app.models.user import User, UserFarm


router = APIRouter()


def check_farm_access(db: Session, user: User, farm_id: int, required_role: str = "viewer") -> bool:
    """Check if user has access to farm with required role"""
    if user.role == "admin":
        return True

    user_farm = db.query(UserFarm).filter(
        UserFarm.user_id == user.id,
        UserFarm.farm_id == farm_id
    ).first()

    if not user_farm:
        return False

    role_hierarchy = {"viewer": 0, "manager": 1, "admin": 2}
    user_role_level = role_hierarchy.get(user_farm.role, -1)
    required_role_level = role_hierarchy.get(required_role, 99)

    return user_role_level >= required_role_level


@router.get("/", response_model=List[FieldRead])
def get_fields(
    skip: int = 0,
    limit: int = 100,
    farm_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of fields

    - **farm_id**: optional filter by farm
    - If no farm_id provided, returns all accessible fields
    """
    if farm_id:
        # Check access to this farm
        if not check_farm_access(db, current_user, farm_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this farm"
            )

        fields = crud_field.get_farm_fields(db, farm_id=farm_id)
    else:
        # Get all fields from user's farms
        if current_user.role == "admin":
            fields = crud_field.get_fields(db, skip=skip, limit=limit)
        else:
            user_farms = crud_farm.get_user_farms(db, user_id=current_user.id)
            farm_ids = [f.id for f in user_farms]
            # Get fields from all user's farms
            fields = []
            for fid in farm_ids:
                fields.extend(crud_field.get_farm_fields(db, farm_id=fid))

    return fields


@router.get("/{field_id}", response_model=FieldWithStats)
def get_field(
    field_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get field by ID with statistics
    """
    field = crud_field.get_field(db, field_id=field_id)

    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )

    # Check access
    if not check_farm_access(db, current_user, field.farm_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Get stats
    stats = crud_field.get_field_stats(db, field_id=field_id)

    field_dict = {
        **field.__dict__,
        **stats
    }

    return field_dict


@router.post("/", response_model=FieldRead, status_code=status.HTTP_201_CREATED)
def create_field(
    field: FieldCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new field

    - **farm_id**: ID of the farm
    - **area_ha**: Area in hectares (required, > 0)
    - Other fields are optional

    field_code is auto-generated
    """
    # Check if farm exists
    farm = crud_farm.get_farm(db, farm_id=field.farm_id)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )

    # Check access (need manager or admin role)
    if not check_farm_access(db, current_user, field.farm_id, required_role="manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Manager or admin role required."
        )

    # Create field
    new_field = crud_field.create_field(db=db, field=field)

    return new_field


@router.put("/{field_id}", response_model=FieldRead)
def update_field(
    field_id: int,
    field_update: FieldUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update field

    Requires manager or admin role in the farm
    """
    field = crud_field.get_field(db, field_id=field_id)

    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )

    # Check permissions
    if not check_farm_access(db, current_user, field.farm_id, required_role="manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Update field
    updated_field = crud_field.update_field(db, field_id=field_id, field_update=field_update)

    return updated_field


@router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_field(
    field_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete field

    Cannot delete if field has operations
    Requires admin role in the farm or global admin
    """
    field = crud_field.get_field(db, field_id=field_id)

    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )

    # Check permissions (need admin role)
    if not check_farm_access(db, current_user, field.farm_id, required_role="admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin role required."
        )

    # Delete field
    success = crud_field.delete_field(db, field_id=field_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete field with existing operations"
        )

    return None
