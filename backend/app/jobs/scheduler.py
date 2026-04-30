from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone as pytz_timezone

from app.core.config import settings
from app.jobs.scheduled_jobs import (
    run_daily_hospitality_digest,
    run_no_show_alerts,
    run_unchecked_out_alerts,
)

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def get_scheduler() -> BackgroundScheduler | None:
    return _scheduler


def start_scheduler() -> BackgroundScheduler | None:
    global _scheduler
    if not settings.scheduler_enabled:
        logger.info("Scheduler disabled by config; skipping start")
        return None
    if _scheduler is not None:
        return _scheduler

    tz = pytz_timezone(settings.scheduler_timezone)
    scheduler = BackgroundScheduler(timezone=tz)
    scheduler.add_job(
        run_daily_hospitality_digest,
        CronTrigger(hour=settings.daily_digest_hour, minute=0, timezone=tz),
        id="daily_hospitality_digest",
        name="Daily Hospitality Digest",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        run_unchecked_out_alerts,
        CronTrigger(hour=settings.unchecked_out_hour, minute=0, timezone=tz),
        id="unchecked_out_alerts",
        name="Unchecked-Out Visitor Alert",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        run_no_show_alerts,
        CronTrigger(hour=settings.no_show_hour, minute=0, timezone=tz),
        id="no_show_alerts",
        name="No-Show Visitor Alert",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    _scheduler = scheduler
    logger.info(
        "Scheduler started in tz=%s with jobs: daily_digest@%02d:00, unchecked_out@%02d:00, no_show@%02d:00",
        settings.scheduler_timezone,
        settings.daily_digest_hour,
        settings.unchecked_out_hour,
        settings.no_show_hour,
    )
    return scheduler


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler stopped")
