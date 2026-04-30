from __future__ import annotations

from app.db.session import SessionLocal
from app.services.seed_service import seed_default_admin, seed_reference_data


def main() -> None:
    db = SessionLocal()
    try:
        seed_reference_data(db)
        seed_default_admin(db)
        db.commit()
        print("Seed completed successfully.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

