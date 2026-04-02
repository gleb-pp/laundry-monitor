from src.models import Report, Machine
from src.schemas import (
    MachineReportStatus,
    MachineResponseStatus,
    MachineSchema
)
from datetime import datetime, timedelta, UTC


class MachineService:
    """Service class for handling laundry machine operations."""

    def __init__(self, db):
        self.db = db

    def get_machine_reports(
        self,
        machine_id: int,
        limit: int = 10
    ) -> list[Report]:
        """Get the history of a specific laundry machine."""
        return (
            self.db.query(Report)
            .filter(Report.machine_id == machine_id)
            .order_by(Report.timestamp.desc())
            .limit(limit)
            .all()
        )

    def send_report(
        self,
        machine_id: int,
        status: MachineReportStatus,
        time_remaining: int | None = None
    ) -> Report:
        """Send a report about the status of a laundry machine."""
        report = Report(
            machine_id=machine_id,
            status=status,
            time_remaining=time_remaining
        )
        self.db.add(report)
        self.db.flush()
        return report

    def _get_machine_status(self, machine: Machine) -> MachineResponseStatus:
        """Determine the current status of a machine."""

        machine_reports = self.get_machine_reports(machine.id, limit=1)
        if not machine_reports:
            return MachineResponseStatus.FREE
        latest_report = machine_reports[0]

        if latest_report.status == MachineReportStatus.UNAVAILABLE:
            return MachineResponseStatus.UNAVAILABLE
        if latest_report.status == MachineReportStatus.FREE:
            return MachineResponseStatus.FREE

        if latest_report.time_remaining is None:
            deadline = (
                latest_report.timestamp.replace(tzinfo=UTC) +
                timedelta(hours=4)
            )
            if (datetime.now(tz=UTC) < deadline):
                return MachineResponseStatus.BUSY
            else:
                return MachineResponseStatus.PROBABLY_FREE
        elif (datetime.now(tz=UTC) <
              latest_report.timestamp.replace(tzinfo=UTC) +
              timedelta(minutes=latest_report.time_remaining)):
            return MachineResponseStatus.BUSY
        else:
            return MachineResponseStatus.FREE

    def get_machines_with_reports(self) -> list[MachineSchema]:
        """Get a list of all laundry machines with their latest report."""
        machines = self.db.query(Machine).all()
        machines_with_reports = []
        for mach in machines:
            status = self._get_machine_status(mach)
            machines_with_reports.append(MachineSchema(
                id=mach.id,
                dormitory=mach.dormitory,
                name=mach.name,
                type=mach.type,
                status=status
            ))
        return machines_with_reports
