from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from .config import AutoReportConfig, load_config_from_yaml
from .table_builder import DEFAULT_EXCLUDED_FUNCTION_COLUMNS
from .workflow import AutoOTFReport


NON_FUNCTION_COLUMNS = {"Taxon"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a MetaX Auto OTF HTML report.")
    parser.add_argument("--otf", help="Path to the OTF table.")
    parser.add_argument("--out", help="Output report directory.")
    parser.add_argument("--meta", help="Path to the metadata table.")
    parser.add_argument("--group", help="Metadata column used for grouping.")
    parser.add_argument("--control", help="Control group inside the grouping column.")
    parser.add_argument("--taxa-levels", help="Comma-separated taxa levels, e.g. p,g,s or all.")
    parser.add_argument(
        "--func",
        help=(
            "Comma-separated function annotation columns; or one of: auto, all, prompt. "
            "Use prompt to list available function columns in the OTF file and interactively choose."
        ),
    )
    parser.add_argument(
        "--list-func",
        action="store_true",
        help="List available function annotation columns in the OTF file and exit.",
    )
    parser.add_argument(
        "--select-func",
        action="store_true",
        help="Interactively select function annotation columns from the OTF file (same as --func prompt).",
    )
    parser.add_argument("--config", help="YAML configuration file.")
    parser.add_argument("--sample-col-prefix", help="Sample intensity column prefix.")
    parser.add_argument("--peptide-col-name", help="Peptide column name.")
    parser.add_argument("--protein-col-name", help="Protein column name.")
    parser.add_argument("--top-n", type=int, help="Top-N value for report plots.")
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
    if args.func is not None or args.select_func:
        func_value = "prompt" if args.select_func else str(args.func)
        func_value_lower = func_value.strip().lower()
        if func_value_lower == "auto":
            config.tables.function_columns = "auto"
        elif func_value_lower == "all":
            config.tables.function_columns = _detect_available_function_columns(config.input.otf_path)
        elif func_value_lower in {"prompt", "select"}:
            config.tables.function_columns = _prompt_function_columns(config.input.otf_path)
        else:
            config.tables.function_columns = _split_csv(func_value)
    if args.sample_col_prefix is not None:
        config.input.sample_col_prefix = args.sample_col_prefix
    if args.peptide_col_name is not None:
        config.input.peptide_col_name = args.peptide_col_name
    if args.protein_col_name is not None:
        config.input.protein_col_name = args.protein_col_name
    if args.top_n is not None:
        config.plots.top_n = args.top_n
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
        if args.list_func:
            if args.otf:
                otf_path = args.otf
            elif args.config:
                config = load_config_from_yaml(args.config)
                if not config.input.otf_path:
                    parser.error("Config does not define input.otf_path and --otf was not provided.")
                otf_path = config.input.otf_path
            else:
                parser.error("--otf is required for --list-func unless --config is provided.")

            available = _detect_available_function_columns(otf_path)
            if not available:
                print("No function annotation columns detected (requires both <name> and <name>_prop columns).")
                return 0
            print("Available function annotation columns:")
            for item in available:
                print(f"- {item}")
            return 0
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


def _detect_available_function_columns(otf_path: str | Path) -> list[str]:
    path = Path(otf_path)
    if not path.exists():
        raise FileNotFoundError(f"OTF file does not exist: {path}")
    header = _read_tsv_header(path)
    column_set = set(header)
    detected: set[str] = set()
    for col in header:
        if not str(col).endswith("_prop"):
            continue
        base = str(col)[: -len("_prop")]
        if base and base in column_set:
            detected.add(base)

    # Keep stable order for usability.
    available = [name for name in header if name in detected]
    # De-dup while preserving order.
    seen: set[str] = set()
    ordered: list[str] = []
    for name in available:
        if name in NON_FUNCTION_COLUMNS or name in seen:
            continue
        ordered.append(name)
        seen.add(name)
    return ordered


def _read_tsv_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        return next(reader)


def _prompt_function_columns(otf_path: str | Path) -> list[str]:
    available = _detect_available_function_columns(otf_path)
    if not available:
        raise ValueError(
            "No function annotation columns detected in OTF (requires both <name> and <name>_prop columns)."
        )

    print("Detected function annotation columns in OTF:")
    for idx, name in enumerate(available, start=1):
        excluded = " (excluded by default)" if name in DEFAULT_EXCLUDED_FUNCTION_COLUMNS else ""
        print(f"  {idx:>3}. {name}{excluded}")

    prompt = (
        "Select functions by number or name (comma-separated). "
        "Examples: 1,2,5  |  KEGG_ko_name,Gene  |  all\n"
        "> "
    )
    raw = input(prompt).strip()
    if not raw:
        raise ValueError("No function selection provided.")
    if raw.lower() == "all":
        return list(available)

    tokens = [item.strip() for item in raw.split(",") if item.strip()]
    selected: list[str] = []
    for token in tokens:
        if token.isdigit():
            idx = int(token)
            if idx < 1 or idx > len(available):
                raise ValueError(f"Invalid function index: {idx}. Valid range: 1..{len(available)}")
            name = available[idx - 1]
        else:
            # Case-insensitive match; must be unique.
            matches = [item for item in available if item.lower() == token.lower()]
            if not matches:
                raise ValueError(f"Unknown function column: {token}. Use --list-func to see options.")
            if len(matches) > 1:
                raise ValueError(f"Ambiguous function column name: {token}")
            name = matches[0]
        if name not in selected:
            selected.append(name)

    if not selected:
        raise ValueError("No functions selected.")
    return selected


if __name__ == "__main__":
    raise SystemExit(main())
