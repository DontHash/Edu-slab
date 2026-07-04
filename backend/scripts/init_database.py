"""
Create a fresh diagnostic_platform database.

Usage (from backend/):
    python scripts/init_database.py
    python scripts/init_database.py --reset
"""
import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings  # noqa: E402
from app.db.database import Base, engine  # noqa: E402
import app.models  # noqa: F401, E402 — register all active models


def resolve_db_path() -> Path | None:
    url = settings.DATABASE_URL
    if not url.startswith("sqlite"):
        return None
    # sqlite:///./data/file.db → backend/data/file.db
    relative = url.replace("sqlite:///", "").lstrip("/")
    if relative.startswith("./"):
        relative = relative[2:]
    return BACKEND_ROOT / relative


def remove_legacy_databases() -> None:
    legacy_names = ["eduassess.db", "eduassess.db-journal"]
    for name in legacy_names:
        path = BACKEND_ROOT / name
        if path.exists():
            path.unlink()
            print(f"Removed legacy database: {path}")


def init_database(reset: bool = False) -> None:
    data_dir = BACKEND_ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    db_path = resolve_db_path()
    if db_path and reset and db_path.exists():
        db_path.unlink()
        journal = Path(str(db_path) + "-journal")
        if journal.exists():
            journal.unlink()
        print(f"Removed existing database: {db_path}")

    remove_legacy_databases()

    Base.metadata.create_all(bind=engine)

    print(f"Database ready: {settings.DATABASE_URL}")
    if db_path:
        print(f"File: {db_path} ({db_path.stat().st_size} bytes)")
    print(f"Tables: {', '.join(sorted(Base.metadata.tables.keys()))}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize diagnostic platform database")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete the current database file before creating tables",
    )
    args = parser.parse_args()
    init_database(reset=args.reset)
