import textwrap

import pytest

from metax.utils import metax_updater


def _make_updater():
    updater = metax_updater.Updater.__new__(metax_updater.Updater)
    updater.update_log_browser = None
    return updater


def test_dependency_check_detects_installed_version_below_minimum(tmp_path, monkeypatch):
    (tmp_path / "pyproject.toml").write_text(
        textwrap.dedent(
            """
            [project]
            dependencies = [
                "numpy>=1.25.1",
                "metaumbra[gui-pyqt5]>=1.3.3",
                "qt-material==2.14",
            ]
            """
        ),
        encoding="utf-8",
    )

    installed_versions = {
        "numpy": "1.25.1",
        "metaumbra": "1.3.2",
        "qt-material": "2.14",
    }
    monkeypatch.setattr(
        metax_updater.importlib_metadata,
        "version",
        lambda name: installed_versions[name],
    )

    updater = _make_updater()
    success, output = updater.check_project_dependencies(str(tmp_path))

    assert not success
    assert "metaumbra: installed 1.3.2; requires >=1.3.3" in output
    assert "numpy" not in output
    assert "qt-material" not in output


def test_dependency_check_detects_missing_requirement(tmp_path, monkeypatch):
    (tmp_path / "requirements.txt").write_text(
        "PyQt5>=5.15.9\nopenpyxl\n",
        encoding="utf-8",
    )

    def fake_version(name):
        if name == "PyQt5":
            raise metax_updater.importlib_metadata.PackageNotFoundError(name)
        return "3.1.5"

    monkeypatch.setattr(metax_updater.importlib_metadata, "version", fake_version)

    updater = _make_updater()
    success, output = updater.check_project_dependencies(str(tmp_path))

    assert not success
    assert "PyQt5: not installed; requires >=5.15.9" in output
    assert "openpyxl" not in output


@pytest.mark.parametrize(
    "requirement",
    [
        "numpy>=1.25.1; python_version < '3.0'",
        "pandas>=2.0.3; sys_platform == 'never'",
    ],
)
def test_dependency_check_ignores_non_matching_markers(tmp_path, monkeypatch, requirement):
    (tmp_path / "requirements.txt").write_text(requirement, encoding="utf-8")
    monkeypatch.setattr(
        metax_updater.importlib_metadata,
        "version",
        lambda name: (_ for _ in ()).throw(AssertionError(f"unexpected lookup: {name}")),
    )

    updater = _make_updater()
    success, output = updater.check_project_dependencies(str(tmp_path))

    assert success
    assert output == ""
