import pytest
import pandas as pd
from types import SimpleNamespace

from metax.taxafunc_analyzer.analyzer_utils.basic_stats import BasicStats

def test_get_stats_taxa_level(tfa_object):
    """
    Test that get_stats_taxa_level accurately aggregates taxa 
    counts and respects the peptide minimum threshold.
    """
    # BasicStats object is attached to tfa
    basic_stats = tfa_object.BasicStats
    
    # Run taxa level stats with a low threshold
    stats_df = basic_stats.get_stats_taxa_level(peptide_num=1)
    
    assert isinstance(stats_df, pd.DataFrame), "Result must be a DataFrame"
    assert 'taxa_level' in stats_df.columns
    assert 'count' in stats_df.columns
    
    # Run with a very high threshold to ensure filtering works
    stats_df_high = basic_stats.get_stats_taxa_level(peptide_num=99999)
    # Most counts should be 0 or heavily reduced compared to peptide_num=1
    assert stats_df_high['count'].sum() < stats_df['count'].sum()

def test_get_stats_func_prop(tfa_object):
    """
    Test get_stats_func_prop returns proper proportions 
    for the given functional annotation.
    """
    basic_stats = tfa_object.BasicStats
    func_name = tfa_object.func_name
    
    # The original Example_OTF might not have {func_name}_prop accurately 
    # but we will just ensure it runs and returns the expected shape.
    stats_df = basic_stats.get_stats_func_prop(func_name=func_name)
    
    assert isinstance(stats_df, pd.DataFrame), "Result must be a DataFrame"
    assert 'prop' in stats_df.columns
    assert 'freq' in stats_df.columns
    assert 'label' in stats_df.columns
    assert len(stats_df) == 11, "Should have 11 proportion bins (0-0.1 up to 1)"
    
    # The total frequency should sum approximately to 100% (within rounding margin)
    # Note: if data is empty, it might be 0, but if populated it should be close to 100
    if stats_df['n'].sum() > 0:
        assert abs(stats_df['freq'].sum() - 100.0) < 1.0, "Frequency should sum to roughly 100%"


def _full_taxon(genome):
    return (
        "d__Bacteria|p__Firmicutes|c__Bacilli|o__Lactobacillales|"
        f"f__Lactobacillaceae|g__Lactobacillus|s__acidophilus|m__{genome}"
    )


def _unit_specific_stats_tfa(df):
    return SimpleNamespace(
        original_df=df,
        peptide_col_name="Sequence",
        any_df_mode=False,
        genome_mode=True,
        func_list=["KEGG_ko"],
    )


def test_get_stats_peptide_num_in_taxa_counts_unique_sequences_per_lca_level():
    df = pd.DataFrame(
        {
            "analysis_unit_id": ["u1", "u2", "u3"],
            "Sequence": ["PEPA", "PEPA", "PEPB"],
            "LCA_level": ["genome", "genome", "species"],
            "Taxon": [_full_taxon("g1"), _full_taxon("g1"), _full_taxon("g2")],
            "KEGG_ko": ["K00001", "K00001", "K00002"],
            "KEGG_ko_prop": [1.0, 1.0, 1.0],
        }
    )

    stats_df = BasicStats(_unit_specific_stats_tfa(df)).get_stats_peptide_num_in_taxa()

    counts = stats_df.set_index("LCA_level")["count"]
    assert counts["genome"] == 1
    assert counts["species"] == 1


def test_get_stats_taxa_level_threshold_counts_unique_sequences():
    df = pd.DataFrame(
        {
            "analysis_unit_id": ["u1", "u2", "u3", "u4"],
            "Sequence": ["PEPA", "PEPA", "PEPB", "PEPC"],
            "LCA_level": ["genome"] * 4,
            "Taxon": [
                _full_taxon("g1"),
                _full_taxon("g1"),
                _full_taxon("g2"),
                _full_taxon("g2"),
            ],
            "KEGG_ko": ["K00001", "K00001", "K00002", "K00002"],
            "KEGG_ko_prop": [1.0, 1.0, 1.0, 1.0],
        }
    )

    basic_stats = BasicStats(_unit_specific_stats_tfa(df))
    stats_df = basic_stats.get_stats_taxa_level(peptide_num=2)
    stats_df_low = basic_stats.get_stats_taxa_level(peptide_num=1)

    counts = stats_df.set_index("taxa_level")["count"]
    counts_low = stats_df_low.set_index("taxa_level")["count"]
    assert counts["genome"] == 1
    assert counts_low["genome"] == 2


def test_get_stats_func_prop_counts_unique_sequences_per_bin():
    df = pd.DataFrame(
        {
            "analysis_unit_id": ["u1", "u2", "u3"],
            "Sequence": ["PEPA", "PEPA", "PEPB"],
            "LCA_level": ["genome"] * 3,
            "Taxon": [_full_taxon("g1"), _full_taxon("g1"), _full_taxon("g2")],
            "KEGG_ko": ["K00001", "K00001", "K00002"],
            "KEGG_ko_prop": [0.95, 0.95, 0.95],
        }
    )

    stats_df = BasicStats(_unit_specific_stats_tfa(df)).get_stats_func_prop("KEGG_ko")

    assert stats_df.loc[stats_df["prop"] == "0.9-1", "n"].item() == 2
