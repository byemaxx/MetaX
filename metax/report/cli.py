from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from metax.utils.version import __version__

from .config import AutoReportConfig, load_config_from_yaml
from .workflow import AutoOTFReport

REPORT_WORKFLOW_API_VERSION = "1.0"
REPORT_RESULT_SCHEMA_VERSION = "metax.report_result.v1"
REPORT_CAPABILITIES_SCHEMA_VERSION = "metax.report_capabilities.v1"


class ReportCLIValidationError(ValueError):
    """Command-line validation failure that should be reported as exit code 2."""


class ReportArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self._print_message(f"{self.prog}: error: {message}\n", sys.stderr)
        raise ReportCLIValidationError(message)


def build_parser() -> argparse.ArgumentParser:
    parser = ReportArgumentParser(description="Generate a MetaX Auto OTF HTML report.")
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
    parser.add_argument("--result-json", help="Write the versioned machine-readable result contract.")
    parser.add_argument("--capabilities", action="store_true", help="Print the report CLI capability contract as JSON and exit.")
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
    result_json_path = _find_result_json_path(argv)
    parser = build_parser()
    config: AutoReportConfig | None = None
    try:
        args = parser.parse_args(argv)
        result_json_path = args.result_json
        if args.capabilities:
            print(
                json.dumps(
                    {
                        "schema_version": REPORT_CAPABILITIES_SCHEMA_VERSION,
                        "available": True,
                        "metax_version": __version__,
                        "workflow_api_version": REPORT_WORKFLOW_API_VERSION,
                        "result_schema_version": REPORT_RESULT_SCHEMA_VERSION,
                    },
                    indent=2,
                )
            )
            return 0

        config = config_from_args(args, parser)
        result = AutoOTFReport(config).run()
        payload = _success_result(config, result)
        _write_result_json(result_json_path, payload)
        print(Path(result.index_html_path))
        return 0
    except ReportCLIValidationError as exc:
        _write_result_json(
            result_json_path,
            _terminal_result("failed", config, error=str(exc)),
        )
        return 2
    except KeyboardInterrupt:
        _write_result_json(
            result_json_path,
            _terminal_result("cancelled", config, error="Report generation was cancelled."),
        )
        return 130
    except Exception as exc:
        _write_result_json(result_json_path, _terminal_result("failed", config, error=str(exc)))
        print(f"metax-report failed: {exc}", file=sys.stderr)
        return 1


def _success_result(config: AutoReportConfig, result: Any) -> dict[str, Any]:
    index_html = Path(result.index_html_path).expanduser().resolve()
    if not index_html.is_file() or index_html.stat().st_size == 0:
        raise RuntimeError(
            f"Report backend did not produce a non-empty index.html: {index_html}"
        )
    registry = result.registry.to_dict()
    return {
        **_terminal_result("completed", config),
        "outputs": {
            "output_directory": str(Path(result.output_dir).resolve()),
            "index_html": str(index_html),
            "summary_json": str(Path(result.summary_json_path).resolve()),
            "reproducibility_artifacts": {
                key: str(Path(path).resolve())
                for key, path in result.reproducibility_artifacts.items()
            },
        },
        "summary": {
            "tables": len(registry["tables"]),
            "statistics": len(registry["stats"]),
            "figures": len(registry["figures"]),
            "interactive_html": len(registry["html"]),
        },
        "warnings": registry["warnings"],
        "errors": registry["errors"],
        "runtime": registry["runtime"],
    }


def _terminal_result(
    status: str,
    config: AutoReportConfig | None,
    *,
    error: str = "",
) -> dict[str, Any]:
    otf_path = _absolute_path(config.input.otf_path) if config else None
    metadata_path = _absolute_path(config.input.meta_path) if config else None
    return {
        "schema_version": REPORT_RESULT_SCHEMA_VERSION,
        "workflow_api_version": REPORT_WORKFLOW_API_VERSION,
        "status": status,
        "software": {"metax_version": __version__},
        "inputs": {
            "otf_table": otf_path,
            "metadata_table": metadata_path,
        },
        "outputs": {},
        "summary": {},
        "warnings": [],
        "errors": [{"message": error, "source": "metax-report"}] if error else [],
        "runtime": {},
    }


def _write_result_json(path: str | None, payload: dict[str, Any]) -> None:
    if not path:
        return
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    try:
        temporary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temporary_path.replace(output_path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _absolute_path(path: str | None) -> str | None:
    if not path:
        return None
    return str(Path(path).expanduser().resolve())


def _find_result_json_path(argv: list[str] | None) -> str | None:
    """Find the result path before full parsing so parser errors can be recorded."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    for index, argument in enumerate(arguments):
        if argument.startswith("--result-json="):
            return argument.split("=", 1)[1] or None
        if argument == "--result-json" and index + 1 < len(arguments):
            candidate = arguments[index + 1]
            if not candidate.startswith("-"):
                return candidate
    return None


def _split_csv(value: str) -> list[str]:
    if value.lower() == "all":
        return ["all"]
    return [item.strip() for item in value.split(",") if item.strip()]


if __name__ == "__main__":
    raise SystemExit(main())
