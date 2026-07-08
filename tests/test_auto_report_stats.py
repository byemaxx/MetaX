from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from metax.report import AutoReportConfig
from metax.report.paths import ReportPaths
from metax.report.plot_builder import PlotBuilder
from metax.report.registry import ResultRegistry
from metax.report.stats_builder import StatsBuilder


class _FakeCrossTest:
    def __init__(self):
        self.kwargs = None

    def get_stats_limma_against_control(self, **kwargs):
        self.kwargs = kwargs
        frame = pd.DataFrame(
            {
                "baseMean": [1.5, 3.0],
                "log2FoldChange": [2.0, -1.0],
                "stat": [4.0, -2.0],
                "pvalue": [0.01, 0.1],
                "padj": [0.02, 0.2],
                "A1": [0.0, 2.0],
                "A2": [0.0, 2.0],
                "B1": [4.0, 4.0],
                "B2": [4.0, 4.0],
            },
            index=["all_zero_in_control", "feature_2"],
        )
        return pd.concat({"B": frame}, axis=1)


def _stats_builder(tmp_path: Path):
    config = AutoReportConfig()
    config.analysis.control_group = "A"
    config.statistics.diff_method = "limma"
    paths = ReportPaths(tmp_path)
    paths.create()
    cross_test = _FakeCrossTest()
    tfa = SimpleNamespace(CrossTest=cross_test)
    context = SimpleNamespace(
        config=config,
        tfa=tfa,
        paths=paths,
        registry=ResultRegistry(),
        generated_stats=[],
        logger=SimpleNamespace(info=lambda *args: None),
    )
    return StatsBuilder(context), context, cross_test


def test_limma_group_vs_control_uses_backend_contract(tmp_path):
    builder, context, cross_test = _stats_builder(tmp_path)
    artifact = {
        "key": "taxa_s",
        "title": "Species",
        "df": pd.DataFrame(
            {"A1": [0.0], "A2": [0.0], "B1": [4.0], "B2": [4.0]},
            index=["all_zero_in_control"],
        ),
    }

    builder._run_limma("taxa", artifact, ["A", "B"], "A")

    assert cross_test.kwargs["log2_transform"] is True
    assert cross_test.kwargs["zero_to_nan"] is False
    assert cross_test.kwargs["concat_sample_to_result"] is True
    result = context.generated_stats[0]["df"]
    assert {"feature_id", "log2FoldChange", "pvalue", "padj"}.issubset(result.columns)
    assert "all_zero_in_control" in result["feature_id"].tolist()
    assert context.generated_stats[0]["sample_value_transform"] == "log2(x + 1)"
    assert context.registry.stats[0]["sample_value_transform"] == "log2(x + 1)"
    assert "Appended sample abundance columns contain log2(x + 1)" in context.registry.stats[0]["description"]


def test_volcano_uses_limma_columns_without_legacy_remapping(tmp_path):
    config = AutoReportConfig()
    captured = {}
    builder = PlotBuilder.__new__(PlotBuilder)
    builder.config = config
    builder.volcano_plot = object()
    builder.context = SimpleNamespace(
        paths=SimpleNamespace(differential_figures_dir=tmp_path),
    )
    builder._save_volcano_pair = lambda df, *_args: captured.setdefault("df", df.copy())

    def run_plot(_key, path, action, **_kwargs):
        action(path)

    builder._plot_optional = run_plot
    builder._plot_volcano(
        {
            "key": "taxa_s_B_vs_A",
            "title": "B vs A",
            "df": pd.DataFrame(
                {
                    "feature_id": ["f1"],
                    "log2FoldChange": [1.25],
                    "pvalue": [0.01],
                    "padj": [0.02],
                }
            ),
        }
    )

    assert captured["df"].loc["f1", "log2FoldChange"] == 1.25
    assert captured["df"].loc["f1", "padj"] == 0.02


def test_deseq2_warning_names_the_configured_backend(tmp_path):
    config = AutoReportConfig()
    config.statistics.run_deseq2 = True
    config.statistics.diff_method = "limma"
    context = SimpleNamespace(
        config=config,
        tfa=SimpleNamespace(),
        registry=ResultRegistry(),
        logger=SimpleNamespace(info=lambda *args: None),
    )

    StatsBuilder(context).run_all()

    warning = context.registry.warnings[0]
    assert "not implemented in Auto Report" in warning["message"]
    assert "limma via InMoose" in warning["message"]
