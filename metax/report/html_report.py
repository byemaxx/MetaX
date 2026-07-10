from __future__ import annotations

import os
import re
import shutil
from html import escape
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

if TYPE_CHECKING:
    from .workflow import ReportContext


class HtmlReportBuilder:
    def __init__(self, context: "ReportContext"):
        self.context = context
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render(self) -> Path:
        output_path = self.context.paths.output_dir / "index.html"
        template = self.env.get_template("report.html.j2")
        html = template.render(**self._template_context())
        output_path.write_text(html, encoding="utf-8")
        self.context.registry.add_html(
            "index_html",
            output_path,
            title="HTML report",
            description="Final MetaX Auto OTF report.",
        )
        self.context.logger.info("Rendered HTML report: %s", output_path)
        return output_path

    def _template_context(self) -> dict[str, Any]:
        registry = self.context.registry.to_dict()
        tables = [self._artifact(item) for item in registry["tables"]]
        stats = [self._artifact(item) for item in registry["stats"]]
        all_figures = [self._artifact(item) for item in registry["figures"]]
        figures = [
            item
            for item in all_figures
            if Path(str(item["path"])).suffix.lower() not in {".pdf", ".svg"}
        ]
        html_items = [self._artifact(item) for item in registry["html"]]
        self._attach_result_table_links(figures, tables + stats)
        figures_by_kind = self._group_figures_by_kind(figures)
        basic_plot_subgroups = {
            kind: self._group_basic_figures_by_scope(items)
            for kind, items in figures_by_kind.items()
        }
        basic_plot_otf_function_groups = {
            kind: self._group_basic_otf_figures_by_function(items)
            for kind, items in figures_by_kind.items()
        }
        result_files_by_category = self._result_files_by_category(tables, stats)
        differential_figures = [item for item in figures if item.get("category") == "differential"]

        return {
            "title": self.context.config.report.title,
            "config": self.context.config.to_dict(),
            "config_yaml": yaml.safe_dump(self.context.config.to_dict(), sort_keys=False, allow_unicode=False),
            "dataset_summary": self.context.dataset_summary,
            "run_summary": self._run_summary(tables, stats, all_figures),
            "tables": tables,
            "tables_by_category": self._group_by_category(tables),
            "result_files": tables + stats,
            "result_files_by_category": result_files_by_category,
            "result_file_count": sum(len(items) for items in result_files_by_category.values()),
            "stats": stats,
            "figures": figures,
            "figures_by_category": self._group_by_category(figures),
            "overview_figures_by_group": self._group_overview_figures(
                [item for item in figures if item.get("category") == "overview"]
            ),
            "figures_by_kind": figures_by_kind,
            "basic_plot_subgroups": basic_plot_subgroups,
            "basic_plot_otf_function_groups": basic_plot_otf_function_groups,
            "basic_plot_figure_count": sum(len(items) for items in figures_by_kind.values()),
            "basic_plot_family_notes": _basic_plot_family_notes(),
            "differential_figures_by_scope": self._group_differential_figures(differential_figures),
            "html_items": html_items,
            "warnings": registry["warnings"],
            "errors": registry["errors"],
            "warning_run_info": self._warning_run_info(),
            "runtime": registry["runtime"],
            "embed_interactive_html": self.context.config.report.embed_interactive_html,
            "selected_taxa_levels": self.context.taxa_levels,
            "selected_function_columns": self.context.function_columns,
            "favicon_path": self._copy_report_icon(),
        }

    def _run_summary(self, tables: list[dict[str, Any]], stats: list[dict[str, Any]], figures: list[dict[str, Any]]) -> dict[str, Any]:
        config = self.context.config
        return {
            "otf_file": config.input.otf_path,
            "meta_file": config.input.meta_path or "Generated internally",
            "n_samples": self.context.dataset_summary.get("n_samples", 0),
            "n_groups": self.context.dataset_summary.get("n_groups", 0),
            "group_column": config.analysis.group_meta or "None",
            "control_group": config.analysis.control_group or "None",
            "main_taxa_level": config.analysis.main_taxa_level,
            "main_function": config.analysis.main_function or "auto",
            "n_tables": len(tables),
            "n_stats": len(stats),
            "n_figures": len(figures),
            "n_warnings": len(self.context.registry.warnings),
        }

    def _warning_run_info(self) -> dict[str, Any]:
        config = self.context.config
        return {
            "group_meta": config.analysis.group_meta or "None",
            "control_group": config.analysis.control_group or "None",
            "taxa_levels": ", ".join(self.context.taxa_levels) or "None",
            "function_columns": ", ".join(self.context.function_columns) or "None",
            "top_n": config.plots.top_n,
            "heatmap_top_n": config.plots.heatmap_top_n,
            "alpha": config.statistics.alpha,
            "log2fc_cutoff": config.statistics.log2fc_cutoff,
            "pseudo_count": config.statistics.pseudo_count,
        }

    def _artifact(self, item: dict[str, Any]) -> dict[str, Any]:
        artifact = dict(item)
        path = Path(str(item["path"]))
        artifact["relative_path"] = self._relative_path(path)
        artifact["category"] = self._category(path)
        artifact["result_scope"] = "main" if self._is_main_result(artifact) else "extended"
        artifact["rich_title"] = self._rich_title(str(artifact.get("title", artifact.get("key", ""))))
        alternate_path = artifact.get("alternate_interactive_path")
        if alternate_path:
            alternate = Path(str(alternate_path))
            artifact["alternate_interactive_relative_path"] = self._relative_path(alternate)
        if path.suffix.lower() in {".tsv", ".csv"} and path.exists():
            preview_path = self._write_table_preview(path, item["key"])
            if preview_path:
                artifact["preview_relative_path"] = self._relative_path(preview_path)
        return artifact

    def _copy_report_icon(self) -> str | None:
        source = Path(__file__).resolve().parents[1] / "gui" / "metax_gui" / "resources" / "logo.png"
        if not source.exists():
            self.context.registry.add_warning(
                f"Report icon was not found: {source}",
                source="html_report",
            )
            return None
        try:
            destination = self.context.paths.assets_dir / "logo.png"
            shutil.copyfile(source, destination)
            return self._relative_path(destination)
        except Exception as exc:
            self.context.registry.add_warning(
                f"Could not copy report icon: {exc}",
                source="html_report",
            )
            return None

    def _attach_result_table_links(
        self,
        figures: list[dict[str, Any]],
        result_files: list[dict[str, Any]],
    ) -> None:
        result_by_key = {str(item.get("key", "")): item for item in result_files}
        for figure in figures:
            result = self._matching_result_file(figure, result_by_key)
            if not result:
                continue
            figure["table_title"] = result.get("title") or result.get("key", "Result table")
            figure["table_relative_path"] = result.get("relative_path")
            if result.get("preview_relative_path"):
                figure["table_preview_relative_path"] = result["preview_relative_path"]

    def _matching_result_file(
        self,
        figure: dict[str, Any],
        result_by_key: dict[str, dict[str, Any]],
    ) -> dict[str, Any] | None:
        key = str(figure.get("key", ""))
        candidates: list[str] = []

        prefix_map = [
            "pca_3d_",
            "pca_",
            "tsne_",
            "sample_correlation_",
            "top_feature_heatmap_",
            "boxplot_",
            "bar_",
            "upset_",
            "alpha_diversity_",
            "beta_diversity_",
            "treemap_",
            "sunburst_",
            "sankey_",
            "differential_heatmap_",
            "dunnett_heatmap_",
            "volcano_",
            "deseq2_sankey_",
        ]
        for prefix in prefix_map:
            if key.startswith(prefix):
                candidates.append(key[len(prefix):])
                break

        if key in {"taxa_stats_pie", "taxa_number_bar"}:
            main_key = f"taxa_{self.context.config.analysis.main_taxa_level}"
            candidates.extend([main_key, *[item for item in result_by_key if item.startswith("taxa_") and "_" not in item[5:]]])
        elif key.startswith("function_proportion_"):
            candidates.append(f"function_{key.removeprefix('function_proportion_')}")

        for candidate in candidates:
            if candidate in result_by_key:
                return result_by_key[candidate]

        for result_key in sorted(result_by_key, key=len, reverse=True):
            if result_key and (key.endswith(result_key) or f"_{result_key}_" in f"_{key}_"):
                return result_by_key[result_key]
        return None

    def _write_table_preview(self, path: Path, key: str) -> Path | None:
        sep = "\t" if path.suffix.lower() == ".tsv" else ","
        try:
            df = pd.read_csv(path, sep=sep, nrows=max(self.context.config.report.show_top_rows, 500))
            preview_dir = self.context.paths.assets_dir / "previews"
            preview_dir.mkdir(parents=True, exist_ok=True)
            preview_path = preview_dir / f"{_safe_filename(key)}.html"
            if df.empty:
                body = "<p class=\"muted\">No rows in this file.</p>"
            else:
                body = df.to_html(index=False, classes="preview-table", border=0, escape=True, table_id="preview-table")
            preview_path.write_text(
                self._preview_document(
                    path,
                    body,
                    actual_rows=len(df.index),
                    download_path=self._relative_path_from(path, preview_dir),
                ),
                encoding="utf-8",
            )
            return preview_path
        except Exception as exc:
            self.context.logger.warning("Could not preview table %s: %s", path, exc)
            return None

    def _preview_document(
        self,
        source_path: Path,
        body: str,
        actual_rows: int,
        download_path: str,
    ) -> str:
        page_size = self.context.config.report.show_top_rows
        title = escape(source_path.name)
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <style>
    body {{ margin: 0; font: 12px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #1f2933; }}
    .preview-meta {{ position: sticky; top: 0; z-index: 2; display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 8px 10px; background: #edf3f7; border-bottom: 1px solid #d8dee8; }}
    .pager {{ display: flex; align-items: center; gap: 7px; white-space: nowrap; }}
    .pager button {{ border: 1px solid #cbd5e1; background: #fff; border-radius: 6px; padding: 3px 8px; cursor: pointer; }}
    .pager button:disabled {{ opacity: .45; cursor: default; }}
    .muted {{ color: #687584; }}
    .download-link {{ color: #136f63; font-weight: 700; }}
    table.preview-table {{ width: 100%; border-collapse: collapse; background: #fff; }}
    .preview-table th, .preview-table td {{ border-bottom: 1px solid #e8edf3; padding: 6px 8px; text-align: left; white-space: nowrap; }}
    .preview-table th {{ position: sticky; top: 37px; background: #f7f9fc; z-index: 1; }}
  </style>
</head>
<body>
  <div class="preview-meta">
    <div>
      <strong>{title}</strong>
      <span class="muted">Previewing the first {actual_rows} rows. Download the full TSV for complete results.</span>
      <a class="download-link" href="{escape(download_path)}">Download full table</a>
    </div>
    <div class="pager">
      <button id="prev-page" type="button">Prev</button>
      <span id="page-status"></span>
      <button id="next-page" type="button">Next</button>
    </div>
  </div>
  {body}
  <script>
    const pageSize = {page_size};
    const rows = Array.from(document.querySelectorAll("#preview-table tbody tr"));
    const prev = document.getElementById("prev-page");
    const next = document.getElementById("next-page");
    const status = document.getElementById("page-status");
    let page = 0;
    const totalPages = Math.max(1, Math.ceil(rows.length / pageSize));
    function renderPage() {{
      rows.forEach((row, index) => {{
        row.style.display = index >= page * pageSize && index < (page + 1) * pageSize ? "" : "none";
      }});
      status.textContent = `${{page + 1}} / ${{totalPages}}`;
      prev.disabled = page === 0;
      next.disabled = page >= totalPages - 1;
    }}
    prev.addEventListener("click", () => {{ if (page > 0) {{ page -= 1; renderPage(); }} }});
    next.addEventListener("click", () => {{ if (page < totalPages - 1) {{ page += 1; renderPage(); }} }});
    renderPage();
  </script>
</body>
</html>"""

    def _relative_path(self, path: Path) -> str:
        return self._relative_path_from(path, self.context.paths.output_dir)

    @staticmethod
    def _relative_path_from(path: Path, start: Path) -> str:
        try:
            return os.path.relpath(path.resolve(), start.resolve()).replace("\\", "/")
        except Exception:
            return str(path).replace("\\", "/")

    def _category(self, path: Path) -> str:
        parts = list(path.parts)
        for marker in ["tables", "stats", "figures"]:
            if marker in parts:
                index = parts.index(marker)
                if len(parts) > index + 1:
                    return parts[index + 1]
        return "other"

    def _group_by_category(self, artifacts: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for artifact in artifacts:
            grouped.setdefault(artifact["category"], []).append(artifact)
        return grouped

    def _result_files_by_category(
        self,
        tables: list[dict[str, Any]],
        stats: list[dict[str, Any]],
    ) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        main_results = [
            item for item in [*tables, *stats] if item.get("result_scope") == "main"
        ]
        if main_results:
            grouped["main_results"] = main_results
        for table in tables:
            if table.get("result_scope") == "main":
                continue
            grouped.setdefault(table["category"], []).append(table)
        for stat in stats:
            if stat.get("result_scope") == "main":
                continue
            category = f"comparison_{stat.get('category', 'other')}"
            grouped.setdefault(category, []).append(stat)
        return grouped

    def _is_main_result(self, artifact: dict[str, Any]) -> bool:
        key = str(artifact.get("key", ""))
        main_taxa = self.context.config.analysis.main_taxa_level
        main_function = (
            self.context.config.analysis.main_function
            or (self.context.function_columns[0] if self.context.function_columns else None)
        )
        safe_function = _safe_filename(main_function) if main_function else None
        if key == f"taxa_{main_taxa}" or key.startswith(f"taxa_{main_taxa}_"):
            return True
        if safe_function and (
            key == f"function_{safe_function}"
            or key.startswith(f"function_{safe_function}_")
            or key == f"otf_{main_taxa}_{safe_function}"
            or key.startswith(f"otf_{main_taxa}_{safe_function}_")
        ):
            return True
        return False

    def _group_overview_figures(self, figures: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        grouped = {
            "Taxonomy and dataset coverage": [],
            "Function annotation coverage": [],
        }
        for figure in figures:
            key = str(figure.get("key", ""))
            if key.startswith("function_proportion_"):
                grouped["Function annotation coverage"].append(figure)
            else:
                grouped["Taxonomy and dataset coverage"].append(figure)
        return {name: items for name, items in grouped.items() if items}

    def _group_figures_by_kind(self, figures: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        labels = {
            "pca": "PCA",
            "pca_3d": "3D PCA",
            "tsne": "t-SNE",
            "correlation": "Correlation Heatmap",
            "heatmap": "Heatmap",
            "box": "Box",
            "bar": "Bar",
            "upset": "UpSet",
            "alpha_diversity": "Alpha Diversity",
            "beta_diversity": "Beta Diversity",
            "treemap": "TreeMap",
            "sunburst": "Sunburst",
            "sankey": "Sankey",
            "differential": "Differential",
            "taxa_function": "Taxa-function links",
            "other": "Other figures",
        }
        for figure in figures:
            if figure.get("category") not in {"basic", "composition"}:
                continue
            key = str(figure.get("key", ""))
            if key.startswith("pca_3d_"):
                kind = "pca_3d"
            elif key.startswith("pca_"):
                kind = "pca"
            elif key.startswith("tsne_"):
                kind = "tsne"
            elif key.startswith("sample_correlation_"):
                kind = "correlation"
            elif key.startswith("top_feature_heatmap_"):
                kind = "heatmap"
            elif key.startswith("boxplot_"):
                kind = "box"
            elif key.startswith("bar_"):
                kind = "bar"
            elif key.startswith("upset_"):
                kind = "upset"
            elif key.startswith("alpha_diversity_"):
                kind = "alpha_diversity"
            elif key.startswith("beta_diversity_"):
                kind = "beta_diversity"
            elif key.startswith("treemap_"):
                kind = "treemap"
            elif key.startswith("sunburst_"):
                kind = "sunburst"
            elif key.startswith("sankey_"):
                kind = "sankey"
            else:
                kind = "other"
            label = labels[kind]
            grouped.setdefault(label, []).append(figure)
        return grouped

    def _group_basic_figures_by_scope(self, figures: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for figure in figures:
            scope = self._basic_figure_scope(figure)
            grouped.setdefault(scope, []).append(figure)
        ordered: dict[str, list[dict[str, Any]]] = {}
        for scope in ["Taxa", "Function", "OTF", "Other"]:
            if scope in grouped:
                ordered[scope] = grouped[scope]
        return ordered

    def _basic_figure_scope(self, figure: dict[str, Any]) -> str:
        key = str(figure.get("key", ""))
        title = str(figure.get("title", "")).lower()
        if "_otf_" in key or "taxa-function links" in title:
            return "OTF"
        if "_function_" in key or "function abundance" in title:
            return "Function"
        if "_taxa_" in key or "taxa abundance" in title:
            return "Taxa"
        return "Other"

    def _group_basic_otf_figures_by_function(self, figures: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        otf_figures = [figure for figure in figures if self._basic_figure_scope(figure) == "OTF"]
        grouped: dict[str, list[dict[str, Any]]] = {}
        for figure in otf_figures:
            function_name = self._figure_function_name(figure)
            grouped.setdefault(function_name, []).append(figure)
        ordered: dict[str, list[dict[str, Any]]] = {}
        for function_name in self.context.function_columns:
            if function_name in grouped:
                ordered[function_name] = grouped[function_name]
        for function_name, items in grouped.items():
            if function_name not in ordered:
                ordered[function_name] = items
        return ordered

    def _figure_function_name(self, figure: dict[str, Any]) -> str:
        key = str(figure.get("key", ""))
        title = str(figure.get("title", ""))
        for function_name in self.context.function_columns:
            safe_name = _safe_filename(function_name)
            if safe_name in key or function_name in title:
                return function_name
        match = re.search(r"(?:and|with)\s+([A-Za-z0-9_.-]+)", title)
        if match:
            return match.group(1)
        return "Other function"

    def _group_differential_figures(
        self,
        figures: list[dict[str, Any]],
    ) -> dict[str, dict[str, list[dict[str, Any]]]]:
        grouped: dict[str, dict[str, list[dict[str, Any]]]] = {}
        for figure in figures:
            scope = self._differential_scope(figure)
            plot_type = self._differential_plot_type(figure)
            if scope == "Taxa" and plot_type in {"Heatmap", "Volcano"}:
                plot_type = f"{plot_type} - {self._differential_taxa_level(figure)}"
            grouped.setdefault(scope, {}).setdefault(plot_type, []).append(figure)

        ordered: dict[str, dict[str, list[dict[str, Any]]]] = {}
        for scope in ["Taxa", "Function", "OTF", "Other"]:
            if scope in grouped:
                ordered[scope] = grouped[scope]
        return ordered

    def _differential_scope(self, figure: dict[str, Any]) -> str:
        key = str(figure.get("key", ""))
        title = str(figure.get("title", "")).lower()
        if "_otf_" in key or "taxa-function links" in title:
            return "OTF"
        if "_function_" in key or "function abundance" in title:
            return "Function"
        if "_taxa_" in key or "taxa abundance" in title:
            return "Taxa"
        return "Other"

    def _differential_plot_type(self, figure: dict[str, Any]) -> str:
        key = str(figure.get("key", ""))
        title = str(figure.get("title", "")).lower()
        if key.startswith("volcano_") or "volcano" in title:
            return "Volcano"
        if "heatmap" in key or "heatmap" in title:
            return "Heatmap"
        if "sankey" in key or "sankey" in title:
            return "Sankey"
        return "Other differential plots"

    def _differential_taxa_level(self, figure: dict[str, Any]) -> str:
        key = str(figure.get("key", ""))
        title = str(figure.get("title", "")).lower()
        for level in self.context.taxa_levels:
            label = _taxa_level_label(level)
            if f"_taxa_{level}_" in key or f" {label} " in f" {title} ":
                return label
        return "taxa level"

    def _rich_title(self, title: str) -> str:
        rich = escape(title)
        tokens: list[tuple[str, str]] = []
        seen_tokens: set[str] = set()

        def add_token(value: str | None, kind: str) -> None:
            if not value:
                return
            key = str(value)
            if key in seen_tokens:
                return
            seen_tokens.add(key)
            tokens.append((key, kind))

        for function_name in self.context.function_columns:
            add_token(function_name, "function")
        for level in self.context.taxa_levels:
            label = _taxa_level_label(level)
            add_token(label, "taxa")
        control = self.context.config.analysis.control_group
        group_meta = self.context.config.analysis.group_meta
        if group_meta and group_meta in self.context.tfa.meta_df.columns:
            groups = sorted(set(str(item) for item in self.context.tfa.meta_df[group_meta].dropna()))
            for group in groups:
                if control and group == control:
                    continue
                add_token(group, "group")
        add_token(control, "control")

        for token, kind in sorted(tokens, key=lambda item: len(item[0]), reverse=True):
            if not token:
                continue
            escaped_token = escape(token)
            pattern = re.compile(rf"(?<![\w.-]){re.escape(escaped_token)}(?![\w.-])")
            rich = pattern.sub(f'<span class="title-token title-token-{kind}">{escaped_token}</span>', rich)
        return rich


def _safe_filename(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return safe.strip("._") or "preview"


def _taxa_level_label(level: str) -> str:
    labels = {
        "d": "domain",
        "p": "phylum",
        "c": "class",
        "o": "order",
        "f": "family",
        "g": "genus",
        "s": "species",
        "m": "genome",
        "l": "life",
    }
    return labels.get(level, level)


def _basic_plot_family_notes() -> dict[str, dict[str, str]]:
    return {
        "PCA": {
            "purpose": "Ordination view for checking whether samples separate by the selected metadata group.",
            "read": "Nearby points have more similar abundance profiles. Clear group separation suggests strong global differences.",
        },
        "3D PCA": {
            "purpose": "Interactive 3D ordination view for datasets where the first two PCs do not capture enough structure.",
            "read": "Rotate the plot to inspect separation that may be hidden in a 2D projection.",
        },
        "t-SNE": {
            "purpose": "Nonlinear sample embedding for exploratory clustering.",
            "read": "Use as exploratory evidence only; local neighborhoods are more meaningful than global distances.",
        },
        "Correlation Heatmap": {
            "purpose": "Sample-to-sample similarity check.",
            "read": "Blocks of high correlation indicate samples with similar taxa/function/OTF profiles.",
        },
        "Heatmap": {
            "purpose": "Top feature abundance patterns across samples.",
            "read": "Rows are top-N features; columns are samples. Clustering highlights shared abundance patterns.",
        },
        "Box": {
            "purpose": "Intensity distribution by metadata group.",
            "read": "Large shifts or outlier-heavy groups can indicate normalization or biological differences.",
        },
        "Bar": {
            "purpose": "Composition or abundance contribution of top features.",
            "read": "Use the interactive legend and zoom controls to focus on major contributors.",
        },
        "UpSet": {
            "purpose": "Feature presence/absence overlap between groups or samples.",
            "read": "Large intersections show features shared across multiple groups.",
        },
        "Alpha Diversity": {
            "purpose": "Within-sample richness/evenness summary.",
            "read": "Higher values indicate more diverse abundance profiles within a sample or group.",
        },
        "Beta Diversity": {
            "purpose": "Between-sample distance summary.",
            "read": "Separated groups indicate distinct community or function profiles.",
        },
        "TreeMap": {
            "purpose": "Hierarchical taxa composition summary.",
            "read": "Area reflects total abundance; nested boxes follow the taxonomic hierarchy.",
        },
        "Sunburst": {
            "purpose": "Radial hierarchical taxa composition summary.",
            "read": "Inner rings are broader taxa levels; outer rings are more specific levels.",
        },
        "Sankey": {
            "purpose": "Flow-style view of taxa or taxa-function abundance relationships.",
            "read": "Wider links represent larger abundance contributions.",
        },
    }
