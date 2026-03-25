from pathlib import Path

from openpyxl import Workbook
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db import Base
from app.models import MedicationCatalog
from app.services.catalog_sync import sync_catalog


def _write_catalog(path: Path):
    wb = Workbook()
    ws = wb.active
    ws.title = "catalog"
    ws.append(["product_class", "product_name", "unique_id", "sort_order", "is_active"])
    ws.append(["Induction", "Propofol 1% 20mL", "P001", 10, True])
    ws.append(["Relaxant", "Rocuronium 50mg/5mL", "R001", 20, True])
    wb.save(path)


def test_sync_catalog_imports_rows(tmp_path: Path):
    catalog = tmp_path / "catalog.xlsx"
    _write_catalog(catalog)

    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        count = sync_catalog(session, catalog)
        assert count == 2
        rows = session.scalars(select(MedicationCatalog).order_by(MedicationCatalog.product_name)).all()
        assert [r.unique_id for r in rows] == ["P001", "R001"]


def test_sync_catalog_marks_missing_rows_inactive(tmp_path: Path):
    catalog = tmp_path / "catalog.xlsx"
    _write_catalog(catalog)

    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(MedicationCatalog(product_class="Legacy", product_name="Old Med", unique_id="OLD", is_active=True))
        session.commit()

        sync_catalog(session, catalog)

        old = session.scalar(select(MedicationCatalog).where(MedicationCatalog.product_name == "Old Med"))
        assert old is not None
        assert old.is_active is False


def test_sync_catalog_normalizes_unique_id_numeric_suffix(tmp_path: Path):
    catalog = tmp_path / "catalog.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "catalog"
    ws.append(["product_class", "product_name", "unique_id"])
    ws.append(["Numeric", "Code Med", 2002612175.0])
    wb.save(catalog)

    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        sync_catalog(session, catalog)
        row = session.scalar(select(MedicationCatalog).where(MedicationCatalog.product_name == "Code Med"))
        assert row is not None
        assert row.unique_id == "2002612175"
