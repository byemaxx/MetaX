from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import AutoReportConfig, load_config_from_yaml
from .workflow import AutoOTFReport


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a MetaX Auto OTF HTML report.")
    parser.add_argument("--otf", help="Path to the OTF table.")
    parser.add_argument("--out", help="Output report directory.")
    parser.add_argument("--meta", help="Path to the metadata table.")
    parser.add_argument("--group", help="Metadata column used for grouping.")
    parser.add_argument("--control", help="Control group inside the grouping column.")
    parser.add_argument("--taxa-levels", help="Comma-separated taxa levels, e.g. p,g,s or all.")
    parser.add_argument("--func", help="Comma-separated function annotation columns, or auto.")
    parser.add_argument("--config", help="YAML configuration file.")
    parser.add_argument("--sample-col-prefix", help="Sample intensity column prefix.")
    parser.add_argument("--peptide-col-name", help="Peptide column name.")
    parser.add_argument("--protein-col-name", help="Protein column name.")
    parser.add_argument("--top-n", type=int, help="Top-N value for report plots.")
    parser.add_argument("--diff-method", choices=["limma", "dunnett"], help="Group-vs-control statistics backend.")
    parser.add_argument("--figure-formats", help="Comma-separated static figure formats: png,svg,pdf.")
    parser.add_argument("--dpi", type=int, help="DPI for raster report figures.")
    parser.add_argument("--run-deseq2", action="store_true", default=None, help="Request optional DESeq2-like analysis.")
    parser.add_argument("--no-diversity", action="store_true", default=None, help="Disable diversity plots.")
    parser.add_argument("--run-network", action="store_true", default=None, help="Enable heavy taxa-function network plots.")
    parser.add_argument("--no-network", action="store_true", default=None, help="Disable network plots.")
    parser.add_argument("--overwrite", action="store_true", default=None, help="Allow writing into an existing output directory.")
    return parser


def config_from_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> AutoReportConfig:
    if args.config:
        config = load_config_from_yaml(args.config)
    else:
        config = AutoReportConfig()

    if args.otf is not None:
        config.input.otf_path = args.otf
    if args.meta is not None:
        config.input.meta_path = args.meta
    if args.out is not None:
        config.report.output_dir = args.out
    if args.group is not None:
        config.analysis.group_meta = args.group
    if args.control is not None:
        config.analysis.control_group = args.control
    if args.taxa_levels is not None:
        config.tables.taxa_levels = _split_csv(args.taxa_levels)
    if args.func is not None:
        config.tables.function_columns = "auto" if args.func == "auto" else _split_csv(args.func)
    if args.sample_col_prefix is not None:
        config.input.sample_col_prefix = args.sample_col_prefix
    if args.peptide_col_name is not None:
        config.input.peptide_col_name = args.peptide_col_name
    if args.protein_col_name is not None:
        config.input.protein_col_name = args.protein_col_name
    if args.top_n is not None:
        config.plots.top_n = args.top_n
    if args.diff_method is not None:
        config.statistics.diff_method = args.diff_method
    if args.figure_formats is not None:
        config.report.figure_formats = [item.lower() for item in _split_csv(args.figure_formats)]
    if args.dpi is not None:
        config.report.dpi = args.dpi
    if args.run_deseq2:
        config.statistics.run_deseq2 = True
    if args.no_diversity:
        config.plots.run_diversity = False
        config.plots.run_alpha_diversity = False
        config.plots.run_beta_diversity = False
    if args.run_network:
        config.plots.run_network = True
    if args.no_network:
        config.plots.run_network = False
    if args.overwrite:
        config.report.overwrite = True

    if not args.config and not config.input.otf_path:
        parser.error("--otf is required unless --config is provided.")
    if not args.config and not args.out:
        parser.error("--out is required unless --config is provided.")
    if not config.input.otf_path:
        parser.error("Config does not define input.otf_path and --otf was not provided.")
    return config


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = config_from_args(args, parser)
        result = AutoOTFReport(config).run()
        print(Path(result.index_html_path))
        return 0
    except Exception as exc:
        print(f"metax-report failed: {exc}", file=sys.stderr)
        return 1


def _split_csv(value: str) -> list[str]:
    if value.lower() == "all":
        return ["all"]
    return [item.strip() for item in value.split(",") if item.strip()]


if __name__ == "__main__":
    raise SystemExit(main())
