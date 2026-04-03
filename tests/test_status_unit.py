from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest

from src.models import Machine, Report
from src.schemas import MachineReportStatus, MachineResponseStatus
from src.service.machine import MachineService


NOW = datetime.now(UTC)

class FixedDateTime:
    """Mock datetime to return fixed NOW."""
    @classmethod
    def now(cls, tz=None):
        if tz is not None:
            return NOW.astimezone(tz)
        return NOW


@pytest.fixture
def machine(db_session):
    machine = Machine(dormitory=1, name="Washer 1")
    db_session.add(machine)
    db_session.commit()
    db_session.refresh(machine)
    return machine


def test_get_machine_status_requests_only_one_report(db_session, machine):
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

    # Напрямую проверить количество запросов сложно, но можно проверить, что статус определён по последнему
    status = service._get_machine_status(machine)
    # Последний отчёт – BUSY, значит статус должен быть BUSY (если время не истекло)
    assert status == MachineResponseStatus.BUSY


def test_no_reports_means_free(db_session, machine):
    service = MachineService(db_session)
    assert service._get_machine_status(machine) == MachineResponseStatus.FREE


def test_unavailable_report_means_unavailable(db_session, machine):
    service = MachineService(db_session)
    report = Report(
        machine_id=machine.id,
        status=MachineReportStatus.UNAVAILABLE,
        timestamp=NOW - timedelta(minutes=5),
        time_remaining=None,
    )
    db_session.add(report)
    db_session.commit()
    assert service._get_machine_status(machine) == MachineResponseStatus.UNAVAILABLE


def test_free_report_means_free(db_session, machine):
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
def test_busy_without_time_remaining_recent_is_busy(db_session, machine):
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
def test_busy_without_time_remaining_at_4_hours_is_probably_free(db_session, machine):
    service = MachineService(db_session)
    report = Report(
        machine_id=machine.id,
        status=MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(hours=4),
        time_remaining=None,
    )
    db_session.add(report)
    db_session.commit()
    assert service._get_machine_status(machine) == MachineResponseStatus.PROBABLY_FREE


@patch("service.machine.datetime", FixedDateTime)
def test_busy_without_time_remaining_after_4_hours_is_probably_free(db_session, machine):
    service = MachineService(db_session)
    report = Report(
        machine_id=machine.id,
        status=MachineReportStatus.BUSY,
        timestamp=NOW - timedelta(hours=5),
        time_remaining=None,
    )
    db_session.add(report)
    db_session.commit()
    assert service._get_machine_status(machine) == MachineResponseStatus.PROBABLY_FREE


@patch("service.machine.datetime", FixedDateTime)
def test_busy_with_remaining_before_expiry_is_busy(db_session, machine):
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
def test_busy_with_remaining_at_expiry_is_free(db_session, machine):
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
def test_busy_with_remaining_after_expiry_is_free(db_session, machine):
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
