from datetime import UTC, datetime, timedelta, timezone
from unittest.mock import patch

from hypothesis import assume, given
from hypothesis import strategies as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.base import Base
from src.models.machines import Machine
from src.models.reports import Report
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


def create_service_and_data(report: Report) -> tuple[MachineService, Machine]:
    """Create a service and add a machine and report to the database."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = session_local()
    machine = Machine(dormitory=1, name="Washer 1")
    db.add(machine)
    db.commit()
    db.refresh(machine)
    report.machine_id = machine.id
    db.add(report)
    db.commit()
    service = MachineService(db)
    return service, machine


@given(days_ago=st.integers(min_value=0, max_value=365))
def test_unavailable_always_stays_unavailable(days_ago: int) -> None:
    """Check that an UNAVAILABLE report always makes a machine UNAVAILABLE."""
    report = Report(
        machine_id=1,
        status=MachineReportStatus.UNAVAILABLE,
        timestamp=NOW - timedelta(days=days_ago),
        time_remaining=None,
    )
    service, machine = create_service_and_data(report)
    with patch("service.machine.datetime", FixedDateTime):
        assert service._get_machine_status(machine) == MachineResponseStatus.UNAVAILABLE


@given(minutes_ago=st.integers(min_value=0, max_value=239))
def test_busy_without_remaining_under_4_hours_is_busy(minutes_ago: int) -> None:
    """Check that a BUSY report without time_remaining under 4 hours is considered BUSY."""
    report = Report(
        machine_id=1,
        status=MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(minutes=minutes_ago),
        time_remaining=None,
    )
    service, machine = create_service_and_data(report)
    with patch("service.machine.datetime", FixedDateTime):
        assert service._get_machine_status(machine) == MachineResponseStatus.BUSY


@given(minutes_ago=st.integers(min_value=240, max_value=10_000))
def test_busy_without_remaining_from_4_hours_is_probably_free(minutes_ago: int) -> None:
    """Check that a BUSY report without time_remaining from 4 hours is considered PROBABLY_FREE."""
    report = Report(
        machine_id=1,
        status=MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(minutes=minutes_ago),
        time_remaining=None,
    )
    service, machine = create_service_and_data(report)
    with patch("service.machine.datetime", FixedDateTime):
        assert service._get_machine_status(machine) == MachineResponseStatus.PROBABLY_FREE


@given(
    remaining=st.integers(min_value=1, max_value=500),
    elapsed=st.integers(min_value=0, max_value=1000),
)
def test_busy_with_remaining_before_expiry_is_busy(remaining: int, elapsed: int) -> None:
    """Check that a BUSY report with time_remaining that has not yet expired is considered BUSY."""
    assume(elapsed < remaining)
    report = Report(
        machine_id=1,
        status=MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(minutes=elapsed),
        time_remaining=remaining,
    )
    service, machine = create_service_and_data(report)
    with patch("service.machine.datetime", FixedDateTime):
        assert service._get_machine_status(machine) == MachineResponseStatus.BUSY


@given(
    remaining=st.integers(min_value=1, max_value=500),
    elapsed=st.integers(min_value=1, max_value=1000),
)
def test_busy_with_remaining_at_or_after_expiry_is_free(remaining: int, elapsed: int) -> None:
    """Check that a BUSY report with time_remaining that has expired is considered FREE."""
    assume(elapsed >= remaining)
    report = Report(
        machine_id=1,
        status=MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(minutes=elapsed),
        time_remaining=remaining,
    )
    service, machine = create_service_and_data(report)
    with patch("service.machine.datetime", FixedDateTime):
        assert service._get_machine_status(machine) == MachineResponseStatus.FREE
