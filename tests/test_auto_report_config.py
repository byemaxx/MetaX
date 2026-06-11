from pathlib import Path

from metax.report.config import AutoReportConfig, load_config_from_yaml, save_config_to_yaml
from metax.report.paths import ReportPaths
from metax.report.registry import ResultRegistry
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
