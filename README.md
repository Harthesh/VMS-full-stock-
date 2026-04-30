# Visitor Management System

Production-style full-stack Visitor Management System built with React, Vite, Tailwind CSS, FastAPI, PostgreSQL, SQLAlchemy, Redis, and JWT authentication.

## Structure

```text
backend/
  alembic/
  app/
    api/
    core/
    db/
    models/
    schemas/
    services/
    workflows/
  scripts/
frontend/
  src/
    api/
    app/
    components/
    modules/
    pages/
    router/
infra/
docs/
docker-compose.yml
```

## Backend Features
- JWT auth and role-based access control
- Visitor request CRUD
- Backend-enforced approval workflow engine
- Gate lookup, check-in, and check-out
- Badge and QR generation
- Blacklist/watchlist validation
- Hospitality/logistics support
- Notifications and audit logs
- Local file storage abstraction for document uploads
- Reports and dashboard endpoints

## Frontend Features
- Protected routes with role-aware sidebar
- Dashboard widgets and trend visualization
- Request create, edit, detail, and submit flow
- Pending approvals and approval actions
- Gate scan/check-in/check-out screens
- Blacklist, users, roles, settings, reports, and badge preview screens

## Local Setup

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python3 scripts/seed.py
uvicorn app.main:app --reload
```

`backend/.env.example` is for local development and points at PostgreSQL on `localhost:5433` and Redis on `localhost:6380`.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### 3. Docker

```bash
docker compose up --build
```

Docker Compose uses `backend/.env.docker.example`, which points at the internal `postgres` and `redis` service hostnames.

## Default Admin
- Email: `admin@vms.example.com` by default, or the value from `DEFAULT_ADMIN_EMAIL`
- Password: value from `DEFAULT_ADMIN_PASSWORD`

## Seeded Roles
- Employee
- HR
- BD / Sales
- Manager
- HOD
- CEO Office
- Security
- IT
- Gatekeeper
- Admin

## Notes
- Document uploads are stored under `backend/uploads/`.
- `LocalStorageService` is the default storage backend; swap this service to add S3 or MinIO later.
- Forgot password UI is intentionally marked as an integration placeholder pending email reset implementation.
- Reports are exposed as REST endpoints and can be exported by extending the report service.
