import datetime as dt
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict
from .enums import CraneStatus


class CraneModelOut(BaseModel):
    """Schema for crane model specifications in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    model_name: str
    max_lifting_capacity_ton_m: Optional[int] = None
    max_working_height_m: Optional[float] = None
    max_working_radius_m: Optional[float] = None
    optional_specs: Optional[List[str]] = None


class CraneOut(BaseModel):
    """Schema for crane information in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_org_id: str
    serial_no: Optional[str] = None
    status: CraneStatus
    model: CraneModelOut
    created_at: dt.datetime
    updated_at: dt.datetime


class CraneModelBase(BaseModel):
    model_name: str
    max_lifting_capacity_ton_m: Optional[int] = None
    max_working_height_m: Optional[float] = None
    max_working_radius_m: Optional[float] = None
    iver_torque_phi_mm: Optional[str] = None
    boom_sections: Optional[int] = None
    tele_speed_m_sec: Optional[str] = None
    boom_angle_speed_deg_sec: Optional[str] = None
    lifting_load_distance_kg_m: Optional[Any] = None
    optional_specs: Optional[List[str]] = None


class CraneModelCreate(CraneModelBase):
    pass


class CraneModelUpdate(CraneModelBase):
    pass


class CraneBase(BaseModel):
    model_id: Optional[str] = None
    serial_no: Optional[str] = None
    status: Optional[CraneStatus] = CraneStatus.NORMAL
    owner_org_id: Optional[str] = None


class CraneCreate(CraneBase):
    model_id: str
    owner_org_id: str


class CraneUpdate(CraneBase):
    pass
