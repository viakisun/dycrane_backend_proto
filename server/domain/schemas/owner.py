from pydantic import BaseModel, ConfigDict


class OwnerStatsOut(BaseModel):
    """Schema for an owner organization with crane fleet statistics."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    total_cranes: int
    available_cranes: int
