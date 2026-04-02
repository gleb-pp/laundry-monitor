from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from src.models.reports import Report
from src.schemas.machines import MachineReportStatus, MachineResponseStatus
from src.service.machine import MachineService


def _machine_status(service: MachineService, machine_id: int) -> MachineResponseStatus:
    """Get the current status of a machine."""
    machines = service.get_machines_with_reports()
    machine = next(m for m in machines if m.id == machine_id)
    return machine.status


def test_get_machine_reports_returns_desc_order(db_session: Session) -> None:
    """Test that the machine reports are returned in descending order."""
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
    """Test that machines with no reports are considered free."""
    service = MachineService(db_session)

    assert _machine_status(service, 1) == MachineResponseStatus.FREE


def test_unavailable_report_makes_machine_unavailable(db_session: Session) -> None:
    """Test that an unavailable report makes a machine unavailable."""
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
    """Test that a free report makes a machine free."""
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
    """Test that a busy report without time remaining that is recent makes a machine busy."""
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
    """Test that a busy report without time remaining that is old makes a machine probably free."""
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
    """Test that a busy report with time remaining that is not expired makes a machine busy."""
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
    """Test that a busy report with time remaining that is expired makes a machine free."""
    service = MachineService(db_session)

    db_session.add(
        Report(
            machine_id=1,
            status=MachineReportStatus.BUSY,
            timestamp=datetime.now(UTC) - timedelta(minutes=40),
            time_remaining=30,
        ),
    )
    db_session.commit()

    assert _machine_status(service, 1) == MachineResponseStatus.FREE
