# Annotation CLI

`metax-annotate` is a Qt-free annotation entry point with three explicit genome-selection sources. It never guesses the source from a filename or table columns.

```bash
python -m metax.cli.annotate \
  --input-source metaumbra-manifest \
  --peptide-table report.parquet \
  --metaumbra-manifest results/genome_selection_manifest.json \
  --taxafunc-db MetaX_taxafunc.db \
  --digested-genome-folders UHGP_digested \
  --genome-threshold auto \
  --output OTF.tsv \
  --result-json result.json
```

MetaX automatic selection remains available for non-MetaUmbra inputs:

```bash
python -m metax.cli.annotate --input-source metax-automatic \
  --peptide-table peptides.tsv --taxafunc-db MetaX_taxafunc.db \
  --digested-genome-folders UHGP_digested \
  --intensity-col-prefix Intensity --output OTF.tsv
```

For an explicit genome set, use `--input-source genome-list` with either `--genome-list-file genomes.txt` or `--selected-genomes g1 g2`.
For delimited non-MetaUmbra peptide tables, `--intensity-col-prefix` identifies the input sample columns; the GUI forwards the editable **Prefix of Intensity Column** value to the same backend.

`--genome-threshold` accepts `auto`, `q0.05`, or `q0.01`. `auto` uses `selection.default_genome_threshold` from the manifest. There is no global/unit-specific mode selector and MetaX does not infer genome IDs from a TSV.

The annotation backend always performs the same sequence:

1. Validate `metaumbra.genome_selection_manifest.v1`.
   A unit with no genomes at the selected threshold is rejected before annotation.
2. Resolve every manifest sample ID to a DIA-NN run or prepared intensity column.
3. Scan the union of selected genome digest files once.
4. Annotate each analysis unit using its samples and selected genomes.
5. Merge unit outputs while retaining `analysis_unit_id`.

The result JSON uses `metax.annotation_result.v2` and records `input_source`. Manifest runs additionally record the manifest path/schema, number of units, selected threshold, sample mapping, and per-unit summary; non-manifest runs set those manifest-only fields to null. Exit codes are `0` success, `2` invalid configuration, `3` missing input, `4` missing optional dependency, `5` annotation failure, and `130` cancellation.
