from datetime import UTC, datetime, timedelta, timezone
from unittest.mock import patch
from unittest.mock import Mock

from src.models import Machine, Report
from src.schemas import MachineReportStatus, MachineResponseStatus
from service.machine import MachineService


NOW = datetime.now(timezone.utc)

class FixedDateTime:
    """Mock datetime to return fixed NOW."""
    @classmethod
    def now(cls, tz=None):
        if tz is not None:
            return NOW.astimezone(tz)
        return NOW

def test_get_machine_status_requests_only_one_report():
    service = MachineService(db=None)
    service.get_machine_reports = Mock(return_value=[
        Mock(status=MachineReportStatus.FREE)
    ])

    machine = Machine(id=1, dormitory=1, name="M1")
    status = service._get_machine_status(machine)

    assert status == MachineResponseStatus.FREE
    service.get_machine_reports.assert_called_once_with(1, limit=1)

class FixedDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        if tz is None:
            return NOW.replace(tzinfo=None)
        return NOW.astimezone(tz)


def make_machine(machine_id: int = 1) -> Machine:
    return Machine(id=machine_id, dormitory=1, name="Washer 1")


def make_report(
    status: MachineReportStatus,
    *,
    timestamp: datetime,
    time_remaining: int | None = None,
    machine_id: int = 1,
) -> Report:
    return Report(
        machine_id=machine_id,
        status=status,
        timestamp=timestamp,
        time_remaining=time_remaining,
    )


def test_no_reports_means_free():
    service = MachineService(db=None)
    machine = make_machine()

    service.get_machine_reports = lambda machine_id, limit=1: []

    assert service._get_machine_status(machine) == MachineResponseStatus.FREE


def test_unavailable_report_means_unavailable():
    service = MachineService(db=None)
    machine = make_machine()
    report = make_report(
        MachineReportStatus.UNAVAILABLE,
        timestamp=NOW - timedelta(minutes=5),
    )
    service.get_machine_reports = lambda machine_id, limit=1: [report]

    assert service._get_machine_status(machine) == MachineResponseStatus.UNAVAILABLE


def test_free_report_means_free():
    service = MachineService(db=None)
    machine = make_machine()
    report = make_report(
        MachineReportStatus.FREE,
        timestamp=NOW - timedelta(minutes=5),
    )
    service.get_machine_reports = lambda machine_id, limit=1: [report]

    assert service._get_machine_status(machine) == MachineResponseStatus.FREE


@patch("service.machine.datetime", FixedDateTime)
def test_busy_without_time_remaining_recent_is_busy():
    service = MachineService(db=None)
    machine = make_machine()
    report = make_report(
        MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(hours=1),
        time_remaining=None,
    )
    service.get_machine_reports = lambda machine_id, limit=1: [report]

    assert service._get_machine_status(machine) == MachineResponseStatus.BUSY


@patch("service.machine.datetime", FixedDateTime)
def test_busy_without_time_remaining_at_4_hours_is_probably_free():
    service = MachineService(db=None)
    machine = make_machine()
    report = make_report(
        MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(hours=4),
        time_remaining=None,
    )
    service.get_machine_reports = lambda machine_id, limit=1: [report]

    assert service._get_machine_status(machine) == MachineResponseStatus.PROBABLY_FREE


@patch("service.machine.datetime", FixedDateTime)
def test_busy_without_time_remaining_after_4_hours_is_probably_free():
    service = MachineService(db=None)
    machine = make_machine()
    report = make_report(
        MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(hours=5),
        time_remaining=None,
    )
    service.get_machine_reports = lambda machine_id, limit=1: [report]

    assert service._get_machine_status(machine) == MachineResponseStatus.PROBABLY_FREE


@patch("service.machine.datetime", FixedDateTime)
def test_busy_with_remaining_before_expiry_is_busy():
    service = MachineService(db=None)
    machine = make_machine()
    report = make_report(
        MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(minutes=10),
        time_remaining=30,
    )
    service.get_machine_reports = lambda machine_id, limit=1: [report]

    assert service._get_machine_status(machine) == MachineResponseStatus.BUSY


@patch("service.machine.datetime", FixedDateTime)
def test_busy_with_remaining_at_expiry_is_free():
    service = MachineService(db=None)
    machine = make_machine()
    report = make_report(
        MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(minutes=30),
        time_remaining=30,
    )
    service.get_machine_reports = lambda machine_id, limit=1: [report]

    assert service._get_machine_status(machine) == MachineResponseStatus.FREE


@patch("service.machine.datetime", FixedDateTime)
def test_busy_with_remaining_after_expiry_is_free():
    service = MachineService(db=None)
    machine = make_machine()
    report = make_report(
        MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(minutes=45),
        time_remaining=30,
    )
    service.get_machine_reports = lambda machine_id, limit=1: [report]

    assert service._get_machine_status(machine) == MachineResponseStatus.FREE
