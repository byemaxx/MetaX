import pytest
from pathlib import Path

@pytest.fixture(scope="session")
def tfa_object():
    """
    Fixture to initialize a TaxaFuncAnalyzer object with example data.
    This fixture is shared across all test modules.
    """
    from metax.taxafunc_analyzer.analyzer import TaxaFuncAnalyzer

    repo_root = Path(__file__).resolve().parents[1]
    otf_path = str(repo_root / "metax" / "data" / "example_data" / "Example_OTF.tsv")
    meta_path = str(repo_root / "metax" / "data" / "example_data" / "Example_Meta.tsv")
    
    tfa = TaxaFuncAnalyzer(
        df_path=otf_path,
        meta_path=meta_path,
        sample_col_prefix="Intensity"
    )
    # Set group and function so that tfa is fully ready for plotting and stats tasks
    tfa.set_group("Sugar_type")
    tfa.set_func("KEGG_ko_name")
    
    return tfa
