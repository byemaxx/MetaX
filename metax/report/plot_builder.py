from __future__ import annotations

import importlib
import math
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Iterator

_mpl_config_dir = Path(tempfile.gettempdir()) / "metax_matplotlib"
_mpl_config_dir.mkdir(parents=True, exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(_mpl_config_dir)

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import pandas as pd

from .table_builder import safe_filename

if TYPE_CHECKING:
    from .workflow import ReportContext


class PlotBuilder:
    """Thin orchestration layer around the plotters used by the MetaX GUI."""

    def __init__(self, context: "ReportContext"):
        self.context = context
        self.config = context.config
        self.tfa = context.tfa
        self._ensure_gui_group()
        self.basic_plot = self._plotter("metax.taxafunc_ploter.basic_plot", "BasicPlot", self.tfa)
        self.pca_3d_plot = self._plotter("metax.taxafunc_ploter.pca_plot_js", "PcaPlot_js", self.tfa)
        self.bar_plot = self._plotter("metax.taxafunc_ploter.bar_plot_js", "BarPlot", self.tfa)
        self.diversity_plot = self._plotter("metax.taxafunc_ploter.diversity_plot", "DiversityPlot", self.tfa)
        self.heatmap_plot = self._plotter("metax.taxafunc_ploter.heatmap_plot", "HeatmapPlot", self.tfa)
        self.network_plot = self._plotter("metax.taxafunc_ploter.network_plot", "NetworkPlot", self.tfa)
        self.sankey_plot = self._plotter("metax.taxafunc_ploter.sankey_plot", "SankeyPlot", self.tfa)
        self.sunburst_plot = self._plotter("metax.taxafunc_ploter.sunburst_plot", "SunburstPlot")
        self.treemap_plot = self._plotter("metax.taxafunc_ploter.treemap_plot", "TreeMapPlot")
        self.volcano_plot = self._plotter("metax.taxafunc_ploter.volcano_plot", "VolcanoPlot")
        self.volcano_plot_js = self._plotter("metax.taxafunc_ploter.volcano_plot_js", "VolcanoPlotJS")

    def plot_all(self) -> None:
        if self.config.plots.run_overview:
            self.context.logger.info("Generating GUI overview plots")
            self.plot_overview_gui()
        self.context.logger.info("Generating GUI basic plots")
        self.plot_basic_gui()
        self.context.logger.info("Generating GUI differential plots")
        self.plot_differential_gui()
        self.context.logger.info("Skipping standalone taxa-function link plots because OTF plots are shown under Basic Plot")

    def plot_overview_gui(self) -> None:
        if self.basic_plot is None:
            return
        self._plot_optional(
            "taxa_stats_pie",
            self.context.paths.overview_figures_dir / "taxa_stats_pie.png",
            lambda path: self._save_matplotlib(self.basic_plot.plot_taxa_stats_pie(theme="Auto", res_type="pic"), path),
            title="Taxonomic assignment coverage",
            description="GUI BasicPlot.plot_taxa_stats_pie overview.",
            figure_type="overview",
        )
        self._plot_optional(
            "taxa_number_bar",
            self.context.paths.overview_figures_dir / "taxa_number_bar.png",
            lambda path: self._save_matplotlib(
                self.basic_plot.plot_taxa_number(
                    theme="Auto",
                    peptide_num=self.config.preprocessing.taxa_peptide_num_threshold,
                    res_type="pic",
                ),
                path,
            ),
            title="Detected taxa by level",
            description="GUI BasicPlot.plot_taxa_number overview.",
            figure_type="overview",
        )
        for func_name in self.context.function_columns:
            safe_name = safe_filename(func_name)
            self._plot_optional(
                f"function_proportion_{safe_name}",
                self.context.paths.overview_figures_dir / f"function_proportion_{safe_name}.png",
                lambda path, func_name=func_name: self._save_matplotlib(
                    self.basic_plot.plot_prop_stats(func_name=func_name, res_type="pic"),
                    path,
                ),
                title=f"Function annotation coverage - {func_name}",
                description=f"GUI BasicPlot.plot_prop_stats overview for {func_name}.",
                figure_type="overview",
            )

    def plot_basic_gui(self) -> None:
        for table_type in ["taxa", "function", "otf"]:
            for artifact in self.context.generated_tables.get(table_type, []):
                matrix = self._matrix_from_table(artifact["df"])
                if matrix is None or matrix.empty:
                    self.context.registry.add_warning(
                        f"No numeric sample matrix available for [{artifact['title']}]. GUI Basic Plot outputs were skipped.",
                        "PlotBuilder",
                        details=self._artifact_warning_details(
                            artifact,
                            {
                                "step": "basic plots",
                                "reason": "no numeric sample columns after table generation",
                            },
                        ),
                    )
                    continue
                slug = safe_filename(artifact["key"])
                title = artifact["title"]
                top_matrix = self._top_features(matrix, self.config.plots.top_n)
                log_matrix = self._log2_matrix(matrix)
                log_top_matrix = self._top_features(log_matrix, self.config.plots.top_n)

                self._plot_pca_family(slug, title, log_matrix)
                self._plot_distribution_family(slug, title, log_matrix, log_top_matrix, top_matrix)
                self._plot_diversity_family(slug, title, artifact)
                self._plot_taxa_composition_family(slug, title, artifact)

    def plot_differential_gui(self) -> None:
        for stat in self.context.generated_stats:
            analysis = stat.get("analysis")
            if analysis in {"anova", "ttest"}:
                self._plot_test_heatmap(stat)
            elif analysis == "dunnett_all":
                self._plot_dunnett_heatmap(stat)
            elif analysis == "group_vs_control":
                self._plot_volcano(stat)

    def plot_taxa_function_gui(self) -> None:
        for artifact in self.context.generated_tables.get("otf", []):
            matrix = self._matrix_from_table(artifact["df"])
            if matrix is None or matrix.empty:
                continue
            top_matrix = self._top_features(matrix, self.config.plots.network_top_n)
            slug = safe_filename(artifact["key"])
            title = artifact["title"]

            if self.config.plots.run_heatmap and self.heatmap_plot is not None:
                self._plot_optional(
                    f"tf_link_heatmap_{slug}",
                    self.context.paths.taxa_function_figures_dir / f"tf_link_heatmap_{slug}.png",
                    lambda path, top_matrix=top_matrix, title=title: self._save_matplotlib(
                        self.heatmap_plot.plot_basic_heatmap(
                            df=top_matrix.copy(),
                            title=f"Taxa-function link heatmap - {title}",
                            fig_size=(14, 12),
                            scale="row",
                            rename_taxa=True,
                            font_size=8,
                            show_all_labels=(top_matrix.shape[1] <= 30, top_matrix.shape[0] <= 50),
                            linecolor="none",
                            linewidths=0,
                        ),
                        path,
                    ),
                    title=f"Taxa-function heatmap - {title}",
                    description="GUI HeatmapPlot.plot_basic_heatmap on top taxa-function links.",
                    figure_type="taxa_function",
                )
            if self.config.plots.run_bar and self.bar_plot is not None:
                self._plot_optional(
                    f"tf_link_bar_{slug}",
                    self.context.paths.taxa_function_figures_dir / f"tf_link_bar_{slug}.html",
                    lambda path, top_matrix=top_matrix, title=title: self._save_pyecharts(
                        self.bar_plot.plot_intensity_bar_js(
                            df=top_matrix.copy(),
                            width=1100,
                            height=700,
                            title=f"Taxa-function link intensity - {title}",
                            rename_taxa=True,
                            show_legend=True,
                            font_size=9,
                            rename_sample=False,
                            plot_mean=True,
                            plot_percent=False,
                            sub_meta="None",
                        ),
                        path,
                    ),
                    title=f"Taxa-function bar - {title}",
                    description="GUI BarPlot.plot_intensity_bar_js on top taxa-function links.",
                    figure_type="taxa_function",
                )
            if self.config.plots.run_sankey and self.sankey_plot is not None:
                self._plot_optional(
                    f"tf_link_sankey_{slug}",
                    self.context.paths.taxa_function_figures_dir / f"tf_link_sankey_{slug}.html",
                    lambda path, top_matrix=top_matrix, title=title: self._save_pyecharts(
                        self.sankey_plot.plot_intensity_sankey(
                            df=top_matrix.copy(),
                            width=11,
                            height=7,
                            title=f"Taxa-function sankey - {title}",
                            font_size=10,
                            show_legend=True,
                            sub_meta="None",
                            plot_mean=True,
                        ),
                        path,
                    ),
                    title=f"Taxa-function Sankey - {title}",
                    description="GUI SankeyPlot.plot_intensity_sankey on top taxa-function links.",
                    figure_type="taxa_function",
                )
            if self.config.plots.run_network and self.network_plot is not None:
                self._plot_optional(
                    f"tf_link_network_{slug}",
                    self.context.paths.taxa_function_figures_dir / f"tf_link_network_{slug}.html",
                    lambda path, artifact=artifact, top_matrix=top_matrix: self._plot_network(artifact, top_matrix, path),
                    title=f"Taxa-function network - {title}",
                    description="GUI NetworkPlot.plot_tflink_network on top taxa-function links.",
                    figure_type="taxa_function",
                )

    def _plot_pca_family(self, slug: str, title: str, matrix: pd.DataFrame) -> None:
        if self.config.plots.run_pca and self.basic_plot is not None:
            html_path = self.context.paths.basic_figures_dir / f"pca_{slug}.html"
            has_js_version = self.pca_3d_plot is not None and min(matrix.shape[0], matrix.shape[1]) >= 3
            self._plot_optional(
                f"pca_{slug}",
                self.context.paths.basic_figures_dir / f"pca_{slug}.png",
                lambda path, matrix=matrix, title=title, html_path=html_path, has_js_version=has_js_version: self._save_pca_pair(
                    matrix,
                    path,
                    html_path if has_js_version else None,
                    title,
                ),
                title=f"PCA - {title}",
                description="GUI BasicPlot.plot_pca_sns on log2-transformed abundance; JS version uses GUI PcaPlot_js.plot_pca_pyecharts_3d.",
                figure_type="basic_pca",
                alternate_interactive_path=str(html_path) if has_js_version else None,
                alternate_interactive_title=f"Interactive PCA - {title}" if has_js_version else None,
            )
        if self.config.plots.run_pca_3d and self.pca_3d_plot is not None:
            if min(matrix.shape[0], matrix.shape[1]) < 3:
                self.context.registry.add_warning(
                    f"3D PCA skipped for [{title}] because at least 3 samples and features are required.",
                    "PlotBuilder",
                    details={
                        "plot": "3D PCA",
                        "table": title,
                        "features": matrix.shape[0],
                        "samples": matrix.shape[1],
                        "required": "at least 3 features and 3 samples",
                    },
                )
            else:
                self._plot_optional(
                    f"pca_3d_{slug}",
                    self.context.paths.basic_figures_dir / f"pca_3d_{slug}.html",
                    lambda path, matrix=matrix, title=title: self._save_pyecharts(
                        self.pca_3d_plot.plot_pca_pyecharts_3d(
                            df=matrix.copy(),
                            title_name=title,
                            show_label=matrix.shape[1] <= 30,
                            rename_sample=True,
                            width=10,
                            height=7,
                            font_size=9,
                            legend_col_num=None,
                        ),
                        path,
                    ),
                    title=f"3D PCA - {title}",
                    description="GUI PcaPlot_js.plot_pca_pyecharts_3d.",
                    figure_type="basic_pca_3d",
                )
        if self.config.plots.run_tsne and self.basic_plot is not None:
            self._plot_optional(
                f"tsne_{slug}",
                self.context.paths.basic_figures_dir / f"tsne_{slug}.png",
                lambda path, matrix=matrix, title=title: self._save_matplotlib(
                    self.basic_plot.plot_tsne_sns(
                        df=matrix.copy(),
                        title_name=title,
                        show_label=matrix.shape[1] <= 30,
                        perplexity=max(2, min(30, matrix.shape[1] // 3)),
                        width=8,
                        height=6,
                        font_size=9,
                        rename_sample=True,
                        theme="Auto",
                        legend_col_num=None,
                    ),
                    path,
                ),
                title=f"t-SNE - {title}",
                description="GUI BasicPlot.plot_tsne_sns.",
                figure_type="basic_tsne",
            )

    def _plot_distribution_family(
        self,
        slug: str,
        title: str,
        matrix: pd.DataFrame,
        top_matrix: pd.DataFrame,
        raw_top_matrix: pd.DataFrame,
    ) -> None:
        if self.config.plots.run_correlation and self.basic_plot is not None:
            self._plot_optional(
                f"sample_correlation_{slug}",
                self.context.paths.basic_figures_dir / f"sample_correlation_{slug}.png",
                lambda path, matrix=matrix, title=title: self._save_matplotlib(
                    self.basic_plot.plot_corr_sns(
                        df=matrix.copy(),
                        title_name=title,
                        cluster=True,
                        width=9,
                        height=8,
                        font_size=8,
                        show_all_labels=(matrix.shape[1] <= 30, matrix.shape[1] <= 30),
                        theme="Auto",
                        corr_method="pearson",
                        rename_sample=True,
                    ),
                    path,
                ),
                title=f"Correlation Heatmap - {title}",
                description="GUI BasicPlot.plot_corr_sns.",
                figure_type="basic_correlation",
            )
        if self.config.plots.run_heatmap and self.heatmap_plot is not None:
            self._plot_optional(
                f"top_feature_heatmap_{slug}",
                self.context.paths.basic_figures_dir / f"top_feature_heatmap_{slug}.png",
                lambda path, top_matrix=top_matrix, title=title: self._save_matplotlib(
                    self.heatmap_plot.plot_basic_heatmap(
                        df=top_matrix.copy(),
                        title=f"Top feature heatmap - {title}",
                        fig_size=(14, 12),
                        scale="row",
                        rename_taxa=True,
                        font_size=8,
                        show_all_labels=(top_matrix.shape[1] <= 30, top_matrix.shape[0] <= 50),
                        linecolor="none",
                        linewidths=0,
                    ),
                    path,
                ),
                title=f"Heatmap - {title}",
                description="GUI HeatmapPlot.plot_basic_heatmap on top features.",
                figure_type="basic_heatmap",
            )
        if self.config.plots.run_box and self.basic_plot is not None:
            self._plot_optional(
                f"boxplot_{slug}",
                self.context.paths.basic_figures_dir / f"boxplot_{slug}.png",
                lambda path, matrix=matrix, title=title: self._save_matplotlib(
                    self.basic_plot.plot_box_sns(
                        df=matrix.copy(),
                        title_name=title,
                        show_fliers=False,
                        width=9,
                        height=6,
                        font_size=8,
                        theme="Auto",
                        rename_sample=False,
                        plot_samples=False,
                        legend_col_num=None,
                        sub_meta="None",
                    ),
                    path,
                ),
                title=f"Box - {title}",
                description="GUI BasicPlot.plot_box_sns.",
                figure_type="basic_box",
            )
        if self.config.plots.run_bar and self.bar_plot is not None:
            html_path = self.context.paths.basic_figures_dir / f"bar_{slug}.html"
            self._plot_optional(
                f"bar_{slug}",
                self.context.paths.basic_figures_dir / f"bar_{slug}.png",
                lambda path, top_matrix=raw_top_matrix, title=title, html_path=html_path: self._save_bar_pair(top_matrix, path, html_path, title),
                title=f"Bar - {title}",
                description="GUI BarPlot.plot_intensity_bar_sns static top-20 per-sample view with GUI BarPlot.plot_intensity_bar_js interactive version.",
                figure_type="basic_bar",
                alternate_interactive_path=str(html_path),
                alternate_interactive_title=f"Interactive Bar - {title}",
            )
        if self.config.plots.run_upset and self.basic_plot is not None:
            self._plot_optional(
                f"upset_{slug}",
                self.context.paths.basic_figures_dir / f"upset_{slug}.png",
                lambda path, top_matrix=top_matrix, title=title: self._plot_upset(top_matrix.copy(), title, path),
                title=f"UpSet - {title}",
                description="GUI BasicPlot.plot_upset.",
                figure_type="basic_upset",
            )

    def _plot_diversity_family(self, slug: str, title: str, artifact: dict) -> None:
        if artifact.get("table_type") != "taxa" or self.diversity_plot is None:
            return
        gui_df_type = self._gui_df_type(artifact)
        with self._activate_gui_table(artifact):
            if self.config.plots.run_diversity and self.config.plots.run_alpha_diversity:
                self._plot_optional(
                    f"alpha_diversity_{slug}",
                    self.context.paths.basic_figures_dir / f"alpha_diversity_{slug}.png",
                    lambda path, title=title, gui_df_type=gui_df_type: self._save_matplotlib(
                        self.diversity_plot.plot_alpha_diversity(
                            metric="shannon",
                            sample_list=self.tfa.sample_list,
                            width=8,
                            height=6,
                            font_size=8,
                            plot_all_samples=False,
                            theme="Auto",
                            sub_meta="None",
                            df_type=gui_df_type,
                            title_name=title,
                        )[0],
                        path,
                    ),
                    title=f"Alpha Diversity - {title}",
                    description="GUI DiversityPlot.plot_alpha_diversity.",
                    figure_type="basic_alpha_diversity",
                )
            if self.config.plots.run_diversity and self.config.plots.run_beta_diversity:
                self._plot_optional(
                    f"beta_diversity_{slug}",
                    self.context.paths.basic_figures_dir / f"beta_diversity_{slug}.png",
                    lambda path, title=title, gui_df_type=gui_df_type: self._save_matplotlib(
                        self.diversity_plot.plot_beta_diversity(
                            metric="braycurtis",
                            sample_list=self.tfa.sample_list,
                            width=8,
                            height=6,
                            font_size=8,
                            show_label=False,
                            rename_sample=False,
                            theme="Auto",
                            sub_meta="None",
                            df_type=gui_df_type,
                            title_name=title,
                        )[0],
                        path,
                    ),
                    title=f"Beta Diversity - {title}",
                    description="GUI DiversityPlot.plot_beta_diversity.",
                    figure_type="basic_beta_diversity",
                )

    def _plot_taxa_composition_family(self, slug: str, title: str, artifact: dict) -> None:
        if artifact.get("table_type") != "taxa":
            return
        matrix = self._matrix_from_table(artifact["df"])
        if matrix is None or matrix.empty:
            return
        top_matrix = self._top_features(matrix, self.config.plots.top_n)
        if self.config.plots.run_treemap and self.treemap_plot is not None:
            self._plot_optional(
                f"treemap_{slug}",
                self.context.paths.composition_figures_dir / f"treemap_{slug}.html",
                lambda path, matrix=top_matrix, title=title: self._save_pyecharts(
                    self.treemap_plot.create_treemap_chart(
                        taxa_df=matrix.copy(),
                        width=10,
                        height=7,
                        title=f"TreeMap - {title}",
                        show_sub_title=False,
                        font_size=8,
                    ),
                    path,
                ),
                title=f"TreeMap - {title}",
                description="GUI TreeMapPlot.create_treemap_chart.",
                figure_type="basic_treemap",
            )
        if self.config.plots.run_sunburst and self.sunburst_plot is not None:
            self._plot_optional(
                f"sunburst_{slug}",
                self.context.paths.composition_figures_dir / f"sunburst_{slug}.html",
                lambda path, matrix=top_matrix, title=title: self._save_pyecharts(
                    self.sunburst_plot.create_sunburst_chart(
                        taxa_df=matrix.copy(),
                        width=10,
                        height=7,
                        title=f"Sunburst - {title}",
                        show_label="all",
                        label_font_size=8,
                    ),
                    path,
                ),
                title=f"Sunburst - {title}",
                description="GUI SunburstPlot.create_sunburst_chart.",
                figure_type="basic_sunburst",
            )
        if self.config.plots.run_sankey and self.sankey_plot is not None:
            self._plot_optional(
                f"sankey_{slug}",
                self.context.paths.composition_figures_dir / f"sankey_{slug}.html",
                lambda path, matrix=top_matrix, title=title: self._save_pyecharts(
                    self.sankey_plot.plot_intensity_sankey(
                        df=matrix.copy(),
                        width=11,
                        height=7,
                        title=f"Sankey - {title}",
                        font_size=10,
                        show_legend=True,
                        sub_meta="None",
                        plot_mean=True,
                    ),
                    path,
                ),
                title=f"Sankey - {title}",
                description="GUI SankeyPlot.plot_intensity_sankey.",
                figure_type="basic_sankey",
            )

    def _plot_test_heatmap(self, stat: dict) -> None:
        if self.heatmap_plot is None or not self.config.plots.run_heatmap:
            return
        slug = safe_filename(stat["key"])
        self._plot_optional(
            f"differential_heatmap_{slug}",
            self.context.paths.differential_figures_dir / f"differential_heatmap_{slug}.png",
            lambda path, stat=stat: self._save_matplotlib(
                self.heatmap_plot.plot_basic_heatmap_of_test_res(
                    df=stat["df"].copy(),
                    top_number=self.config.plots.heatmap_top_n,
                    value_type="pvalue",
                    fig_size=self._differential_heatmap_fig_size(stat["df"]),
                    pvalue=self.config.statistics.alpha,
                    scale="row",
                    rename_taxa=True,
                    font_size=8,
                    show_all_labels=(False, True),
                    sort_by="padj",
                    p_type="padj",
                    linecolor="none",
                ),
                path,
            ),
            title=f"Differential heatmap - {stat['title']}",
            description="GUI HeatmapPlot.plot_basic_heatmap_of_test_res.",
            figure_type="differential_heatmap",
        )

    def _plot_dunnett_heatmap(self, stat: dict) -> None:
        if self.heatmap_plot is None or not self.config.plots.run_heatmap:
            return
        slug = safe_filename(stat["key"])
        self._plot_optional(
            f"dunnett_heatmap_{slug}",
            self.context.paths.differential_figures_dir / f"dunnett_heatmap_{slug}.png",
            lambda path, stat=stat: self._save_matplotlib(
                self.heatmap_plot.plot_heatmap_of_dunnett_test_res(
                    df=stat["df"].copy(),
                    pvalue=self.config.statistics.alpha,
                    scale=None,
                    fig_size=self._differential_heatmap_fig_size(stat["df"]),
                    rename_taxa=True,
                    font_size=8,
                    show_all_labels=(False, True),
                    p_type="padj",
                    linecolor="none",
                ),
                path,
            ),
            title=f"Dunnett heatmap - {stat['title']}",
            description="GUI HeatmapPlot.plot_heatmap_of_dunnett_test_res.",
            figure_type="differential_heatmap",
        )

    def _plot_volcano(self, stat: dict) -> None:
        if self.volcano_plot is None or not self.config.plots.run_volcano:
            return
        volcano_df = stat["df"].copy()
        if "feature_id" in volcano_df.columns:
            volcano_df = volcano_df.set_index("feature_id")
        volcano_df["log2FoldChange"] = pd.to_numeric(volcano_df.get("log2FC"), errors="coerce")
        volcano_df["pvalue"] = pd.to_numeric(volcano_df.get("p_value"), errors="coerce")
        volcano_df["padj"] = pd.to_numeric(volcano_df.get("q_value"), errors="coerce").fillna(volcano_df["pvalue"])
        slug = safe_filename(stat["key"])
        html_path = self.context.paths.differential_figures_dir / f"volcano_{slug}.html"
        self._plot_optional(
            f"volcano_{slug}",
            self.context.paths.differential_figures_dir / f"volcano_{slug}.png",
            lambda path, volcano_df=volcano_df, stat=stat, html_path=html_path: self._save_volcano_pair(volcano_df, path, html_path, stat["title"]),
            title=f"Volcano - {stat['title']}",
            description="GUI VolcanoPlot.plot_volcano static view with GUI VolcanoPlotJS.plot_volcano_js interactive version.",
            figure_type="differential_volcano",
            alternate_interactive_path=str(html_path),
            alternate_interactive_title=f"Interactive Volcano - {stat['title']}",
        )

    def _save_volcano_pair(self, volcano_df: pd.DataFrame, png_path: Path, html_path: Path, title: str) -> None:
        self._save_matplotlib(
            self.volcano_plot.plot_volcano(
                df_fc=volcano_df.copy(),
                pvalue=self.config.statistics.alpha,
                p_type="padj",
                log2fc_min=self.config.statistics.log2fc_cutoff,
                title_name=title,
                font_size=10,
                width=10,
                height=7,
                dot_size=6,
                theme="Auto",
            ),
            png_path,
        )
        if self.volcano_plot_js is not None:
            self._save_pyecharts(
                self.volcano_plot_js.plot_volcano_js(
                    df_fc=volcano_df.copy(),
                    pvalue=self.config.statistics.alpha,
                    p_type="padj",
                    log2fc_min=self.config.statistics.log2fc_cutoff,
                    title_name=title,
                    font_size=10,
                    width=10,
                    height=7,
                    dot_size=6,
                ),
                html_path,
            )

    def _save_pca_pair(self, matrix: pd.DataFrame, png_path: Path, html_path: Path | None, title: str) -> None:
        self._save_matplotlib(
            self.basic_plot.plot_pca_sns(
                df=matrix.copy(),
                title_name=title,
                show_label=matrix.shape[1] <= 30,
                width=8,
                height=6,
                font_size=9,
                rename_sample=True,
                theme="Auto",
                legend_col_num=None,
            ),
            png_path,
        )
        if html_path is not None and self.pca_3d_plot is not None:
            self._save_pyecharts(
                self.pca_3d_plot.plot_pca_pyecharts_3d(
                    df=matrix.copy(),
                    title_name=title,
                    show_label=matrix.shape[1] <= 30,
                    rename_sample=True,
                    width=10,
                    height=7,
                    font_size=9,
                    legend_col_num=None,
                ),
                html_path,
            )

    def _save_bar_pair(self, matrix: pd.DataFrame, png_path: Path, html_path: Path, title: str) -> None:
        static_width = max(12, min(24, matrix.shape[1] * 0.08))
        self._save_matplotlib(
            self.bar_plot.plot_intensity_bar_sns(
                df=matrix.copy(),
                width=static_width,
                height=8,
                title=f"Top 20 intensity bar - {title}",
                rename_taxa=True,
                show_legend=True,
                font_size=8,
                rename_sample=True,
                plot_mean=False,
                plot_percent=False,
                sub_meta="None",
                plt_theme="Auto",
            ),
            png_path,
        )
        self._save_pyecharts(
            self.bar_plot.plot_intensity_bar_js(
                df=matrix.copy(),
                width=1200,
                height=800,
                title=f"Top 20 intensity bar - {title}",
                rename_taxa=True,
                show_legend=True,
                font_size=9,
                rename_sample=True,
                plot_mean=False,
                plot_percent=False,
                sub_meta="None",
                show_all_labels=(False, False),
            ),
            html_path,
        )

    def _plot_upset(self, matrix: pd.DataFrame, title: str, path: Path) -> None:
        self.basic_plot.plot_upset(
            df=matrix,
            title_name=title,
            width=12,
            height=6,
            font_size=9,
            plot_sample=False,
            sub_meta="None",
            show_label=True,
            rename_sample=False,
        )
        self._save_matplotlib(plt.gcf(), path)

    def _plot_network(self, artifact: dict, top_matrix: pd.DataFrame, path: Path) -> None:
        with self._activate_gui_table(artifact, df_override=top_matrix):
            chart, _, _ = self.network_plot.plot_tflink_network(
                sample_list=list(top_matrix.columns),
                width=11,
                height=7,
                focus_list=[],
                plot_list_only=False,
            )
            self._save_pyecharts(chart, path)

    def _plotter(self, module_name: str, class_name: str, *args: Any, **kwargs: Any) -> Any | None:
        try:
            module = importlib.import_module(module_name)
            plotter_cls = getattr(module, class_name)
            return plotter_cls(*args, **kwargs)
        except Exception as exc:
            self.context.registry.add_warning(
                f"GUI plotter [{class_name}] is unavailable and related plots will be skipped: {exc}",
                "PlotBuilder",
                details={
                    "module": module_name,
                    "class": class_name,
                    "error": str(exc),
                },
            )
            return None

    def _plot_optional(
        self,
        key: str,
        path: Path,
        action: Callable[[Path], None],
        title: str,
        description: str,
        figure_type: str,
        **metadata: Any,
    ) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            action(path)
            self.context.registry.add_figure(key, path, title=title, description=description, figure_type=figure_type, **metadata)
            self.context.logger.info("Generated figure: %s", path)
        except Exception as exc:
            self.context.logger.exception("Optional GUI plot failed: %s", key)
            self.context.registry.add_warning(
                f"Optional GUI plot [{title}] failed: {exc}",
                "PlotBuilder",
                details=self._plot_warning_details(key, path, title, figure_type, metadata, exc),
            )
        finally:
            plt.close("all")

    def _plot_warning_details(
        self,
        key: str,
        path: Path,
        title: str,
        figure_type: str,
        metadata: dict[str, Any],
        exc: Exception,
    ) -> dict[str, Any]:
        details: dict[str, Any] = {
            "plot_key": key,
            "plot_title": title,
            "figure_type": figure_type,
            "output_path": str(path),
            "error": str(exc),
            "top_n": self.config.plots.top_n,
            "heatmap_top_n": self.config.plots.heatmap_top_n,
        }
        details.update({name: value for name, value in metadata.items() if value is not None})
        for level in self.context.taxa_levels:
            if f"_taxa_{level}" in key or f"_{level}_" in key:
                details.setdefault("taxa_level", level)
                break
        for function_name in self.context.function_columns:
            safe_name = safe_filename(function_name)
            if safe_name in key or function_name in title:
                details.setdefault("function_column", function_name)
                break
        return details

    def _artifact_warning_details(self, artifact: dict[str, Any], extra: dict[str, Any] | None = None) -> dict[str, Any]:
        details: dict[str, Any] = {
            "table_key": artifact.get("key"),
            "table_title": artifact.get("title"),
            "table_type": artifact.get("table_type"),
            "taxa_level": artifact.get("taxa_level"),
            "function_column": artifact.get("function_column"),
            "rows": artifact.get("df").shape[0] if hasattr(artifact.get("df"), "shape") else None,
        }
        if extra:
            details.update(extra)
        return {key: value for key, value in details.items() if value is not None and value != ""}

    def _save_matplotlib(self, plot_obj: Any, path: Path) -> None:
        if isinstance(plot_obj, tuple):
            plot_obj = plot_obj[0]
        if hasattr(plot_obj, "savefig"):
            fig = plot_obj
        elif hasattr(plot_obj, "fig") and hasattr(plot_obj.fig, "savefig"):
            fig = plot_obj.fig
        elif hasattr(plot_obj, "figure") and hasattr(plot_obj.figure, "savefig"):
            fig = plot_obj.figure
        elif hasattr(plot_obj, "get_figure"):
            fig = plot_obj.get_figure()
        else:
            fig = plt.gcf()
        fig.savefig(path, dpi=180, bbox_inches="tight")

    def _save_pyecharts(self, chart: Any, path: Path) -> None:
        if isinstance(chart, tuple):
            chart = chart[0]
        chart.render(str(path))

    @contextmanager
    def _activate_gui_table(self, artifact: dict, df_override: pd.DataFrame | None = None) -> Iterator[str]:
        df_type = artifact.get("df_type")
        old_state = {
            "taxa_df": getattr(self.tfa, "taxa_df", None),
            "func_df": getattr(self.tfa, "func_df", None),
            "taxa_func_df": getattr(self.tfa, "taxa_func_df", None),
            "func_name": getattr(self.tfa, "func_name", None),
            "taxa_level": getattr(self.tfa, "taxa_level", None),
        }
        table_df = df_override.copy() if df_override is not None else artifact["df"].copy()
        try:
            if df_type == "taxa":
                self.tfa.taxa_df = table_df
                if artifact.get("taxa_level"):
                    self.tfa.taxa_level = artifact["taxa_level"]
            elif df_type == "func":
                self.tfa.func_df = table_df
                if artifact.get("function_column"):
                    self.tfa.func_name = artifact["function_column"]
            elif df_type == "taxa-func":
                self.tfa.taxa_func_df = table_df
                if artifact.get("function_column"):
                    self.tfa.func_name = artifact["function_column"]
                if artifact.get("taxa_level"):
                    self.tfa.taxa_level = artifact["taxa_level"]
            yield self._gui_df_type(artifact)
        finally:
            for attr, value in old_state.items():
                setattr(self.tfa, attr, value)

    def _ensure_gui_group(self) -> None:
        group_meta = self.config.analysis.group_meta
        if group_meta and group_meta in self.tfa.meta_df.columns:
            self.tfa.set_group(group_meta)
            return
        if getattr(self.tfa, "group_list", None) is not None:
            return
        fallback_group = "AutoReportGroup"
        if fallback_group not in self.tfa.meta_df.columns:
            self.tfa.meta_df[fallback_group] = "All"
        self.tfa.set_group(fallback_group)

    def _matrix_from_table(self, df: pd.DataFrame) -> pd.DataFrame | None:
        sample_cols = [sample for sample in self.tfa.sample_list or [] if sample in df.columns]
        if not sample_cols:
            return None
        matrix = df[sample_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
        matrix = matrix.loc[(matrix != 0).any(axis=1)]
        return matrix

    def _top_features(self, matrix: pd.DataFrame, top_n: int) -> pd.DataFrame:
        if matrix.empty:
            return matrix
        means = matrix.mean(axis=1).sort_values(ascending=False)
        return matrix.loc[means.head(top_n).index]

    def _log2_matrix(self, matrix: pd.DataFrame) -> pd.DataFrame:
        values = matrix.apply(pd.to_numeric, errors="coerce").fillna(0)
        pseudo_count = self.config.statistics.pseudo_count
        return values.apply(lambda column: column.map(lambda value: math.log2(max(float(value), 0.0) + pseudo_count)))

    def _differential_heatmap_fig_size(self, df: pd.DataFrame) -> tuple[float, float]:
        matrix = self._matrix_from_table(df)
        n_cols = matrix.shape[1] if matrix is not None and not matrix.empty else 2
        n_rows = min(self.config.plots.heatmap_top_n, len(df)) if len(df) else 10
        width = max(8.0, min(18.0, 6.5 + n_cols * 0.55))
        if n_cols <= 3:
            width = 8.5
        elif n_cols <= 8:
            width = 10.5
        height = max(7.0, min(24.0, 4.5 + n_rows * 0.28))
        return (width, height)

    def _gui_df_type(self, artifact: dict) -> str:
        df_type = artifact.get("df_type")
        if df_type == "taxa-func":
            return "taxa_func"
        return str(df_type)
