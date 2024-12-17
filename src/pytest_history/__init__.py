import os

import pytest

from pytest_history import report

DEFAULT_DB = ".test-results.db"


def pytest_addoption(parser: pytest.Parser):
    history = parser.getgroup("history")
    history.addoption("--history-email", help="Email to use for history reporting")
    history.addoption(
        "--history-password", help="Password to use for history reporting"
    )
    parser.addini(
        "history-email",
        "Email to use for history reporting",
        type="string",
        default=None,
    )
    # Password not in ini because it's insecure


def pytest_configure(config: pytest.Config):
    if not hasattr(config, "workerinput"):
        email = config.option.history_email or os.environ.get(
            "PYTEST_HISTORY_EMAIL", config.getini("history-email")
        )
        password = config.option.history_password or os.environ.get(
            "PYTEST_HISTORY_PASSWORD"
        )
        if not email or not password:
            print("No email or password provided to login to db, skipping history reporting")
            return

        try:
            test_reporter = report.Supabase(email, password)
        except Exception as e:
            print(f"Error configuring pytest-history: {repr(e)}")
            return

        config.stash["sql-reporter"] = test_reporter
        config.pluginmanager.register(test_reporter)


def pytest_unconfigure(config: pytest.Config):
    if hasattr(config, "workerinput"):
        if reporter := config.stash.get("sql-reporter"):
            del reporter
