from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import Any

import yaml


@dataclass
class AnalysisStep:
    title: str
    step_type: str
    code: str
    parameters: dict[str, Any] = field(default_factory=dict)
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowRecord:
    title: str = "MetaX GUI Workflow"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    metadata: dict[str, Any] = field(default_factory=dict)
    steps: list[AnalysisStep] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["steps"] = [step.to_dict() for step in self.steps]
        return data


@dataclass(frozen=True)
class WorkflowExportPaths:
    yaml_path: Path
    python_path: Path
    notebook_path: Path

    def as_dict(self) -> dict[str, Path]:
        return {
            "workflow_yaml": self.yaml_path,
            "workflow_python": self.python_path,
            "workflow_notebook": self.notebook_path,
        }


class WorkflowRecorder:
    def __init__(self, title: str = "MetaX GUI Workflow", metadata: dict[str, Any] | None = None):
        self.record = WorkflowRecord(title=title, metadata=metadata or {})
        self.enabled = True

    @property
    def steps(self) -> list[AnalysisStep]:
        return self.record.steps

    def clear(self) -> None:
        self.record.steps.clear()

    def add_step(self, step: AnalysisStep) -> AnalysisStep:
        if not self.enabled:
            return step
        self.record.steps.append(step)
        return step

    def add_auto_otf_report(self, config_path: str | Path, result: Any | None = None) -> AnalysisStep:
        step = auto_otf_report_step(config_path, result)
        return self.add_step(step)

    def to_dict(self) -> dict[str, Any]:
        return self.record.to_dict()

    def export_all(self, output_dir: str | Path, basename: str = "metax_gui_workflow") -> WorkflowExportPaths:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        paths = WorkflowExportPaths(
            yaml_path=output_path / f"{basename}.yaml",
            python_path=output_path / f"{basename}.py",
            notebook_path=output_path / f"{basename}.ipynb",
        )
        self.save_yaml(paths.yaml_path)
        self.save_python(paths.python_path)
        self.save_notebook(paths.notebook_path)
        return paths

    def save_yaml(self, path: str | Path) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(self.to_dict(), handle, sort_keys=False, allow_unicode=False)
        return output_path

    def save_python(self, path: str | Path) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.to_python_script(), encoding="utf-8")
        return output_path

    def save_notebook(self, path: str | Path) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(self.to_notebook(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return output_path

    def to_python_script(self) -> str:
        lines = [
            "# Auto-generated from a MetaX GUI workflow.",
            "# Run cells individually in an editor that supports '# %%' cells.",
            "",
            "# %%",
            _environment_setup_code(self.record.metadata).rstrip(),
            "",
            "# %%",
            _gui_action_replay_helper_code().rstrip(),
            "",
        ]
        for index, step in enumerate(self.steps, start=1):
            lines.extend(
                [
                    "# %%",
                    f"# Step {index}: {step.title}",
                    f"# Type: {step.step_type}",
                    step.code.rstrip(),
                    "",
                ]
            )
        return "\n".join(lines).rstrip() + "\n"

    def to_notebook(self) -> dict[str, Any]:
        cells = [
            _markdown_cell(
                f"# {self.record.title}\n\n"
                "This notebook was generated from semantic MetaX GUI analysis steps."
            ),
            _code_cell(_environment_setup_code(self.record.metadata)),
            _code_cell(_gui_action_replay_helper_code()),
        ]
        if self.record.metadata:
            cells.append(_code_cell(_assignment("workflow_metadata", self.record.metadata)))

        for index, step in enumerate(self.steps, start=1):
            cells.append(_markdown_cell(_step_markdown(index, step)))
            cells.append(_code_cell(step.code.rstrip() + "\n"))

        return {
            "cells": cells,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3",
                },
                "language_info": {
                    "name": "python",
                    "pygments_lexer": "ipython3",
                },
            },
            "nbformat": 4,
            "nbformat_minor": 5,
        }


def auto_otf_report_step(config_path: str | Path, result: Any | None = None) -> AnalysisStep:
    resolved_config_path = Path(config_path).expanduser().resolve()
    output_dir = _path_from_result(result, "output_dir")
    index_html_path = _path_from_result(result, "index_html_path")

    code = dedent(
        f"""\
        from pathlib import Path

        from metax.report.config import load_config_from_yaml
        from metax.report.workflow import AutoOTFReport


        config_path = Path(r"{resolved_config_path}")
        config = load_config_from_yaml(config_path)
        result = AutoOTFReport(config).run()
        print(result.index_html_path)
        """
    )

    outputs = {}
    if output_dir:
        outputs["output_dir"] = output_dir
    if index_html_path:
        outputs["index_html_path"] = index_html_path

    return AnalysisStep(
        title="Generate Auto OTF Report",
        step_type="auto_otf_report",
        inputs={"config_path": str(resolved_config_path)},
        parameters={"config_path": str(resolved_config_path)},
        outputs=outputs,
        code=code,
        notes=["Created from the MetaX GUI Auto OTF Report action."],
    )


def unit_specific_otf_step(params: dict[str, Any]) -> AnalysisStep:
    parameters = dict(params)
    code = _join_code(
        "from metax.peptide_annotator.unit_specific_otf import UnitSpecificOTFAnnotator",
        "",
        _assignment("unit_specific_otf_params", parameters),
        "unit_specific_otf = UnitSpecificOTFAnnotator(**unit_specific_otf_params)",
        "unit_specific_otf_result = unit_specific_otf.run()",
        'print(f"Saved unit-specific OTF: {unit_specific_otf.output_path}")',
    )
    return AnalysisStep(
        title="Run Unit-specific Peptide Direct to OTF",
        step_type="unit_specific_peptide_direct_to_otf",
        inputs={
            "peptide_table_path": parameters.get("peptide_table_path"),
            "digested_genome_folders": parameters.get("digested_genome_folders"),
            "taxafunc_anno_db_path": parameters.get("taxafunc_anno_db_path"),
            "unit_specific_manifest_path": parameters.get("unit_specific_manifest_path"),
        },
        outputs={"output_path": parameters.get("output_path")},
        parameters=parameters,
        code=code,
        notes=["Recorded from the MetaX GUI unit-specific direct-to-OTF workflow."],
    )


def taxafunc_analyzer_step(
    params: dict[str, Any],
    group_name: str | None = None,
    summary: dict[str, Any] | None = None,
) -> AnalysisStep:
    setup_lines = [
        "from metax.taxafunc_analyzer.analyzer import TaxaFuncAnalyzer",
        "",
        _assignment("taxafunc_params", params),
        "tfa = TaxaFuncAnalyzer(**taxafunc_params)",
    ]
    if group_name:
        setup_lines.append(f"tfa.set_group({_python_literal(group_name)})")
    setup_lines.append('print("Loaded OTF object")')
    code = _join_code(*setup_lines)

    outputs = summary or {}
    parameters = dict(params)
    if group_name:
        parameters["group"] = group_name

    return AnalysisStep(
        title="Load OTF and Meta Tables",
        step_type="load_taxafunc_analyzer",
        inputs={
            "otf_path": params.get("df_path"),
            "meta_path": params.get("meta_path"),
        },
        parameters=parameters,
        outputs=outputs,
        code=code,
        notes=["Created from the MetaX GUI OTF Analyzer load action. Later OTF Analyzer steps use this `tfa` object."],
    )


def set_multi_tables_step(function_name: str, params: dict[str, Any]) -> AnalysisStep:
    code = _join_code(
        "# Requires `tfa` from the OTF loading step.",
        f"tfa.set_func({_python_literal(function_name)})",
        _assignment("set_multi_table_params", params),
        "tfa.set_multi_tables(**set_multi_table_params)",
        'print("Created processed MetaX OTF tables")',
    )
    return AnalysisStep(
        title="Create Processed OTF Tables",
        step_type="set_multi_tables",
        parameters={"function_name": function_name, **dict(params)},
        outputs={"tables": ["peptides", "taxa", "functions", "taxa-functions"]},
        code=code,
        notes=["Created from the MetaX GUI Set Multi Table action. This step updates the `tfa` OTF Analyzer object."],
    )


def method_call_step(
    *,
    title: str,
    step_type: str,
    target: str,
    method_name: str,
    parameters: dict[str, Any],
    output_name: str = "result",
    gui_table_names: list[str] | None = None,
    notes: list[str] | None = None,
) -> AnalysisStep:
    safe_parameters = _safe_parameters(parameters)
    setup_lines = [
        "# Requires `tfa` from the OTF loading step and any processed tables from previous cells.",
        _assignment("params", safe_parameters),
        f"{output_name} = {target}.{method_name}(**params)",
    ]
    if gui_table_names:
        if len(gui_table_names) == 1:
            setup_lines.append(f"stats_results[{gui_table_names[0]!r}] = {output_name}")
        else:
            for idx, tbl_name in enumerate(gui_table_names):
                setup_lines.append(f"stats_results[{tbl_name!r}] = {output_name}[{idx}]")
    setup_lines.append(f"print(type({output_name}))")
    code = _join_code(*setup_lines)

    return AnalysisStep(
        title=title,
        step_type=step_type,
        parameters={"gui_table_names": gui_table_names, **safe_parameters} if gui_table_names else safe_parameters,
        outputs={"python_variable": output_name},
        code=code,
        notes=notes or [],
    )


def deseq2_step(
    *,
    title: str,
    method_name: str,
    df_type: str,
    parameters: dict[str, Any],
    output_name: str = "df_deseq2",
) -> AnalysisStep:
    safe_params = _safe_parameters(parameters)
    if method_name == "get_stats_deseq2_against_control":
        key_expr = f"'deseq2all(' + df_type.lower() + ')'"
    elif method_name == "get_stats_deseq2_against_control_with_conditon":
        key_expr = f"'deseq2allinCondition(' + df_type.lower() + ')'"
    else:
        key_expr = f"'deseq2(' + df_type.lower() + ')'"

    code_lines = [
        "# Requires `tfa` from the OTF loading step.",
        "def _get_metax_df_by_type(tfa, df_type):",
        "    key = df_type.lower()",
        "    if key == 'taxa': return getattr(tfa, 'taxa_df', None)",
        "    if key in {'func', 'function', 'functions'}: return getattr(tfa, 'func_df', None)",
        "    if key in {'taxa-func', 'taxa-function', 'taxa-functions'}: return getattr(tfa, 'taxa_func_df', None)",
        "    if key in {'peptide', 'peptides'}: return getattr(tfa, 'peptide_df', None)",
        "    if key in {'protein', 'proteins'}: return getattr(tfa, 'protein_df', None)",
        "    if key == 'custom': return getattr(tfa, 'custom_df', None)",
        "    raise ValueError(f'Unsupported df_type: {df_type}')",
        "",
        f"df_type = {_python_literal(df_type)}",
        "df = _get_metax_df_by_type(tfa, df_type)",
        "if df is None:",
        "    raise ValueError(f'Could not find table for {df_type}.')",
        "",
    ]
    
    # Store parameters that should be recorded
    recorded_params = {"df_type": df_type, **safe_params}
    
    # Handle invert_transform in generated code
    if "invert_transform" in safe_params:
        invert_val = safe_params.pop("invert_transform")
        code_lines.extend([
            f"invert_method = {_python_literal(invert_val)}",
            "df = tfa.CrossTest.prepare_deseq2_input(df, invert_transform=invert_method, validate=True)",
            ""
        ])
    else:
        code_lines.extend([
            "df = tfa.CrossTest.prepare_deseq2_input(df, invert_transform=None, validate=True)",
            ""
        ])

    safe_params["input_prepared"] = True
    code_lines.extend([
        _assignment("deseq2_params", safe_params),
        f"{output_name} = tfa.CrossTest.{method_name}(df=df, **deseq2_params)",
        f"stats_results[{key_expr}] = {output_name}",
        f"print(type({output_name}))",
    ])
    
    code = _join_code(*code_lines)
    return AnalysisStep(
        title=title,
        step_type="deseq2_test",
        parameters=recorded_params,
        outputs={"python_variable": output_name},
        code=code,
        notes=["Run DESeq2 differential analysis using InMoose."],
    )


def limma_step(
    *,
    title: str,
    method_name: str,
    df_type: str,
    parameters: dict[str, Any],
    output_name: str = "df_limma",
) -> AnalysisStep:
    safe_params = _safe_parameters(parameters)
    recorded_params = {"df_type": df_type, **safe_params}
    if method_name == "get_stats_limma_against_control":
        key_expr = f"'limmaall(' + df_type.lower() + ')'"
    elif method_name == "get_stats_limma_against_control_with_conditon":
        key_expr = f"'limmaallinCondition(' + df_type.lower() + ')'"
    else:
        key_expr = f"'limma(' + df_type.lower() + ')'"

    code_lines = [
        "# Requires `tfa` from the OTF loading step.",
        "def _get_metax_df_by_type(tfa, df_type):",
        "    key = df_type.lower()",
        "    if key == 'taxa': return getattr(tfa, 'taxa_df', None)",
        "    if key in {'func', 'function', 'functions'}: return getattr(tfa, 'func_df', None)",
        "    if key in {'taxa-func', 'taxa-function', 'taxa-functions'}: return getattr(tfa, 'taxa_func_df', None)",
        "    if key in {'peptide', 'peptides'}: return getattr(tfa, 'peptide_df', None)",
        "    if key in {'protein', 'proteins'}: return getattr(tfa, 'protein_df', None)",
        "    if key == 'custom': return getattr(tfa, 'custom_df', None)",
        "    raise ValueError(f'Unsupported df_type: {df_type}')",
        "",
        f"df_type = {_python_literal(df_type)}",
        "df = _get_metax_df_by_type(tfa, df_type)",
        "if df is None:",
        "    raise ValueError(f'Could not find table for {df_type}.')",
        "",
    ] 

    invert_val = safe_params.get("invert_transform", None)
    log2_val = safe_params.get("log2_transform", False)
    zero_to_nan_val = safe_params.get("zero_to_nan", False)
    safe_params.setdefault("invert_transform", invert_val)
    safe_params.setdefault("log2_transform", log2_val)
    safe_params.setdefault("zero_to_nan", zero_to_nan_val)
    recorded_params.setdefault("invert_transform", invert_val)
    recorded_params.setdefault("log2_transform", log2_val)
    recorded_params.setdefault("zero_to_nan", zero_to_nan_val)

    code_lines.extend([
        _assignment("limma_params", safe_params),
        f"{output_name} = tfa.CrossTest.{method_name}(df=df, **limma_params)",
        f"stats_results[{key_expr}] = {output_name}",
        f"print(type({output_name}))",
    ])

    code = _join_code(*code_lines)
    return AnalysisStep(
        title=title,
        step_type="limma_test",
        parameters=recorded_params,
        outputs={"python_variable": output_name},
        code=code,
        notes=["Run limma differential analysis using log2-transformed data with optional zero-to-NaN conversion."],
    )


def gui_action_step(
    *,
    title: str,
    step_type: str,
    action_name: str,
    parameters: dict[str, Any] | None = None,
    data_source: str = "tfa",
    notes: list[str] | None = None,
) -> AnalysisStep:
    safe_parameters = _safe_parameters(parameters or {})
    safe_parameters.setdefault("data_source", data_source)
    code = _join_code(
        "# This cell records a GUI action based on the `tfa` OTF Analyzer object.",
        f"action_name = {_python_literal(action_name)}",
        _assignment("parameters", safe_parameters),
        "replay_metax_gui_action(tfa, action_name, parameters, stats_tables=stats_results)",
    )
    return AnalysisStep(
        title=title,
        step_type=step_type,
        parameters=safe_parameters,
        code=code,
        notes=notes or ["Recorded from a MetaX GUI action. The OTF Analyzer workflow is centered on the `tfa` object."],
    )


def _path_from_result(result: Any | None, attr: str) -> str | None:
    if result is None:
        return None
    value = getattr(result, attr, None)
    return str(value) if value else None


def _join_code(*parts: str) -> str:
    return "\n".join(parts).rstrip() + "\n"


def _environment_setup_code(metadata: dict[str, Any]) -> str:
    package_root = metadata.get("metax_package_root") or ""
    return _join_code(
        "from pathlib import Path",
        "import sys",
        "",
        f"metax_package_root = Path(r{package_root!r}) if {bool(package_root)!r} else Path.cwd()",
        "if str(metax_package_root) not in sys.path:",
        "    sys.path.insert(0, str(metax_package_root))",
        "print(f'MetaX package root: {metax_package_root}')",
        "",
        "# Global registry to hold statistical results for downstream plotting.",
        "stats_results = {}",
    )


def _gui_action_replay_helper_code() -> str:
    return dedent(
        """\
        def _metax_table_from_tfa(tfa, table_name):
            normalized = str(table_name).lower()
            table_map = {
                "taxa": getattr(tfa, "taxa_df", None),
                "functions": getattr(tfa, "func_df", None),
                "function": getattr(tfa, "func_df", None),
                "taxa-functions": getattr(tfa, "taxa_func_df", None),
                "functions-taxa": getattr(tfa, "func_taxa_df", None),
                "peptides": getattr(tfa, "peptide_df", None),
                "peptide": getattr(tfa, "peptide_df", None),
                "proteins": getattr(tfa, "protein_df", None),
                "protein": getattr(tfa, "protein_df", None),
                "custom": getattr(tfa, "custom_df", None),
            }
            table = table_map.get(normalized)
            if table is None:
                raise ValueError(f"Cannot resolve table from tfa: {table_name}")
            return table


        def replay_metax_gui_action(tfa, action_name, parameters, stats_tables=None):
            stats_tables = stats_tables or {}
            data_source = parameters.get("data_source", "tfa")

            if action_name == "plot_basic_info_sns":
                from metax.taxafunc_ploter.basic_plot import BasicPlot

                method = parameters["method"]
                table_name = parameters["table_name"]
                sample_list = parameters.get("sample_list") or getattr(tfa, "sample_list", [])
                df = _metax_table_from_tfa(tfa, table_name)[sample_list]
                common = {
                    "title_name": parameters.get("title_name", table_name),
                    "width": parameters.get("width"),
                    "height": parameters.get("height"),
                    "font_size": parameters.get("font_size"),
                    "theme": parameters.get("theme"),
                    "sub_meta": parameters.get("sub_meta", "None"),
                    "rename_sample": parameters.get("rename_sample", False),
                }
                if method == "pca":
                    return BasicPlot(tfa).plot_pca_sns(
                        df=df,
                        show_label=parameters.get("show_label", True),
                        **common,
                    )
                if method == "box":
                    return BasicPlot(tfa).plot_box_sns(df=df, **common)
                if method == "corr":
                    return BasicPlot(tfa).plot_corr_sns(df=df, **common)
                if method == "pca_3d":
                    from metax.taxafunc_ploter.pca_plot_js import PcaPlot_js
                    pic = PcaPlot_js(tfa, theme=parameters.get("theme", "white")).plot_pca_pyecharts_3d(
                        df=df,
                        title_name=common["title_name"],
                        show_label=parameters.get("show_label", True),
                        rename_sample=parameters.get("rename_sample", False),
                        width=parameters.get("width"),
                        height=parameters.get("height"),
                        font_size=parameters.get("font_size"),
                        legend_col_num=parameters.get("legend_col_num"),
                    )
                    if "js_width" in parameters:
                        pic.width = parameters["js_width"]
                    if "js_height" in parameters:
                        pic.height = parameters["js_height"]
                    return pic.render_notebook()
                if method == "sunburst":
                    from metax.taxafunc_ploter.sunburst_plot import SunburstPlot
                    pic = SunburstPlot(theme=parameters.get("theme", "white")).create_sunburst_chart(
                        taxa_df=df,
                        width=parameters.get("width"),
                        height=parameters.get("height"),
                        title='Sunburst of Taxa',
                        show_label=parameters.get("show_label", 'last'),
                        label_font_size=parameters.get("font_size"),
                    )
                    if "js_width" in parameters:
                        pic.width = parameters["js_width"]
                    if "js_height" in parameters:
                        pic.height = parameters["js_height"]
                    return pic.render_notebook()
                if method == "treemap":
                    from metax.taxafunc_ploter.treemap_plot import TreeMapPlot
                    pic = TreeMapPlot(theme=parameters.get("theme", "white")).create_treemap_chart(
                        taxa_df=df,
                        width=parameters.get("width"),
                        height=parameters.get("height"),
                        show_sub_title=parameters.get("show_label", True),
                        font_size=parameters.get("font_size"),
                    )
                    if "js_width" in parameters:
                        pic.width = parameters["js_width"]
                    if "js_height" in parameters:
                        pic.height = parameters["js_height"]
                    return pic.render_notebook()
                if method == "sankey":
                    from metax.taxafunc_ploter.sankey_plot import SankeyPlot
                    pic = SankeyPlot(tfa, theme=parameters.get("theme", "white")).plot_intensity_sankey(
                        df=df,
                        width=parameters.get("width"),
                        height=parameters.get("height"),
                        font_size=parameters.get("font_size"),
                        title='',
                        subtitle='',
                        sub_meta=parameters.get("sub_meta", "None"),
                    )
                    if "js_width" in parameters:
                        pic.width = parameters["js_width"]
                    if "js_height" in parameters:
                        pic.height = parameters["js_height"]
                    return pic.render_notebook()
                if method == "tsne":
                    return BasicPlot(tfa).plot_tsne_sns(
                        df=df,
                        title_name=common["title_name"],
                        show_label=parameters.get("show_label", True),
                        perplexity=parameters.get("perplexity", 30),
                        n_iter=parameters.get("n_iter", 1000),
                        width=parameters.get("width"),
                        height=parameters.get("height"),
                        font_size=parameters.get("font_size"),
                        rename_sample=common["rename_sample"],
                        font_transparency=parameters.get("font_transparency", 0.6),
                        adjust_label=parameters.get("adjust_label", False),
                        theme=common["theme"],
                        sub_meta=common["sub_meta"],
                        legend_col_num=parameters.get("legend_col_num"),
                        dot_size=parameters.get("dot_size"),
                        early_exaggeration=parameters.get("early_exaggeration", 12.0),
                        learning_rate='auto',
                        random_state=2025
                    )
                if method == "alpha_div":
                    from metax.taxafunc_ploter.diversity_plot import DiversityPlot
                    fig, alpha_df = DiversityPlot(tfa).plot_alpha_diversity(
                        metric=parameters["metric"],
                        sample_list=sample_list,
                        width=parameters.get("width"),
                        height=parameters.get("height"),
                        font_size=parameters.get("font_size"),
                        plot_all_samples=parameters.get("plot_all_samples", False),
                        theme=parameters.get("theme"),
                        sub_meta=parameters.get("sub_meta", "None"),
                        show_fliers=parameters.get("show_fliers", True),
                        legend_col_num=parameters.get("legend_col_num"),
                        rename_sample=parameters.get("rename_sample", False),
                        df_type=table_name,
                        title_name=common["title_name"]
                    )
                    stats_tables[f"alpha_diversity({common['title_name']})"] = alpha_df
                    return fig
                if method == "beta_div":
                    from metax.taxafunc_ploter.diversity_plot import DiversityPlot
                    fig, beta_df = DiversityPlot(tfa).plot_beta_diversity(
                        metric=parameters["metric"],
                        sample_list=sample_list,
                        width=parameters.get("width"),
                        height=parameters.get("height"),
                        font_size=parameters.get("font_size"),
                        font_transparency=parameters.get("font_transparency", 0.6),
                        rename_sample=parameters.get("rename_sample", False),
                        show_label=parameters.get("show_label", True),
                        adjust_label=parameters.get("adjust_label", False),
                        theme=parameters.get("theme"),
                        sub_meta=parameters.get("sub_meta", "None"),
                        legend_col_num=parameters.get("legend_col_num"),
                        dot_size=parameters.get("dot_size"),
                        df_type=table_name,
                        title_name=common["title_name"]
                    )
                    stats_tables[f"beta_diversity_distance_matrix({common['title_name']})"] = beta_df
                    return fig
                if method == "num_bar":
                    return BasicPlot(tfa).plot_number_bar(
                        df=df,
                        title_name=common["title_name"],
                        font_size=parameters.get("font_size"),
                        width=parameters.get("width"),
                        height=parameters.get("height"),
                        theme=parameters.get("theme"),
                        plot_sample=parameters.get("plot_sample", False),
                        show_label=parameters.get("show_label", True),
                        rename_sample=parameters.get("rename_sample", False),
                        legend_col_num=parameters.get("legend_col_num"),
                        sub_meta=parameters.get("sub_meta", "None")
                    )
                if method == "upset":
                    upset_df = BasicPlot(tfa).plot_upset(
                        df=df,
                        title_name=common["title_name"],
                        show_label=parameters.get("show_label", True),
                        width=parameters.get("width"),
                        height=parameters.get("height"),
                        font_size=parameters.get("font_size"),
                        plot_sample=parameters.get("plot_sample", False),
                        sub_meta=parameters.get("sub_meta", "None"),
                        rename_sample=parameters.get("rename_sample", False),
                        show_percentages=parameters.get("show_percentages", True),
                        min_subset_size=parameters.get("min_subset_size", 0),
                        max_subset_rank=parameters.get("max_subset_rank", 10)
                    )
                    stats_tables[f"upset_all({common['title_name']})"] = upset_df
                    return upset_df
                raise NotImplementedError(
                    f"Replay helper does not yet implement plot_basic_info_sns method={method!r}."
                )

            if action_name == "plot_basic_list":
                from metax.taxafunc_ploter.basic_plot import BasicPlot
                from metax.taxafunc_ploter.heatmap_plot import HeatmapPlot

                plot_type = parameters["plot_type"]
                table_name = parameters["table_name"]
                sample_list = parameters.get("sample_list") or getattr(tfa, "sample_list", [])
                selected_items = parameters.get("selected_items") or []
                dft = _metax_table_from_tfa(tfa, table_name)
                dft = dft[sample_list]
                if selected_items and selected_items[0] not in {
                    "All Taxa", "All Functions", "All Peptides", "All Taxa-Functions", "All Proteins", "All Items"
                }:
                    df = dft.loc[selected_items]
                else:
                    df = dft
                if plot_type == "heatmap":
                    df, sample_to_group_dict = tfa.BasicStats.prepare_dataframe_for_heatmap(
                        df=df,
                        sub_meta=parameters.get("sub_meta", "None"),
                        rename_sample=parameters.get("rename_sample", False),
                        plot_mean=parameters.get("plot_mean", False)
                    )
                    if parameters.get("row_cluster", False) or (parameters.get("scale", "None") == 'row'):
                        df = df.drop(df.index[(df == 0).all(axis=1)], errors='ignore')
                    if parameters.get("col_cluster", False) or (parameters.get("scale", "None") == 'col'):
                        df = df.drop(df.columns[(df == 0).all(axis=0)], errors='ignore')
                    return HeatmapPlot(tfa).plot_basic_heatmap(
                        df=df,
                        title=f"Heatmap of {table_name}",
                        fig_size=(int(parameters["width"]), int(parameters["height"])),
                        scale=parameters.get("scale", "None"),
                        row_cluster=parameters.get("row_cluster", False),
                        col_cluster=parameters.get("col_cluster", False),
                        cmap=parameters.get("cmap"),
                        rename_taxa=parameters.get("rename_taxa", False),
                        font_size=parameters.get("font_size", 10),
                        show_all_labels=parameters.get("show_all_labels", (False, False)),
                        linecolor=parameters.get("linecolor", "none"),
                        scale_method=parameters.get("scale_method", "maxmin"),
                        return_type="fig",
                        sample_to_group_dict=sample_to_group_dict,
                    )
                if plot_type == "bar":
                    from metax.taxafunc_ploter.bar_plot import BarPlot
                    df = df.loc[(df!=0).any(axis=1)]
                    js_bar = parameters.get("js_bar", False)
                    if js_bar:
                        pic = BarPlot(tfa, theme=parameters.get("theme", "white")).plot_intensity_bar_js(
                            df=df,
                            width=parameters.get("width") * 100 if parameters.get("width") else None,
                            height=parameters.get("height") * 100 if parameters.get("height") else None,
                            title='',
                            rename_taxa=parameters.get("rename_taxa", False),
                            show_legend=parameters.get("show_legend", True),
                            font_size=parameters.get("font_size"),
                            rename_sample=parameters.get("rename_sample", False),
                            plot_mean=parameters.get("plot_mean", False),
                            plot_percent=parameters.get("plot_percent", False),
                            sub_meta=parameters.get("sub_meta", "None"),
                            show_all_labels=parameters.get("show_all_labels", (False, False)),
                            use_3d=parameters.get("use_3d_for_sub_meta", False)
                        )
                        if "js_width" in parameters:
                            pic.width = parameters["js_width"]
                        if "js_height" in parameters:
                            pic.height = parameters["js_height"]
                        return pic.render_notebook()
                    else:
                        return BarPlot(tfa, theme=parameters.get("theme", "white")).plot_intensity_bar_sns(
                            df=df,
                            width=parameters.get("width"),
                            height=parameters.get("height"),
                            title='',
                            rename_taxa=parameters.get("rename_taxa", False),
                            show_legend=parameters.get("show_legend", True),
                            font_size=parameters.get("font_size"),
                            rename_sample=parameters.get("rename_sample", False),
                            plot_mean=parameters.get("plot_mean", False),
                            plot_percent=parameters.get("plot_percent", False),
                            sub_meta=parameters.get("sub_meta", "None"),
                            plt_theme=parameters.get("plt_theme")
                        )
                if plot_type == "pca":
                    use_3d_pca = parameters.get("use_3d_pca", False)
                    title_name = parameters.get("title_name", table_name)
                    if use_3d_pca:
                        from metax.taxafunc_ploter.pca_plot_js import PcaPlot_js
                        pic = PcaPlot_js(tfa, theme=parameters.get("theme", "white")).plot_pca_pyecharts_3d(
                            df=df,
                            title_name=title_name,
                            show_label=parameters.get("show_label", True),
                            rename_sample=parameters.get("rename_sample", False),
                            width=parameters.get("width"),
                            height=parameters.get("height"),
                            font_size=parameters.get("font_size"),
                            legend_col_num=None,
                        )
                        if "js_width" in parameters:
                            pic.width = parameters["js_width"]
                        if "js_height" in parameters:
                            pic.height = parameters["js_height"]
                        return pic.render_notebook()
                    else:
                        return BasicPlot(tfa).plot_pca_sns(
                            df=df,
                            title_name=title_name,
                            show_label=parameters.get("show_label", True),
                            rename_sample=parameters.get("rename_sample", False),
                            width=parameters.get("width"),
                            height=parameters.get("height"),
                            font_size=parameters.get("font_size"),
                            sub_meta=parameters.get("sub_meta", "None"),
                        )
                if plot_type == "sankey":
                    from metax.taxafunc_ploter.sankey_plot import SankeyPlot
                    pic = SankeyPlot(tfa, theme=parameters.get("theme", "white")).plot_intensity_sankey(
                        df=df,
                        width=parameters.get("width"),
                        height=parameters.get("height"),
                        title=parameters.get("title_new", ""),
                        subtitle=parameters.get("subtitle", ""),
                        font_size=parameters.get("font_size"),
                        sub_meta=parameters.get("sub_meta", "None"),
                        plot_mean=parameters.get("plot_mean", False),
                        show_legend=parameters.get("show_legend", True)
                    )
                    if "js_width" in parameters:
                        pic.width = parameters["js_width"]
                    if "js_height" in parameters:
                        pic.height = parameters["js_height"]
                    return pic.render_notebook()
                if plot_type == "get_table":
                    if parameters.get("plot_mean") and parameters.get("sub_meta", "None") == 'None':
                        df = tfa.BasicStats.get_stats_mean_df_by_group(df)
                    elif parameters.get("sub_meta", "None") != 'None':
                        df, _ = tfa.BasicStats.get_combined_sub_meta_df(
                            df=df,
                            sub_meta=parameters["sub_meta"],
                            rename_sample=parameters.get("rename_sample", False),
                            plot_mean=parameters.get("plot_mean", False)
                        )
                    else:
                        if parameters.get("rename_sample", False):
                            df = tfa.rename_sample(df)
                    if parameters.get("rename_taxa", False):
                        df = tfa.rename_taxa(df)
                    return df
                raise NotImplementedError(
                    f"Replay helper does not yet implement plot_basic_list plot_type={plot_type!r}."
                )

            if action_name == "plot_top_heatmap":
                from metax.taxafunc_ploter.heatmap_plot import HeatmapPlot

                table_name = parameters["table_name"]
                if stats_tables.get(table_name) is None:
                    raise KeyError(
                        f"plot_top_heatmap needs stats_tables[{table_name!r}]. "
                        "Set it to the DataFrame produced by the previous statistical test cell."
                    )
                df = stats_tables[table_name]
                
                common_kwargs = {
                    "fig_size": (int(parameters.get("width", 10)), int(parameters.get("height", 8))),
                    "pvalue": parameters.get("pvalue", 0.05),
                    "scale": parameters.get("scale", "None"),
                    "col_cluster": parameters.get("col_cluster", False),
                    "row_cluster": parameters.get("row_cluster", False),
                    "cmap": None,
                    "rename_taxa": parameters.get("rename_taxa", False),
                    "font_size": parameters.get("font_size", 10),
                    "show_all_labels": parameters.get("show_all_labels", (False, False)),
                    "scale_method": parameters.get("scale_method", "maxmin"),
                    "linecolor": parameters.get("linecolor", "none"),
                    "p_type": parameters.get("p_type", "padj"),
                    "x_filter_list": parameters.get("x_filter_list", []),
                    "y_filter_list": parameters.get("y_filter_list", []),
                    "filter_by_regex": parameters.get("filter_by_regex", False),
                }

                if table_name.startswith('dunnett_test'):
                    return HeatmapPlot(tfa).plot_heatmap_of_dunnett_test_res(
                        df=df,
                        **common_kwargs
                    )
                elif table_name.startswith('deseq2all'):
                    return HeatmapPlot(tfa).plot_heatmap_of_all_condition_res(
                        df=df,
                        res_df_type='deseq2',
                        log2fc_min=parameters.get("log2fc_min", -1),
                        log2fc_max=parameters.get("log2fc_max", 1),
                        three_levels_df_type=parameters.get("three_levels_df_type", "same_trends"),
                        remove_zero_col=parameters.get("remove_zero_col", True),
                        return_type="fig",
                        **common_kwargs
                    )
                elif table_name.startswith('dunnettAllCondtion'):
                    return HeatmapPlot(tfa).plot_heatmap_of_all_condition_res(
                        df=df,
                        res_df_type='dunnett',
                        three_levels_df_type=parameters.get("three_levels_df_type", "same_trends"),
                        remove_zero_col=parameters.get("remove_zero_col", True),
                        return_type="fig",
                        **common_kwargs
                    )
                elif 'taxa-functions' in table_name:
                    title = ""
                    if 'NonSigTaxa_SigFuncs(taxa-functions)' in table_name:
                        title = "Taxa Non-Significant; Related Functions Significantly Different Across Groups"
                    elif 'SigTaxa_NonSigFuncs(taxa-functions)' in table_name:
                        title = "Functions Non-Significant; Related Taxa Significantly Different Across Groups"
                    return HeatmapPlot(tfa).plot_top_taxa_func_heatmap_of_test_res(
                        df=df,
                        top_number=parameters.get("top_num", 20),
                        value_type=parameters.get("sort_by", "padj"),
                        title=title,
                        **common_kwargs
                    )
                else:
                    return HeatmapPlot(tfa).plot_basic_heatmap_of_test_res(
                        df=df,
                        top_number=parameters.get("top_num", 20),
                        value_type=parameters.get("sort_by", "padj"),
                        rename_sample=parameters.get("rename_sample", False),
                        sort_by=parameters.get("sort_by", "padj"),
                        return_type="fig",
                        **common_kwargs
                    )

            if action_name == "plot_deseq2_volcano":
                table_name = parameters["table_name"]
                if stats_tables.get(table_name) is None:
                    raise KeyError(
                        f"plot_deseq2_volcano needs stats_tables[{table_name!r}]. "
                        "Set it to the DESeq2 result DataFrame from the previous statistical test cell."
                    )
                df = stats_tables[table_name]
                if parameters.get("plot_js", False):
                    from metax.taxafunc_ploter.volcano_plot_js import VolcanoPlotJS
                    pic = VolcanoPlotJS(theme=parameters.get("theme", "white")).plot_volcano_js(
                        df,
                        pvalue=parameters.get("pvalue", 0.05),
                        p_type=parameters.get("p_type", "padj"),
                        log2fc_min=parameters.get("log2fc_min", -1),
                        log2fc_max=parameters.get("log2fc_max", 1),
                        title_name=f"{parameters.get('group2')} vs {parameters.get('group1')}",
                        width=parameters.get("width"),
                        height=parameters.get("height"),
                        font_size=parameters.get("font_size"),
                        dot_size=parameters.get("dot_size"),
                    )
                    if "js_width" in parameters:
                        pic.width = parameters["js_width"]
                    if "js_height" in parameters:
                        pic.height = parameters["js_height"]
                    return pic.render_notebook()
                else:
                    from metax.taxafunc_ploter.volcano_plot import VolcanoPlot
                    return VolcanoPlot().plot_volcano(
                        df,
                        pvalue=parameters.get("pvalue", 0.05),
                        p_type=parameters.get("p_type", "padj"),
                        log2fc_min=parameters.get("log2fc_min", -1),
                        log2fc_max=parameters.get("log2fc_max", 1),
                        title_name=f"{parameters.get('group2')} vs {parameters.get('group1')}",
                        width=parameters.get("width"),
                        height=parameters.get("height"),
                        font_size=parameters.get("font_size"),
                        dot_size=parameters.get("dot_size"),
                    )

            if action_name == "plot_trends_cluster":
                from metax.taxafunc_ploter.trends_plot import TrendsPlot
                table_name = parameters["table_name"]
                sample_list = parameters.get("sample_list") or getattr(tfa, "sample_list", [])
                selected_items = parameters.get("selected_items") or []
                dft = _metax_table_from_tfa(tfa, table_name)
                dft = dft[sample_list]
                if selected_items and selected_items[0] not in {
                    "All Taxa", "All Functions", "All Peptides", "All Taxa-Functions", "All Proteins", "All Items"
                }:
                    df = dft.loc[selected_items]
                else:
                    df = dft
                df = df.loc[(df!=0).any(axis=1)]
                num_cluster = parameters.get("num_cluster", 4)
                num_col = parameters.get("num_col", num_cluster)
                if num_col > num_cluster:
                    num_col = num_cluster
                fig, cluster_df = TrendsPlot(tfa).plot_trends(
                    df=df,
                    num_cluster=num_cluster,
                    width=parameters.get("width"),
                    height=parameters.get("height"),
                    title="Cluster",
                    font_size=parameters.get("font_size"),
                    num_col=num_col
                )
                save_table_name = f"cluster({table_name.lower()})"
                stats_tables[save_table_name] = cluster_df
                return fig

            if action_name == "plot_trends_interactive_line":
                from metax.taxafunc_ploter.trends_plot_js import TrendsPlot_js
                table_name = parameters["table_name"]
                cluster_num = parameters["cluster_num"]
                save_table_name = f"cluster({table_name.lower()})"
                if stats_tables.get(save_table_name) is None:
                    raise KeyError(f"plot_trends_interactive_line needs stats_tables[{save_table_name!r}].")
                df = stats_tables[save_table_name].copy()
                df = df[df["Cluster"] == cluster_num].drop("Cluster", axis=1)

                plot_samples = parameters.get("plot_samples", False)
                get_intensity = parameters.get("get_intensity", False)
                condition = parameters.get("condition")

                if plot_samples or get_intensity:
                    dft = _metax_table_from_tfa(tfa, table_name)
                    sample_list = parameters.get("sample_list") or getattr(tfa, "sample_list", [])
                    group_list = parameters.get("group_list") or getattr(tfa, "group_list", [])

                    if get_intensity:
                        if plot_samples:
                            dft = dft[sample_list]
                            extract_row = df.index.tolist()
                            df = dft.loc[extract_row, sample_list]
                        else:
                            dft = tfa.BasicStats.get_stats_mean_df_by_group(dft, condition=condition)
                            extract_row = df.index.tolist()
                            df = dft.loc[extract_row, group_list]
                    else:
                        dft = dft[sample_list]
                        extract_row = df.index.tolist()
                        df = dft.loc[extract_row, sample_list]

                pic = TrendsPlot_js(tfa, theme=parameters.get("theme", "white")).plot_trends_js(
                    df=df,
                    width=parameters.get("width") * 100 if parameters.get("width") else None,
                    height=parameters.get("height") * 100 if parameters.get("height") else None,
                    title=f"Cluster {cluster_num+1} of {table_name}",
                    rename_taxa=parameters.get("rename_taxa", False),
                    show_legend=parameters.get("show_legend", True),
                    add_group_name=plot_samples,
                    font_size=parameters.get("font_size")
                )
                if "js_width" in parameters:
                    pic.width = parameters["js_width"]
                if "js_height" in parameters:
                    pic.height = parameters["js_height"]
                return pic.render_notebook()

            if action_name == "plot_co_expr":
                plot_type = parameters["plot_type"]
                df_type = parameters["df_type"]
                corr_method = parameters["corr_method"]
                sample_list = parameters.get("sample_list") or getattr(tfa, "sample_list", [])
                focus_list = parameters.get("focus_list") or []
                plot_list_only = parameters.get("plot_list_only", False)
                rename_taxa = parameters.get("rename_taxa", False)
                font_size = parameters.get("font_size")

                if plot_type == "heatmap":
                    from metax.taxafunc_ploter.basic_plot import BasicPlot
                    df = tfa.BasicStats.get_correlation(
                        df_type=df_type,
                        sample_list=sample_list,
                        focus_list=focus_list,
                        plot_list_only=plot_list_only,
                        rename_taxa=rename_taxa,
                        method=corr_method
                    )
                    stats_tables[f"{corr_method} correlation heatmap({df_type})"] = df
                    return BasicPlot(tfa).plot_items_corr_heatmap(
                        df=df,
                        title_name=f"{corr_method.capitalize()} Correlation of {df_type}",
                        cluster=True,
                        cmap=parameters.get("cmap"),
                        width=parameters.get("width"),
                        height=parameters.get("height"),
                        font_size=font_size,
                        show_all_labels=parameters.get("show_all_labels", (False, False)),
                        linecolor=parameters.get("linecolor", "none")
                    )

                if plot_type == "network":
                    from metax.taxafunc_ploter.network_plot import NetworkPlot
                    net_params = parameters.get("tf_link_net_params", {})
                    pic, corr_df = NetworkPlot(
                        tfa,
                        show_labels=parameters.get("show_labels", True),
                        rename_taxa=rename_taxa,
                        font_size=font_size,
                        theme=parameters.get("theme", "white"),
                        **net_params
                    ).plot_co_expression_network(
                        df_type=df_type,
                        corr_method=corr_method,
                        corr_threshold=parameters.get("corr_threshold", 0.8),
                        sample_list=sample_list,
                        width=parameters.get("width"),
                        height=parameters.get("height"),
                        focus_list=focus_list,
                        plot_list_only=plot_list_only
                    )
                    stats_tables[f"co-expression_network({df_type})"] = corr_df
                    if "js_width" in parameters:
                        pic.width = parameters["js_width"]
                    if "js_height" in parameters:
                        pic.height = parameters["js_height"]
                    return pic.render_notebook()

            if action_name == "plot_network":
                from metax.taxafunc_ploter.network_plot import NetworkPlot
                net_params = parameters.get("tf_link_net_params", {})
                pic, network_df, attributes_df = NetworkPlot(
                    tfa,
                    show_labels=parameters.get("show_labels", True),
                    rename_taxa=parameters.get("rename_taxa", False),
                    font_size=parameters.get("font_size"),
                    theme=parameters.get("theme", "white"),
                    **net_params
                ).plot_tflink_network(
                    sample_list=parameters.get("sample_list") or getattr(tfa, "sample_list", []),
                    width=parameters.get("width"),
                    height=parameters.get("height"),
                    focus_list=parameters.get("focus_list") or [],
                    plot_list_only=parameters.get("plot_list_only", False),
                    list_only_no_link=parameters.get("list_only_no_link", False)
                )
                stats_tables["taxa-func_network"] = network_df
                stats_tables["taxa-func_network_attributes"] = attributes_df
                if "js_width" in parameters:
                    pic.width = parameters["js_width"]
                if "js_height" in parameters:
                    pic.height = parameters["js_height"]
                return pic.render_notebook()

            if action_name == "plot_tflink_heatmap":
                from metax.taxafunc_ploter.heatmap_plot import HeatmapPlot
                taxa = parameters.get("taxa")
                func = parameters.get("func")
                width = parameters.get("width")
                height = parameters.get("height")
                font_size = parameters.get("font_size")
                scale = parameters.get("scale")
                cmap = parameters.get("cmap")
                rename_taxa = parameters.get("rename_taxa", False)
                show_all_labels = parameters.get("show_all_labels", (False, False))
                plot_mean = parameters.get("plot_mean", False)
                rename_sample = parameters.get("rename_sample", False)
                row_cluster = parameters.get("row_cluster", False)
                col_cluster = parameters.get("col_cluster", False)
                sub_meta = parameters.get("sub_meta", "None")
                linecolor = parameters.get("linecolor", "none")
                return_type = parameters.get("return_type", "fig")
                sample_list = parameters.get("sample_list") or getattr(tfa, "sample_list", [])

                title = ''
                params = {'sample_list': sample_list}
                if taxa:
                    params['taxon_name'] = taxa
                    title = taxa.split('|')[-1] if rename_taxa else taxa
                if func:
                    params['func_name'] = func
                    title = func
                if taxa and func:
                    short_taxa = taxa.split('|')[-1] if rename_taxa else taxa
                    title = f"{short_taxa}\\n{func}"

                df = tfa.GetMatrix.get_intensity_matrix(**params)
                if df.empty:
                    raise ValueError("Intensity matrix is empty for the given taxa/func.")

                df, sample_to_group_dict = tfa.BasicStats.prepare_dataframe_for_heatmap(
                    df=df,
                    sub_meta=sub_meta,
                    rename_sample=rename_sample,
                    plot_mean=plot_mean
                )
                if row_cluster or (scale == 'row'):
                    df = df.drop(df.index[(df == 0).all(axis=1)], errors='ignore')
                if col_cluster or (scale == 'column'):
                    df = df.drop(df.columns[(df == 0).all(axis=0)], errors='ignore')

                fig_res = HeatmapPlot(tfa).plot_basic_heatmap(
                    df=df,
                    title=title,
                    fig_size=(int(width), int(height)) if width and height else (10, 8),
                    scale=scale,
                    row_cluster=row_cluster,
                    col_cluster=col_cluster,
                    cmap=cmap,
                    rename_taxa=rename_taxa,
                    font_size=font_size,
                    show_all_labels=show_all_labels,
                    return_type=return_type,
                    sample_to_group_dict=sample_to_group_dict,
                    linecolor=linecolor
                )
                return fig_res

            if action_name == "plot_tflink_bar":
                from metax.taxafunc_ploter.bar_plot import BarPlot
                taxa = parameters.get("taxa")
                func = parameters.get("func")
                width = parameters.get("width")
                height = parameters.get("height")
                font_size = parameters.get("font_size")
                rename_taxa = parameters.get("rename_taxa", False)
                show_legend = parameters.get("show_legend", True)
                plot_mean = parameters.get("plot_mean", False)
                show_all_labels = parameters.get("show_all_labels", (False, False))
                sub_meta = parameters.get("sub_meta", "None")
                rename_sample = parameters.get("rename_sample", False)
                plot_percent = parameters.get("plot_percent", False)
                sample_list = parameters.get("sample_list") or getattr(tfa, "sample_list", [])

                params = {
                    'sample_list': sample_list,
                    'rename_sample': rename_sample,
                    'plot_percent': plot_percent
                }
                if taxa:
                    params['taxon_name'] = taxa
                if func:
                    params['func_name'] = func
                if rename_taxa:
                    params['rename_taxa'] = rename_taxa
                if width and height:
                    params['width'] = width * 100
                    params['height'] = height * 100
                params['show_legend'] = show_legend
                params['font_size'] = font_size
                params['plot_mean'] = plot_mean
                params['show_all_labels'] = show_all_labels
                params['sub_meta'] = sub_meta

                pic = BarPlot(tfa, theme=parameters.get("theme", "white")).plot_intensity_bar_js(**params)
                if "js_width" in parameters:
                    pic.width = parameters["js_width"]
                if "js_height" in parameters:
                    pic.height = parameters["js_height"]
                return pic.render_notebook()

            if action_name == "plot_tukey":
                from metax.taxafunc_ploter.tukey_plot import TukeyPlot
                table_name = parameters.get("table_name", "tukey_test")
                if stats_tables.get(table_name) is None:
                    raise KeyError(f"plot_tukey needs stats_tables[{table_name!r}].")
                df = stats_tables[table_name]
                return TukeyPlot().plot_tukey(df)

            raise NotImplementedError(
                f"Replay helper does not yet implement action_name={action_name!r}. "
                f"data_source={data_source!r}; parameters are available in this cell."
            )
        """
    )


def _stats_tables_hint(parameters: dict[str, Any]) -> str:
    if parameters.get("data_source") != "statistical_result_table":
        return "stats_tables = {}"
    table_name = parameters.get("table_name", "result_table")
    return (
        f"# Replace None with the DataFrame variable produced by the corresponding stats cell.\n"
        f"stats_tables = {{{table_name!r}: None}}"
    )


def _safe_parameters(parameters: dict[str, Any]) -> dict[str, Any]:
    safe = {}
    for key, value in parameters.items():
        if _is_simple_value(value):
            safe[key] = value
        elif isinstance(value, dict):
            safe[key] = _safe_parameters(value)
        elif isinstance(value, (list, tuple)):
            safe[key] = [_safe_parameters({"value": item})["value"] for item in value]
        else:
            safe[key] = repr(value)
    return safe


def _is_simple_value(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def _python_literal(value: Any) -> str:
    return _format_python_literal(_safe_python_value(value))


def _assignment(name: str, value: Any) -> str:
    return f"{name} = {_python_literal(value)}"


def _safe_python_value(value: Any) -> Any:
    if _is_simple_value(value):
        return value
    if isinstance(value, dict):
        return {key: _safe_python_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return tuple(_safe_python_value(item) for item in value)
    if isinstance(value, list):
        return [_safe_python_value(item) for item in value]
    return repr(value)


def _format_python_literal(value: Any, indent: int = 0) -> str:
    if isinstance(value, str):
        return repr(value)
    if value is None or isinstance(value, (int, float, bool)):
        return repr(value)
    if isinstance(value, tuple):
        return _format_sequence(value, "(", ")", indent)
    if isinstance(value, list):
        return _format_sequence(value, "[", "]", indent)
    if isinstance(value, dict):
        if not value:
            return "{}"
        child_indent = indent + 4
        lines = ["{"]
        for key, item in value.items():
            item_text = _format_python_literal(item, child_indent)
            lines.append(f"{' ' * child_indent}{repr(key)}: {item_text},")
        lines.append(f"{' ' * indent}}}")
        return "\n".join(lines)
    return repr(value)


def _format_sequence(value: list[Any] | tuple[Any, ...], open_char: str, close_char: str, indent: int) -> str:
    if not value:
        return open_char + close_char

    inline_items = [_format_python_literal(item, indent) for item in value]
    inline_text = open_char + ", ".join(inline_items) + close_char
    if _all_scalar_items(value) or (len(inline_text) <= 160 and all("\n" not in item for item in inline_items)):
        if open_char == "(" and len(value) == 1:
            return f"({inline_items[0]},)"
        return inline_text

    child_indent = indent + 4
    lines = [open_char]
    for item in value:
        item_text = _format_python_literal(item, child_indent)
        lines.append(f"{' ' * child_indent}{item_text},")
    lines.append(f"{' ' * indent}{close_char}")
    return "\n".join(lines)


def _all_scalar_items(value: list[Any] | tuple[Any, ...]) -> bool:
    return all(_is_simple_value(item) for item in value)


def _markdown_cell(source: str) -> dict[str, Any]:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }


def _code_cell(source: str) -> dict[str, Any]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def _step_markdown(index: int, step: AnalysisStep) -> str:
    lines = [
        f"## Step {index}: {step.title}",
        "",
        f"- Type: `{step.step_type}`",
        f"- Recorded at: `{step.created_at}`",
    ]
    if step.inputs:
        lines.append(f"- Inputs: `{json.dumps(step.inputs, ensure_ascii=False)}`")
    if step.outputs:
        lines.append(f"- Outputs: `{json.dumps(step.outputs, ensure_ascii=False)}`")
    if step.notes:
        lines.append("")
        lines.extend(step.notes)
    return "\n".join(lines)
