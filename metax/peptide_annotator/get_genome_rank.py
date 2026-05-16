"""Compatibility wrapper for the renamed peptide coverage ranker module.

New code should import ``PeptideCoverageRanker`` from
``metax.peptide_annotator.peptide_coverage_ranker``. This module remains so
older imports of ``GenomeRank`` continue to work.
"""

from metax.peptide_annotator.peptide_coverage_ranker import GenomeRank, PeptideCoverageRanker

__all__ = ["GenomeRank", "PeptideCoverageRanker"]
