import subprocess
from datetime import datetime
from typing import Protocol

from supabase import create_client
from supabase.client import ClientOptions

PUBLIC_SUPABASE_URL = "https://ynesgbuoxmszjrkzazxz.supabase.co"
PUBLIC_SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InluZXNnYnVveG1zempya3phenh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQzNzg5NDYsImV4cCI6MjA0OTk1NDk0Nn0.6KxEoSHTgyV4jKnnLAG5-Y9tWfHOzpl0qnA_NPzGUBo"



class Test(Protocol):
    nodeid: str
    outcome: str
    duration: float
    location: tuple[str, int, str]


def _get_githash() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"])
            .decode("utf-8")
            .strip()
        )
    except Exception:
        return "<unknown>"


class Supabase:
    def __init__(self, email: str, password: str):
        self.supabase = create_client(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_KEY, options=ClientOptions(auto_refresh_token=False))
        self.supabase.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )
        response = self.supabase.table("test.runs").insert(
            {
                "start": f"{datetime.now()}",
                "githash": _get_githash(),
            }
        ).execute()

        self._test_run = response.data[0]["id"]

    def pytest_runtest_logreport(self, report):
        if report.when != "teardown":
            return
        self.report(report)

    def report(self, test: Test):
        file, lineno, testcase = test.location
        self.supabase.table("test.results").insert(
            {
                "test_run": self._test_run,
                "node_id": test.nodeid,
                "file": file,
                "lineno": lineno,
                "testcase": testcase,
                "outcome": test.outcome,
                "duration": test.duration,
            }
        ).execute()
