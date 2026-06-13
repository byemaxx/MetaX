from pathlib import Path

from metax.report.config import AutoReportConfig, load_config_from_yaml, save_config_to_yaml
from metax.report.paths import ReportPaths
from metax.report.registry import ResultRegistry


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


def test_cli_function_detection_excludes_taxon(tmp_path: Path):
    from metax.report.cli import _detect_available_function_columns

    otf_path = tmp_path / "otf.tsv"
    otf_path.write_text(
        "Sequence\tTaxon\tTaxon_prop\tGene\tGene_prop\tKEGG_ko_name\tKEGG_ko_name_prop\n"
        "pep1\td__Bacteria\t1\tgeneA\t1\tkoA\t1\n",
        encoding="utf-8",
    )

    assert _detect_available_function_columns(otf_path) == ["Gene", "KEGG_ko_name"]


def test_cli_function_detection_handles_utf8_bom(tmp_path: Path):
    from metax.report.cli import _detect_available_function_columns

    otf_path = tmp_path / "bom_otf.tsv"
    otf_path.write_text(
        "Gene\tGene_prop\tTaxon\tTaxon_prop\n"
        "geneA\t1\td__Bacteria\t1\n",
        encoding="utf-8-sig",
    )

    assert _detect_available_function_columns(otf_path) == ["Gene"]


def test_cli_func_all_excludes_taxon_from_config(tmp_path: Path):
    from metax.report.cli import build_parser, config_from_args

    otf_path = tmp_path / "otf.tsv"
    otf_path.write_text(
        "Sequence\tTaxon\tTaxon_prop\tGene\tGene_prop\n"
        "pep1\td__Bacteria\t1\tgeneA\t1\n",
        encoding="utf-8",
    )

    parser = build_parser()
    args = parser.parse_args(["--otf", str(otf_path), "--out", str(tmp_path / "report"), "--func", "all"])
    config = config_from_args(args, parser)

    assert config.tables.function_columns == ["Gene"]
