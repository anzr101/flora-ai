"""Diagnosis persistence — the gateway's only stateful concern.

One table: every successful /diagnose call is recorded so users (and
recruiters) can see a history of what the system concluded. SQLite by
default for zero-setup dev; point FLORA_DATABASE_URL at Postgres in
production — the code path is identical (SQLAlchemy async).

Tables are created lazily on first use so the web layer needs no startup
hook and tests need no fixtures.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone

from flora_common import get_logger
from sqlalchemy import JSON, DateTime, Float, String, Text, select
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from floragateway.config import settings

log = get_logger("floragateway.db")


class Base(DeclarativeBase):
    pass


class DiagnosisRecord(Base):
    __tablename__ = "diagnoses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    question: Mapped[str] = mapped_column(Text)
    species_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    species_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    health_label: Mapped[str | None] = mapped_column(String(50), nullable=True)
    health_risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    advice: Mapped[str] = mapped_column(Text)
    citations: Mapped[list] = mapped_column(JSON, default=list)
    services_called: Mapped[list] = mapped_column(JSON, default=list)


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker | None = None
_tables_ready = False
_init_lock = asyncio.Lock()


def reset() -> None:
    """Drop cached engine/state — used by tests to point at a fresh database."""
    global _engine, _session_factory, _tables_ready
    _engine = None
    _session_factory = None
    _tables_ready = False


def _factory() -> async_sessionmaker:
    global _engine, _session_factory
    if _session_factory is None:
        _engine = create_async_engine(settings.database_url, echo=False)
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    return _session_factory


async def _ensure_tables() -> None:
    global _tables_ready
    if _tables_ready:
        return
    async with _init_lock:
        if _tables_ready:
            return
        _factory()  # builds the engine
        assert _engine is not None
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        _tables_ready = True
        log.info(f"diagnosis table ready ({settings.database_url.split('@')[-1]})")


async def save_diagnosis(
    *,
    question: str,
    species_label: str | None,
    species_confidence: float | None,
    health_label: str | None,
    health_risk_score: float | None,
    advice: str,
    citations: list[dict],
    services_called: list[str],
) -> str:
    await _ensure_tables()
    record = DiagnosisRecord(
        id=str(uuid.uuid4()),
        created_at=datetime.now(timezone.utc),
        question=question,
        species_label=species_label,
        species_confidence=species_confidence,
        health_label=health_label,
        health_risk_score=health_risk_score,
        advice=advice,
        citations=citations,
        services_called=services_called,
    )
    factory = _factory()
    async with factory() as session:
        session.add(record)
        await session.commit()
    return record.id


async def list_recent(limit: int = 20) -> list[dict]:
    await _ensure_tables()
    factory = _factory()
    async with factory() as session:
        rows = (
            await session.execute(
                select(DiagnosisRecord)
                .order_by(DiagnosisRecord.created_at.desc())
                .limit(limit)
            )
        ).scalars().all()
    return [
        {
            "id": r.id,
            "created_at": r.created_at.isoformat(),
            "question": r.question,
            "species_label": r.species_label,
            "species_confidence": r.species_confidence,
            "health_label": r.health_label,
            "health_risk_score": r.health_risk_score,
            "advice": r.advice,
            "citations": r.citations,
            "services_called": r.services_called,
        }
        for r in rows
    ]
