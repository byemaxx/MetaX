from __future__ import annotations

import importlib
import importlib.util
import json
import sys

from metax.utils.version import __version__


REPORT_EXTRA = "MetaXTools[report]"
# These names cover the optional ``report`` extra and the analyzer modules that
# the report workflow loads.  Probe them with ``find_spec`` rather than imports:
# capabilities must not initialize Qt, plotting backends, or scientific work.
REPORT_IMPORT_ROOTS = (
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
)
REPORT_WORKFLOW_API_VERSION = "1.0"
REPORT_RESULT_SCHEMA_VERSION = "metax.report_result.v1"
REPORT_CAPABILITIES_SCHEMA_VERSION = "metax.report_capabilities.v1"


def _missing_report_message(missing_module: str | None = None) -> str:
    detail = f" Missing module: {missing_module}." if missing_module else ""
    return (
        "The MetaX report and analyzer dependencies are not installed."
        f"{detail} Install them with: python -m pip install \"{REPORT_EXTRA}\""
    )


def report_capabilities() -> dict[str, object]:
    """Return the lightweight, machine-readable report runtime contract."""
    missing = [
        module
        for module in REPORT_IMPORT_ROOTS
        if importlib.util.find_spec(module) is None
    ]
    available = not missing
    return {
        "schema_version": REPORT_CAPABILITIES_SCHEMA_VERSION,
        "available": available,
        "metax_version": __version__,
        "workflow_api_version": REPORT_WORKFLOW_API_VERSION,
        "result_schema_version": REPORT_RESULT_SCHEMA_VERSION,
        "missing_dependencies": missing,
        "reason": "" if available else "MetaX report dependencies are not installed.",
        "install_hint": "" if available else f'pip install "{REPORT_EXTRA}"',
    }


def main(argv: list[str] | None = None) -> int:
    """Load the report CLI only when the headless analysis stack is installed."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments == ["--capabilities"]:
        print(json.dumps(report_capabilities(), indent=2))
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
