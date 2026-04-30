from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.deps import require_roles
from app.core.enums import RoleKey
from app.jobs.scheduled_jobs import run_job_by_id
from app.jobs.scheduler import get_scheduler
from app.models.rbac import User

router = APIRouter()


class ScheduledJobInfo(BaseModel):
    id: str
    name: str
    next_run_time: str | None
    trigger: str


class SchedulerStatus(BaseModel):
    running: bool
    timezone: str | None
    jobs: list[ScheduledJobInfo]


@router.get("/status", response_model=SchedulerStatus)
def scheduler_status(_: User = Depends(require_roles(RoleKey.ADMIN))) -> SchedulerStatus:
    scheduler = get_scheduler()
    if scheduler is None:
        return SchedulerStatus(running=False, timezone=None, jobs=[])
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append(
            ScheduledJobInfo(
                id=job.id,
                name=job.name,
                next_run_time=job.next_run_time.isoformat() if job.next_run_time else None,
                trigger=str(job.trigger),
            )
        )
    return SchedulerStatus(running=scheduler.running, timezone=str(scheduler.timezone), jobs=jobs)


@router.post("/jobs/{job_id}/run", status_code=status.HTTP_202_ACCEPTED)
def run_job(job_id: str, _: User = Depends(require_roles(RoleKey.ADMIN))) -> dict:
    try:
        run_job_by_id(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "executed", "job_id": job_id}
