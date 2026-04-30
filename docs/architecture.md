# Visitor Management System Architecture

## Backend
- FastAPI application with modular layers under `backend/app/`.
- SQLAlchemy models cover users, RBAC, visitor requests, approvals, gate logs, blacklist, notifications, settings, and audit logs.
- Workflow rules are defined in `backend/app/workflows/definitions.py` and enforced in `backend/app/services/workflow_service.py`.
- Document uploads use `LocalStorageService`; the interface is intentionally abstracted so S3/MinIO can replace it without changing route logic.
- Notifications are persisted to the `notifications` table and can be extended to Redis jobs or SMTP adapters.

## Frontend
- React + Vite + Tailwind application under `frontend/src/`.
- Auth is centralized in `AuthProvider`; routes and sidebar visibility are role-aware.
- Shared API clients mirror backend modules: auth, requests, approvals, gate, blacklist, admin, settings.
- Request creation, approval handling, gate actions, badge preview, and admin screens all use the same backend contracts.

## Operational Flow
1. Request creators submit visitor requests based on role and visitor type.
2. Backend workflow service generates approval steps and drives state transitions.
3. Approval actions are logged in approval history and audit logs.
4. Gate module validates approval state and blacklist matches before allowing entry.
5. Badge and QR values are generated once the request becomes gate-eligible.

