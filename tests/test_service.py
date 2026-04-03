from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from src.models.machines import Machine
from src.models.reports import Report
from src.schemas.machines import (
    MachineReportStatus,
    MachineResponseStatus,
    MachineSchema,
    MachineType,
)
from src.service.machine import MachineService


def _machine_status(service: MachineService, machine_id: int) -> MachineResponseStatus:
    machines = service.get_machines_with_reports()
    machine = next(m for m in machines if m.id == machine_id)
    return machine.status


def test_get_machine_reports_returns_desc_order(db_session: Session) -> None:
    """Check that get_machine_reports returns reports in descending order of timestamp."""
    service = MachineService(db_session)

    older = Report(
        machine_id=1,
        status=MachineReportStatus.FREE,
        timestamp=datetime.now(UTC) - timedelta(hours=2),
        time_remaining=None,
    )
    newer = Report(
        machine_id=1,
        status=MachineReportStatus.BUSY,
        timestamp=datetime.now(UTC) - timedelta(minutes=10),
        time_remaining=20,
    )

    db_session.add_all([older, newer])
    db_session.commit()

    reports = service.get_machine_reports(1, limit=2)

    assert len(reports) == 2
    assert reports[0].id == newer.id
    assert reports[1].id == older.id


def test_get_machines_with_no_reports_are_free(db_session: Session) -> None:
    """Check that machines with no reports are considered FREE."""
    service = MachineService(db_session)

    assert _machine_status(service, 1) == MachineResponseStatus.FREE


def test_unavailable_report_makes_machine_unavailable(db_session: Session) -> None:
    """Check that an UNAVAILABLE report makes a machine UNAVAILABLE."""
    service = MachineService(db_session)

    db_session.add(
        Report(
            machine_id=1,
            status=MachineReportStatus.UNAVAILABLE,
            timestamp=datetime.now(UTC),
            time_remaining=None,
        ),
    )
    db_session.commit()

    assert _machine_status(service, 1) == MachineResponseStatus.UNAVAILABLE


def test_free_report_makes_machine_free(db_session: Session) -> None:
    """Check that a FREE report makes a machine FREE."""
    service = MachineService(db_session)

    db_session.add(
        Report(
            machine_id=1,
            status=MachineReportStatus.FREE,
            timestamp=datetime.now(UTC),
            time_remaining=None,
        ),
    )
    db_session.commit()

    assert _machine_status(service, 1) == MachineResponseStatus.FREE


def test_busy_without_time_remaining_recent_is_busy(db_session: Session) -> None:
    """Check that a recent BUSY report without time_remaining makes a machine BUSY."""
    service = MachineService(db_session)

    db_session.add(
        Report(
            machine_id=1,
            status=MachineReportStatus.BUSY,
            timestamp=datetime.now(UTC) - timedelta(hours=1),
            time_remaining=None,
        ),
    )
    db_session.commit()

    assert _machine_status(service, 1) == MachineResponseStatus.BUSY


def test_busy_without_time_remaining_old_is_probably_free(db_session: Session) -> None:
    """Check that an old BUSY report without time_remaining makes a machine PROBABLY_FREE."""
    service = MachineService(db_session)

    db_session.add(
        Report(
            machine_id=1,
            status=MachineReportStatus.BUSY,
            timestamp=datetime.now(UTC) - timedelta(hours=5),
            time_remaining=None,
        ),
    )
    db_session.commit()

    assert _machine_status(service, 1) == MachineResponseStatus.PROBABLY_FREE


def test_busy_with_remaining_time_not_expired_is_busy(db_session: Session) -> None:
    """Check that a BUSY report with time_remaining that has not expired makes a machine BUSY."""
    service = MachineService(db_session)

    db_session.add(
        Report(
            machine_id=1,
            status=MachineReportStatus.BUSY,
            timestamp=datetime.now(UTC) - timedelta(minutes=10),
            time_remaining=30,
        ),
    )
    db_session.commit()

    assert _machine_status(service, 1) == MachineResponseStatus.BUSY


def test_busy_with_remaining_time_expired_is_free(db_session: Session) -> None:
    """Check that a BUSY report with time_remaining that has expired makes a machine FREE."""
    machine = Machine(
        dormitory=1,
        name="Machine 1",
    )
    db_session.add(machine)
    db_session.commit()
    db_session.refresh(machine)

    service = MachineService(db_session)

    db_session.add(
        Report(
            machine_id=machine.id,
            status=MachineReportStatus.BUSY,
            timestamp=datetime.now(UTC) - timedelta(minutes=40),
            time_remaining=30,
        ),
    )
    db_session.commit()

    assert _machine_status(service, machine.id) == MachineResponseStatus.FREE

def test_get_machine_reports_filters_orders_and_limits(db_session: Session) -> None:
    """Check that get_machine_reports filters, orders, and applies limit."""
    machine1 = Machine(dormitory=1, name="M1")
    machine2 = Machine(dormitory=1, name="M2")
    db_session.add_all([machine1, machine2])
    db_session.commit()
    db_session.refresh(machine1)
    db_session.refresh(machine2)

    old = datetime.now(UTC) - timedelta(hours=2)
    new = datetime.now(UTC) - timedelta(hours=1)

    db_session.add_all([
        Report(machine_id=machine1.id, status=MachineReportStatus.FREE, timestamp=old),
        Report(machine_id=machine1.id, status=MachineReportStatus.BUSY, timestamp=new),
        Report(machine_id=machine2.id, status=MachineReportStatus.UNAVAILABLE, timestamp=new),
    ])
    db_session.commit()

    service = MachineService(db_session)
    reports = service.get_machine_reports(machine1.id, limit=2)

    assert len(reports) == 2
    assert all(r.machine_id == machine1.id for r in reports)
    assert reports[0].timestamp >= reports[1].timestamp
    assert reports[0].status == MachineReportStatus.BUSY
    assert reports[1].status == MachineReportStatus.FREE

def test_send_report_creates_and_returns_report(db_session: Session) -> None:
    """Check that send_report creates a report in the database and returns it."""
    machine = Machine(dormitory=1, name="M1")
    db_session.add(machine)
    db_session.commit()
    db_session.refresh(machine)

    service = MachineService(db_session)
    report = service.send_report(
        machine_id=machine.id,
        status=MachineReportStatus.BUSY,
        time_remaining=25,
    )
    db_session.commit()

    assert report.id is not None
    assert report.machine_id == machine.id
    assert report.status == MachineReportStatus.BUSY
    assert report.time_remaining == 25

    saved = db_session.query(Report).filter(Report.id == report.id).one()
    assert saved.machine_id == machine.id
    assert saved.status == MachineReportStatus.BUSY
    assert saved.time_remaining == 25

def test_send_report_allows_none_time_remaining(db_session: Session) -> None:
    """Check that send_report allows time_remaining to be None."""
    machine = Machine(dormitory=1, name="M1")
    db_session.add(machine)
    db_session.commit()
    db_session.refresh(machine)

    service = MachineService(db_session)
    report = service.send_report(
        machine_id=machine.id,
        status=MachineReportStatus.UNAVAILABLE,
        time_remaining=None,
    )
    db_session.commit()

    assert report.time_remaining is None
    assert report.status == MachineReportStatus.UNAVAILABLE

def test_machine_status_uses_latest_report(db_session: Session) -> None:
    """Check that the machine status is determined by the latest report."""
    machine = Machine(dormitory=1, name="M1")
    db_session.add(machine)
    db_session.commit()
    db_session.refresh(machine)

    db_session.add_all([
        Report(
            machine_id=machine.id,
            status=MachineReportStatus.UNAVAILABLE,
            timestamp=datetime.now(UTC) - timedelta(hours=2),
        ),
        Report(
            machine_id=machine.id,
            status=MachineReportStatus.FREE,
            timestamp=datetime.now(UTC) - timedelta(minutes=5),
        ),
    ])
    db_session.commit()

    service = MachineService(db_session)
    assert service._get_machine_status(machine) == MachineResponseStatus.FREE

def test_get_machine_reports_uses_default_limit_10(db_session: Session) -> None:
    """Check that get_machine_reports returns at most 10 reports by default."""
    machine = Machine(dormitory=1, name="M1")
    db_session.add(machine)
    db_session.commit()
    db_session.refresh(machine)

    base_time = datetime.now(UTC)

    for i in range(12):
        db_session.add(
            Report(
                machine_id=machine.id,
                status=MachineReportStatus.FREE,
                timestamp=base_time - timedelta(minutes=i),
            ),
        )
    db_session.commit()

    service = MachineService(db_session)
    reports = service.get_machine_reports(machine.id)

    assert len(reports) == 10

def test_machine_service_stores_db(db_session: Session) -> None:
    """Check that the MachineService stores the provided database session."""
    service = MachineService(db_session)
    assert service.db is db_session

def test_get_machines_with_reports_returns_complete_schema(db_session: Session) -> None:
    """Check that get_machines_with_reports returns machines with complete schema including status."""
    service = MachineService(db_session)

    machines = service.get_machines_with_reports()

    assert len(machines) == 4

    washer_1 = next(m for m in machines if m.id == 1)
    assert isinstance(washer_1, MachineSchema)
    assert washer_1.dormitory == 1
    assert washer_1.name == "Washer 1"
    assert washer_1.type == MachineType.WASHING
    assert washer_1.status == MachineResponseStatus.FREE


def test_get_machines_with_reports_applies_status_per_machine(db_session: Session) -> None:
    """Check that get_machines_with_reports applies the correct status for each machine based on its latest report."""
    service = MachineService(db_session)

    db_session.add_all([
        Report(
            machine_id=1,
            status=MachineReportStatus.BUSY,
            timestamp=datetime.now(UTC) - timedelta(minutes=10),
            time_remaining=30,
        ),
        Report(
            machine_id=2,
            status=MachineReportStatus.UNAVAILABLE,
            timestamp=datetime.now(UTC),
            time_remaining=None,
        ),
    ])
    db_session.commit()

    machines = {m.id: m for m in service.get_machines_with_reports()}

    assert machines[1].status == MachineResponseStatus.BUSY
    assert machines[2].status == MachineResponseStatus.UNAVAILABLE
    assert machines[3].status == MachineResponseStatus.FREE
    assert machines[4].status == MachineResponseStatus.FREE
