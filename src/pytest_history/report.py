import subprocess
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Protocol

import pytest
from supabase import create_client
from supabase.client import Client, ClientOptions

if TYPE_CHECKING:
    from _pytest.terminal import TerminalReporter


class Test(Protocol):
    nodeid: str
    outcome: str
    duration: float
    location: tuple[str, int, str]


def _get_githash() -> str | None:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"])
            .decode("utf-8")
            .strip()
        )
    except subprocess.CalledProcessError:
        return None


class SupabaseReporter:
    def __init__(self, email: str, password: str, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(
            supabase_url,
            supabase_key,
            options=ClientOptions(auto_refresh_token=False),
        )
        self.supabase.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )
        self._test_run: Optional[int] = None
        self._report_count: int = 0

    def pytest_configure(self, config) -> None:
        """Configure the plugin"""
        response = (
            self.supabase.table("test_runs")
            .insert(
                {
                    "start": f"{datetime.now()}",
                    "githash": _get_githash(),
                }
            )
            .execute()
        )
        self._test_run = response.data[0]["id"]

    def pytest_runtest_logreport(self, report) -> None:
        """Process a test report"""
        if report.when != "call":  # Only process the actual test call
            return

        try:
            self.report(report)
        except Exception as e:
            print(f"Error reporting {report.nodeid}: {e}")

    def report(self, test: Test) -> None:
        """Report a test result to Supabase.

        Args:
            test: The test result to report
        """
        if self._test_run is None:
            return

        file, lineno, testcase = test.location
        self.supabase.table("test_results").insert(
            {
                "test_runs_id": self._test_run,
                "nodeid": test.nodeid,
                "file": file,
                "lineno": lineno,
                "testcase": testcase,
                "outcome": test.outcome,
                "duration": test.duration,
            }
        ).execute()
        self._report_count += 1

    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(self, session):
        print(f"Reported {self._report_count} tests")
        # TODO: execute the request here

    def pytest_terminal_summary(self, terminalreporter: "TerminalReporter"):
        terminalreporter.write_line(f"Recorded {self._report_count} tests for posterity")
