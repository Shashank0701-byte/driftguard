import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db.models import DriftEvent, Snapshot
from core.engine.differ import diff
from core.engine.parser import parse_compose
from core.engine.scorer import score
from core.engine.snapshotter import snapshot_live

logger = logging.getLogger("driftguard.poller")


async def run_scan(db: AsyncSession) -> dict:
    """Core scan logic called by the scheduler and manual trigger."""
    try:
        desired = parse_compose(settings.compose_file_path)
        actual = snapshot_live(settings.docker_socket)
        drifts = diff(desired, actual)
        risk = score(drifts)

        current_keys = {
            (
                d.service,
                d.field,
                str(d.expected) if d.expected is not None else None,
                str(d.actual) if d.actual is not None else None,
                d.severity.value,
            )
            for d in drifts
        }

        existing_result = await db.execute(
            select(DriftEvent).where(DriftEvent.resolved == "false")
        )
        existing_events = existing_result.scalars().all()
        existing_by_key = {
            (e.service, e.field, e.expected, e.actual, e.severity): e
            for e in existing_events
        }
        seen_existing_keys = set()

        for event in existing_events:
            key = (event.service, event.field, event.expected, event.actual, event.severity)
            if key in seen_existing_keys:
                event.resolved = "true"
                continue

            seen_existing_keys.add(key)
            if key not in current_keys:
                event.resolved = "true"

        snap = Snapshot(
            desired=desired,
            actual=actual,
            drift_count=len(drifts),
            risk_score=risk,
        )
        db.add(snap)

        for d in drifts:
            expected = str(d.expected) if d.expected is not None else None
            actual_value = str(d.actual) if d.actual is not None else None
            key = (d.service, d.field, expected, actual_value, d.severity.value)

            existing = existing_by_key.get(key)
            if existing:
                existing.risk_score = risk
                existing.resolved = "false"
                continue

            db.add(
                DriftEvent(
                    service=d.service,
                    field=d.field,
                    expected=expected,
                    actual=actual_value,
                    severity=d.severity.value,
                    risk_score=risk,
                )
            )

        await db.commit()

        logger.info("Scan complete - %s drift(s), risk score %s", len(drifts), risk)
        return {
            "drifts": len(drifts),
            "risk_score": risk,
            "services": list(desired.keys()),
        }
    except Exception:
        await db.rollback()
        logger.exception("Scan failed")
        raise
