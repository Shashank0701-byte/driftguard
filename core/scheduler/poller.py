import logging

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

        snap = Snapshot(
            desired=desired,
            actual=actual,
            drift_count=len(drifts),
            risk_score=risk,
        )
        db.add(snap)

        for d in drifts:
            event = DriftEvent(
                service=d.service,
                field=d.field,
                expected=str(d.expected) if d.expected is not None else None,
                actual=str(d.actual) if d.actual is not None else None,
                severity=d.severity.value,
                risk_score=risk,
            )
            db.add(event)

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
