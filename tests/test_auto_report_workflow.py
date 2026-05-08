from pathlib import Path

import pandas as pd

from metax.report import AutoOTFReport, AutoReportConfig


def test_auto_report_runs_on_example_dataset(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    config = AutoReportConfig()
    config.input.otf_path = str(repo_root / "metax" / "data" / "example_data" / "Example_OTF.tsv")
    config.input.meta_path = str(repo_root / "metax" / "data" / "example_data" / "Example_Meta.tsv")
    config.analysis.group_meta = "Sugar_type"
    config.analysis.control_group = "PBS"
    config.report.output_dir = str(tmp_path / "example_report")
    config.report.overwrite = True
    config.plots.run_correlation = False
    config.plots.run_heatmap = False
    config.plots.run_box = False
    config.plots.run_bar = False
    config.plots.run_diversity = False
    config.plots.run_alpha_diversity = False
    config.plots.run_beta_diversity = False
    config.plots.run_treemap = False
    config.plots.run_sunburst = False
    config.plots.run_sankey = False

    result = AutoOTFReport(config).run()

    assert result.index_html_path.exists()
    assert result.summary_json_path.exists()
    assert (result.output_dir / "config_used.yaml").exists()
    for level in ["p", "g", "s"]:
        assert (result.output_dir / "tables" / "taxa" / f"taxa_table_{level}.tsv").exists()
    for function_name in ["KEGG_ko_name", "Gene"]:
        assert (result.output_dir / "tables" / "function" / f"function_table_{function_name}.tsv").exists()
        for level in ["p", "g", "s"]:
            assert (result.output_dir / "tables" / "otf" / f"otf_table_{level}_{function_name}.tsv").exists()
    otf_table = result.output_dir / "tables" / "otf" / "otf_table_s_KEGG_ko_name.tsv"
    assert not pd.read_csv(otf_table, sep="\t").empty
    taxa_anova = result.output_dir / "stats" / "taxa" / "taxa_s_anova.tsv"
    taxa_cho_vs_pbs = result.output_dir / "stats" / "taxa" / "taxa_s_CHO_vs_PBS.tsv"
    taxa_dunnett = result.output_dir / "stats" / "taxa" / "taxa_s_dunnett.tsv"
    pca = result.output_dir / "figures" / "basic" / "pca_taxa_s.png"
    pca_js = result.output_dir / "figures" / "basic" / "pca_taxa_s.html"
    volcano = result.output_dir / "figures" / "differential" / "volcano_taxa_s_CHO_vs_PBS.png"
    volcano_js = result.output_dir / "figures" / "differential" / "volcano_taxa_s_CHO_vs_PBS.html"
    assert taxa_anova.exists()
    assert taxa_dunnett.exists()
    assert taxa_cho_vs_pbs.exists()
    assert pca.exists()
    assert pca_js.exists()
    assert volcano.exists()
    assert volcano_js.exists()
    stats_df = pd.read_csv(taxa_cho_vs_pbs, sep="\t")
    assert {"feature_id", "log2FC", "p_value", "q_value", "significant", "direction"}.issubset(stats_df.columns)
    assert not stats_df.empty
    assert len(result.registry.stats) >= 3
    assert len(result.registry.figures) >= 1


def test_plot_builder_uses_gui_plotters_only():
    source = (Path(__file__).resolve().parents[1] / "metax" / "report" / "plot_builder.py").read_text()

    forbidden_tokens = [
        "from sklearn",
        "import seaborn",
        "import numpy",
        "sns.scatterplot",
        "sns.heatmap",
        "sns.clustermap",
        "sns.boxplot",
        "sns.barplot",
        "PCA(",
        "StandardScaler",
    ]
    for token in forbidden_tokens:
        assert token not in source
