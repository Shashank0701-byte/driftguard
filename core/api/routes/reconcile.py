from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from core.api.auth import require_api_key
from core.db.session import get_db
from core.db.models import DriftEvent
from core.engine.parser import parse_compose
from core.config import settings
import docker

router = APIRouter(
    prefix="/reconcile",
    tags=["reconcile"],
    dependencies=[Depends(require_api_key)],
)

@router.post("/{service}")
async def reconcile_service(
    service: str,
    dry_run: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Reconcile a drifted service back to desired state."""
    try:
        desired = parse_compose(settings.compose_file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="docker-compose.yml not found")

    if service not in desired:
        raise HTTPException(status_code=404, detail=f"Service '{service}' not in compose file")

    target = desired[service]

    if dry_run:
        return {
            "service": service,
            "dry_run": True,
            "would_pull": target.get("image"),
            "message": "Dry run — no changes applied"
        }

    try:
        client = docker.DockerClient(base_url=settings.docker_socket)

        # Pull latest desired image
        client.images.pull(target["image"])

        # Stop and remove drifted container
        containers = client.containers.list(
            filters={"label": f"com.docker.compose.service={service}"}
        )
        for c in containers:
            c.stop()
            c.remove()

        # Mark drift events for this service as resolved
        q = select(DriftEvent).where(
            DriftEvent.service == service,
            DriftEvent.resolved == "false"
        )
        result = await db.execute(q)
        events = result.scalars().all()
        for e in events:
            e.resolved = "true"
        await db.commit()

        client.close()
        return {
            "service":    service,
            "image":      target["image"],
            "resolved":   len(events),
            "message":    f"Reconciled. Run docker-compose up to restart {service}."
        }

    except docker.errors.APIError as e:
        raise HTTPException(status_code=500, detail=str(e))
