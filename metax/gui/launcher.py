from __future__ import annotations

import importlib
import sys


GUI_EXTRA = "MetaXTools[gui]"
GUI_IMPORT_ROOTS = {
    "adjustText",
    "distinctipy",
    "inmoose",
    "ipykernel",
    "jinja2",
    "joblib",
    "matplotlib",
    "numba",
    "openpyxl",
    "packaging",
    "pyecharts",
    "PyQt5",
    "PyQtWebEngine",
    "qt_material",
    "qtawesome",
    "requests",
    "scipy",
    "seaborn",
    "sklearn",
    "statsmodels",
    "upsetplot",
}
NATIVE_IMPORT_ERROR_MARKERS = (
    "cannot open shared object file",
    "dll load failed",
    "image not found",
    "library not loaded",
)


def _missing_gui_message(missing_module: str | None = None) -> str:
    detail = f" Missing module: {missing_module}." if missing_module else ""
    return (
        "The MetaX desktop GUI dependencies are not installed."
        f"{detail} Install them with: python -m pip install \"{GUI_EXTRA}\""
    )


def _is_gui_dependency_import_error(exc: ImportError) -> bool:
    missing_root = (exc.name or "").split(".", 1)[0]
    if missing_root in GUI_IMPORT_ROOTS:
        return True
    error_message = str(exc).casefold()
    return any(marker in error_message for marker in NATIVE_IMPORT_ERROR_MARKERS)


def main() -> int:
    """Load the desktop application only when the optional GUI stack is present."""
    try:
        main_gui = importlib.import_module("metax.gui.main_gui")
    except ImportError as exc:
        if _is_gui_dependency_import_error(exc):
            print(_missing_gui_message(exc.name), file=sys.stderr)
            return 4
        raise
    return main_gui.runGUI()


if __name__ == "__main__":
    raise SystemExit(main())
