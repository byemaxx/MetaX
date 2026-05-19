from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any, Optional, Union

import yaml


@dataclass
class InputConfig:
    otf_path: str = ""
    meta_path: Optional[str] = None
    peptide_col_name: str = "Sequence"
    protein_col_name: str = "Proteins"
    sample_col_prefix: str = "Intensity"
    any_df_mode: bool = False
    custom_col_name: Optional[str] = None


@dataclass
class AnalysisConfig:
    group_meta: Optional[str] = None
    control_group: Optional[str] = None
    condition_meta: Optional[str] = None
    main_taxa_level: str = "s"
    main_function: Optional[str] = None


@dataclass
class PreprocessConfig:
    quant_method: str = "sum"
    outlier_detect_method: str | list[Any] = "missing-value"
    outlier_handle_method: str = "fillzero"
    detection_by_group: Optional[str] = None
    handle_by_group: Optional[str] = None
    normalize_method: str = "None"
    transform_method: str = "None"
    batch_meta: Optional[str] = None
    taxa_peptide_num_threshold: int = 3
    func_peptide_num_threshold: int = 3
    otf_peptide_num_threshold: int = 3


@dataclass
class TableConfig:
    taxa_levels: list[str] = field(default_factory=lambda: ["p", "g", "s"])
    function_columns: Union[str, list[str]] = "auto"
    generate_taxa_tables: bool = True
    generate_function_tables: bool = True
    generate_otf_tables: bool = True
    generate_protein_table: bool = False
    split_func: bool = False
    split_by: str = "|"
    keep_unknown_func: bool = False
    share_intensity: bool = False

    def __post_init__(self) -> None:
        if isinstance(self.taxa_levels, str):
            self.taxa_levels = _split_csv(self.taxa_levels)
        if isinstance(self.function_columns, str) and self.function_columns != "auto":
            self.function_columns = _split_csv(self.function_columns)


@dataclass
class StatsConfig:
    run_anova: bool = True
    run_ttest: bool = True
    run_group_vs_control: bool = True
    diff_method: str = "dunnett"
    p_adjust_method: str = "fdr_bh"
    alpha: float = 0.05
    log2fc_cutoff: float = 1.0
    pseudo_count: float = 1.0
    min_prevalence: float = 0.1
    run_deseq2: bool = False


@dataclass
class PlotConfig:
    top_n: int = 20
    heatmap_top_n: int = 50
    network_top_n: int = 50
    run_overview: bool = True
    run_pca: bool = True
    run_pca_3d: bool = False
    run_tsne: bool = False
    run_correlation: bool = True
    run_heatmap: bool = True
    run_box: bool = True
    run_bar: bool = True
    run_barplot: bool = True
    run_upset: bool = False
    run_alpha_diversity: bool = True
    run_beta_diversity: bool = True
    run_diversity: bool = True
    run_volcano: bool = True
    run_sankey: bool = True
    run_sunburst: bool = True
    run_treemap: bool = True
    run_network: bool = False


@dataclass
class HtmlReportConfig:
    title: str = "MetaX Auto Report"
    output_dir: str = "report_output"
    embed_interactive_html: bool = False
    show_top_rows: int = 20
    copy_static_assets: bool = True
    overwrite: bool = False


@dataclass
class AutoReportConfig:
    input: InputConfig = field(default_factory=InputConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    preprocessing: PreprocessConfig = field(default_factory=PreprocessConfig)
    tables: TableConfig = field(default_factory=TableConfig)
    statistics: StatsConfig = field(default_factory=StatsConfig)
    plots: PlotConfig = field(default_factory=PlotConfig)
    report: HtmlReportConfig = field(default_factory=HtmlReportConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "AutoReportConfig":
        data = data or {}
        return cls(
            input=_dataclass_from_dict(InputConfig, data.get("input", {})),
            analysis=_dataclass_from_dict(AnalysisConfig, data.get("analysis", {})),
            preprocessing=_dataclass_from_dict(PreprocessConfig, data.get("preprocessing", {})),
            tables=_dataclass_from_dict(TableConfig, data.get("tables", {})),
            statistics=_dataclass_from_dict(StatsConfig, data.get("statistics", {})),
            plots=_dataclass_from_dict(PlotConfig, data.get("plots", {})),
            report=_dataclass_from_dict(HtmlReportConfig, data.get("report", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_config_from_yaml(path: str | Path) -> AutoReportConfig:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML config must contain a mapping at the top level: {config_path}")
    return AutoReportConfig.from_dict(data)


def save_config_to_yaml(config: AutoReportConfig, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(config.to_dict(), handle, sort_keys=False, allow_unicode=False)


def save_config_used(config: AutoReportConfig, output_dir: str | Path) -> None:
    save_config_to_yaml(config, Path(output_dir) / "config_used.yaml")


def _dataclass_from_dict(cls: type, data: dict[str, Any] | None):
    data = data or {}
    valid_fields = {item.name for item in fields(cls)}
    kwargs = {key: value for key, value in data.items() if key in valid_fields}
    return cls(**kwargs)


def _split_csv(value: str) -> list[str]:
    if value.lower() == "all":
        return ["all"]
    return [item.strip() for item in value.split(",") if item.strip()]
