import io
import sqlite3
import sys
import tarfile
from types import SimpleNamespace

import pandas as pd
import pytest

from metax.database_updater import database_updater


class MockResponse:
    def __init__(self, content, status_error=None):
        self.content = content
        self.status_error = status_error

    def raise_for_status(self):
        if self.status_error:
            raise self.status_error

    def iter_content(self, chunk_size):
        yield self.content


def _mock_requests(monkeypatch, response):
    monkeypatch.setitem(
        sys.modules,
        "requests",
        SimpleNamespace(get=lambda *args, **kwargs: response),
    )


def _create_database(path, annotation=None):
    if annotation is None:
        annotation = pd.DataFrame(
            {"ID": ["protein_1", "protein_2"], "old_annotation": ["old_1", "old_2"]}
        )
    id2taxa = pd.DataFrame(
        {"ID": annotation["ID"], "taxa": ["taxa_1", "taxa_2"][: len(annotation)]}
    )
    with sqlite3.connect(path) as connection:
        annotation.to_sql("id2annotation", connection, index=False)
        id2taxa.to_sql("id2taxa", connection, index=False)


def _dbcan_archive_bytes():
    table = (
        "protein\tEC\tHMMER\teCAMI\tDIAMOND\tNumOfTools\n"
        "protein_1\t1.1.1.1\tGH1(1-10)\tGH1\tGH1\t4\n"
    ).encode()
    archive = io.BytesIO()
    with tarfile.open(fileobj=archive, mode="w:gz") as tar:
        info = tarfile.TarInfo("overview.txt")
        info.size = len(table)
        tar.addfile(info, io.BytesIO(table))
    return archive.getvalue()


@pytest.mark.parametrize("content", [b"<html>service unavailable</html>", b"Invalid file"])
def test_download_file_rejects_server_error_content(monkeypatch, tmp_path, content):
    _mock_requests(monkeypatch, MockResponse(content))

    with pytest.raises(ValueError, match="non-archive response"):
        database_updater.download_file(
            "https://pro.unl.edu/dbCAN_seq/download_file.php?file=HUMAN%20GUT/dbCAN_overview.tar.gz",
            tmp_path,
        )


def test_download_file_rejects_empty_response(monkeypatch, tmp_path):
    _mock_requests(monkeypatch, MockResponse(b""))

    with pytest.raises(ValueError, match="empty"):
        database_updater.download_file(
            "https://pro.unl.edu/dbCAN_seq/download_file.php?file=HUMAN%20GUT/dbCAN_overview.tar.gz",
            tmp_path,
        )


def test_download_file_and_merge_valid_archive(monkeypatch, tmp_path):
    _mock_requests(monkeypatch, MockResponse(_dbcan_archive_bytes()))

    path = database_updater.download_file(
        "https://pro.unl.edu/dbCAN_seq/download_file.php?file=HUMAN%20GUT/dbCAN_overview.tar.gz",
        tmp_path,
    )
    result = database_updater.merge_dbcan(path)

    assert result.to_dict("records") == [
        {
            "ID": "protein_1",
            "dbcan_EC": "1.1.1.1",
            "dbcan_HMMER": "GH1",
            "dbcan_eCAMI": "GH1",
            "dbcan_DIAMOND": "GH1",
        }
    ]


def test_check_table_match_rejects_zero_overlap(tmp_path):
    old_db_path = tmp_path / "old.db"
    _create_database(old_db_path)

    with pytest.raises(ValueError, match="zero matching protein IDs"):
        database_updater.check_table_match(
            old_db_path, pd.DataFrame({"ID": ["different_protein"]})
        )


def test_check_table_match_reports_partial_overlap(tmp_path):
    old_db_path = tmp_path / "old.db"
    _create_database(old_db_path)

    stats = database_updater.check_table_match(
        old_db_path, pd.DataFrame({"ID": ["protein_1", "new_protein"]})
    )

    assert stats == {
        "old_n": 2,
        "new_n": 2,
        "matched_n": 1,
        "match_rate_old": 0.5,
        "match_rate_new": 0.5,
    }


def test_create_new_database_replaces_all_conflicting_annotations(tmp_path):
    old_db_path = tmp_path / "old.db"
    new_db_path = tmp_path / "updated.db"
    _create_database(
        old_db_path,
        pd.DataFrame(
            {
                "ID": ["protein_1", "protein_2"],
                "old_annotation": ["old_1", "old_2"],
                "dbcan_EC": ["old_EC_1", "old_EC_2"],
            }
        ),
    )
    incoming = pd.DataFrame(
        {"ID": ["protein_1", "protein_2"], "old_annotation": ["new_1", "new_2"], "dbcan_EC": ["EC1", "EC2"]}
    )
    stats = database_updater.check_table_match(old_db_path, incoming)

    database_updater.create_new_database(
        old_db_path,
        new_db_path,
        incoming,
        stats,
        {"source_name": "test source", "source_url": "https://example.test", "update_mode": "exact_id_merge"},
    )

    with sqlite3.connect(new_db_path) as connection:
        annotations = pd.read_sql_query("SELECT * FROM id2annotation", connection)
        taxa = pd.read_sql_query("SELECT * FROM id2taxa", connection)
        provenance = pd.read_sql_query("SELECT * FROM annotation_update_metadata", connection)

    assert annotations["old_annotation"].tolist() == ["new_1", "new_2"]
    assert annotations["dbcan_EC"].tolist() == ["EC1", "EC2"]
    assert "old_annotation_update" not in annotations
    assert "dbcan_seq_EC" not in annotations
    assert taxa.to_dict("records") == [
        {"ID": "protein_1", "taxa": "taxa_1"},
        {"ID": "protein_2", "taxa": "taxa_2"},
    ]
    assert provenance.loc[0, "source_name"] == "test source"
    assert provenance.loc[0, "matched_id_count"] == 2


def test_run_db_update_custom_tsv_executes_full_update_workflow(tmp_path):
    old_db_path = tmp_path / "old.db"
    new_db_path = tmp_path / "updated.db"
    tsv_path = tmp_path / "custom_annotations.tsv"
    _create_database(old_db_path)
    pd.DataFrame(
        {"protein_name": ["protein_1", "protein_2"], "new_annotation": ["new_1", "new_2"]}
    ).to_csv(tsv_path, sep="\t", index=False)

    assert database_updater.run_db_update(
        "custom", str(tsv_path), str(old_db_path), str(new_db_path)
    )

    with sqlite3.connect(new_db_path) as connection:
        annotations = pd.read_sql_query("SELECT * FROM id2annotation", connection)
        provenance = pd.read_sql_query("SELECT * FROM annotation_update_metadata", connection)
    assert annotations["old_annotation"].tolist() == ["old_1", "old_2"]
    assert annotations["new_annotation"].tolist() == ["new_1", "new_2"]
    assert provenance.loc[0, "update_mode"] == "exact_id_merge"
