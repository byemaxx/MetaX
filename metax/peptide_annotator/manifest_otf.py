"""Canonical manifest-driven OTF annotation API."""

from .unit_specific_otf import (
    ManifestOTFAnnotator,
    ManifestOTFRunResult,
    build_manifest_peptide_protein_map,
)

__all__ = [
    "ManifestOTFAnnotator",
    "ManifestOTFRunResult",
    "build_manifest_peptide_protein_map",
]
