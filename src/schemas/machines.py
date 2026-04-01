from pydantic import BaseModel, ConfigDict
from enum import Enum


class MachineType(Enum):
    """Type of laundry machine."""
    WASHING = "washing"
    DRYING = "drying"
    
    def __str__(self):
        return self.value


class MachineResponseStatus(Enum):
    """Status of a machine as determined by the system based on user reports."""
    FREE = "free"
    PROBABLY_FREE = "probably_free"
    BUSY = "busy"
    UNAVAILABLE = "unavailable"

    def __str__(self):
        return self.value


class MachineReportStatus(Enum):
    """Status of a machine as reported by a user."""
    FREE = "free"
    BUSY = "busy"
    UNAVAILABLE = "unavailable"

    def __str__(self):
        return self.value

class MachineSchema(BaseModel):
    """Schema for representing a laundry machine with its current status."""
    id: int
    dormitory: int
    name: str
    type: MachineType
    status: MachineResponseStatus
    model_config = ConfigDict(from_attributes=True)
