from datetime import UTC, datetime, timedelta

from src.models.machines import Machine
from src.models.reports import Report
from src.schemas.machines import MachineReportStatus, MachineResponseStatus
from src.service.machine import MachineService


def _machine_status(service: MachineService, machine_id: int):
    machines = service.get_machines_with_reports()
    machine = next(m for m in machines if m.id == machine_id)
    return machine.status


def test_get_machine_reports_returns_desc_order(db_session):
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


def test_get_machines_with_no_reports_are_free(db_session):
    service = MachineService(db_session)

    assert _machine_status(service, 1) == MachineResponseStatus.FREE


def test_unavailable_report_makes_machine_unavailable(db_session):
    service = MachineService(db_session)

    db_session.add(
        Report(
            machine_id=1,
            status=MachineReportStatus.UNAVAILABLE,
            timestamp=datetime.now(UTC),
            time_remaining=None,
        )
    )
    db_session.commit()

    assert _machine_status(service, 1) == MachineResponseStatus.UNAVAILABLE


def test_free_report_makes_machine_free(db_session):
    service = MachineService(db_session)

    db_session.add(
        Report(
            machine_id=1,
            status=MachineReportStatus.FREE,
            timestamp=datetime.now(UTC),
            time_remaining=None,
        )
    )
    db_session.commit()

    assert _machine_status(service, 1) == MachineResponseStatus.FREE


def test_busy_without_time_remaining_recent_is_busy(db_session):
    service = MachineService(db_session)

    db_session.add(
        Report(
            machine_id=1,
            status=MachineReportStatus.BUSY,
            timestamp=datetime.now(UTC) - timedelta(hours=1),
            time_remaining=None,
        )
    )
    db_session.commit()

    assert _machine_status(service, 1) == MachineResponseStatus.BUSY


def test_busy_without_time_remaining_old_is_probably_free(db_session):
    service = MachineService(db_session)

    db_session.add(
        Report(
            machine_id=1,
            status=MachineReportStatus.BUSY,
            timestamp=datetime.now(UTC) - timedelta(hours=5),
            time_remaining=None,
        )
    )
    db_session.commit()

    assert _machine_status(service, 1) == MachineResponseStatus.PROBABLY_FREE


def test_busy_with_remaining_time_not_expired_is_busy(db_session):
    service = MachineService(db_session)

    db_session.add(
        Report(
            machine_id=1,
            status=MachineReportStatus.BUSY,
            timestamp=datetime.now(UTC) - timedelta(minutes=10),
            time_remaining=30,
        )
    )
    db_session.commit()

    assert _machine_status(service, 1) == MachineResponseStatus.BUSY


def test_busy_with_remaining_time_expired_is_free(db_session):
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
        )
    )
    db_session.commit()

    assert _machine_status(service, machine.id) == MachineResponseStatus.FREE

def test_get_machine_reports_filters_orders_and_limits(db_session):
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

def test_send_report_creates_and_returns_report(db_session):
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

def test_send_report_allows_none_time_remaining(db_session):
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

def test_machine_status_uses_latest_report(db_session):
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

def test_get_machine_reports_uses_default_limit_10(db_session):
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
            )
        )
    db_session.commit()

    service = MachineService(db_session)
    reports = service.get_machine_reports(machine.id)

    assert len(reports) == 10
