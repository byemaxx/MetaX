# MetaX CLI

MetaX provides command-line entry points for launching the desktop application, annotating peptides to Operational Taxon-Functions (OTFs), generating complete HTML reports, and building an MGnify annotation database. This page documents every user-facing command currently available in the project.

MetaX does not currently expose a separate general-purpose `metax analyze` command for every interactive Analyzer plot. Use **Restore > Export Workflow Notebook** in the GUI when a downstream Analyzer workflow must be replayed without manual interaction; the exported notebook and optional Python script use the same analysis APIs.

## 1. Installation Profiles

Install MetaX into the Python environment from which the commands will be run.

```bash
# Peptide-to-OTF annotation without Qt
python -m pip install MetaXTools

# Annotation plus the headless Auto OTF Report stack
python -m pip install "MetaXTools[report]"

# Desktop GUI and all optional analysis/report dependencies
python -m pip install "MetaXTools[full]"
```

Use the lightweight base installation for annotation servers and workflow managers. Use the report profile for headless analysis and HTML reporting. The full profile is required for the desktop application and is also the safest choice for the legacy MGnify database-builder module.

## 2. Command Overview

| Command | Purpose | Recommended installation |
| --- | --- | --- |
| `metax` | Launch the MetaX desktop application | `MetaXTools[full]` |
| `metax-annotate` | Convert a peptide-intensity table to an OTF table | `MetaXTools` |
| `metax-report` | Generate a self-contained Auto OTF HTML report | `MetaXTools[report]` |
| `python -m metax.database_builder.database_builder_mag` | Download or build an MGnify annotation database | `MetaXTools[full]` |

The two headless commands also have module forms, which are useful when several Python installations are present:

```bash
python -m metax.cli.annotate --help
python -m metax.cli.report --help
```

Using `python -m ...` guarantees that the command runs with the same interpreter that contains the selected MetaX installation.

## 3. Desktop Launcher

```bash
metax
```

The launcher opens the desktop GUI and does not define additional command-line options. If GUI dependencies are unavailable, it exits with code `4` and identifies the required installation extra.

## 4. Peptide-to-OTF Annotation

### 4.1 Input Sources

`metax-annotate` supports the three genome-selection sources available on the **Peptide Direct to OTFs** GUI tab. The source must be selected explicitly; MetaX does not infer it from a filename or table columns.

| `--input-source` | Genome selection | Source-specific input |
| --- | --- | --- |
| `metaumbra-manifest` | Per-analysis-unit genomes selected by MetaUmbra | `--metaumbra-manifest` |
| `metax-automatic` | MetaX automatic selection from the supplied peptide table | No genome-list argument |
| `genome-list` | A user-supplied fixed genome set | `--genome-list-file` or `--selected-genomes` |

### 4.2 MetaUmbra Manifest Workflow (Recommended)

```bash
metax-annotate \
  --input-source metaumbra-manifest \
  --peptide-table report.parquet \
  --metaumbra-manifest results/genome_selection_manifest.json \
  --taxafunc-db MetaX_taxafunc.db \
  --digested-genome-folders UHGP_digested \
  --genome-threshold auto \
  --output OTF.tsv \
  --result-json annotation_result.json
```

`--genome-threshold auto` uses `selection.default_genome_threshold` from the manifest. Use `q0.05` or `q0.01` to select a specific manifest threshold. MetaX validates analysis units, sample mappings, selected genomes, and required files before annotation.

### 4.3 MetaX Automatic Genome Selection

```bash
metax-annotate \
  --input-source metax-automatic \
  --peptide-table peptides.tsv \
  --taxafunc-db MetaX_taxafunc.db \
  --digested-genome-folders UHGP_digested \
  --intensity-col-prefix Intensity \
  --output OTF.tsv
```

### 4.4 Custom Genome List

```bash
metax-annotate \
  --input-source genome-list \
  --genome-list-file genomes.txt \
  --peptide-table peptides.tsv \
  --taxafunc-db MetaX_taxafunc.db \
  --digested-genome-folders UHGP_digested \
  --output OTF.tsv
```

For a short inline list, replace `--genome-list-file genomes.txt` with `--selected-genomes genome_1 genome_2`. Text, TSV, and CSV genome-list files are accepted.

### 4.5 Annotation Configuration File

YAML and JSON configurations are supported. Relative paths are resolved from the configuration file directory, and explicit command-line arguments override configuration values.

```yaml
workflow_api_version: "1.0"
inputs:
  peptide_table: report.parquet
  metaumbra_manifest: results/genome_selection_manifest.json
  taxafunc_db: databases/MetaX_taxafunc.db
  digested_genome_folders:
    - databases/UHGP_digested
options:
  input_source: metaumbra-manifest
  genome_threshold: auto
  peptide_col: Stripped.Sequence
  diann_intensity_col: Precursor.Normalised
  n_jobs: 8
output:
  otf: results/OTF.tsv
  result_json: results/annotation_result.json
```

Run it with:

```bash
metax-annotate --config annotation.yaml
```

### 4.6 Annotation Option Reference

**Core inputs and outputs**

| Option | Meaning |
| --- | --- |
| `--config PATH` | YAML or JSON workflow configuration |
| `--peptide-table PATH` | Peptide-intensity table; delimited text or DIA-NN parquet |
| `--input-source SOURCE` | `metaumbra-manifest`, `metax-automatic`, or `genome-list` |
| `--metaumbra-manifest PATH` | MetaUmbra `genome_selection_manifest.json` |
| `--genome-list-file PATH` | Text, TSV, or CSV file containing genome IDs |
| `--selected-genomes ID ...` | Genome IDs supplied directly on the command line |
| `--taxafunc-db PATH` | MetaX taxa-function annotation SQLite database |
| `--peptide-db PATH` | Optional SQLite peptide-to-protein cache/database |
| `--digested-genome-folders PATH ...` | One or more directories containing digested genome TSV files |
| `--output PATH` | Output OTF TSV |
| `--result-json PATH` | Structured execution result for automation and diagnostics |

**Columns and input preparation**

| Option | Meaning / default |
| --- | --- |
| `--peptide-col NAME` | Peptide column; default `Sequence` |
| `--intensity-col-prefix PREFIX` | Input sample-column prefix for automatic and genome-list modes; default `Intensity` |
| `--input-sample-col-prefix PREFIX` | Optional input prefix removed while matching manifest sample IDs |
| `--output-sample-col-prefix Intensity_` | Canonical OTF sample prefix; currently fixed to `Intensity_` |
| `--table-separator SEP` | Delimited-table separator; default tab (`\t`) |
| `--diann-intensity-col COLUMN` | DIA-NN parquet intensity source: `Precursor.Normalised` or `Precursor.Quantity` |

For DIA-NN parquet, MetaX reads `Run` and `Stripped.Sequence`, prefers `Precursor.Normalised`, and falls back to `Precursor.Quantity` when no explicit DIA-NN intensity option is supplied. Output sample columns use `Intensity_<sample>`.

**Annotation behavior**

| Option | Meaning / values |
| --- | --- |
| `--genome-threshold VALUE` | `auto`, `q0.05`, or `q0.01` |
| `--lca-threshold FLOAT` | LCA agreement threshold from `0` to `1`; default `1.0` |
| `--genome-mode` / `--no-genome-mode` | Enable or disable genome-mode annotation |
| `--distinct-genome-threshold N` | Minimum distinct-genome filter; default `0` |
| `--exclude-protein-startwith TEXT` | Exclude protein IDs beginning with the supplied text |
| `--protein-separator TEXT` | Separator between protein assignments; default `;` |
| `--protein-genome-separator TEXT` | Separator between genome and protein IDs; default `_` |
| `--duplicate-peptide-handling-mode MODE` | `sum`, `max`, `min`, `mean`, `first`, or `keep`; default `sum` |

**Manifest execution and performance**

| Option | Meaning / default |
| --- | --- |
| `--save-per-unit-outputs` / `--no-save-per-unit-outputs` | Save a separate OTF file for each analysis unit |
| `--on-missing-sample MODE` | `error` or `warn-skip`; default `error` |
| `--on-empty-unit MODE` | `error` or `warn-skip`; default `warn-skip` |
| `--n-jobs N` | Worker count; must be at least `1` when supplied |
| `--merge-chunksize N` | Merge chunk size; default `100000` |
| `--collect-unique-stats` / `--no-collect-unique-stats` | Collect additional unique-peptide statistics |

### 4.7 Annotation Outputs and Exit Codes

The main output is an OTF TSV. Manifest-based runs retain `analysis_unit_id` and can additionally write sample-mapping, unit-summary, and optional per-unit artifacts. `--result-json` records the input source, effective parameters, stage status, output paths, warnings, and errors using the current `metax.annotation_result.v2` contract.

| Exit code | Meaning |
| --- | --- |
| `0` | Success |
| `2` | Invalid configuration or arguments |
| `3` | Required input file is missing |
| `4` | Optional dependency is unavailable |
| `5` | Annotation failed |
| `130` | Cancelled or interrupted |

## 5. Auto OTF HTML Report

Install the report profile, then generate a report directly from an OTF table:

```bash
metax-report \
  --otf OTF.tsv \
  --meta metadata.tsv \
  --out MetaX_Report \
  --group Treatment \
  --control Control \
  --taxa-levels p,g,s \
  --func eggNOG_OGs,KEGG_ko \
  --diff-method limma \
  --figure-formats png,svg,pdf \
  --dpi 300
```

Without `--config`, `--otf` and `--out` are required. With a configuration file, command-line options override the corresponding configuration values.

### 5.1 Report Configuration File

```yaml
input:
  otf_path: OTF.tsv
  meta_path: metadata.tsv
  peptide_col_name: Sequence
  protein_col_name: Proteins
  sample_col_prefix: Intensity
analysis:
  group_meta: Treatment
  control_group: Control
  main_taxa_level: s
tables:
  taxa_levels: [p, g, s]
  function_columns: [eggNOG_OGs, KEGG_ko]
statistics:
  diff_method: limma
  alpha: 0.05
  log2fc_cutoff: 1.0
plots:
  top_n: 20
  run_network: false
report:
  output_dir: MetaX_Report
  figure_formats: [png, svg, pdf]
  dpi: 300
  overwrite: false
```

```bash
metax-report --config report.yaml
```

### 5.2 Report Option Reference

| Option | Meaning |
| --- | --- |
| `--otf PATH` | Input OTF table |
| `--out DIR` | Output report directory |
| `--meta PATH` | Optional metadata table |
| `--group COLUMN` | Metadata grouping column |
| `--control VALUE` | Control value within the grouping column |
| `--taxa-levels LIST` | Comma-separated levels such as `p,g,s`, or `all` |
| `--func LIST` | Comma-separated function columns, or `auto` |
| `--config PATH` | YAML report configuration |
| `--sample-col-prefix PREFIX` | OTF sample-intensity prefix |
| `--peptide-col-name NAME` | Peptide column name |
| `--protein-col-name NAME` | Protein column name |
| `--top-n N` | Top features displayed in report plots |
| `--diff-method METHOD` | `limma` or `dunnett` |
| `--figure-formats LIST` | Comma-separated `png`, `svg`, and/or `pdf` |
| `--dpi N` | Raster-figure DPI |
| `--run-deseq2` | Request optional DESeq2-like analysis |
| `--no-diversity` | Disable alpha- and beta-diversity plots |
| `--run-network` | Enable heavier taxa-function network plots |
| `--no-network` | Disable network plots |
| `--overwrite` | Replace report files in a non-empty output directory |

The command prints the generated report `index.html` path on success and returns `0`. A report failure returns `1`; a missing optional report dependency returns `4`. The report directory also contains tables, figures, logs, `summary.json`, `config_used.yaml`, and reproducibility helpers.

## 6. MGnify Database Builder Module

The current database builder is available as a Python module rather than a separate installed console command. Use the full installation profile.

### 6.1 Automatic Build

```bash
python -m metax.database_builder.database_builder_mag \
  --auto \
  --db_type human-gut
```

This downloads the selected MGnify catalogue and writes `MetaX_database/MetaX.db` under the current directory.

### 6.2 Custom Output Location

```bash
python -m metax.database_builder.database_builder_mag \
  --save_dir databases \
  --db_name MetaX.db \
  --db_type marine
```

To reuse already downloaded source data, also supply `--meta_path` for `genomes-all_metadata.tsv` and `--mgyg_dir` for the eggNOG annotation directory.

| Option | Meaning |
| --- | --- |
| `--auto` | Use `MetaX_database/MetaX.db` under the current directory |
| `--save_dir PATH` | Database output directory |
| `--db_name NAME` | SQLite database filename |
| `--meta_path PATH` | Existing `genomes-all_metadata.tsv` |
| `--mgyg_dir PATH` | Existing MGnify eggNOG annotation directory |
| `--db_type TYPE` | MGnify catalogue; run `--help` for the catalogues supported by the installed version |

## 7. Reproducible Analyzer Workflows

The OTF Analyzer is currently exposed through the desktop GUI and Python analysis APIs, not a single public `metax analyze` command. For a reproducible command-line deliverable:

1. Run the supported analysis in the GUI.
2. Open **Restore > Export Workflow Notebook**.
3. Keep the default Jupyter notebook, and optionally export the Python script and YAML workflow.
4. Run the exported artifact with the Python environment recorded by MetaX.

Use `metax-report` when a standardized, unattended overview is sufficient. Use workflow export when the exact sequence of interactive Analyzer operations must be reproduced.

## 8. Shell and Automation Notes

- Examples use Bash line continuation (`\`). In PowerShell, replace each trailing backslash with a backtick or put the command on one line.
- Quote paths containing spaces.
- Prefer module invocation (`python -m metax.cli.annotate`) when the shell may resolve a command from the wrong Python environment.
- Use annotation `--result-json` and process exit codes in workflow managers; do not determine success only by checking whether an output file exists.
- Use a new report directory or pass `--overwrite` intentionally. MetaX rejects a non-empty report directory by default so unrelated runs are not mixed.
- Run each command with `--help` to inspect the exact options supported by the installed MetaX version.
