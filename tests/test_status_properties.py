from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from hypothesis import assume, given, strategies as st

from models import Machine, Report
from schemas import MachineReportStatus, MachineResponseStatus
from service.machine import MachineService


NOW = datetime(2026, 4, 2, 12, 0, tzinfo=UTC)


class FixedDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        if tz is None:
            return NOW.replace(tzinfo=None)
        return NOW.astimezone(tz)


def make_machine() -> Machine:
    return Machine(id=1, dormitory=1, name="Washer 1")


def make_service_with_report(report: Report) -> MachineService:
    service = MachineService(db=None)
    service.get_machine_reports = lambda machine_id, limit=1: [report]
    return service


@given(days_ago=st.integers(min_value=0, max_value=365))
def test_unavailable_always_stays_unavailable(days_ago):
    report = Report(
        machine_id=1,
        status=MachineReportStatus.UNAVAILABLE,
        timestamp=NOW - timedelta(days=days_ago),
        time_remaining=None,
    )
    service = make_service_with_report(report)

    with patch("service.machine.datetime", FixedDateTime):
        assert service._get_machine_status(make_machine()) == MachineResponseStatus.UNAVAILABLE


@given(minutes_ago=st.integers(min_value=0, max_value=239))
def test_busy_without_remaining_under_4_hours_is_busy(minutes_ago):
    report = Report(
        machine_id=1,
        status=MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(minutes=minutes_ago),
        time_remaining=None,
    )
    service = make_service_with_report(report)

    with patch("service.machine.datetime", FixedDateTime):
        assert service._get_machine_status(make_machine()) == MachineResponseStatus.BUSY


@given(minutes_ago=st.integers(min_value=240, max_value=10_000))
def test_busy_without_remaining_from_4_hours_is_probably_free(minutes_ago):
    report = Report(
        machine_id=1,
        status=MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(minutes=minutes_ago),
        time_remaining=None,
    )
    service = make_service_with_report(report)

    with patch("service.machine.datetime", FixedDateTime):
        assert service._get_machine_status(make_machine()) == MachineResponseStatus.PROBABLY_FREE


@given(
    remaining=st.integers(min_value=1, max_value=500),
    elapsed=st.integers(min_value=0, max_value=1000),
)
def test_busy_with_remaining_before_expiry_is_busy(remaining, elapsed):
    assume(elapsed < remaining)

    report = Report(
        machine_id=1,
        status=MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(minutes=elapsed),
        time_remaining=remaining,
    )
    service = make_service_with_report(report)

    with patch("service.machine.datetime", FixedDateTime):
        assert service._get_machine_status(make_machine()) == MachineResponseStatus.BUSY


@given(
    remaining=st.integers(min_value=1, max_value=500),
    elapsed=st.integers(min_value=1, max_value=1000),
)
def test_busy_with_remaining_at_or_after_expiry_is_free(remaining, elapsed):
    assume(elapsed >= remaining)

    report = Report(
        machine_id=1,
        status=MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(minutes=elapsed),
        time_remaining=remaining,
    )
    service = make_service_with_report(report)

    with patch("service.machine.datetime", FixedDateTime):
        assert service._get_machine_status(make_machine()) == MachineResponseStatus.FREE
