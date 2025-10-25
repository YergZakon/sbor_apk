"""
Farms API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_admin
from app.crud import farm as crud_farm
from app.schemas.farm import FarmCreate, FarmUpdate, FarmRead, FarmWithStats
from app.models.user import User


router = APIRouter()


@router.get("/", response_model=List[FarmRead])
def get_farms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of farms

    - Admins see all farms
    - Regular users see only their farms
    """
    if current_user.role == "admin":
        farms = crud_farm.get_farms(db, skip=skip, limit=limit)
    else:
        farms = crud_farm.get_user_farms(db, user_id=current_user.id)

    return farms


@router.get("/{farm_id}", response_model=FarmWithStats)
def get_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get farm by ID with statistics

    Returns farm info plus:
    - fields_count
    - total_field_area
    - operations_count
    """
    farm = crud_farm.get_farm(db, farm_id=farm_id)

    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )

    # Check access (admin or user has access to this farm)
    if current_user.role != "admin":
        user_farms = crud_farm.get_user_farms(db, user_id=current_user.id)
        if farm not in user_farms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

    # Get stats
    stats = crud_farm.get_farm_stats(db, farm_id=farm_id)

    # Combine farm data with stats
    farm_dict = {
        **farm.__dict__,
        **stats
    }

    return farm_dict


@router.post("/", response_model=FarmRead, status_code=status.HTTP_201_CREATED)
def create_farm(
    farm: FarmCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new farm

    - **bin**: БИН хозяйства (12 digits, unique)
    - **name**: Name of the farm
    - Other fields are optional

    The creator is automatically added as admin of the farm
    """
    # Check if BIN already exists
    existing_farm = crud_farm.get_farm_by_bin(db, bin=farm.bin)
    if existing_farm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Farm with this BIN already exists"
        )

    # Create farm
    new_farm = crud_farm.create_farm(db=db, farm=farm, creator_id=current_user.id)

    return new_farm


@router.put("/{farm_id}", response_model=FarmRead)
def update_farm(
    farm_id: int,
    farm_update: FarmUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update farm

    Only admins or farm admins can update
    """
    farm = crud_farm.get_farm(db, farm_id=farm_id)

    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )

    # Check permissions
    if current_user.role != "admin":
        # Check if user is admin of this farm
        from app.models.user import UserFarm
        user_farm = db.query(UserFarm).filter(
            UserFarm.user_id == current_user.id,
            UserFarm.farm_id == farm_id,
            UserFarm.role == "admin"
        ).first()

        if not user_farm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

    # Update farm
    updated_farm = crud_farm.update_farm(db, farm_id=farm_id, farm_update=farm_update)

    return updated_farm


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete farm

    Only admins can delete farms
    """
    success = crud_farm.delete_farm(db, farm_id=farm_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )

    return None
