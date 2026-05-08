from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ReportPaths:
    output_dir: Path

    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir)
        self.tables_dir = self.output_dir / "tables"
        self.taxa_tables_dir = self.tables_dir / "taxa"
        self.function_tables_dir = self.tables_dir / "function"
        self.otf_tables_dir = self.tables_dir / "otf"
        self.protein_tables_dir = self.tables_dir / "protein"
        self.qc_tables_dir = self.tables_dir / "qc"
        self.stats_dir = self.output_dir / "stats"
        self.taxa_stats_dir = self.stats_dir / "taxa"
        self.function_stats_dir = self.stats_dir / "function"
        self.otf_stats_dir = self.stats_dir / "otf"
        self.figures_dir = self.output_dir / "figures"
        self.overview_figures_dir = self.figures_dir / "overview"
        self.basic_figures_dir = self.figures_dir / "basic"
        self.composition_figures_dir = self.figures_dir / "composition"
        self.differential_figures_dir = self.figures_dir / "differential"
        self.taxa_function_figures_dir = self.figures_dir / "taxa_function"
        self.assets_dir = self.output_dir / "assets"
        self.logs_dir = self.output_dir / "logs"

    def create(self) -> None:
        for path in self.all_dirs():
            path.mkdir(parents=True, exist_ok=True)

    def all_dirs(self) -> list[Path]:
        return [
            self.output_dir,
            self.tables_dir,
            self.taxa_tables_dir,
            self.function_tables_dir,
            self.otf_tables_dir,
            self.protein_tables_dir,
            self.qc_tables_dir,
            self.stats_dir,
            self.taxa_stats_dir,
            self.function_stats_dir,
            self.otf_stats_dir,
            self.figures_dir,
            self.overview_figures_dir,
            self.basic_figures_dir,
            self.composition_figures_dir,
            self.differential_figures_dir,
            self.taxa_function_figures_dir,
            self.assets_dir,
            self.logs_dir,
        ]
