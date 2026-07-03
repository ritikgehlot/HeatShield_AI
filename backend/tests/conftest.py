"""Shared pytest setup.

Sets DATABASE_URL to a dedicated test-only SQLite file before any test module
imports backend.main — conftest.py is collected before test modules, which is
what makes this safe. The original single-test-file design set DATABASE_URL
right before its own import of backend.main; that only worked because there
was exactly one test file. Splitting into multiple files without this would
silently make every file after the first reuse whichever engine got
initialized first, since backend.db/backend.config are cached in
sys.modules — a real bug that would have been easy to introduce quietly.
"""
import os
from pathlib import Path

TEST_DB_PATH = Path(__file__).resolve().parent.parent.parent / "test_heatshield.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ.setdefault("APP_ENV", "test")

import pytest  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _clean_test_db():
    TEST_DB_PATH.unlink(missing_ok=True)
    yield
    TEST_DB_PATH.unlink(missing_ok=True)
