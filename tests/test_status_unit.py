from datetime import UTC, datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session

from src.models import Machine, Report
from src.schemas import MachineReportStatus, MachineResponseStatus
from src.service.machine import MachineService

NOW = datetime.now(UTC)


class FixedDateTime:
    """Mock datetime to return fixed NOW."""

    @classmethod
    def now(cls: type, tz: timezone | None = None) -> datetime:
        """Return the fixed NOW, optionally converted to a timezone."""
        if tz is not None:
            return NOW.astimezone(tz)
        return NOW


@pytest.fixture
def machine(db_session: Session) -> Machine:
    """Create a machine for testing."""
    machine = Machine(dormitory=1, name="Washer 1")
    db_session.add(machine)
    db_session.commit()
    db_session.refresh(machine)
    return machine


def test_get_machine_status_requests_only_one_report(
    db_session: Session,
    machine: Machine,
) -> None:
    """Check that _get_machine_status only considers the latest report."""
    service = MachineService(db_session)
    # Добавляем два отчёта, но метод должен запросить только один
    db_session.add(Report(
        machine_id=machine.id,
        status=MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(minutes=5),
        time_remaining=30,
    ))
    db_session.add(Report(
        machine_id=machine.id,
        status=MachineReportStatus.FREE,
        timestamp=NOW - timedelta(hours=1),
        time_remaining=None,
    ))
    db_session.commit()
    status = service._get_machine_status(machine)
    assert status == MachineResponseStatus.BUSY


def test_no_reports_means_free(db_session: Session, machine: Machine) -> None:
    """Check that if there are no reports for a machine, its status is FREE."""
    service = MachineService(db_session)
    assert service._get_machine_status(machine) == MachineResponseStatus.FREE


def test_unavailable_report_means_unavailable(
    db_session: Session,
    machine: Machine,
) -> None:
    """Check that an UNAVAILABLE report makes a machine UNAVAILABLE."""
    service = MachineService(db_session)
    report = Report(
        machine_id=machine.id,
        status=MachineReportStatus.UNAVAILABLE,
        timestamp=NOW - timedelta(minutes=5),
        time_remaining=None,
    )
    db_session.add(report)
    db_session.commit()
    assert (
        service._get_machine_status(machine)
        == MachineResponseStatus.UNAVAILABLE
    )


def test_free_report_means_free(db_session: Session, machine: Machine) -> None:
    """Check that a FREE report makes a machine FREE."""
    service = MachineService(db_session)
    report = Report(
        machine_id=machine.id,
        status=MachineReportStatus.FREE,
        timestamp=NOW - timedelta(minutes=5),
        time_remaining=None,
    )
    db_session.add(report)
    db_session.commit()
    assert service._get_machine_status(machine) == MachineResponseStatus.FREE


@patch("service.machine.datetime", FixedDateTime)
def test_busy_without_time_remaining_recent_is_busy(
    db_session: Session,
    machine: Machine,
) -> None:
    """Check that a recent BUSY report without time_remaining is BUSY."""
    service = MachineService(db_session)
    report = Report(
        machine_id=machine.id,
        status=MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(hours=1),
        time_remaining=None,
    )
    db_session.add(report)
    db_session.commit()
    assert service._get_machine_status(machine) == MachineResponseStatus.BUSY


@patch("service.machine.datetime", FixedDateTime)
def test_busy_without_time_remaining_at_4_hours_is_probably_free(
    db_session: Session,
    machine: Machine,
) -> None:
    """Check that a BUSY report without time after 4 hours is PROBABLY_FREE."""
    service = MachineService(db_session)
    report = Report(
        machine_id=machine.id,
        status=MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(hours=4),
        time_remaining=None,
    )
    db_session.add(report)
    db_session.commit()
    assert (
        service._get_machine_status(machine) ==
        MachineResponseStatus.PROBABLY_FREE
    )


@patch("service.machine.datetime", FixedDateTime)
def test_busy_without_time_remaining_after_4_hours_is_probably_free(
    db_session: Session,
    machine: Machine,
) -> None:
    """Check that a BUSY report without time after 4 hours is PROBABLY_FREE."""
    service = MachineService(db_session)
    report = Report(
        machine_id=machine.id,
        status=MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(hours=5),
        time_remaining=None,
    )
    db_session.add(report)
    db_session.commit()
    assert (
        service._get_machine_status(machine) ==
        MachineResponseStatus.PROBABLY_FREE
    )


@patch("service.machine.datetime", FixedDateTime)
def test_busy_with_remaining_before_expiry_is_busy(
    db_session: Session,
    machine: Machine,
) -> None:
    """Check that a BUSY report with time that has not yet expired is BUSY."""
    service = MachineService(db_session)
    report = Report(
        machine_id=machine.id,
        status=MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(minutes=10),
        time_remaining=30,
    )
    db_session.add(report)
    db_session.commit()
    assert service._get_machine_status(machine) == MachineResponseStatus.BUSY


@patch("service.machine.datetime", FixedDateTime)
def test_busy_with_remaining_at_expiry_is_free(
    db_session: Session,
    machine: Machine,
) -> None:
    """Check that a BUSY report with time that has expired is FREE."""
    service = MachineService(db_session)
    report = Report(
        machine_id=machine.id,
        status=MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(minutes=30),
        time_remaining=30,
    )
    db_session.add(report)
    db_session.commit()
    assert service._get_machine_status(machine) == MachineResponseStatus.FREE


@patch("service.machine.datetime", FixedDateTime)
def test_busy_with_remaining_after_expiry_is_free(
    db_session: Session,
    machine: Machine,
) -> None:
    """Check that a BUSY report with time that has expired is FREE."""
    service = MachineService(db_session)
    report = Report(
        machine_id=machine.id,
        status=MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(minutes=45),
        time_remaining=30,
    )
    db_session.add(report)
    db_session.commit()
    assert service._get_machine_status(machine) == MachineResponseStatus.FREE
