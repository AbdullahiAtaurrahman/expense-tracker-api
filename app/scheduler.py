import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database import AsyncSessionLocal
from app.services.recurring_transaction_execution import (
    RecurringTransactionExecutionService,
)

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="UTC")


async def process_recurring_transactions():

    today = datetime.now(timezone.utc).date()

    async with AsyncSessionLocal() as session:

        service = RecurringTransactionExecutionService(session)

        processed_count = await service.process_due_transactions(today)

        logger.info(
            "Recurring transactions processed: %s",
            processed_count,
        )


def start_scheduler():

    if not scheduler.running:

        scheduler.add_job(
            process_recurring_transactions,
            trigger="cron",
            hour=0,
            minute=5,
            id="recurring_transaction_processor",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )

        scheduler.start()
        logger.info("Recurring transaction scheduler started.")


def stop_scheduler():

    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Recurring transaction scheduler stopped.")
