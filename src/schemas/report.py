from datetime import datetime

from pydantic import BaseModel

from schemas.machines import MachineReportStatus


class ReportSchema(BaseModel):
    """Schema for representing a report about the machine status."""

    id: int
    machine_id: int
    status: MachineReportStatus
    timestamp: datetime
    time_remaining: int | None = None
