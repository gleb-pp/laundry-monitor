from fastapi import APIRouter, Depends
from schemas import (
    Success,
    MachineSchema,
    MachineReportStatus,
    ReportSchema,
)
from get_db import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from service import MachineService

router = APIRouter()

@router.post("/report")
async def send_report(
    db: Annotated[Session, Depends(get_db)],
    machine_id: int,
    status: MachineReportStatus,
    time_remaining: int | None = None,
) -> Success:
    """Send a report about the status of a laundry machine."""
    service = MachineService(db)
    service.send_report(machine_id, status, time_remaining)
    db.commit()
    return Success()

@router.get("/machines")
async def get_machines(
    db: Annotated[Session, Depends(get_db)]
) -> list[MachineSchema]:
    """Get a list of all laundry machines."""
    service = MachineService(db)
    return service.get_machines_with_reports()

@router.get("/machines/{id}/history")
async def get_machine_history(
    db: Annotated[Session, Depends(get_db)],
    id: int,
    limit: int = 10,
) -> list[ReportSchema]:
    """Get the history of a specific laundry machine."""
    service = MachineService(db)
    reports = service.get_machine_reports(id, limit)
    return [ReportSchema.model_validate(report, from_attributes=True) for report in reports]
