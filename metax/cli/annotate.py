from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
import warnings
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from metax.peptide_annotator.annotation_workflow import (
    ANNOTATION_WORKFLOW_API_VERSION,
    AnnotationConfigurationError,
    GlobalOTFAnnotator,
    OptionalDependencyUnavailable,
)
from metax.peptide_annotator.peptide_table_prepare import DIANN_INTENSITY_CANDIDATES
from metax.peptide_annotator.manifest_otf import ManifestOTFAnnotator
from metax.utils.version import __version__


class ExitCode(IntEnum):
    SUCCESS = 0
    INVALID_CONFIGURATION = 2
    MISSING_FILE = 3
    OPTIONAL_DEPENDENCY_UNAVAILABLE = 4
    ANNOTATION_FAILED = 5
    CANCELLED = 130


class AnnotationArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise AnnotationConfigurationError(message)


ANNOTATION_RESULT_SCHEMA_VERSION = "metax.annotation_result.v2"
_CONFIG_PATH_FIELDS = {
    "peptide_table",
    "metaumbra_manifest",
    "taxafunc_db",
    "output",
    "peptide_db",
    "genome_list_file",
    "result_json",
}
_CONFIG_MULTI_PATH_FIELDS = {"digested_genome_folders"}


def _decode_separator(value: str) -> str:
    if value == r"\t":
        return "\t"
    if value == r"\n":
        return "\n"
    return value


def _config_key(value: str) -> str:
    return str(value).strip().replace("-", "_")


def _flatten_config(raw_config: Mapping[str, Any]) -> dict[str, Any]:
    config = {_config_key(key): value for key, value in raw_config.items()}
    flattened: dict[str, Any] = {}
    for section in ("inputs", "options", "metaumbra"):
        section_value = config.pop(section, None)
        if section_value is None:
            continue
        if not isinstance(section_value, Mapping):
            raise AnnotationConfigurationError(f"Config section {section!r} must be a mapping")
        flattened.update({_config_key(key): value for key, value in section_value.items()})

    output_section = config.get("output")
    if isinstance(output_section, Mapping):
        config.pop("output")
        output_values = {_config_key(key): value for key, value in output_section.items()}
        flattened["output"] = output_values.pop("otf", output_values.pop("path", None))
        flattened.update(output_values)

    flattened.update(config)
    if "genome_list" in flattened and "genome_list_file" not in flattened:
        genome_list = flattened.pop("genome_list")
        if isinstance(genome_list, str) and Path(genome_list).suffix.lower() in {
            ".txt", ".tsv", ".csv"
        }:
            flattened["genome_list_file"] = genome_list
        else:
            flattened["selected_genomes"] = genome_list
    return flattened


def _resolve_config_path_value(value: Any, config_dir: Path) -> Any:
    if value is None or not isinstance(value, (str, Path)):
        return value
    raw_value = os.path.expanduser(str(value))
    if not raw_value.strip():
        return raw_value
    candidate = Path(raw_value)
    return raw_value if candidate.is_absolute() else str(config_dir / candidate)


def _resolve_config_paths(config: Mapping[str, Any], config_dir: Path) -> dict[str, Any]:
    resolved = dict(config)
    for field_name in _CONFIG_PATH_FIELDS:
        if field_name in resolved:
            resolved[field_name] = _resolve_config_path_value(
                resolved[field_name], config_dir
            )
    for field_name in _CONFIG_MULTI_PATH_FIELDS:
        if field_name not in resolved:
            continue
        value = resolved[field_name]
        if isinstance(value, (str, Path)):
            resolved[field_name] = _resolve_config_path_value(value, config_dir)
        elif value is not None:
            resolved[field_name] = [
                _resolve_config_path_value(item, config_dir) for item in value
            ]
    return resolved


def load_config_file(path: str | Path) -> dict[str, Any]:
    config_path = Path(path).expanduser()
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    suffix = config_path.suffix.lower()
    try:
        if suffix == ".json":
            loaded = json.loads(config_path.read_text(encoding="utf-8"))
        elif suffix in {".yaml", ".yml"}:
            try:
                import yaml
            except ImportError as exc:
                raise OptionalDependencyUnavailable(
                    "YAML configuration requires PyYAML; install the MetaX annotation dependencies."
                ) from exc
            loaded = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        else:
            raise AnnotationConfigurationError(
                "Configuration file must use .json, .yaml, or .yml"
            )
    except (AnnotationConfigurationError, OptionalDependencyUnavailable):
        raise
    except Exception as exc:
        raise AnnotationConfigurationError(
            f"Failed to parse configuration file {config_path}: {exc}"
        ) from exc
    if loaded is None:
        loaded = {}
    if not isinstance(loaded, Mapping):
        raise AnnotationConfigurationError("Annotation configuration must be a mapping")
    config_path = config_path.resolve()
    config = _resolve_config_paths(
        _flatten_config(loaded),
        config_path.parent,
    )
    requested_api = str(
        config.pop("workflow_api_version", config.pop("api_version", ANNOTATION_WORKFLOW_API_VERSION))
    )
    if requested_api.split(".", 1)[0] != ANNOTATION_WORKFLOW_API_VERSION.split(".", 1)[0]:
        raise AnnotationConfigurationError(
            f"Unsupported workflow API version {requested_api!r}; "
            f"this MetaX supports {ANNOTATION_WORKFLOW_API_VERSION!r}"
        )
    config["config_path"] = str(config_path)
    return config


def _default(defaults: Mapping[str, Any], key: str, fallback: Any) -> Any:
    value = defaults.get(key, fallback)
    return fallback if value is None and fallback is not None else value


def build_parser(defaults: Mapping[str, Any] | None = None) -> argparse.ArgumentParser:
    defaults = dict(defaults or {})
    parser = AnnotationArgumentParser(
        prog="metax-annotate",
        allow_abbrev=False,
        description=(
            "Run peptide-to-OTF annotation from a MetaUmbra manifest, MetaX automatic selection, or an explicit genome list. "
            "CLI arguments override values loaded with --config."
        ),
    )
    parser.add_argument("--config", default=defaults.get("config_path"), help="YAML or JSON workflow configuration")
    parser.add_argument("--result-json", default=defaults.get("result_json"), help="Write the machine-readable execution result to this JSON file")
    parser.add_argument("--peptide-table", default=defaults.get("peptide_table"), help="Input peptide intensity table")
    parser.add_argument(
        "--input-source",
        choices=["metaumbra-manifest", "metax-automatic", "genome-list"],
        default=_default(defaults, "input_source", "metaumbra-manifest"),
        help="Explicit genome-selection source; no file-content mode inference is performed",
    )
    parser.add_argument("--metaumbra-manifest", default=defaults.get("metaumbra_manifest"), help="MetaUmbra genome_selection_manifest.json")
    parser.add_argument("--genome-list-file", default=defaults.get("genome_list_file"), help="Plain text/TSV/CSV genome list for --input-source genome-list")
    parser.add_argument("--selected-genomes", nargs="+", default=defaults.get("selected_genomes"), help="Genome IDs for --input-source genome-list")
    parser.add_argument("--taxafunc-db", default=defaults.get("taxafunc_db"), help="MetaX taxa-function annotation SQLite database")
    parser.add_argument("--output", default=defaults.get("output"), help="Output OTF TSV")
    parser.add_argument("--peptide-db", default=defaults.get("peptide_db"), help="SQLite peptide-to-protein database")
    parser.add_argument(
        "--digested-genome-folders",
        nargs="+",
        default=defaults.get("digested_genome_folders"),
        help="One or more folders containing digested genome TSV files",
    )
    parser.add_argument("--genome-threshold", choices=["auto", "q0.05", "q0.01"], default=_default(defaults, "genome_threshold", "auto"), help="Genome threshold; auto uses the manifest default")
    parser.add_argument("--peptide-col", default=_default(defaults, "peptide_col", "Sequence"))
    parser.add_argument(
        "--intensity-col-prefix",
        default=_default(defaults, "intensity_col_prefix", "Intensity"),
        help="Input intensity-column prefix for metax-automatic and genome-list sources",
    )
    parser.add_argument(
        "--output-sample-col-prefix",
        default=_default(defaults, "output_sample_col_prefix", "Intensity_"),
        choices=["Intensity_"],
        help="Canonical output sample prefix",
    )
    parser.add_argument("--input-sample-col-prefix", default=defaults.get("input_sample_col_prefix"), help="Optional input prefix to strip when matching manifest samples")
    parser.add_argument("--table-separator", default=_default(defaults, "table_separator", r"\t"))
    parser.add_argument("--lca-threshold", type=float, default=_default(defaults, "lca_threshold", 1.0))
    parser.add_argument(
        "--genome-mode",
        action=argparse.BooleanOptionalAction,
        default=_default(defaults, "genome_mode", True),
        help="Enable genome-mode taxa-function annotation",
    )
    parser.add_argument("--distinct-genome-threshold", type=int, default=_default(defaults, "distinct_genome_threshold", 0))
    parser.add_argument("--exclude-protein-startwith", default=defaults.get("exclude_protein_startwith"))
    parser.add_argument("--protein-separator", default=_default(defaults, "protein_separator", ";"))
    parser.add_argument("--protein-genome-separator", default=_default(defaults, "protein_genome_separator", "_"))
    parser.add_argument("--save-per-unit-outputs", action=argparse.BooleanOptionalAction, default=_default(defaults, "save_per_unit_outputs", False))
    parser.add_argument(
        "--duplicate-peptide-handling-mode",
        choices=["sum", "max", "min", "mean", "first", "keep"],
        default=_default(defaults, "duplicate_peptide_handling_mode", "sum"),
    )
    parser.add_argument("--on-missing-sample", choices=["error", "warn-skip"], default=_default(defaults, "on_missing_sample", "error"))
    parser.add_argument("--on-empty-unit", choices=["error", "warn-skip"], default=_default(defaults, "on_empty_unit", "warn-skip"))
    parser.add_argument("--n-jobs", type=int, default=defaults.get("n_jobs"))
    parser.add_argument("--merge-chunksize", type=int, default=_default(defaults, "merge_chunksize", 100_000))
    parser.add_argument("--collect-unique-stats", action=argparse.BooleanOptionalAction, default=_default(defaults, "collect_unique_stats", False))
    parser.add_argument("--diann-intensity-col", choices=DIANN_INTENSITY_CANDIDATES, default=defaults.get("diann_intensity_col"))
    return parser


def _known_config_keys() -> set[str]:
    parser = build_parser()
    return {action.dest for action in parser._actions} | {"config_path"}


def _validate_config_keys(config: Mapping[str, Any]) -> None:
    unknown = sorted(set(config) - _known_config_keys())
    if unknown:
        raise AnnotationConfigurationError(
            f"Unknown annotation configuration keys: {', '.join(unknown)}"
        )


def _normalise_digest_folders(value: Any) -> str | list[str] | None:
    if value is None:
        return None
    if isinstance(value, (str, Path)):
        return str(value)
    values = [str(item) for item in value]
    return values[0] if len(values) == 1 else values


def _require(value: Any, label: str) -> Any:
    if value is None or (isinstance(value, str) and not value.strip()):
        raise AnnotationConfigurationError(f"{label} is required")
    return value


def _validate_scientific_parameters(args: argparse.Namespace) -> None:
    if not 0 <= args.lca_threshold <= 1:
        raise AnnotationConfigurationError("--lca-threshold must be between 0 and 1")
    if args.distinct_genome_threshold < 0:
        raise AnnotationConfigurationError(
            "--distinct-genome-threshold must be greater than or equal to 0"
        )
    if args.n_jobs is not None and args.n_jobs < 1:
        raise AnnotationConfigurationError("--n-jobs must be greater than or equal to 1")


def _run_metadata(
    *,
    mode: str | None,
    exit_code: ExitCode,
    started_at: str,
    started_perf: float,
    run_id: str,
    software: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    finished_at = datetime.now().astimezone()
    software_info = {
        "metax_version": __version__,
        "workflow_api_version": ANNOTATION_WORKFLOW_API_VERSION,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }
    software_info.update(software or {})
    return {
        "id": run_id,
        "status": "success" if exit_code == ExitCode.SUCCESS else "error",
        "exit_code": int(exit_code),
        "mode": mode,
        "started_at": started_at,
        "finished_at": finished_at.isoformat(timespec="milliseconds"),
        "duration_seconds": round(time.perf_counter() - started_perf, 6),
        "software": software_info,
    }


def _path_input(path: Any, *, format_name: str | None = None) -> dict[str, Any]:
    entry: dict[str, Any] = {"path": str(path)}
    if format_name:
        entry["format"] = format_name
    file_path = Path(str(path))
    if file_path.is_file():
        stat = file_path.stat()
        entry["size_bytes"] = int(stat.st_size)
        entry["modified_at"] = datetime.fromtimestamp(
            stat.st_mtime
        ).astimezone().isoformat(timespec="seconds")
    return entry


def _argument_inputs(args: argparse.Namespace | None) -> dict[str, Any]:
    if args is None:
        return {}
    inputs: dict[str, Any] = {}
    path_fields = {
        "config": (getattr(args, "config", None), None),
        "peptide_table": (getattr(args, "peptide_table", None), None),
        "metaumbra_manifest": (
            getattr(args, "metaumbra_manifest", None),
            "json",
        ),
        "taxafunc_database": (getattr(args, "taxafunc_db", None), "sqlite"),
        "peptide_database": (getattr(args, "peptide_db", None), "sqlite"),
        "genome_list": (getattr(args, "genome_list_file", None), None),
    }
    for name, (path, format_name) in path_fields.items():
        if path:
            inputs[name] = _path_input(path, format_name=format_name)
    digest_dirs = getattr(args, "digested_genome_folders", None)
    if digest_dirs:
        values = [digest_dirs] if isinstance(digest_dirs, str) else digest_dirs
        inputs["digested_genome_directories"] = [
            {"path": str(path)} for path in values
        ]
    return inputs


def _effective_parameters(args: argparse.Namespace | None, mode: str | None) -> dict[str, Any]:
    if args is None:
        return {}
    common = [
        "peptide_col",
        "table_separator",
        "lca_threshold",
        "genome_mode",
        "distinct_genome_threshold",
        "exclude_protein_startwith",
        "protein_separator",
        "protein_genome_separator",
        "duplicate_peptide_handling_mode",
        "n_jobs",
        "diann_intensity_col",
        "intensity_col_prefix",
    ]
    manifest_parameters = [
        "genome_threshold",
        "input_sample_col_prefix",
        "output_sample_col_prefix",
        "save_per_unit_outputs",
        "on_missing_sample",
        "on_empty_unit",
        "merge_chunksize",
        "collect_unique_stats",
    ]
    names = common + manifest_parameters
    return {
        name: getattr(args, name)
        for name in names
        if hasattr(args, name) and getattr(args, name) is not None
    }


def _empty_result(
    *,
    mode: str | None,
    exit_code: ExitCode,
    started_at: str,
    started_perf: float,
    run_id: str,
    args: argparse.Namespace | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": ANNOTATION_RESULT_SCHEMA_VERSION,
        "run": _run_metadata(
            mode=mode,
            exit_code=exit_code,
            started_at=started_at,
            started_perf=started_perf,
            run_id=run_id,
        ),
        "inputs": _argument_inputs(args),
        "parameters": _effective_parameters(args, mode),
        "stages": {},
        "genome_selection": {},
        "metrics": {},
        "outputs": {},
        "diagnostics": {"warnings": [], "error": None},
    }


def _write_result_json(path: str | None, result: Mapping[str, Any]) -> None:
    if not path:
        return
    result_path = Path(path)
    if not result_path.parent.is_dir():
        raise FileNotFoundError(f"Result JSON directory not found: {result_path.parent}")
    temporary_path = result_path.with_name(f".{result_path.name}.tmp")
    temporary_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(result_path)


def _run_manifest(args: argparse.Namespace) -> tuple[Any, list[str]]:
    _require(args.peptide_table, "--peptide-table")
    _require(args.metaumbra_manifest, "--metaumbra-manifest")
    _require(args.taxafunc_db, "--taxafunc-db")
    _require(args.output, "--output")
    if bool(args.peptide_db) == bool(args.digested_genome_folders):
        raise AnnotationConfigurationError(
            "Exactly one of --peptide-db or --digested-genome-folders is required"
        )
    genome_threshold = None if args.genome_threshold == "auto" else args.genome_threshold
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        result = ManifestOTFAnnotator(
            peptide_table_path=args.peptide_table,
            metaumbra_manifest_path=args.metaumbra_manifest,
            taxafunc_anno_db_path=args.taxafunc_db,
            output_path=args.output,
            db_path=args.peptide_db,
            digested_genome_folders=_normalise_digest_folders(args.digested_genome_folders),
            genome_threshold=genome_threshold,
            peptide_col=args.peptide_col,
            input_sample_col_prefix=args.input_sample_col_prefix,
            output_sample_col_prefix=args.output_sample_col_prefix,
            table_separator=_decode_separator(args.table_separator),
            lca_threshold=args.lca_threshold,
            genome_mode=args.genome_mode,
            distinct_genome_threshold=args.distinct_genome_threshold,
            exclude_protein_startwith=args.exclude_protein_startwith,
            protein_separator=args.protein_separator,
            protein_genome_separator=args.protein_genome_separator,
            save_per_unit_outputs=args.save_per_unit_outputs,
            duplicate_peptide_handling_mode=args.duplicate_peptide_handling_mode,
            on_missing_sample=args.on_missing_sample,
            on_empty_unit=args.on_empty_unit,
            n_jobs=args.n_jobs,
            merge_chunksize=args.merge_chunksize,
            collect_unique_stats=args.collect_unique_stats,
            diann_intensity_col=args.diann_intensity_col,
        ).run()
    return result, [str(item.message) for item in recorded]


def _run_non_manifest(args: argparse.Namespace) -> tuple[Any, list[str]]:
    _require(args.peptide_table, "--peptide-table")
    _require(args.taxafunc_db, "--taxafunc-db")
    _require(args.output, "--output")
    if bool(args.peptide_db) == bool(args.digested_genome_folders):
        raise AnnotationConfigurationError(
            "Exactly one of --peptide-db or --digested-genome-folders is required"
        )
    selection_mode = "automatic" if args.input_source == "metax-automatic" else "provided"
    if selection_mode == "provided" and not args.genome_list_file and not args.selected_genomes:
        raise AnnotationConfigurationError(
            "--input-source genome-list requires --genome-list-file or --selected-genomes"
        )
    if selection_mode == "automatic" and (args.genome_list_file or args.selected_genomes):
        raise AnnotationConfigurationError(
            "Genome-list options are only valid with --input-source genome-list"
        )
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        result = GlobalOTFAnnotator(
            peptide_table_path=args.peptide_table,
            output_path=args.output,
            taxafunc_anno_db_path=args.taxafunc_db,
            db_path=args.peptide_db,
            digested_genome_folders=_normalise_digest_folders(args.digested_genome_folders),
            selection_mode=selection_mode,
            selected_genomes=args.selected_genomes,
            genome_list_path=args.genome_list_file,
            peptide_col=args.peptide_col,
            intensity_col_prefix=args.intensity_col_prefix,
            table_separator=_decode_separator(args.table_separator),
            lca_threshold=args.lca_threshold,
            genome_mode=args.genome_mode,
            distinct_genome_threshold=args.distinct_genome_threshold,
            exclude_protein_startwith=args.exclude_protein_startwith,
            protein_separator=args.protein_separator,
            protein_genome_separator=args.protein_genome_separator,
            duplicate_peptide_handling_mode=args.duplicate_peptide_handling_mode,
            n_jobs=args.n_jobs,
            diann_intensity_col=args.diann_intensity_col,
            selected_genome_source=(
                args.genome_list_file or "CLI --selected-genomes"
                if selection_mode == "provided"
                else None
            ),
        ).run()
    return result, [str(item.message) for item in recorded]


def _success_result(
    mode: str,
    run_result: Any,
    warning_messages: list[str],
    *,
    args: argparse.Namespace,
    started_at: str,
    started_perf: float,
    run_id: str,
    annotation_duration: float,
) -> dict[str, Any]:
    workflow_software = dict(getattr(run_result, "software", {}))
    result = _empty_result(
        mode=mode,
        exit_code=ExitCode.SUCCESS,
        started_at=started_at,
        started_perf=started_perf,
        run_id=run_id,
        args=args,
    )
    result["run"] = _run_metadata(
        mode=mode,
        exit_code=ExitCode.SUCCESS,
        started_at=started_at,
        started_perf=started_perf,
        run_id=run_id,
        software=workflow_software,
    )
    result["diagnostics"]["warnings"] = warning_messages + list(
        getattr(run_result, "warnings", [])
    )

    run_output_path = getattr(run_result, "output_path", args.output)
    artifacts_dir = Path(run_output_path).with_name(
        f"{Path(run_output_path).stem}_artifacts"
    )
    per_unit_dir = artifacts_dir / "per_unit"
    summary_path = getattr(run_result, "summary_path", None)
    info_path = getattr(run_result, "info_path", None)
    result["stages"] = {
        "manifest_otf_annotation": {
            "status": "success",
            "duration_seconds": round(annotation_duration, 6),
        }
    }
    result["genome_selection"] = {
        "method": "metaumbra_genome_selection_manifest",
        "threshold": getattr(
            run_result,
            "selected_genome_threshold",
            args.genome_threshold,
        ),
    }
    sample_columns = [
        name
        for name in getattr(run_result, "column_names", [])
        if str(name).startswith("Intensity_")
    ]
    result["metrics"] = {
        "units": {
            "completed": int(getattr(run_result, "completed_units", 0)),
            "skipped": int(getattr(run_result, "skipped_units", 0)),
        },
        "output": {
            "rows": int(getattr(run_result, "rows", 0)),
            "columns": int(getattr(run_result, "column_count", 0)),
            "sample_columns": sample_columns,
        },
    }
    outputs: dict[str, Any] = {
        "otf": _path_input(run_output_path, format_name="tsv"),
    }
    outputs["otf"].update(
        {
            "rows": int(getattr(run_result, "rows", 0)),
            "columns": int(getattr(run_result, "column_count", 0)),
        }
    )
    if info_path:
        outputs["annotation_summary"] = _path_input(info_path, format_name="text")
    if summary_path:
        outputs["unit_summary"] = _path_input(summary_path, format_name="tsv")
    if args.save_per_unit_outputs and per_unit_dir.is_dir():
        outputs["per_unit_directory"] = {"path": str(per_unit_dir)}
    sample_mapping_path = artifacts_dir / "unit_sample_column_mapping.tsv"
    if sample_mapping_path.is_file():
        outputs["sample_mapping"] = _path_input(
            sample_mapping_path, format_name="tsv"
        )
    result["outputs"] = outputs
    result["manifest"] = {
        "path": str(args.metaumbra_manifest),
        "schema_version": getattr(run_result, "manifest_schema_version", None),
    }
    result["number_of_units"] = int(getattr(run_result, "completed_units", 0)) + int(
        getattr(run_result, "skipped_units", 0)
    )
    result["selected_threshold"] = getattr(run_result, "selected_genome_threshold", args.genome_threshold)
    result["per_unit_summary"] = outputs.get("unit_summary")
    result["input_source"] = mode
    return result


def _success_result_non_manifest(
    mode: str,
    run_result: Any,
    warning_messages: list[str],
    *,
    args: argparse.Namespace,
    started_at: str,
    started_perf: float,
    run_id: str,
) -> dict[str, Any]:
    result = _empty_result(
        mode=mode,
        exit_code=ExitCode.SUCCESS,
        started_at=started_at,
        started_perf=started_perf,
        run_id=run_id,
        args=args,
    )
    result["run"] = _run_metadata(
        mode=mode,
        exit_code=ExitCode.SUCCESS,
        started_at=started_at,
        started_perf=started_perf,
        run_id=run_id,
        software=getattr(run_result, "software", {}),
    )
    result["inputs"] = dict(getattr(run_result, "inputs", {}))
    result["parameters"] = dict(getattr(run_result, "parameters", {}))
    result["stages"] = dict(getattr(run_result, "stages", {}))
    result["genome_selection"] = dict(getattr(run_result, "genome_selection", {}))
    result["metrics"] = dict(getattr(run_result, "metrics", {}))
    result["outputs"] = dict(getattr(run_result, "outputs", {}))
    result["diagnostics"]["warnings"] = warning_messages + list(
        getattr(run_result, "warnings", [])
    )
    result["input_source"] = mode
    result["manifest"] = None
    result["number_of_units"] = None
    result["selected_threshold"] = None
    result["per_unit_summary"] = None
    return result


def main(argv: list[str] | None = None) -> int:
    started_perf = time.perf_counter()
    stage_started = started_perf
    started_at = datetime.now().astimezone().isoformat(timespec="milliseconds")
    run_id = str(uuid4())
    argv = list(sys.argv[1:] if argv is None else argv)
    pre_parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    pre_parser.add_argument("--config")
    pre_parser.add_argument("--result-json")
    pre_args, _ = pre_parser.parse_known_args(argv)
    result_json_path = pre_args.result_json
    mode: str | None = None
    args: argparse.Namespace | None = None
    result: dict[str, Any] | None = None
    failure_stage = "configuration"

    try:
        config = load_config_file(pre_args.config) if pre_args.config else {}
        result_json_path = result_json_path or config.get("result_json")
        _validate_config_keys(config)
        failure_stage = "argument_parsing"
        stage_started = time.perf_counter()
        parser = build_parser(config)
        args = parser.parse_args(argv)
        mode = args.input_source
        if pre_args.config:
            args.config = config["config_path"]
        _validate_scientific_parameters(args)
        result_json_path = args.result_json
        if result_json_path and not Path(result_json_path).parent.is_dir():
            raise FileNotFoundError(
                f"Result JSON directory not found: {Path(result_json_path).parent}"
            )
        failure_stage = "annotation"
        stage_started = time.perf_counter()
        if args.input_source == "metaumbra-manifest":
            if args.genome_list_file or args.selected_genomes:
                raise AnnotationConfigurationError(
                    "Genome-list options are only valid with --input-source genome-list"
                )
            run_result, warning_messages = _run_manifest(args)
        else:
            if args.metaumbra_manifest:
                raise AnnotationConfigurationError(
                    "--metaumbra-manifest is only valid with --input-source metaumbra-manifest"
                )
            run_result, warning_messages = _run_non_manifest(args)
        annotation_duration = time.perf_counter() - stage_started
        if args.input_source == "metaumbra-manifest":
            result = _success_result(
                mode,
                run_result,
                warning_messages,
                args=args,
                started_at=started_at,
                started_perf=started_perf,
                run_id=run_id,
                annotation_duration=annotation_duration,
            )
        else:
            result = _success_result_non_manifest(
                mode,
                run_result,
                warning_messages,
                args=args,
                started_at=started_at,
                started_perf=started_perf,
                run_id=run_id,
            )
        failure_stage = "result_serialization"
        stage_started = time.perf_counter()
        _write_result_json(result_json_path, result)
        print(f"MetaX annotation completed: {getattr(run_result, 'output_path', args.output)}")
        if result_json_path:
            print(f"Result JSON: {result_json_path}")
        return int(ExitCode.SUCCESS)
    except KeyboardInterrupt as exc:
        exit_code = ExitCode.CANCELLED
        message = "Annotation cancelled"
        error = exc
    except AnnotationConfigurationError as exc:
        exit_code = ExitCode.INVALID_CONFIGURATION
        message = str(exc)
        error = exc
    except FileNotFoundError as exc:
        exit_code = ExitCode.MISSING_FILE
        message = str(exc)
        error = exc
    except OptionalDependencyUnavailable as exc:
        exit_code = ExitCode.OPTIONAL_DEPENDENCY_UNAVAILABLE
        message = str(exc)
        error = exc
    except Exception as exc:
        exit_code = ExitCode.ANNOTATION_FAILED
        message = str(exc)
        error = exc

    print(f"metax-annotate failed: {message}", file=sys.stderr)
    result = _empty_result(
        mode=mode,
        exit_code=exit_code,
        started_at=started_at,
        started_perf=started_perf,
        run_id=run_id,
        args=args,
    )
    if exit_code == ExitCode.CANCELLED:
        result["run"]["status"] = "cancelled"
    category_by_exit_code = {
        ExitCode.INVALID_CONFIGURATION: "configuration",
        ExitCode.MISSING_FILE: "input",
        ExitCode.OPTIONAL_DEPENDENCY_UNAVAILABLE: "dependency",
        ExitCode.ANNOTATION_FAILED: "processing",
        ExitCode.CANCELLED: "cancelled",
    }
    result["stages"] = {
        failure_stage: {
            "status": "cancelled" if exit_code == ExitCode.CANCELLED else "error",
            "duration_seconds": round(time.perf_counter() - stage_started, 6),
        }
    }
    result["diagnostics"]["error"] = {
        "stage": failure_stage,
        "category": category_by_exit_code[exit_code],
        "type": type(error).__name__,
        "message": message,
    }
    try:
        _write_result_json(result_json_path, result)
    except Exception as result_exc:
        print(f"Could not write result JSON: {result_exc}", file=sys.stderr)
    return int(exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
