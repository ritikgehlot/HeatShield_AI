"""CLI import helper.

Usage (from the project root, in either PowerShell or bash):
    python scripts/import_csv.py data/sample_city_features.csv

Fixes a real bug found during the V2 audit: running this exact command, as
originally documented in README.md, failed with
"ModuleNotFoundError: No module named 'backend'" because the project root was
never added to sys.path. The path fix below makes the documented command work
regardless of the caller's working directory or platform.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.db import SessionLocal, init_db  # noqa: E402
from backend.seed import seed_database  # noqa: E402
from backend.services import import_wards_from_csv  # noqa: E402


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
        imported, updated, skipped, run = import_wards_from_csv(db, file_path.read_bytes())
        # Capture these while the session is still open — run is a SQLAlchemy
        # object whose attributes expire on commit; reading them after the
        # `with` block closes the session raises DetachedInstanceError.
        run_id, run_status, run_error = run.id, run.status, run.error_message

    print(f"Imported: {imported} | Updated: {updated} | Skipped: {skipped} | Ingestion run #{run_id} ({run_status})")
    if run_error:
        print(f"Notes: {run_error}")


if __name__ == "__main__":
    main()
