from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.database import AsyncSessionLocal
from app.services.ynab import YNABService

scheduler = AsyncIOScheduler()
_app = None


async def _run_ynab_sync() -> None:
    ynab_service = YNABService()
    ml_service = getattr(_app.state, "ml_service", None) if _app else None
    async with AsyncSessionLocal() as db:
        try:
            result = await ynab_service.sync_transactions(
                db=db,
                ml_service=ml_service,
            )
            print(
                f"Scheduled sync complete: "
                f"fetched={result['fetched']} "
                f"synced={result['synced']} "
                f"errors={len(result['errors'])}"
            )
        except Exception as e:
            print(f"Scheduled sync failed: {e}")


def start_scheduler(app=None) -> None:
    global _app
    _app = app
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