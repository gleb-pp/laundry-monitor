from pydantic import BaseModel
from datetime import datetime
from schemas.machines import MachineReportStatus


class ReportSchema(BaseModel):
    id: int
    machine_id: int
    status: MachineReportStatus
    timestamp: datetime
    time_remaining: int | None = None
