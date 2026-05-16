import os
import tempfile
from pathlib import Path

_mpl_config_dir = Path(tempfile.gettempdir()) / "metax_matplotlib"
_mpl_config_dir.mkdir(parents=True, exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(_mpl_config_dir)

from .config import (
    AnalysisConfig,
    AutoReportConfig,
    HtmlReportConfig,
    InputConfig,
    PlotConfig,
    PreprocessConfig,
    StatsConfig,
    TableConfig,
    load_config_from_yaml,
    save_config_to_yaml,
)
from .workflow import AutoOTFReport, ReportResult

__all__ = [
    "AnalysisConfig",
    "AutoOTFReport",
    "AutoReportConfig",
    "HtmlReportConfig",
    "InputConfig",
    "PlotConfig",
    "PreprocessConfig",
    "ReportResult",
    "StatsConfig",
    "TableConfig",
    "load_config_from_yaml",
    "save_config_to_yaml",
]
