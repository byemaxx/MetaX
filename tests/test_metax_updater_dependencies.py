import textwrap
from pathlib import Path

import pytest

from metax.utils import metax_updater


def _make_updater():
    updater = metax_updater.Updater.__new__(metax_updater.Updater)
    updater.update_log_browser = None
    return updater


def test_dependency_install_disables_script_location_warning(tmp_path, monkeypatch):
    captured = {}

    class FakeProcess:
        stdout = iter(())

        def wait(self):
            return 0

    def fake_popen(command, **kwargs):
        captured["command"] = command
        return FakeProcess()

    monkeypatch.setattr(metax_updater.subprocess, "Popen", fake_popen)

    updater = _make_updater()
    updater.get_downloaded_project_folder_path = lambda: str(tmp_path)

    success, output = updater.install_project_dependencies()

    assert success
    assert output == ""
    assert "--no-warn-script-location" in captured["command"]


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


def test_bundled_runtime_dependency_check_includes_full_profile(tmp_path, monkeypatch):
    (tmp_path / "pyproject.toml").write_text(
        textwrap.dedent(
            """
            [project]
            dependencies = ["numpy>=1.25.1"]

            [project.optional-dependencies]
            full = ["Jinja2>=3.2"]
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / metax_updater.BUNDLED_RUNTIME_MARKER).write_text("{}", encoding="utf-8")

    def fake_version(name):
        if name == "Jinja2":
            raise metax_updater.importlib_metadata.PackageNotFoundError(name)
        return "1.25.1"

    monkeypatch.setattr(metax_updater.importlib_metadata, "version", fake_version)

    updater = _make_updater()
    monkeypatch.setattr(updater, "get_local_project_folder_path", lambda: str(tmp_path))
    success, output = updater.check_project_dependencies(
        str(tmp_path),
        optional_dependency_groups=updater.get_dependency_check_optional_groups(),
    )

    assert not success
    assert "Jinja2: not installed; requires >=3.2" in output


@pytest.mark.parametrize("installed_version", [None, "", "not a version"])
def test_dependency_check_handles_invalid_installed_version_metadata(
    tmp_path, monkeypatch, installed_version
):
    (tmp_path / "requirements.txt").write_text(
        "metaumbra>=1.4.0\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        metax_updater.importlib_metadata,
        "version",
        lambda name: installed_version,
    )

    updater = _make_updater()
    success, output = updater.check_project_dependencies(str(tmp_path))

    assert not success
    assert "metaumbra: installed version metadata is" in output
    assert "requires >=1.4.0" in output


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


def test_bundled_runtime_dependency_change_requires_complete_installer(tmp_path, monkeypatch):
    updater = _make_updater()
    monkeypatch.setattr(updater, "get_local_project_folder_path", lambda: str(tmp_path))
    (tmp_path / metax_updater.BUNDLED_RUNTIME_MARKER).write_text("{}", encoding="utf-8")

    assert updater.bundled_runtime_requires_installer(api_changed=True, dependency_check_success=True)
    assert updater.bundled_runtime_requires_installer(api_changed=False, dependency_check_success=False)
    assert not updater.bundled_runtime_requires_installer(api_changed=False, dependency_check_success=True)


def test_source_install_can_continue_using_pip_for_dependency_change(tmp_path, monkeypatch):
    updater = _make_updater()
    monkeypatch.setattr(updater, "get_local_project_folder_path", lambda: str(tmp_path))

    assert not updater.bundled_runtime_requires_installer(api_changed=True, dependency_check_success=False)


def test_replace_metax_dir_uses_runtime_allowlist_and_preserves_marker(tmp_path, monkeypatch):
    downloaded = tmp_path / "downloaded"
    installed = tmp_path / "installed"
    (downloaded / "metax").mkdir(parents=True)
    (downloaded / "tests").mkdir()
    (installed / "metax").mkdir(parents=True)
    (downloaded / "metax" / "new.py").write_text("new", encoding="utf-8")
    (downloaded / "tests" / "not_runtime.py").write_text("test", encoding="utf-8")
    (downloaded / "README.md").write_text("new readme", encoding="utf-8")
    (installed / "metax" / "old.py").write_text("old", encoding="utf-8")
    marker = installed / metax_updater.BUNDLED_RUNTIME_MARKER
    marker.write_text("{}", encoding="utf-8")

    updater = _make_updater()
    monkeypatch.setattr(updater, "get_downloaded_project_folder_path", lambda: str(downloaded))
    monkeypatch.setattr(updater, "get_local_project_folder_path", lambda: str(installed))

    assert updater.replace_metax_dir()
    assert (installed / "metax" / "new.py").read_text(encoding="utf-8") == "new"
    assert not (installed / "metax" / "old.py").exists()
    assert not (installed / "tests").exists()
    assert marker.is_file()
    assert Path(installed / "README.md").read_text(encoding="utf-8") == "new readme"
