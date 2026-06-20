"""Reset SQLite DB for foundation schema (dev only)."""
import os
from pathlib import Path

DB_FILES = ["eduassess.db", "eduassess.db-journal"]


def main():
    backend_dir = Path(__file__).resolve().parents[1]
    for name in DB_FILES:
        path = backend_dir / name
        if path.exists():
            path.unlink()
            print(f"Removed {path}")


if __name__ == "__main__":
    main()
