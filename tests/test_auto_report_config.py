from pathlib import Path
from types import SimpleNamespace

import matplotlib
import pandas as pd
import pytest

from metax.report.config import AutoReportConfig, load_config_from_yaml, save_config_to_yaml
from metax.report.html_report import HtmlReportBuilder
from metax.report.paths import ReportPaths
from metax.report.plot_builder import PlotBuilder
from metax.report.registry import ResultRegistry
from metax.report.workflow import AutoOTFReport
from metax.report.reproducibility import (
    CONFIG_FILE_NAME,
    PYTHON_SCRIPT_NAME,
    WINDOWS_SCRIPT_NAME,
    save_reproducibility_artifacts,
)


def test_yaml_config_roundtrip(tmp_path: Path):
    config = AutoReportConfig()
    config.input.otf_path = "input.tsv"
    config.input.meta_path = "meta.tsv"
    config.analysis.group_meta = "Group"
    config.report.output_dir = str(tmp_path / "report")

    path = tmp_path / "config.yaml"
    save_config_to_yaml(config, path)
    loaded = load_config_from_yaml(path)

    assert loaded.input.otf_path == "input.tsv"
    assert loaded.input.meta_path == "meta.tsv"
    assert loaded.analysis.group_meta == "Group"
    assert loaded.report.output_dir == str(tmp_path / "report")


def test_auto_report_defaults_match_gui_reuse_plan():
    config = AutoReportConfig()

    assert config.tables.taxa_levels == ["p", "g", "s"]
    assert config.tables.function_columns == "auto"
    assert config.plots.run_pca is True
    assert config.plots.run_correlation is True
    assert config.plots.run_box is True
    assert config.plots.run_bar is True
    assert config.plots.run_alpha_diversity is True
    assert config.plots.run_beta_diversity is True
    assert config.plots.run_treemap is True
    assert config.plots.run_sunburst is True
    assert config.plots.run_sankey is True
    assert config.plots.run_pca_3d is False
    assert config.plots.run_tsne is False
    assert config.plots.run_upset is False
    assert config.plots.run_network is False
    assert config.statistics.diff_method == "limma"
    assert config.report.figure_formats == ["png"]
    assert config.report.dpi == 300


def test_matplotlib_vector_font_settings_preserve_text(tmp_path):
    config = AutoReportConfig()
    builder = PlotBuilder.__new__(PlotBuilder)
    builder.config = config
    figure = matplotlib.figure.Figure()
    builder._save_matplotlib(figure, tmp_path / "font_check.png")
    assert matplotlib.rcParams["pdf.fonttype"] == 42
    assert matplotlib.rcParams["ps.fonttype"] == 42
    assert matplotlib.rcParams["svg.fonttype"] == "none"


def test_matplotlib_saves_configured_vector_formats(tmp_path):
    config = AutoReportConfig()
    config.report.figure_formats = ["png", "pdf", "svg"]
    config.report.dpi = 300
    builder = PlotBuilder.__new__(PlotBuilder)
    builder.config = config

    figure = matplotlib.figure.Figure()
    figure.text(0.5, 0.5, "MetaX")
    output = tmp_path / "figure.png"
    builder._save_matplotlib(figure, output)

    assert output.exists()
    assert output.with_suffix(".pdf").exists()
    assert output.with_suffix(".svg").exists()
    assert "MetaX" in output.with_suffix(".svg").read_text(encoding="utf-8")


def test_nonempty_output_directory_requires_overwrite(tmp_path):
    output = tmp_path / "report"
    output.mkdir()
    (output / "old.txt").write_text("old", encoding="utf-8")
    config = AutoReportConfig()
    config.report.output_dir = str(output)

    with pytest.raises(FileExistsError, match="--overwrite"):
        AutoOTFReport(config)._prepare_output_dir(ReportPaths(output))


def test_unit_aware_summary_counts_units_samples_and_features():
    config = AutoReportConfig()
    context = SimpleNamespace(
        config=config,
        tfa=SimpleNamespace(
            sample_list=["s1", "s2"],
            original_df=pd.DataFrame(
                {
                    "analysis_unit_id": ["u1", "u1", "u2"],
                    "s1": [1.0, 2.0, 0.0],
                    "s2": [0.0, 0.0, 3.0],
                }
            ),
            meta_df=pd.DataFrame(
                {
                    "Sample": ["s1", "s2"],
                    "analysis_unit_id": ["u1", "u2"],
                }
            ),
        ),
    )

    summary = AutoOTFReport(config)._unit_aware_summary(context)

    assert summary["n_analysis_units"] == 2
    assert summary["samples_per_unit"] == {"u1": 1, "u2": 1}
    assert summary["records_per_unit"] == {"u1": 1, "u2": 1}
    assert summary["features_per_unit"] == {"u1": 2, "u2": 1}


def test_unit_aware_summary_does_not_label_metadata_rows_as_features():
    config = AutoReportConfig()
    context = SimpleNamespace(
        config=config,
        tfa=SimpleNamespace(
            sample_list=["s1", "s2", "s3"],
            original_df=pd.DataFrame({"s1": [1.0], "s2": [2.0], "s3": [3.0]}),
            meta_df=pd.DataFrame(
                {
                    "Sample": ["s1", "s2", "s3"],
                    "analysis_unit_id": ["u1", "u1", "u2"],
                }
            ),
        ),
    )

    summary = AutoOTFReport(config)._unit_aware_summary(context)

    assert summary["samples_per_unit"] == {"u1": 2, "u2": 1}
    assert summary["records_per_unit"] == {"u1": 2, "u2": 1}
    assert summary["features_per_unit"] == {}


def test_html_report_paths_are_posix_style_for_windows_relpaths(tmp_path, monkeypatch):
    config = AutoReportConfig()
    paths = ReportPaths(tmp_path / "report")
    paths.create()
    source = paths.taxa_tables_dir / "taxa.tsv"
    source.write_text("feature_id\tvalue\nf1\t1\n", encoding="utf-8")
    context = SimpleNamespace(
        config=config,
        paths=paths,
        logger=SimpleNamespace(warning=lambda *args: None),
    )
    builder = HtmlReportBuilder(context)
    monkeypatch.setattr(
        "metax.report.html_report.os.path.relpath",
        lambda *_args: r"..\..\tables\taxa\taxa.tsv",
    )

    assert builder._relative_path(source) == "../../tables/taxa/taxa.tsv"
    preview = builder._write_table_preview(source, "taxa")
    preview_html = preview.read_text(encoding="utf-8")
    assert 'href="../../tables/taxa/taxa.tsv"' in preview_html
    assert "..\\..\\tables" not in preview_html


def test_report_paths_create_expected_directories(tmp_path: Path):
    paths = ReportPaths(tmp_path / "report")
    paths.create()

    assert paths.output_dir.exists()
    assert paths.taxa_tables_dir.exists()
    assert paths.function_tables_dir.exists()
    assert paths.otf_tables_dir.exists()
    assert paths.qc_tables_dir.exists()
    assert paths.overview_figures_dir.exists()
    assert paths.logs_dir.exists()


def test_result_registry_records_outputs(tmp_path: Path):
    registry = ResultRegistry()
    registry.add_table("table", tmp_path / "table.tsv", title="Table")
    registry.add_figure("figure", tmp_path / "figure.png", figure_type="png")
    registry.add_warning("warning", source="test")

    data = registry.to_dict()
    assert data["tables"][0]["key"] == "table"
    assert data["figures"][0]["figure_type"] == "png"
    assert data["warnings"][0]["message"] == "warning"


def test_reproducibility_artifacts_export_rerunnable_scripts(tmp_path: Path):
    config = AutoReportConfig()
    artifacts = save_reproducibility_artifacts(config, tmp_path)

    python_script = tmp_path / PYTHON_SCRIPT_NAME
    windows_script = tmp_path / WINDOWS_SCRIPT_NAME

    assert artifacts["python_script"] == python_script
    assert artifacts["windows_script"] == windows_script
    assert artifacts["config"] == tmp_path / CONFIG_FILE_NAME
    assert artifacts["config"].exists()
    assert python_script.exists()
    assert windows_script.exists()

    python_text = python_script.read_text(encoding="utf-8")
    assert f'with_name("{CONFIG_FILE_NAME}")' in python_text
    assert "load_config_from_yaml(config_path)" in python_text
    assert "AutoOTFReport(config).run()" in python_text

    windows_text = windows_script.read_text(encoding="utf-8")
    assert "METAX_PYTHON" in windows_text
    assert PYTHON_SCRIPT_NAME in windows_text
