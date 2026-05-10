"""
Mirofish AI - Farms API
Manajemen lokasi budidaya
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime

from app.models.database import Farm, Pond, get_db, generate_uuid

router = APIRouter()


# Pydantic Models
class FarmBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    location: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    description: Optional[str] = None


class FarmCreate(FarmBase):
    pass


class FarmUpdate(FarmBase):
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class FarmResponse(FarmBase):
    id: str
    created_at: datetime
    updated_at: datetime
    pond_count: int = 0
    
    class Config:
        from_attributes = True


class FarmDetailResponse(FarmResponse):
    ponds: List[dict] = []


# API Endpoints
@router.get("", response_model=List[FarmResponse])
def list_farms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all farms."""
    farms = db.query(Farm).offset(skip).limit(limit).all()
    
    result = []
    for farm in farms:
        pond_count = db.query(Pond).filter(Pond.farm_id == farm.id).count()
        farm_dict = {
            "id": farm.id,
            "name": farm.name,
            "location": farm.location,
            "latitude": farm.latitude,
            "longitude": farm.longitude,
            "description": farm.description,
            "created_at": farm.created_at,
            "updated_at": farm.updated_at,
            "pond_count": pond_count
        }
        result.append(farm_dict)
    
    return result


@router.post("", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
def create_farm(farm: FarmCreate, db: Session = Depends(get_db)):
    """Create a new farm."""
    db_farm = Farm(
        id=generate_uuid(),
        name=farm.name,
        location=farm.location,
        latitude=farm.latitude,
        longitude=farm.longitude,
        description=farm.description
    )
    db.add(db_farm)
    db.commit()
    db.refresh(db_farm)
    
    return {
        "id": db_farm.id,
        "name": db_farm.name,
        "location": db_farm.location,
        "latitude": db_farm.latitude,
        "longitude": db_farm.longitude,
        "description": db_farm.description,
        "created_at": db_farm.created_at,
        "updated_at": db_farm.updated_at,
        "pond_count": 0
    }


@router.get("/{farm_id}", response_model=FarmDetailResponse)
def get_farm(farm_id: str, db: Session = Depends(get_db)):
    """Get farm details."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    ponds = db.query(Pond).filter(Pond.farm_id == farm_id).all()
    pond_list = [
        {
            "id": p.id,
            "name": p.name,
            "fish_type": p.fish_type,
            "fish_count": p.fish_count,
            "status": p.status.value if p.status else None
        }
        for p in ponds
    ]
    
    return {
        "id": farm.id,
        "name": farm.name,
        "location": farm.location,
        "latitude": farm.latitude,
        "longitude": farm.longitude,
        "description": farm.description,
        "created_at": farm.created_at,
        "updated_at": farm.updated_at,
        "pond_count": len(ponds),
        "ponds": pond_list
    }


@router.put("/{farm_id}", response_model=FarmResponse)
def update_farm(farm_id: str, farm_update: FarmUpdate, db: Session = Depends(get_db)):
    """Update farm."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    update_data = farm_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(farm, field, value)
    
    db.commit()
    db.refresh(farm)
    
    pond_count = db.query(Pond).filter(Pond.farm_id == farm_id).count()
    
    return {
        "id": farm.id,
        "name": farm.name,
        "location": farm.location,
        "latitude": farm.latitude,
        "longitude": farm.longitude,
        "description": farm.description,
        "created_at": farm.created_at,
        "updated_at": farm.updated_at,
        "pond_count": pond_count
    }


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farm(farm_id: str, db: Session = Depends(get_db)):
    """Delete farm."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    # Delete associated ponds first
    db.query(Pond).filter(Pond.farm_id == farm_id).delete()
    db.delete(farm)
    db.commit()
    
    return None
