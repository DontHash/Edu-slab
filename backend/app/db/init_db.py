"""
Database initialization — delegates to scripts/init_database.py
"""
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from scripts.init_database import init_database  # noqa: E402


def init_db(reset: bool = False):
    init_database(reset=reset)


if __name__ == "__main__":
    init_database(reset=True)
