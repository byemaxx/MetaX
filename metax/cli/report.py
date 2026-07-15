from __future__ import annotations

import importlib
import sys


REPORT_EXTRA = "MetaXTools[report]"
REPORT_IMPORT_ROOTS = {
    "adjustText",
    "distinctipy",
    "inmoose",
    "jinja2",
    "joblib",
    "matplotlib",
    "numba",
    "pyecharts",
    "scipy",
    "seaborn",
    "sklearn",
    "statsmodels",
    "upsetplot",
}


def _missing_report_message(missing_module: str | None = None) -> str:
    detail = f" Missing module: {missing_module}." if missing_module else ""
    return (
        "The MetaX report and analyzer dependencies are not installed."
        f"{detail} Install them with: python -m pip install \"{REPORT_EXTRA}\""
    )


def main(argv: list[str] | None = None) -> int:
    """Load the report CLI only when the headless analysis stack is installed."""
    try:
        report_cli = importlib.import_module("metax.report.cli")
    except ModuleNotFoundError as exc:
        missing_root = (exc.name or "").split(".", 1)[0]
        if missing_root in REPORT_IMPORT_ROOTS:
            print(_missing_report_message(exc.name), file=sys.stderr)
            return 4
        raise
    return report_cli.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
