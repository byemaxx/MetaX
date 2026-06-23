import pandas as pd
import pytest

from metax.peptide_annotator.peptide_table_prepare import (
    prepare_diann_parquet_for_direct_otf,
)


@pytest.mark.parametrize(
    ("intensity_col", "expected_prefix"),
    [
        ("Precursor.Normalised", "Precursor.Normalised."),
        ("Precursor.Quantity", "Precursor.Quantity."),
    ],
)
def test_prepare_diann_parquet_supports_intensity_aliases(
    tmp_path,
    intensity_col,
    expected_prefix,
):
    parquet_path = tmp_path / "report.parquet"
    pd.DataFrame(
        {
            "Run": ["s1.raw", "s1.raw", "s2.raw"],
            "Stripped.Sequence": ["PEPA", "PEPA", "PEPA"],
            "Evidence": [1.0, 2.0, 3.0],
            "Q.Value": [0.02, 0.01, 0.03],
            intensity_col: [4.0, 6.0, 20.0],
        }
    ).to_parquet(parquet_path)

    prepared = prepare_diann_parquet_for_direct_otf(
        parquet_path,
        require_score_columns=True,
    )

    assert prepared.intensity_col == intensity_col
    assert prepared.intensity_col_prefix == expected_prefix
    assert prepared.dataframe.loc[0, f"{expected_prefix}s1"] == 10.0
    assert prepared.dataframe.loc[0, f"{expected_prefix}s2"] == 20.0
    assert prepared.dataframe.loc[0, "Evidence"] == 3.0
    assert prepared.dataframe.loc[0, "Q.Value"] == 0.01
    assert prepared.metadata["diann_intensity_column"] == intensity_col


def test_prepare_diann_parquet_prefers_normalised_when_both_aliases_exist(tmp_path):
    parquet_path = tmp_path / "report.parquet"
    pd.DataFrame(
        {
            "Run": ["s1"],
            "Stripped.Sequence": ["PEPA"],
            "Precursor.Normalised": [10.0],
            "Precursor.Quantity": [99.0],
        }
    ).to_parquet(parquet_path)

    prepared = prepare_diann_parquet_for_direct_otf(
        parquet_path,
        sample_column_prefix="",
    )

    assert prepared.intensity_col == "Precursor.Normalised"
    assert prepared.dataframe.loc[0, "s1"] == 10.0


def test_prepare_diann_parquet_reports_missing_intensity_alias(tmp_path):
    parquet_path = tmp_path / "report.parquet"
    pd.DataFrame(
        {
            "Run": ["s1"],
            "Stripped.Sequence": ["PEPA"],
        }
    ).to_parquet(parquet_path)

    with pytest.raises(ValueError, match="Expected one of.*Precursor.Normalised.*Precursor.Quantity"):
        prepare_diann_parquet_for_direct_otf(parquet_path)
