from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class MedicationCatalog(Base):
    __tablename__ = "medication_catalog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_class: Mapped[str] = mapped_column(String(128), nullable=False)
    product_name: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    unique_id: Mapped[str] = mapped_column(String(128), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    source_hash: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Preset(Base):
    __tablename__ = "presets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(500), default="", nullable=False)

    items: Mapped[list["PresetItem"]] = relationship(back_populates="preset", cascade="all, delete-orphan")


class PresetItem(Base):
    __tablename__ = "preset_items"
    __table_args__ = (UniqueConstraint("preset_id", "catalog_id", name="uq_preset_catalog"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    preset_id: Mapped[int] = mapped_column(ForeignKey("presets.id"), nullable=False)
    catalog_id: Mapped[int] = mapped_column(ForeignKey("medication_catalog.id"), nullable=False)
    default_quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    preset: Mapped[Preset] = relationship(back_populates="items")
    catalog: Mapped[MedicationCatalog] = relationship()
