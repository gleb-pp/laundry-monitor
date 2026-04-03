from sqlalchemy import create_engine, inspect

from src.models.base import Base
from src.models.machines import Machine
from src.models.reports import Report
from src.schemas.machines import MachineReportStatus, MachineType


def test_machine_table_name() -> None:
    """Check that the Machine model has the correct table name."""
    assert Machine.__tablename__ == "machines"


def test_machine_columns() -> None:
    """Check that the Machine model has the correct columns."""
    columns = Machine.__table__.columns
    assert set(columns.keys()) == {"id", "dormitory", "name", "type"}


def test_machine_type_uses_machine_type_enum() -> None:
    """Check that the Machine model uses the correct type enum."""
    assert Machine.__table__.c["type"].type.enum_class is MachineType


def test_machine_has_dormitory_check_constraint() -> None:
    """Check that the Machine model has the correct dormitory constraint."""
    constraints = [
        str(constraint.sqltext)
        for constraint in Machine.__table__.constraints
        if hasattr(constraint, "sqltext")
    ]
    assert any("dormitory BETWEEN 1 AND 7" in text for text in constraints)


def test_report_table_name() -> None:
    """Check that the Report model has the correct table name."""
    assert Report.__tablename__ == "reports"


def test_report_columns() -> None:
    """Check that the Report model has the correct columns."""
    columns = Report.__table__.columns
    assert set(columns.keys()) == {
        "id",
        "machine_id",
        "status",
        "timestamp",
        "time_remaining",
    }


def test_report_status_uses_machine_report_status_enum() -> None:
    """Check that the Report model uses the correct status enum."""
    assert Report.__table__.c["status"].type.enum_class is MachineReportStatus


def test_report_time_remaining_is_nullable() -> None:
    """Check that the Report model has a nullable time_remaining column."""
    assert Report.__table__.c["time_remaining"].nullable is True


def test_report_foreign_key_points_to_machines() -> None:
    """Check that the Report model has the correct foreign key constraint."""
    foreign_keys = list(Report.__table__.c["machine_id"].foreign_keys)
    assert len(foreign_keys) == 1
    assert foreign_keys[0].target_fullname == "machines.id"


def test_report_timestamp_default_is_callable() -> None:
    """Check that the Report model has a default timestamp that is callable."""
    default = Report.__table__.c["timestamp"].default
    assert default is not None
    assert callable(default.arg)


def test_metadata_can_create_tables() -> None:
    """Check that the metadata can create tables in an in-memory SQLite."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    assert {"machines", "reports"}.issubset(table_names)
