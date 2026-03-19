from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.api.auth import require_api_key
from core.db.models import DriftEvent, Snapshot
from core.db.session import get_db
from core.scheduler.poller import run_scan

router = APIRouter(
    prefix="/drifts",
    tags=["drifts"],
    dependencies=[Depends(require_api_key)],
)


@router.get("/")
async def list_drifts(
    limit: int = Query(50, le=200),
    severity: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List recent drift events."""
    q = select(DriftEvent).order_by(desc(DriftEvent.created_at)).limit(limit)
    if severity:
        q = q.where(DriftEvent.severity == severity.upper())
    result = await db.execute(q)
    rows = result.scalars().all()
    return [
        {
            "id": r.id,
            "service": r.service,
            "field": r.field,
            "expected": r.expected,
            "actual": r.actual,
            "severity": r.severity,
            "risk_score": r.risk_score,
            "resolved": r.resolved,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@router.get("/latest-snapshot")
async def latest_snapshot(db: AsyncSession = Depends(get_db)):
    """Return the most recent snapshot with desired vs actual state."""
    q = select(Snapshot).order_by(desc(Snapshot.created_at)).limit(1)
    result = await db.execute(q)
    snap = result.scalar_one_or_none()
    if not snap:
        return {"message": "No snapshots yet. Scan is running."}
    return {
        "id": snap.id,
        "desired": snap.desired,
        "actual": snap.actual,
        "drift_count": snap.drift_count,
        "risk_score": snap.risk_score,
        "created_at": snap.created_at.isoformat(),
    }


@router.post("/scan")
async def trigger_scan(db: AsyncSession = Depends(get_db)):
    """Manually trigger a drift scan."""
    try:
        return await run_scan(db)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
