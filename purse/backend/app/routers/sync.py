from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.ynab import YNABService

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])
ynab_service = YNABService()


@router.post("/trigger", status_code=202)
async def trigger_sync(db: AsyncSession = Depends(get_db)):
    """Manually trigger a YNAB sync."""
    result = await ynab_service.sync_transactions(db=db)
    return {"status": "sync_completed", "result": result}


@router.get("/status")
async def sync_status():
    """Return the status of the last sync."""
    from sync.scheduler import scheduler
    job = scheduler.get_job("ynab_sync")
    next_run = job.next_run_time.isoformat() if job and job.next_run_time else None
    return {
        "status": "scheduled",
        "next_sync": next_run,
        "last_sync": None,
    }