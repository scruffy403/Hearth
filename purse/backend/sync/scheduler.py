from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.database import AsyncSessionLocal
from app.services.ynab import YNABService

scheduler = AsyncIOScheduler()


async def _run_ynab_sync() -> None:
    """
    Scheduled YNAB sync job.
    Creates its own DB session since it runs outside the request cycle.
    """
    ynab_service = YNABService()
    async with AsyncSessionLocal() as db:
        try:
            result = await ynab_service.sync_transactions(db=db)
            print(
                f"Scheduled sync complete: "
                f"fetched={result['fetched']} "
                f"synced={result['synced']} "
                f"errors={len(result['errors'])}"
            )
        except Exception as e:
            print(f"Scheduled sync failed: {e}")


def start_scheduler() -> None:
    scheduler.add_job(
        _run_ynab_sync,
        trigger=IntervalTrigger(hours=settings.sync_interval_hours),
        id="ynab_sync",
        name="YNAB transaction sync",
        replace_existing=True,
    )
    scheduler.start()


def stop_scheduler() -> None:
    scheduler.shutdown()