import json
import ast
import shutil
import sqlite3
import subprocess
import sys
import tomllib
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest
from packaging.requirements import Requirement

import metax.cli.annotate as annotate_cli
import metax.cli.report as report_launcher
import metax.peptide_annotator.annotation_workflow as annotation_workflow
from metax.cli.annotate import (
    ANNOTATION_RESULT_SCHEMA_VERSION,
    ExitCode,
    build_parser,
    load_config_file,
    main,
)
from metax.peptide_annotator.annotation_workflow import (
    ANNOTATION_WORKFLOW_API_VERSION,
    AnnotationConfigurationError,
    GlobalOTFAnnotator,
)
from metax.gui import launcher as gui_launcher


def _write_peptide_db(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        connection.execute(
            "CREATE TABLE peptide_proteins (peptide TEXT PRIMARY KEY, proteins TEXT)"
        )
        connection.executemany(
            "INSERT INTO peptide_proteins VALUES (?, ?)",
            [
                ("PEPA", json.dumps(["g1_p1", "g2_p2"])),
                ("PEPB", json.dumps(["g2_p3"])),
            ],
        )


def _write_taxafunc_db(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE id2taxa (ID TEXT PRIMARY KEY, Taxa TEXT)")
        connection.execute(
            "CREATE TABLE id2annotation (ID TEXT PRIMARY KEY, KEGG_ko TEXT)"
        )
        connection.executemany(
            "INSERT INTO id2taxa VALUES (?, ?)",
            [
                ("g1", "d__Bacteria;p__P1;c__C1;o__O1;f__F1;g__G1;s__S1"),
                ("g2", "d__Bacteria;p__P2;c__C2;o__O2;f__F2;g__G2;s__S2"),
            ],
        )
        connection.executemany(
            "INSERT INTO id2annotation VALUES (?, ?)",
            [("g1_p1", "K00001"), ("g2_p2", "K00002"), ("g2_p3", "K00003")],
        )


@pytest.fixture
def annotation_inputs(tmp_path):
    peptide_table = tmp_path / "peptides.tsv"
    pd.DataFrame(
        {
            "Sequence": ["PEPA", "PEPB"],
            "Intensity_s1": [10.0, 0.0],
            "Intensity_s2": [20.0, 5.0],
        }
    ).to_csv(peptide_table, sep="\t", index=False)
    peptide_db = tmp_path / "peptide.db"
    taxafunc_db = tmp_path / "taxafunc.db"
    _write_peptide_db(peptide_db)
    _write_taxafunc_db(taxafunc_db)
    return peptide_table, peptide_db, taxafunc_db


def test_global_annotation_cli_writes_result_json(annotation_inputs, tmp_path):
    peptide_table, peptide_db, taxafunc_db = annotation_inputs
    output = tmp_path / "global_otf.tsv"
    result_json = tmp_path / "global_result.json"

    exit_code = main(
        [
            "--mode",
            "global",
            "--peptide-table",
            str(peptide_table),
            "--peptide-db",
            str(peptide_db),
            "--taxafunc-db",
            str(taxafunc_db),
            "--output",
            str(output),
            "--selection-mode",
            "provided",
            "--selected-genomes",
            "g1",
            "--result-json",
            str(result_json),
        ]
    )

    assert exit_code == ExitCode.SUCCESS
    assert output.is_file()
    result = json.loads(result_json.read_text(encoding="utf-8"))
    assert result["schema_version"] == ANNOTATION_RESULT_SCHEMA_VERSION
    assert set(result) == {
        "schema_version",
        "run",
        "inputs",
        "parameters",
        "stages",
        "genome_selection",
        "metrics",
        "outputs",
        "diagnostics",
    }
    assert result["run"]["status"] == "success"
    assert result["run"]["mode"] == "global"
    assert result["run"]["software"]["workflow_api_version"] == ANNOTATION_WORKFLOW_API_VERSION
    assert result["run"]["duration_seconds"] >= 0
    assert result["parameters"]["selection_mode"] == "provided"
    assert result["genome_selection"]["genomes_selected"] == 1
    assert result["metrics"]["mapping"]["peptides_before_mapping"] == 2
    assert result["metrics"]["mapping"]["peptides_after_mapping"] == 1
    assert result["metrics"]["output"]["rows"] == 1
    assert result["outputs"]["otf"]["path"] == str(output)
    assert Path(result["outputs"]["annotation_summary"]["path"]).is_file()
    assert result["diagnostics"] == {"warnings": [], "error": None}
    assert "artifacts" not in result


def test_global_annotation_cli_reports_renamed_output_when_target_exists(
    annotation_inputs,
    tmp_path,
    capsys,
):
    peptide_table, peptide_db, taxafunc_db = annotation_inputs
    requested_output = tmp_path / "global_otf.tsv"
    requested_output.write_text("stale output\n", encoding="utf-8")
    result_json = tmp_path / "global_result.json"
    result_json.write_text("stale result\n", encoding="utf-8")

    exit_code = main(
        [
            "--mode",
            "global",
            "--peptide-table",
            str(peptide_table),
            "--peptide-db",
            str(peptide_db),
            "--taxafunc-db",
            str(taxafunc_db),
            "--output",
            str(requested_output),
            "--selection-mode",
            "provided",
            "--selected-genomes",
            "g1",
            "--result-json",
            str(result_json),
        ]
    )

    assert exit_code == ExitCode.SUCCESS
    assert requested_output.read_text(encoding="utf-8") == "stale output\n"
    result = json.loads(result_json.read_text(encoding="utf-8"))
    actual_output = Path(result["outputs"]["otf"]["path"])
    actual_info = Path(result["outputs"]["annotation_summary"]["path"])
    assert actual_output != requested_output
    assert actual_output.is_file()
    assert actual_info == actual_output.with_name(f"{actual_output.stem}_info.txt")
    assert actual_info.is_file()
    assert f"MetaX annotation completed: {actual_output}" in capsys.readouterr().out


def test_global_cli_accepts_long_diann_parquet(annotation_inputs, tmp_path):
    _peptide_table, peptide_db, taxafunc_db = annotation_inputs
    parquet = tmp_path / "report.parquet"
    pd.DataFrame(
        {
            "Run": ["s1.raw", "s2.raw"],
            "Stripped.Sequence": ["PEPA", "PEPA"],
            "Precursor.Normalised": [10.0, 20.0],
        }
    ).to_parquet(parquet, index=False)
    output = tmp_path / "diann_otf.tsv"
    result_json = tmp_path / "diann_result.json"

    exit_code = main(
        [
            "--mode",
            "global",
            "--peptide-table",
            str(parquet),
            "--peptide-db",
            str(peptide_db),
            "--taxafunc-db",
            str(taxafunc_db),
            "--output",
            str(output),
            "--selection-mode",
            "provided",
            "--selected-genomes",
            "g1",
            "--diann-intensity-col",
            "Precursor.Normalised",
            "--result-json",
            str(result_json),
        ]
    )

    assert exit_code == ExitCode.SUCCESS
    result = json.loads(result_json.read_text(encoding="utf-8"))
    peptide_input = result["inputs"]["peptide_table"]
    assert peptide_input["format"] == "diann_parquet"
    assert peptide_input["diann"]["intensity_column"] == "Precursor.Normalised"
    assert result["metrics"]["input"] == {
        "rows": 2,
        "columns": 3,
        "rows_with_required_values": 2,
        "runs": 2,
        "unique_peptides": 1,
        "aggregated_run_peptide_rows": 2,
        "prepared_peptides": 1,
        "sample_columns": 2,
    }
    assert set(result["metrics"]["output"]["samples"]) == {
        "Intensity_s1",
        "Intensity_s2",
    }
    output_columns = pd.read_csv(output, sep="\t", nrows=0).columns.tolist()
    assert "Intensity_s1" in output_columns
    assert "Intensity_s2" in output_columns


def test_global_backend_preserves_metaumbra_provenance(monkeypatch, tmp_path):
    peptide_table = tmp_path / "peptides.tsv"
    pd.DataFrame(
        {
            "Sequence": ["PEPA"],
            "Evidence": [0.9],
            "Q.Value": [0.001],
            "Intensity_s1": [10.0],
        }
    ).to_csv(peptide_table, sep="\t", index=False)
    digests = tmp_path / "digests"
    digests.mkdir()
    taxafunc_db = tmp_path / "taxafunc.db"
    taxafunc_db.touch()
    output = tmp_path / "otf.tsv"
    captured = {}

    def fake_scoring(**kwargs):
        pd.DataFrame(
            {"genome_id": ["g1", "g2"], "qvalue": [0.01, 0.2]}
        ).to_csv(kwargs["output_path"], sep="\t", index=False)
        return {"output": kwargs["output_path"], "metaumbra_version": "1.3.7"}

    class FakeMapper:
        original_peptides_before_mapping = 1
        peptides_after_mapping = 1
        removed_peptides_no_matched = 0
        selected_proteins_num = 1
        selected_genomes_num = 1
        protein_ranked_table = ["g1_p1"]
        annotation_run_stats = {}
        annotation_output_metrics = {
            "rows": 1,
            "columns": 3,
            "sample_columns": ["Intensity_s1"],
        }

        def __init__(self, **kwargs):
            self.output_path = Path(kwargs["output_path"])

        def all_in_one(self, **kwargs):
            captured.update(kwargs["genome_selection_metadata"])
            dataframe = pd.DataFrame(
                {
                    "Sequence": ["PEPA"],
                    "Proteins": ["g1_p1"],
                    "Intensity_s1": [10.0],
                }
            )
            dataframe.to_csv(self.output_path, sep="\t", index=False)
            return dataframe

    monkeypatch.setattr(annotation_workflow, "run_metaumbra_scoring", fake_scoring)
    monkeypatch.setattr(annotation_workflow, "peptideProteinsMapper", FakeMapper)

    run_result = GlobalOTFAnnotator(
        peptide_table_path=str(peptide_table),
        output_path=str(output),
        taxafunc_anno_db_path=str(taxafunc_db),
        digested_genome_folders=str(digests),
        selection_mode="metaumbra",
        metaumbra_peptide_score_col="Evidence",
        metaumbra_peptide_error_col="Q.Value",
        metaumbra_single_peptide_error_rate_upper_bound=0.01,
        metaumbra_genome_qvalue_cutoff=0.05,
    ).run()

    assert captured["metaumbra_genome_presence_path"].endswith(
        "_metaumbra_genome_presence.tsv"
    )
    assert captured["metaumbra_version"] == "1.3.7"
    assert captured["metaumbra_peptide_score_col"] == "Evidence"
    assert captured["metaumbra_peptide_error_col"] == "Q.Value"
    assert captured["metaumbra_single_peptide_error_rate_upper_bound"] == 0.01
    assert captured["metaumbra_genome_qvalue_cutoff"] == 0.05
    assert captured["selected_genomes_from_metaumbra_count"] == 1
    assert captured["selected_genomes_input_count"] == 0
    assert run_result.genome_selection["method"] == "metaumbra"
    assert run_result.genome_selection["source"].endswith(
        "_metaumbra_genome_presence.tsv"
    )


def test_unit_specific_annotation_cli_writes_summary_contract(
    annotation_inputs,
    tmp_path,
):
    peptide_table, peptide_db, taxafunc_db = annotation_inputs
    manifest = tmp_path / "unit_specific_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": "metaumbra.unit_specific_manifest.v1",
                "default_genome_threshold": "q0.05",
                "files": {},
                "units": {
                    "u1": {
                        "sample_columns": ["s1"],
                        "n_samples": 1,
                        "genome_ids_q005": ["g1"],
                        "genome_ids_q001": ["g1"],
                    },
                    "u2": {
                        "sample_columns": ["s2"],
                        "n_samples": 1,
                        "genome_ids_q005": ["g2"],
                        "genome_ids_q001": ["g2"],
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "unit_otf.tsv"
    output.write_text("stale unit output\n", encoding="utf-8")
    result_json = tmp_path / "unit_result.json"

    exit_code = main(
        [
            "--mode",
            "unit-specific",
            "--peptide-table",
            str(peptide_table),
            "--unit-specific-manifest",
            str(manifest),
            "--peptide-db",
            str(peptide_db),
            "--taxafunc-db",
            str(taxafunc_db),
            "--output",
            str(output),
            "--result-json",
            str(result_json),
        ]
    )

    assert exit_code == ExitCode.SUCCESS
    assert output.read_text(encoding="utf-8") == "stale unit output\n"
    result = json.loads(result_json.read_text(encoding="utf-8"))
    assert result["run"]["mode"] == "unit-specific"
    actual_output = Path(result["outputs"]["otf"]["path"])
    assert actual_output != output
    assert actual_output.is_file()
    assert Path(result["outputs"]["annotation_summary"]["path"]).is_file()
    unit_summary = Path(result["outputs"]["unit_summary"]["path"])
    assert unit_summary.is_file()
    assert unit_summary.parent == actual_output.with_name(
        f"{actual_output.stem}_artifacts"
    )
    assert "per_unit_directory" not in result["outputs"]
    assert result["metrics"]["units"] == {"completed": 2, "skipped": 0}
    assert result["genome_selection"]["method"] == "unit_specific_manifest"
    assert result["genome_selection"]["threshold"] == "q0.05"


def test_removed_unit_specific_alias_is_rejected():
    with pytest.raises(AnnotationConfigurationError, match="unrecognized arguments"):
        build_parser().parse_args(["--unit-specific"])


def test_global_cli_preserves_gui_metaumbra_scoring_default():
    args = build_parser().parse_args([])

    assert args.metaumbra_single_peptide_error_rate_upper_bound == 0.3
    assert GlobalOTFAnnotator(
        peptide_table_path="input.tsv",
        output_path="output.tsv",
    ).metaumbra_single_peptide_error_rate_upper_bound == 0.3


@pytest.mark.parametrize(
    ("parameter", "value", "message"),
    [
        ("protein_peptide_coverage_cutoff", 0, "protein_peptide_coverage_cutoff"),
        ("protein_peptide_coverage_cutoff", 1.1, "protein_peptide_coverage_cutoff"),
        ("metaumbra_genome_qvalue_cutoff", -0.1, "metaumbra_genome_qvalue_cutoff"),
        (
            "metaumbra_single_peptide_error_rate_upper_bound",
            1.1,
            "metaumbra_single_peptide_error_rate_upper_bound",
        ),
        ("distinct_genome_threshold", -1, "distinct_genome_threshold"),
        ("n_jobs", 0, "n_jobs"),
    ],
)
def test_global_backend_rejects_invalid_scientific_parameters(
    annotation_inputs,
    tmp_path,
    parameter,
    value,
    message,
):
    peptide_table, peptide_db, taxafunc_db = annotation_inputs
    kwargs = {
        "peptide_table_path": str(peptide_table),
        "output_path": str(tmp_path / "invalid.tsv"),
        "taxafunc_anno_db_path": str(taxafunc_db),
        "db_path": str(peptide_db),
        "selection_mode": "automatic",
        parameter: value,
    }

    with pytest.raises(AnnotationConfigurationError, match=message):
        GlobalOTFAnnotator(**kwargs)._validate()


def test_yaml_config_is_parsed_and_cli_values_can_override(tmp_path):
    config_path = tmp_path / "annotation.yaml"
    config_path.write_text(
        """
api_version: "1.0"
mode: global
inputs:
  peptide_table: input.tsv
  peptide_db: peptides.db
  taxafunc_db: taxafunc.db
output:
  otf: configured.tsv
  result_json: result.json
options:
  selection_mode: provided
  selected_genomes: [g1, g2]
""".strip(),
        encoding="utf-8",
    )

    config = load_config_file(config_path)

    assert config["mode"] == "global"
    assert config["output"] == str(tmp_path / "configured.tsv")
    assert config["result_json"] == str(tmp_path / "result.json")
    assert config["peptide_table"] == str(tmp_path / "input.tsv")
    assert config["peptide_db"] == str(tmp_path / "peptides.db")
    assert config["taxafunc_db"] == str(tmp_path / "taxafunc.db")
    assert config["selected_genomes"] == ["g1", "g2"]
    parsed = build_parser(config).parse_args(["--output", "overridden.tsv"])
    assert parsed.output == "overridden.tsv"


@pytest.mark.parametrize(
    ("selection_mode", "selected_genomes", "genome_list", "digest_dirs", "expected"),
    [
        (None, ["g1"], None, [], "provided"),
        (None, [], "genomes.txt", [], "provided"),
        (None, [], None, ["digests"], "metaumbra"),
        (None, [], None, [], "automatic"),
        ("automatic", [], None, ["digests"], "automatic"),
    ],
)
def test_global_selection_mode_resolution(
    selection_mode,
    selected_genomes,
    genome_list,
    digest_dirs,
    expected,
):
    assert annotation_workflow.resolve_global_selection_mode(
        selection_mode,
        selected_genomes=selected_genomes,
        genome_list_path=genome_list,
        digested_genome_folders=digest_dirs,
    ) == expected


@pytest.mark.parametrize(
    ("selection_mode", "selected_genomes", "genome_list", "digest_dirs"),
    [
        ("provided", [], None, []),
        ("automatic", ["g1"], None, []),
        ("metaumbra", ["g1"], None, ["digests"]),
        ("metaumbra-only", [], "genomes.txt", ["digests"]),
        ("provided", ["g1"], "genomes.txt", []),
    ],
)
def test_global_selection_mode_rejects_contradictory_inputs(
    selection_mode,
    selected_genomes,
    genome_list,
    digest_dirs,
):
    with pytest.raises(AnnotationConfigurationError):
        annotation_workflow.resolve_global_selection_mode(
            selection_mode,
            selected_genomes=selected_genomes,
            genome_list_path=genome_list,
            digested_genome_folders=digest_dirs,
        )


def test_metaumbra_mode_requires_digest_directories_when_run(tmp_path):
    peptide_table = tmp_path / "peptides.tsv"
    peptide_table.write_text("Sequence\tEvidence\tQ.Value\nPEPA\t1\t0.01\n", encoding="utf-8")

    annotator = GlobalOTFAnnotator(
        peptide_table_path=str(peptide_table),
        output_path=str(tmp_path / "genome_presence.tsv"),
        selection_mode="metaumbra-only",
    )

    with pytest.raises(
        AnnotationConfigurationError,
        match="requires digested_genome_folders",
    ):
        annotator._validate()


@pytest.mark.parametrize("folder_count", [1, 2])
def test_metaumbra_command_encodes_digest_directories_as_one_argument(
    tmp_path,
    folder_count,
):
    digest_dirs = [
        tmp_path / f"digest folder {index}" for index in range(1, folder_count + 1)
    ]
    command = annotation_workflow._build_metaumbra_scoring_command(
        peptide_table_path=str(tmp_path / "peptides with spaces.tsv"),
        digested_genome_folders=[str(path) for path in digest_dirs],
        output_path=str(tmp_path / "output with spaces.tsv"),
        peptide_col="Sequence",
        peptide_score_col="Evidence",
        peptide_error_col="Q.Value",
        single_peptide_error_rate_upper_bound=0.3,
    )

    option_index = command.index("--genome-digest-dirs")
    assert command[option_index + 1] == ";".join(str(path) for path in digest_dirs)
    assert command[option_index + 2] == "--output"


def test_config_paths_follow_config_directory_and_cli_overrides_follow_cwd(
    annotation_inputs,
    tmp_path,
    monkeypatch,
):
    peptide_table, peptide_db, taxafunc_db = annotation_inputs
    config_dir = tmp_path / "portable config"
    config_dir.mkdir()
    results_dir = config_dir / "results"
    results_dir.mkdir()
    for source in (peptide_table, peptide_db, taxafunc_db):
        shutil.copy2(source, config_dir / source.name)

    config_path = config_dir / "annotation.json"
    config_path.write_text(
        json.dumps(
            {
                "mode": "global",
                "inputs": {
                    "peptide_table": peptide_table.name,
                    "peptide_db": peptide_db.name,
                    "taxafunc_db": taxafunc_db.name,
                },
                "output": {
                    "otf": "results/configured.tsv",
                    "result_json": "results/configured.json",
                },
                "options": {"selected_genomes": ["g1"]},
            }
        ),
        encoding="utf-8",
    )
    launch_dir = tmp_path / "different working directory"
    launch_dir.mkdir()
    monkeypatch.chdir(launch_dir)

    assert main(["--config", str(config_path)]) == ExitCode.SUCCESS
    configured_output = results_dir / "configured.tsv"
    configured_result = results_dir / "configured.json"
    assert configured_output.is_file()
    result = json.loads(configured_result.read_text(encoding="utf-8"))
    assert result["parameters"]["selection_mode"] == "provided"
    assert result["genome_selection"]["source"] == "selected_genomes"
    assert result["outputs"]["otf"]["path"] == str(configured_output)
    assert result["inputs"]["config"]["path"] == str(config_path)

    assert main(
        [
            "--config",
            str(config_path),
            "--output",
            "cli-override.tsv",
            "--result-json",
            "cli-override.json",
        ]
    ) == ExitCode.SUCCESS
    assert (launch_dir / "cli-override.tsv").is_file()
    override_result = json.loads(
        (launch_dir / "cli-override.json").read_text(encoding="utf-8")
    )
    assert override_result["outputs"]["otf"]["path"] == "cli-override.tsv"


def test_config_path_resolution_preserves_absolute_paths_and_resolves_lists(
    tmp_path,
):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    absolute_digest = tmp_path / "absolute digest"
    absolute_digest.mkdir()
    absolute_table = tmp_path / "absolute.tsv"
    config_path = config_dir / "annotation.json"
    config_path.write_text(
        json.dumps(
            {
                "inputs": {
                    "peptide_table": str(absolute_table),
                    "digested_genome_folders": [
                        "relative digest",
                        str(absolute_digest),
                    ],
                }
            }
        ),
        encoding="utf-8",
    )

    config = load_config_file(config_path)

    assert config["peptide_table"] == str(absolute_table)
    assert config["digested_genome_folders"] == [
        str(config_dir / "relative digest"),
        str(absolute_digest),
    ]


def test_metaumbra_only_preserves_existing_output_and_reports_actual_path(
    monkeypatch,
    tmp_path,
):
    peptide_table = tmp_path / "peptides.tsv"
    peptide_table.write_text(
        "Sequence\tEvidence\tQ.Value\nPEPA\t1\t0.01\n",
        encoding="utf-8",
    )
    digest_dir = tmp_path / "digests"
    digest_dir.mkdir()
    requested_output = tmp_path / "genome_presence.tsv"
    requested_output.write_text("stale genome presence\n", encoding="utf-8")

    def fake_scoring(**kwargs):
        pd.DataFrame(
            {"genome_id": ["g1"], "qvalue": [0.01]}
        ).to_csv(kwargs["output_path"], sep="\t", index=False)
        return {"output": kwargs["output_path"], "metaumbra_version": "1.3.7"}

    monkeypatch.setattr(annotation_workflow, "run_metaumbra_scoring", fake_scoring)
    result = GlobalOTFAnnotator(
        peptide_table_path=str(peptide_table),
        output_path=str(requested_output),
        digested_genome_folders=str(digest_dir),
        selection_mode="metaumbra-only",
    ).run()

    actual_output = Path(result.output_path)
    assert requested_output.read_text(encoding="utf-8") == "stale genome presence\n"
    assert actual_output != requested_output
    assert actual_output.is_file()
    assert result.outputs["genome_presence"]["path"] == str(actual_output)
    assert result.genome_selection["source"] == str(actual_output)


def test_config_rejects_incompatible_api_version(tmp_path):
    config_path = tmp_path / "annotation.json"
    config_path.write_text(
        json.dumps({"api_version": "2.0", "mode": "global"}),
        encoding="utf-8",
    )

    with pytest.raises(AnnotationConfigurationError, match="Unsupported workflow API"):
        load_config_file(config_path)


def test_missing_input_uses_missing_file_exit_code_and_result_json(tmp_path):
    result_json = tmp_path / "failed.json"
    exit_code = main(
        [
            "--mode",
            "global",
            "--peptide-table",
            str(tmp_path / "missing.tsv"),
            "--peptide-db",
            str(tmp_path / "missing.db"),
            "--taxafunc-db",
            str(tmp_path / "missing_taxafunc.db"),
            "--output",
            str(tmp_path / "out.tsv"),
            "--selection-mode",
            "automatic",
            "--result-json",
            str(result_json),
        ]
    )

    assert exit_code == ExitCode.MISSING_FILE
    result = json.loads(result_json.read_text(encoding="utf-8"))
    assert result["run"]["status"] == "error"
    assert result["run"]["exit_code"] == ExitCode.MISSING_FILE
    assert result["diagnostics"]["error"] == {
        "stage": "annotation",
        "category": "input",
        "type": "FileNotFoundError",
        "message": f"Peptide table not found: {tmp_path / 'missing.tsv'}",
    }
    assert result["stages"]["annotation"]["status"] == "error"


def test_invalid_configuration_uses_exit_code_two_and_result_json(tmp_path):
    result_json = tmp_path / "invalid.json"

    exit_code = main(["--result-json", str(result_json)])

    assert exit_code == ExitCode.INVALID_CONFIGURATION
    result = json.loads(result_json.read_text(encoding="utf-8"))
    assert result["run"]["exit_code"] == ExitCode.INVALID_CONFIGURATION
    assert result["diagnostics"]["error"]["type"] == "AnnotationConfigurationError"
    assert result["diagnostics"]["error"]["category"] == "configuration"


def test_invalid_scientific_parameter_uses_configuration_exit_code(tmp_path):
    result_json = tmp_path / "invalid_parameter.json"

    exit_code = main(
        [
            "--mode",
            "unit-specific",
            "--n-jobs",
            "0",
            "--result-json",
            str(result_json),
        ]
    )

    assert exit_code == ExitCode.INVALID_CONFIGURATION
    result = json.loads(result_json.read_text(encoding="utf-8"))
    assert result["diagnostics"]["error"]["category"] == "configuration"
    assert "--n-jobs" in result["diagnostics"]["error"]["message"]


@pytest.mark.parametrize(
    ("exception", "expected_code", "expected_status"),
    [
        (
            annotate_cli.OptionalDependencyUnavailable("missing optional runtime"),
            ExitCode.OPTIONAL_DEPENDENCY_UNAVAILABLE,
            "error",
        ),
        (RuntimeError("annotation failed"), ExitCode.ANNOTATION_FAILED, "error"),
        (KeyboardInterrupt(), ExitCode.CANCELLED, "cancelled"),
    ],
)
def test_runtime_failures_use_stable_exit_codes_and_json(
    monkeypatch,
    tmp_path,
    exception,
    expected_code,
    expected_status,
):
    class FakeGlobalAnnotator:
        def __init__(self, **_kwargs):
            pass

        def run(self):
            raise exception

    monkeypatch.setattr(annotate_cli, "GlobalOTFAnnotator", FakeGlobalAnnotator)
    result_json = tmp_path / f"result_{int(expected_code)}.json"

    exit_code = main(
        [
            "--mode",
            "global",
            "--peptide-table",
            "input.tsv",
            "--output",
            "output.tsv",
            "--result-json",
            str(result_json),
        ]
    )

    assert exit_code == expected_code
    result = json.loads(result_json.read_text(encoding="utf-8"))
    assert result["run"]["status"] == expected_status
    assert result["run"]["exit_code"] == expected_code
    assert result["diagnostics"]["error"]["stage"] == "annotation"


def test_annotation_cli_import_does_not_import_pyqt():
    code = (
        "import sys; import metax; import metax.cli.annotate; "
        "assert not any(name.startswith('PyQt') for name in sys.modules)"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr


def test_packaging_defines_headless_analyzer_report_and_desktop_profiles():
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    project = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))["project"]
    base_names = {Requirement(requirement).name.lower() for requirement in project["dependencies"]}
    gui_names = {
        Requirement(requirement).name.lower()
        for requirement in project["optional-dependencies"]["gui"]
    }
    full_names = {
        Requirement(requirement).name.lower()
        for requirement in project["optional-dependencies"]["full"]
    }
    gui_requirements = "\n".join(project["optional-dependencies"]["gui"]).lower()
    analyzer_names = {
        Requirement(requirement).name.lower()
        for requirement in project["optional-dependencies"]["analyzer"]
    }
    report_names = {
        Requirement(requirement).name.lower()
        for requirement in project["optional-dependencies"]["report"]
    }

    qt_names = {"pyqt5", "pyqtwebengine", "qt-material", "qtawesome"}
    assert base_names.isdisjoint(qt_names)
    assert analyzer_names.isdisjoint(qt_names)
    assert report_names.isdisjoint(qt_names)
    assert {
        "scipy",
        "scikit-learn",
        "joblib",
        "statsmodels",
        "numba",
        "inmoose",
    } <= analyzer_names
    assert analyzer_names <= report_names
    assert {
        "matplotlib",
        "seaborn",
        "adjusttext",
        "upsetplot",
        "pyecharts",
        "distinctipy",
        "jinja2",
    } <= report_names
    assert report_names <= gui_names
    assert "pyqt5" in gui_names
    assert "metaumbra[gui-pyqt5]" in gui_requirements
    assert gui_names == full_names
    assert "packaging" in gui_names
    assert "python-dateutil" not in gui_names
    assert "pyproject-toml" not in gui_names
    assert project["scripts"]["metax"] == "metax.gui.launcher:main"
    assert project["scripts"]["metax-report"] == "metax.cli.report:main"


def test_gui_launcher_explains_how_to_install_missing_gui(monkeypatch, capsys):
    def fail_import(_name):
        raise ModuleNotFoundError("No module named 'PyQt5'", name="PyQt5")

    monkeypatch.setattr(gui_launcher.importlib, "import_module", fail_import)

    assert gui_launcher.main() == ExitCode.OPTIONAL_DEPENDENCY_UNAVAILABLE
    error = capsys.readouterr().err
    assert 'pip install "MetaXTools[gui]"' in error
    assert "PyQt5" in error


def test_gui_launcher_delegates_to_existing_desktop_entrypoint(monkeypatch):
    fake_gui = SimpleNamespace(runGUI=lambda: 17)
    monkeypatch.setattr(gui_launcher.importlib, "import_module", lambda _name: fake_gui)

    assert gui_launcher.main() == 17


def test_report_launcher_explains_how_to_install_missing_report_stack(
    monkeypatch,
    capsys,
):
    def fail_import(_name):
        raise ModuleNotFoundError("No module named 'jinja2'", name="jinja2")

    monkeypatch.setattr(report_launcher.importlib, "import_module", fail_import)

    assert report_launcher.main([]) == ExitCode.OPTIONAL_DEPENDENCY_UNAVAILABLE
    error = capsys.readouterr().err
    assert 'pip install "MetaXTools[report]"' in error
    assert "jinja2" in error


def test_report_launcher_delegates_to_report_cli(monkeypatch):
    fake_cli = SimpleNamespace(main=lambda argv=None: 23 if argv == ["--help"] else 0)
    monkeypatch.setattr(
        report_launcher.importlib,
        "import_module",
        lambda _name: fake_cli,
    )

    assert report_launcher.main(["--help"]) == 23


def test_report_launcher_import_does_not_import_report_stack():
    code = (
        "import sys; import metax.cli.report; "
        "assert 'metax.report' not in sys.modules"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr


def test_gui_annotation_handlers_use_shared_backend_classes():
    gui_path = Path(__file__).resolve().parents[1] / "metax" / "gui" / "main_gui.py"
    tree = ast.parse(gui_path.read_text(encoding="utf-8"))
    methods = {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    global_calls = {
        node.func.id
        for node in ast.walk(methods["run_pep_dircet_to_otf"])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    unit_calls = {
        node.func.id
        for node in ast.walk(methods["run_pep_direct_to_otf_unit_specific"])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "GlobalOTFAnnotator" in global_calls
    assert "UnitSpecificOTFAnnotator" in unit_calls
    assert "peptideProteinsMapper" not in global_calls
    assert {
        "_prepare_diann_parquet_for_pep_direct_to_otf",
        "_run_pep_direct_to_otf_metaumbra_scoring",
        "_run_pep_direct_to_otf_with_genome_list",
    }.isdisjoint(methods)
