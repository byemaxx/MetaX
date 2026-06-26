import pandas as pd

from metax.peptide_annotator import convert_id_to_name


def test_add_ec_name_converts_each_unique_value_once(monkeypatch):
    calls = []
    monkeypatch.setattr(
        convert_id_to_name,
        "get_ec_dict",
        lambda: {"1.1.1.1": {"EC_DE": "name"}},
    )

    def fake_lookup(ec_nums, ec_dict, column_name):
        calls.append((tuple(ec_nums), column_name))
        return f"{column_name}:{','.join(ec_nums)}"

    monkeypatch.setattr(
        convert_id_to_name,
        "lookup_and_join_for_EC",
        fake_lookup,
    )
    frame = pd.DataFrame(
        {
            "EC": ["1.1.1.1", "1.1.1.1", "-", None],
            "EC_prop": [1.0, 1.0, 0.0, 0.0],
        }
    )

    result = convert_id_to_name.add_ec_name_to_df(frame)

    assert len(calls) == 4
    assert result.loc[0, "EC_DE"] == "EC_DE:1.1.1.1"
    assert result.loc[1, "EC_DE"] == "EC_DE:1.1.1.1"
    assert result.loc[2, "EC_DE"] == "-"
    assert result.loc[3, "EC_DE"] == "-"


def test_add_go_name_converts_each_unique_value_once(monkeypatch):
    monkeypatch.setattr(
        convert_id_to_name,
        "get_go_dict",
        lambda: {
            "GO:1": ("name1", "namespace1"),
            "GO:2": ("name2", "namespace2"),
        },
    )
    frame = pd.DataFrame(
        {
            "GOs": ["GO:1,GO:2", "GO:1,GO:2", "-", None],
            "GOs_prop": [1.0, 1.0, 0.0, 0.0],
        }
    )

    result = convert_id_to_name.add_go_name_to_df(frame)

    assert result.loc[0, "GO_name"] == "name1|name2"
    assert result.loc[1, "GO_namespace"] == "namespace1|namespace2"
    assert result.loc[2, "GO_name"] == "-"
    assert result.loc[3, "GO_namespace"] == "-"
