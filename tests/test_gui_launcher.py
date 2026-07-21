from types import SimpleNamespace

import pytest

from metax.gui import launcher


def _raise(error):
    def raise_error(_module_name):
        raise error

    return raise_error


def test_launcher_reports_missing_gui_module(monkeypatch, capsys):
    error = ModuleNotFoundError("No module named 'PyQt5'", name="PyQt5")
    monkeypatch.setattr(launcher.importlib, "import_module", _raise(error))

    assert launcher.main() == 4
    message = capsys.readouterr().err
    assert "Missing module: PyQt5" in message
    assert 'python -m pip install "MetaXTools[gui]"' in message


@pytest.mark.parametrize(
    "error",
    [
        ImportError(
            "libGL.so.1: cannot open shared object file: No such file or directory",
            name="PyQt5.QtCore",
        ),
        ImportError(
            "libGL.so.1: cannot open shared object file: No such file or directory"
        ),
    ],
)
def test_launcher_reports_native_gui_import_error(monkeypatch, capsys, error):
    monkeypatch.setattr(launcher.importlib, "import_module", _raise(error))

    assert launcher.main() == 4
    assert "desktop GUI dependencies" in capsys.readouterr().err


def test_launcher_does_not_mask_internal_import_error(monkeypatch):
    error = ImportError("cannot import name 'broken' from 'metax.internal'")
    monkeypatch.setattr(launcher.importlib, "import_module", _raise(error))

    with pytest.raises(ImportError, match="cannot import name 'broken'"):
        launcher.main()


def test_launcher_runs_gui_when_import_succeeds(monkeypatch):
    main_gui = SimpleNamespace(runGUI=lambda: 0)
    monkeypatch.setattr(
        launcher.importlib,
        "import_module",
        lambda module_name: main_gui,
    )

    assert launcher.main() == 0
