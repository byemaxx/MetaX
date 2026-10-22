from pathlib import Path
from types import SimpleNamespace

import pytest

from metax.report.config import AutoReportConfig
from metax.report.paths import ReportPaths
from metax.report.workflow import AutoOTFReport


@pytest.fixture
def report(tmp_path):
    config = AutoReportConfig()
    otf = tmp_path / "input.tsv"
    otf.write_text("Sequence\tIntensity_A\nPEPTIDE\t1\n")
    config.input.otf_path = str(otf)
    config.report.output_dir = str(tmp_path / "report")
    config.report.overwrite = True
    return AutoOTFReport(config)


def test_overwrite_rejects_unowned_directory_and_keeps_user_files(report):
    output = Path(report.config.report.output_dir)
    user_file = output / "tables" / "experiment.tsv"
    user_file.parent.mkdir(parents=True)
    user_file.write_text("user data")
    with pytest.raises(FileExistsError, match="not owned"):
        report.run()
    assert user_file.read_text() == "user data"


def test_overwrite_rejects_different_inputs_and_output_containing_inputs(report):
    output = Path(report.config.report.output_dir)
    report._prepare_output_dir(ReportPaths(output))
    report.config.input.otf_path = str(output.parent / "other.tsv")
    with pytest.raises(FileExistsError, match="not owned"):
        report._prepare_output_dir(ReportPaths(output))
    report.config.input.otf_path = str(output / "input.tsv")
    with pytest.raises(ValueError, match="outside"):
        report._prepare_output_dir(ReportPaths(output))


def test_overwrite_preserves_unrelated_files_in_owned_directory(report):
    output = Path(report.config.report.output_dir)
    report._prepare_output_dir(ReportPaths(output))
    (output / "notes.txt").write_text("user notes")
    with pytest.raises(FileExistsError, match="unrelated"):
        report.run()
    assert (output / "notes.txt").read_text() == "user notes"


@pytest.mark.parametrize("fail", [False, True])
def test_report_replacement_preserves_previous_report_until_success(report, monkeypatch, fail):
    output = Path(report.config.report.output_dir)
    report._prepare_output_dir(ReportPaths(output))
    (output / "index.html").write_text("previous report")

    def generate():
        report._prepare_output_dir(ReportPaths(output))
        (output / "index.html").write_text("new report")
        if fail:
            raise RuntimeError("generation failed")
        return SimpleNamespace(index_html_path=output / "index.html")

    monkeypatch.setattr(report, "_run", generate)
    if fail:
        with pytest.raises(RuntimeError, match="generation failed"):
            report.run()
    else:
        assert report.run().index_html_path == output / "index.html"
    assert (output / "index.html").read_text() == ("previous report" if fail else "new report")
    assert not list(output.parent.glob(".report.previous-*"))


def test_failed_generation_closes_logs_before_restoring_report(report, monkeypatch):
    output = Path(report.config.report.output_dir)
    report._prepare_output_dir(ReportPaths(output))
    (output / "index.html").write_text("previous report")

    def fail():
        raise RuntimeError("analyzer failed")

    monkeypatch.setattr(report, "_init_analyzer", fail)
    with pytest.raises(RuntimeError, match="analyzer failed"):
        report.run()
    assert (output / "index.html").read_text() == "previous report"
    assert not list(output.parent.glob(".report.previous-*"))
