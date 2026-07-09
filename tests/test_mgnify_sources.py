import inspect
from pathlib import Path

import pytest

from metax.database_builder import database_builder_mag, download_mgyg_faa
from metax.database_builder.mgnify_sources import (
    DB_URLS,
    GUI_CATALOGUE_PRIORITY,
    mgnify_catalogue_display_names,
    validate_mgnify_source,
)


NEW_CATALOGUES = {
    "barley-rhizosphere",
    "human-skin",
    "maize-rhizosphere",
    "marine-sediment",
    "soil",
    "tomato-rhizosphere",
}


def test_mgnify_sources_have_required_https_urls():
    for db_type, source in DB_URLS.items():
        assert source["base_url"].startswith("https://"), db_type
        assert source["metadata"]
        assert source["catalogue"]


def test_new_catalogues_are_supported_but_marine_eukaryotes_is_not():
    assert NEW_CATALOGUES.issubset(DB_URLS)
    assert "marine-eukaryotes" not in DB_URLS


def test_database_builders_share_the_single_source_definition():
    assert database_builder_mag.DB_URLS is DB_URLS
    assert download_mgyg_faa.DB_URLS is DB_URLS

    for module in (database_builder_mag, download_mgyg_faa):
        source = Path(inspect.getfile(module)).read_text(encoding="utf-8")
        assert "DB_URLS = {" not in source


def test_cli_database_type_choices_and_help_match_sources():
    parser = database_builder_mag.build_parser()
    db_type_action = next(action for action in parser._actions if action.dest == "db_type")

    assert tuple(db_type_action.choices) == tuple(sorted(DB_URLS))
    help_text = "".join(parser.format_help().split())
    for db_type in DB_URLS:
        assert db_type in help_text


def test_gui_catalogue_display_list_comes_from_all_supported_sources():
    labels = mgnify_catalogue_display_names()
    gui_source = (
        Path(__file__).resolve().parents[1] / "metax" / "gui" / "main_gui.py"
    ).read_text(encoding="utf-8")

    assert all(db_type in labels[index] for index, db_type in enumerate(GUI_CATALOGUE_PRIORITY))
    assert labels[len(GUI_CATALOGUE_PRIORITY):] == sorted(labels[len(GUI_CATALOGUE_PRIORITY):])
    assert all(db_type in " ".join(labels) for db_type in NEW_CATALOGUES)
    assert "marine-eukaryotes" not in " ".join(labels)
    assert "self.comboBox_db_type.addItems(mgnify_catalogue_display_names())" in gui_source


@pytest.mark.parametrize(
    ("mgyg_id", "db_type", "expected_eggnog", "expected_faa"),
    [
        (
            "MGYG000001234",
            "human-gut",
            "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-gut/v2.0.2/species_catalogue/MGYG0000012/MGYG000001234/genome/MGYG000001234_eggNOG.tsv",
            "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-gut/v2.0.2/species_catalogue/MGYG0000012/MGYG000001234/genome/MGYG000001234.faa",
        ),
        (
            "MGYG000123456.1",
            "mouse-gut",
            "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/mouse-gut/v1.0/species_catalogue/MGYG0001234/MGYG000123456.1/genome/MGYG000123456.1_eggNOG.tsv",
            "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/mouse-gut/v1.0/species_catalogue/MGYG0001234/MGYG000123456.1/genome/MGYG000123456.1.faa",
        ),
    ],
)
def test_create_download_list_preserves_existing_mgnify_paths(
    mgyg_id, db_type, expected_eggnog, expected_faa
):
    assert database_builder_mag.create_download_list([mgyg_id], db_type) == [expected_eggnog]
    assert download_mgyg_faa.create_download_list([mgyg_id], db_type) == [expected_faa]


def test_validate_mgnify_source_checks_metadata_and_optional_catalogue(monkeypatch):
    checked_urls = []

    class Response:
        status = 200

        def read(self, _):
            return b"Species_rep\tLineage\n"

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

    def fake_urlopen(url, timeout):
        checked_urls.append((url, timeout))
        return Response()

    monkeypatch.setattr("metax.database_builder.mgnify_sources.urllib.request.urlopen", fake_urlopen)

    assert validate_mgnify_source("human-gut", check_catalogue=True) is DB_URLS["human-gut"]
    assert [url for url, _ in checked_urls] == [
        "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-gut/v2.0.2/genomes-all_metadata.tsv",
        "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-gut/v2.0.2/species_catalogue/",
    ]


def test_validate_mgnify_source_reports_unavailable_url(monkeypatch):
    def unavailable(*_, **__):
        raise OSError("network unavailable")

    monkeypatch.setattr("metax.database_builder.mgnify_sources.urllib.request.urlopen", unavailable)

    with pytest.raises(RuntimeError, match="MGnify metadata URL is unavailable.*human-gut"):
        validate_mgnify_source("human-gut")


def test_validate_mgnify_source_rejects_metadata_without_required_columns(monkeypatch):
    class Response:
        status = 200

        def read(self, _):
            return b"Species_rep\tGenome\n"

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

    monkeypatch.setattr(
        "metax.database_builder.mgnify_sources.urllib.request.urlopen",
        lambda *_, **__: Response(),
    )

    with pytest.raises(ValueError, match="missing required columns Lineage"):
        validate_mgnify_source("human-gut")
