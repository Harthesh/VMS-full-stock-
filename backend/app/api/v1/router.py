from fastapi import APIRouter

from app.api.v1.endpoints import (
    approvals,
    audit,
    auth,
    blacklist,
    dashboard,
    emergency,
    gate,
    hospitality,
    invitations,
    notifications,
    reports,
    scheduler,
    settings,
    users,
    visitor_requests,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(visitor_requests.router, prefix="/visitor-requests", tags=["visitor-requests"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(gate.router, prefix="/gate", tags=["gate"])
api_router.include_router(blacklist.router, prefix="/blacklist", tags=["blacklist"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(audit.router, prefix="/audit-logs", tags=["audit-logs"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(scheduler.router, prefix="/scheduler", tags=["scheduler"])
api_router.include_router(hospitality.router, prefix="/hospitality", tags=["hospitality"])
api_router.include_router(emergency.router, prefix="/emergency", tags=["emergency"])
api_router.include_router(invitations.router, prefix="/invitations", tags=["invitations"])
api_router.include_router(invitations.public_router, prefix="/public/invitations", tags=["invitations-public"])
