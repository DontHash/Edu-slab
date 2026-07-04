"""Deprecated — use: python scripts/init_database.py --reset"""
import subprocess
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    subprocess.run(
        [sys.executable, str(BACKEND_ROOT / "scripts" / "init_database.py"), "--reset"],
        cwd=BACKEND_ROOT,
        check=True,
    )
