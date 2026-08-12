from __future__ import annotations

import importlib
import json
import sys
from importlib.util import find_spec

from metax.utils.version import __version__


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
REPORT_WORKFLOW_API_VERSION = "1.0"
REPORT_RESULT_SCHEMA_VERSION = "metax.report_result.v1"
REPORT_CAPABILITIES_SCHEMA_VERSION = "metax.report_capabilities.v1"


def _missing_report_message(missing_module: str | None = None) -> str:
    detail = f" Missing module: {missing_module}." if missing_module else ""
    return (
        "The MetaX report and analyzer dependencies are not installed."
        f"{detail} Install them with: python -m pip install \"{REPORT_EXTRA}\""
    )


def _report_stack_available() -> bool:
    """Check report dependency availability without importing the report or Qt stacks."""
    return all(find_spec(module_name) is not None for module_name in REPORT_IMPORT_ROOTS)


def main(argv: list[str] | None = None) -> int:
    """Load the report CLI only when the headless analysis stack is installed."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments == ["--capabilities"]:
        print(
            json.dumps(
                {
                    "schema_version": REPORT_CAPABILITIES_SCHEMA_VERSION,
                    "available": _report_stack_available(),
                    "metax_version": __version__,
                    "workflow_api_version": REPORT_WORKFLOW_API_VERSION,
                    "result_schema_version": REPORT_RESULT_SCHEMA_VERSION,
                },
                indent=2,
            )
        )
        return 0
    try:
        report_cli = importlib.import_module("metax.report.cli")
    except ModuleNotFoundError as exc:
        missing_root = (exc.name or "").split(".", 1)[0]
        if missing_root in REPORT_IMPORT_ROOTS:
            print(_missing_report_message(exc.name), file=sys.stderr)
            return 4
        raise
    return report_cli.main(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
