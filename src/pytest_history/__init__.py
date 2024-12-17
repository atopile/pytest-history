import os

import dotenv
import pytest

from pytest_history import report


def pytest_addoption(parser: pytest.Parser):
    history = parser.getgroup("history")

    def _add_option(name: str, help: str, default: str | None = None):
        history.addoption("--" + name, help=help, default=default)
        parser.addini(name, help=help, type="string", default=default)

    _add_option("history-email", "Email to login to Supabase")
    _add_option("history-url", "URL to use for Supabase")
    _add_option("history-key", "Key to use for Supabase")

    history.addoption(
        "--history-password", help="Password to use for history reporting"
    )
    # Password not in ini because it's insecure


def pytest_configure(config: pytest.Config):
    """Configure the pytest-history plugin.

    This runs in both the main process and worker processes to ensure we can
    collect results from all tests.
    """
    # Skip worker nodes if we're running in parallel
    if hasattr(config, "workerinput"):
        return

    try:
        dotenv.load_dotenv()

        def _get_option(name: str) -> str | None:
            underscored = name.replace("-", "_")
            if var := getattr(config.option, underscored):
                return var

            envar = ("pytest_" + underscored).upper()
            if var := os.environ.get(envar):
                return var
            if var := config.getini(name):
                return var
            return None

        email = _get_option("history-email")
        url = _get_option("history-url")
        key = _get_option("history-key")

        password = config.option.history_password or os.environ.get(
            "PYTEST_HISTORY_PASSWORD"
        )

        missing = []
        if not email:
            missing.append("email")
        if not password:
            missing.append("password")
        if not url:
            missing.append("url")
        if not key:
            missing.append("key")
        if missing:
            print(f"Missing {', '.join(missing)} to login to db, skipping history reporting")
            return

        reporter = report.SupabaseReporter(email, password, url, key)
    except Exception as e:
        print(f"Error configuring pytest-history: {repr(e)}")
        return

    config.pluginmanager.register(reporter, "history")


def pytest_unconfigure(config):
    if history := config.pluginmanager.getplugin("history"):
        config.pluginmanager.unregister(history)
