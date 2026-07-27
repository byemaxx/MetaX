from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from metax.cli import report as report_entrypoint
from metax.report import cli
from metax.report.registry import ResultRegistry


def test_report_capabilities_contract(capsys) -> None:
    assert report_entrypoint.main(["--capabilities"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == "metax.report_capabilities.v1"
    assert payload["workflow_api_version"] == "1.0"
    assert payload["result_schema_version"] == "metax.report_result.v1"
    assert payload["available"] is (not payload["missing_dependencies"])
    assert payload["reason"] == ("" if payload["available"] else "MetaX report dependencies are not installed.")


def test_report_capabilities_reports_missing_optional_dependency(monkeypatch) -> None:
    original_find_spec = importlib.util.find_spec

    def find_spec(name: str, package: str | None = None):
        if name == "inmoose":
            return None
        return original_find_spec(name, package)

    monkeypatch.setattr(report_entrypoint.importlib.util, "find_spec", find_spec)

    payload = report_entrypoint.report_capabilities()

    assert payload["available"] is False
    assert "inmoose" in payload["missing_dependencies"]
    assert payload["reason"] == "MetaX report dependencies are not installed."
    assert payload["install_hint"] == 'pip install "MetaXTools[report]"'


def test_report_capabilities_does_not_import_pyqt(monkeypatch) -> None:
    seen: list[str] = []

    def find_spec(name: str, package: str | None = None):
        seen.append(name)
        return object()

    monkeypatch.setattr(report_entrypoint.importlib.util, "find_spec", find_spec)

    assert report_entrypoint.report_capabilities()["available"] is True
    assert all("pyqt" not in name.lower() for name in seen)


def test_report_result_json_contract(tmp_path: Path, monkeypatch) -> None:
    otf_path = tmp_path / "OTF.tsv"
    otf_path.write_text("Sequence\tIntensity_A\nPEPTIDE\t1\n", encoding="utf-8")
    output_dir = tmp_path / "report"
    result_json = tmp_path / "report_result.json"
    registry = ResultRegistry()
    registry.add_table("taxa", output_dir / "tables" / "taxa.tsv")
    registry.add_figure("pca", output_dir / "figures" / "pca.png")
    registry.add_warning("A test warning", "test")
    registry.finish()

    class FakeReport:
        def __init__(self, config) -> None:
            self.config = config

        def run(self):
            output_dir.mkdir()
            index = output_dir / "index.html"
            summary = output_dir / "summary.json"
            config_used = output_dir / "config_used.yaml"
            index.write_text("<html></html>", encoding="utf-8")
            summary.write_text("{}", encoding="utf-8")
            config_used.write_text("input: {}", encoding="utf-8")
            return SimpleNamespace(
                output_dir=output_dir,
                index_html_path=index,
                summary_json_path=summary,
                registry=registry,
                reproducibility_artifacts={"config": config_used},
            )

    monkeypatch.setattr(cli, "AutoOTFReport", FakeReport)

    exit_code = cli.main(
        [
            "--otf",
            str(otf_path),
            "--out",
            str(output_dir),
            "--result-json",
            str(result_json),
        ]
    )

    assert exit_code == 0
    payload = json.loads(result_json.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "metax.report_result.v1"
    assert payload["workflow_api_version"] == "1.0"
    assert payload["status"] == "completed"
    assert payload["inputs"]["otf_table"] == str(otf_path.resolve())
    assert payload["outputs"]["index_html"] == str((output_dir / "index.html").resolve())
    assert payload["summary"] == {
        "tables": 1,
        "statistics": 0,
        "figures": 1,
        "interactive_html": 0,
    }
    assert payload["warnings"][0]["message"] == "A test warning"


def test_report_rejects_missing_index_html(tmp_path: Path, monkeypatch) -> None:
    otf_path = tmp_path / "OTF.tsv"
    otf_path.write_text("Sequence\tIntensity_A\nPEPTIDE\t1\n", encoding="utf-8")
    result_json = tmp_path / "failed.json"
    output_dir = tmp_path / "report"

    class IncompleteReport:
        def __init__(self, config) -> None:
            self.config = config

        def run(self):
            output_dir.mkdir()
            return SimpleNamespace(
                output_dir=output_dir,
                index_html_path=output_dir / "index.html",
                summary_json_path=output_dir / "summary.json",
                registry=ResultRegistry(),
                reproducibility_artifacts={},
            )

    monkeypatch.setattr(cli, "AutoOTFReport", IncompleteReport)

    assert cli.main(
        [
            "--otf",
            str(otf_path),
            "--out",
            str(output_dir),
            "--result-json",
            str(result_json),
        ]
    ) == 1
    payload = json.loads(result_json.read_text(encoding="utf-8"))
    assert payload["status"] == "failed"
    assert "non-empty index.html" in payload["errors"][0]["message"]


def test_report_failure_writes_machine_readable_result(tmp_path: Path, monkeypatch) -> None:
    otf_path = tmp_path / "OTF.tsv"
    otf_path.write_text("Sequence\nPEPTIDE\n", encoding="utf-8")
    result_json = tmp_path / "failed.json"

    class FailingReport:
        def __init__(self, config) -> None:
            self.config = config

        def run(self):
            raise RuntimeError("analysis failed")

    monkeypatch.setattr(cli, "AutoOTFReport", FailingReport)

    exit_code = cli.main(
        [
            "--otf",
            str(otf_path),
            "--out",
            str(tmp_path / "report"),
            "--result-json",
            str(result_json),
        ]
    )

    assert exit_code == 1
    payload = json.loads(result_json.read_text(encoding="utf-8"))
    assert payload["status"] == "failed"
    assert payload["errors"] == [{"message": "analysis failed", "source": "metax-report"}]


def test_report_cancellation_contract(tmp_path: Path, monkeypatch) -> None:
    otf_path = tmp_path / "OTF.tsv"
    otf_path.write_text("Sequence\tIntensity_A\nPEPTIDE\t1\n", encoding="utf-8")
    result_json = tmp_path / "cancelled.json"

    class CancelledReport:
        def __init__(self, config) -> None:
            self.config = config

        def run(self):
            raise KeyboardInterrupt

    monkeypatch.setattr(cli, "AutoOTFReport", CancelledReport)
    assert cli.main(
        [
            "--otf",
            str(otf_path),
            "--out",
            str(tmp_path / "report"),
            "--result-json",
            str(result_json),
        ]
    ) == 130
    payload = json.loads(result_json.read_text(encoding="utf-8"))
    assert payload["status"] == "cancelled"
    assert payload["errors"][0]["source"] == "metax-report"


def test_real_report_cli_contract(tmp_path: Path) -> None:
    fixture_dir = Path(__file__).parent / "fixtures" / "report_contract"
    output_dir = tmp_path / "report output with spaces"
    result_json = tmp_path / "result output" / "metax_report_result.json"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "metax.cli.report",
            "--config",
            str(fixture_dir / "config.yaml"),
            "--otf",
            str(fixture_dir / "OTF.tsv"),
            "--meta",
            str(fixture_dir / "metadata.tsv"),
            "--out",
            str(output_dir),
            "--result-json",
            str(result_json),
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(result_json.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "metax.report_result.v1"
    assert payload["workflow_api_version"].split(".", 1)[0] == "1"
    assert payload["status"] == "completed"
    assert Path(payload["outputs"]["index_html"]).stat().st_size > 0
    assert Path(payload["outputs"]["summary_json"]).is_file()
    assert payload["summary"]["tables"] + payload["summary"]["figures"] >= 1
    assert isinstance(payload["warnings"], list)
    assert isinstance(payload["errors"], list)
    for path in [
        payload["inputs"]["otf_table"],
        payload["inputs"]["metadata_table"],
        payload["outputs"]["output_directory"],
        payload["outputs"]["index_html"],
        payload["outputs"]["summary_json"],
    ]:
        assert Path(path).is_absolute()


def test_report_config_validation_failure_writes_machine_readable_result(
    tmp_path: Path, capsys
) -> None:
    result_json = tmp_path / "invalid_config.json"

    exit_code = cli.main(
        [
            "--otf",
            str(tmp_path / "OTF.tsv"),
            "--result-json",
            str(result_json),
        ]
    )

    assert exit_code == 2
    assert "--out is required unless --config is provided" in capsys.readouterr().err
    payload = json.loads(result_json.read_text(encoding="utf-8"))
    assert payload["status"] == "failed"
    assert payload["errors"] == [
        {
            "message": "--out is required unless --config is provided.",
            "source": "metax-report",
        }
    ]


def test_report_argument_validation_failure_writes_machine_readable_result(
    tmp_path: Path, capsys
) -> None:
    result_json = tmp_path / "invalid_argument.json"

    exit_code = cli.main(
        [
            "--diff-method",
            "invalid",
            "--result-json",
            str(result_json),
        ]
    )

    assert exit_code == 2
    assert "invalid choice" in capsys.readouterr().err
    payload = json.loads(result_json.read_text(encoding="utf-8"))
    assert payload["status"] == "failed"
    assert "invalid choice" in payload["errors"][0]["message"]
