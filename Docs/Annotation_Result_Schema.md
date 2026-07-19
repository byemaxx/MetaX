# Annotation result schema

All annotation sources write a JSON object with schema version `metax.annotation_result.v2`.

```json
{
  "schema_version": "metax.annotation_result.v2",
  "input_source": "metaumbra-manifest",
  "run": {"status": "success", "exit_code": 0, "software": {}},
  "manifest": {
    "path": "results/genome_selection_manifest.json",
    "schema_version": "metaumbra.genome_selection_manifest.v1"
  },
  "number_of_units": 2,
  "selected_threshold": "q0.05",
  "inputs": {},
  "parameters": {},
  "stages": {},
  "genome_selection": {
    "method": "metaumbra_genome_selection_manifest",
    "threshold": "q0.05"
  },
  "metrics": {},
  "outputs": {
    "otf": {"path": "OTF.tsv", "format": "tsv"},
    "sample_mapping": {"path": "OTF_artifacts/unit_sample_column_mapping.tsv"},
    "unit_summary": {"path": "OTF_artifacts/unit_annotation_summary.tsv"}
  },
  "per_unit_summary": {},
  "diagnostics": {"warnings": [], "error": null}
}
```

Manifest-driven OTF output always retains `analysis_unit_id`. A one-unit manifest therefore produces the same table schema as a multi-unit manifest, using `__global__` for the all-samples unit. Keeping the column avoids a schema branch and lets Analyzer use the same unit-aware peptide identity for both one-unit and multi-unit results.

`input_source` is one of `metaumbra-manifest`, `metax-automatic`, or `genome-list`. For the latter two, `manifest`, `number_of_units`, `selected_threshold`, and `per_unit_summary` are null; their existing MetaX OTF schema is retained.
