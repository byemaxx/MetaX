import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from metax.peptide_annotator.genome_selection_manifest import (
    SCHEMA_VERSION,
    load_genome_selection_manifest,
)


def test_metaumbra_generated_manifest_is_loaded_directly_by_metax(tmp_path):
    workspace = Path(__file__).resolve().parents[2]
    configured_source = os.environ.get("METAX_METAUMBRA_SOURCE")
    metaumbra_source = (
        Path(configured_source).expanduser().resolve()
        if configured_source
        else workspace / "MetaUmbra"
    )
    schema_path = metaumbra_source / "docs" / "genome_selection_manifest.v1.schema.json"
    if not schema_path.is_file():
        if os.environ.get("CI"):
            pytest.fail(
                "MetaUmbra contract checkout is required in CI; "
                f"expected schema at {schema_path}"
            )
        pytest.skip("Cross-repository MetaUmbra checkout is not available")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    output = tmp_path / "genome_selection_manifest.json"
    script = r'''
import sys
from pathlib import Path
import pandas as pd
from metaumbra.genome_selection_manifest import build_genome_selection_manifest, write_genome_selection_manifest

output = Path(sys.argv[1])
mapping = pd.DataFrame({"sample_id": ["s1", "s2"], "analysis_unit_id": ["u1", "u2"]})
results = pd.DataFrame({
    "analysis_unit_id": ["u1", "u1", "u2", "u2"],
    "genome_id": ["g1", "g2", "g1", "g2"],
    "pass_q_0_01": [True, False, False, True],
    "pass_q_0_05": [True, True, True, True],
})
manifest = build_genome_selection_manifest(
    mapping_df=mapping,
    unit_genome_results=results,
    unit_mode="per-sample",
    sample_id_column="Run",
    analysis_unit_column=None,
    peptide_table_path=str(output.parent / "report.parquet"),
    metadata_table_path=None,
    genome_digest_directories=[str(output.parent / "digests")],
    artifacts={"unit_genome_results": "unit_genome_results.tsv"},
    scoring_method="per-analysis-unit/empirical-background",
    run_id="cross-repo-test",
)
write_genome_selection_manifest(output, manifest)
'''
    env = dict(os.environ)
    env["PYTHONPATH"] = str(metaumbra_source / "src") + os.pathsep + env.get("PYTHONPATH", "")
    subprocess.run([sys.executable, "-c", script, str(output)], check=True, env=env)
    manifest = load_genome_selection_manifest(output)
    assert schema["$id"] == SCHEMA_VERSION == manifest.schema_version
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert manifest.unit_definition["mode"] == "per-sample"
    assert manifest.units["u1"].sample_ids == ["s1"]
    assert manifest.units["u2"].genome_ids == ["g1", "g2"]
