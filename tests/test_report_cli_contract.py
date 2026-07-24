from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from metax.report import cli
from metax.report.registry import ResultRegistry


def test_report_capabilities_contract(capsys) -> None:
    assert cli.main(["--capabilities"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload == {
        "schema_version": "metax.report_capabilities.v1",
        "available": True,
        "metax_version": "2.6.2",
        "workflow_api_version": "1.0",
        "result_schema_version": "metax.report_result.v1",
    }


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
    assert payload["outputs"]["index_html"] == str((output_dir / "index.html").resolve())
    assert payload["summary"] == {
        "tables": 1,
        "statistics": 0,
        "figures": 1,
        "interactive_html": 0,
    }
    assert payload["warnings"][0]["message"] == "A test warning"


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
