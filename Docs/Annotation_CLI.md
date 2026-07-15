# MetaX Annotation CLI

`metax-annotate` provides Qt-free global and unit-specific peptide-to-OTF annotation.

## Installation

The default package contains the complete annotation backend:

```bash
python -m pip install MetaXTools
```

Analyzer, Report, and desktop installation profiles are described in the
[README](../README.md#installation).

## Global annotation

Run MetaUmbra genome scoring and generate an OTF from DIA-NN parquet:

```bash
metax-annotate \
  --mode global \
  --peptide-table report.parquet \
  --digested-genome-folders digested_genomes \
  --taxafunc-db MetaX_taxafunc.db \
  --output OTF.tsv \
  --selection-mode metaumbra \
  --diann-intensity-col Precursor.Normalised \
  --result-json annotation_result.json
```

Use `--selection-mode provided` with `--selected-genomes` or
`--genome-list-file` to supply genomes directly. Use `automatic` for MetaX's
internal genome ranking, or `metaumbra-only` to stop after genome scoring.

When `--selection-mode` is omitted, selected genome IDs or a genome-list file
imply `provided`; otherwise digest directories imply `metaumbra`; otherwise the
mode is `automatic`. Explicit modes take precedence, and contradictory genome
sources are rejected instead of ignored.

Exactly one peptide-mapping source is required for OTF generation:
`--peptide-db` or `--digested-genome-folders`.

## Unit-specific annotation

Use a MetaUmbra unit-specific manifest:

```bash
metax-annotate \
  --mode unit-specific \
  --peptide-table report.parquet \
  --unit-specific-manifest unit_specific_manifest.json \
  --digested-genome-folders digested_genomes \
  --taxafunc-db MetaX_taxafunc.db \
  --output OTF_unit_specific.tsv \
  --result-json annotation_result.json
```

## YAML or JSON configuration

CLI arguments override configuration-file values:

```yaml
api_version: "1.0"
mode: global

inputs:
  peptide_table: report.parquet
  digested_genome_folders:
    - digested_genomes
  taxafunc_db: MetaX_taxafunc.db

output:
  otf: OTF.tsv
  result_json: annotation_result.json

options:
  selection_mode: metaumbra
  duplicate_peptide_handling_mode: sum
  diann_intensity_col: Precursor.Normalised
```

Run it with:

```bash
metax-annotate --config annotation.yaml
```

Relative paths loaded from a configuration file are resolved from the
configuration file's directory. Relative paths supplied directly on the command
line remain relative to the current working directory.

## Result JSON

When `--result-json` is supplied, MetaX writes schema `2.0` atomically. The
top-level sections are:

```text
run, inputs, parameters, stages, genome_selection, metrics, outputs, diagnostics
```

Use `run.status` and `run.exit_code` for the outcome, `outputs` for generated
files, `metrics` for mapping/QC values, and `diagnostics` for warnings or errors.
Scientific outputs are safely renamed when their requested path already exists,
and `outputs` reports the actual paths. The result JSON itself keeps its requested
stable path and is atomically replaced.
See [Annotation Result Schema](Annotation_Result_Schema.md) for the complete
field reference and examples.

## Exit codes

| Code | Meaning |
| ---: | --- |
| 0 | Successful execution |
| 2 | Invalid arguments or configuration |
| 3 | Missing input, database, directory, or configuration file |
| 4 | Required optional dependency is unavailable |
| 5 | Annotation or external scoring failed |
| 130 | Execution was cancelled |

On interruption, MetaX terminates active MetaUmbra or digested-scan process
trees before writing the cancellation result JSON.

## Python subprocess

Invoke MetaX with the same Python environment in which it is installed:

```python
import subprocess
import sys

completed = subprocess.run(
    [
        sys.executable,
        "-m",
        "metax.cli.annotate",
        "--config",
        "annotation.yaml",
    ],
    check=False,
)
```

Read the process exit code first, then inspect result JSON for structured details.
