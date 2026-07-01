"""CLI import helper.

Usage:
    python scripts/import_csv.py data/sample_city_features.csv
"""
import sys
from pathlib import Path

from backend.db import SessionLocal, init_db
from backend.seed import seed_database
from backend.services import import_wards_from_csv


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/import_csv.py path/to/ward_features.csv")
        raise SystemExit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"File not found: {file_path}")
        raise SystemExit(1)

    init_db()
    with SessionLocal() as db:
        seed_database(db)
        imported, updated, skipped = import_wards_from_csv(db, file_path.read_bytes())
    print(f"Imported: {imported} | Updated: {updated} | Skipped: {skipped}")


if __name__ == "__main__":
    main()
