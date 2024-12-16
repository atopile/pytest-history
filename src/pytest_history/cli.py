from __future__ import annotations

import sys
from enum import IntEnum
from pathlib import Path
from typing import Optional

import rich
import typer
from rich.table import Table

from pytest_history.queries import flakes, newly_added, results, runs

app = typer.Typer(
    help="Provide insights into historic test executions",
    no_args_is_help=True,
)
list_app = typer.Typer(help="List historic data", no_args_is_help=True)
app.add_typer(list_app, name="list")


class ExitCode(IntEnum):
    Success = 0
    Failure = 1


def validate_db(db: Path) -> Path:
    if not db.exists():
        raise typer.BadParameter(f"Database: {db}, does not exist")
    return db


@app.command("flakes")
def print_flakes(
    db: Path = typer.Option(
        ".test-results.db",
        help="Database used for analysing the data",
        callback=validate_db,
    ),
) -> ExitCode:
    """List all flaky tests"""
    exit_code = ExitCode.Success
    for f in flakes(db):
        rich.print(f"{f.node_id}")
        exit_code = ExitCode.Failure
    return exit_code


@list_app.command("results")
def print_results(
    id: int = typer.Argument(
        ..., help="Id of the test run whose result shall be reported"
    ),
    db: Path = typer.Option(
        ".test-results.db",
        help="Database used for analysing the data",
        callback=validate_db,
    ),
) -> ExitCode:
    """List historic test results"""
    table = Table(title=f"Test Results for Run {id}")
    table.add_column("ID")
    table.add_column("Test")
    table.add_column("Duration")
    table.add_column("Outcome")

    for r in results(db, id):
        table.add_row(
            str(r.id),
            r.node_id,
            str(r.duration),
            r.outcome,
        )

    rich.print(table)
    return ExitCode.Success


@list_app.command("runs")
def print_runs(
    db: Path = typer.Option(
        ".test-results.db",
        help="Database used for analysing the data",
        callback=validate_db,
    ),
) -> ExitCode:
    """List historic test runs"""
    table = Table(title="Test Runs")
    table.add_column("ID")
    table.add_column("Git Hash")
    table.add_column("Date/Time")

    for r in runs(db):
        table.add_row(str(r.id), r.githash, str(r.start))

    rich.print(table)
    return ExitCode.Success


@list_app.command("added")
def print_newly_added(
    db: Path = typer.Option(
        ".test-results.db",
        help="Database used for analysing the data",
        callback=validate_db,
    ),
) -> ExitCode:
    """List test added during the most recent run"""
    table = Table(title="Newly Added Tests")
    table.add_column("ID")
    table.add_column("Test")
    table.add_column("Duration")
    table.add_column("Outcome")

    for n in newly_added(db):
        table.add_row(
            str(n.id),
            n.node_id,
            str(n.duration),
            n.outcome,
        )

    rich.print(table)
    return ExitCode.Success


def main(argv: Optional[list[str]] = None) -> None:
    try:
        if argv:
            sys.argv[1:] = argv
        app()
    except Exception as ex:
        rich.print(f"Error occurred, details: {ex}")
        sys.exit(ExitCode.Failure)


if __name__ == "__main__":
    main()
