from datetime import datetime

from pydantic import BaseModel

from src.schemas.machines import MachineReportStatus


class ReportSchema(BaseModel):
    """Schema for representing a report about the status of a laundry machine."""

    id: int
    machine_id: int
    status: MachineReportStatus
    timestamp: datetime
    time_remaining: int | None = None
