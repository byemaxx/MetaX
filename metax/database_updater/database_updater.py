import os
import sqlite3
import tarfile
import tempfile
from io import StringIO
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import pandas as pd


DBCAN_SEQ_URLS = {
    "dbCAN (HUMAN GUT)": "https://pro.unl.edu/dbCAN_seq/download_file.php?file=HUMAN%20GUT/dbCAN_overview.tar.gz",
    "dbCAN (COW RUMEN)": "https://pro.unl.edu/dbCAN_seq/download_file.php?file=COW%20RUMEN/dbCAN_overview.tar.gz",
    "dbCAN (MARINE)": "https://pro.unl.edu/dbCAN_seq/download_file.php?file=MARINE/dbCAN_overview.tar.gz",
}
DBCAN_EXPECTED_COLUMNS = [
    "ID",
    "dbcan_EC",
    "dbcan_HMMER",
    "dbcan_eCAMI",
    "dbcan_DIAMOND",
    "dbcan_NumOfTools",
]
LOW_MATCH_RATE = 0.05


def get_time():
    import datetime

    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _download_file_name(url):
    parsed = urlparse(url)
    requested_file = parse_qs(parsed.query).get("file", [None])[0]
    candidate = unquote(requested_file) if requested_file else parsed.path
    file_name = os.path.basename(candidate)
    if not file_name:
        raise ValueError(f"Cannot determine a file name from download URL: {url}")
    return file_name


def _validate_downloaded_archive(path, url):
    if os.path.getsize(path) == 0:
        raise ValueError(f"Downloaded dbCAN_seq file is empty: {url}")

    with open(path, "rb") as handle:
        preview_bytes = handle.read(200)
    preview = preview_bytes.decode("utf-8", errors="ignore").lstrip().lower()

    if (
        preview.startswith("<!doctype html")
        or preview.startswith("<html")
        or "invalid file" in preview
    ):
        raise ValueError(
            "dbCAN_seq server returned a non-archive response instead of "
            f"dbCAN_overview.tar.gz. Please check the dbCAN_seq download URL: {url}"
        )
    if not preview_bytes.startswith(b"\x1f\x8b"):
        raise ValueError(
            "Downloaded dbCAN_seq file is not a gzip archive. The server may have "
            f"returned an error page. URL: {url}; first bytes: {preview_bytes[:40]!r}"
        )


def download_file(url, save_dir):
    """Download a dbCAN_seq archive safely and return its final local path."""
    import requests

    file_name = _download_file_name(url)
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / file_name
    temp_path = None

    print(f"{get_time()} Start downloading {file_name}...")
    try:
        response = requests.get(
            url,
            timeout=60,
            stream=True,
            headers={"User-Agent": "MetaX database updater"},
        )
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=f"{file_name}.", suffix=".tmp", dir=save_dir, delete=False
        ) as handle:
            temp_path = Path(handle.name)
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)

        if file_name.endswith(".tar.gz"):
            _validate_downloaded_archive(temp_path, url)
        elif temp_path.stat().st_size == 0:
            raise ValueError(f"Downloaded file is empty: {url}")

        os.replace(temp_path, save_path)
        temp_path = None
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()

    print(f"{get_time()} {file_name} downloaded!\tSave path: {save_path}")
    return str(save_path)


def merge_dbcan(file_path):
    """Read dbCAN overview text tables from a validated gzip tar archive."""
    print(f"{get_time()} Start reading files...")
    dataframes = []

    try:
        with tarfile.open(file_path, "r:gz") as archive:
            for member in archive.getmembers():
                if not (member.isfile() and member.name.endswith(".txt")):
                    continue
                extracted = archive.extractfile(member)
                if extracted is None:
                    continue
                with extracted:
                    dataframes.append(
                        pd.read_csv(StringIO(extracted.read().decode("utf-8")), sep="\t")
                    )
    except (OSError, tarfile.TarError) as error:
        raise ValueError(
            f"Invalid dbCAN_seq archive: {file_path}. Expected a gzip tar archive containing overview .txt files."
        ) from error

    if not dataframes:
        raise ValueError(
            f"dbCAN_seq archive contains no .txt overview files: {file_path}"
        )

    print(f"{get_time()} Start concat files...")
    merged_df = pd.concat(dataframes, ignore_index=True)
    if len(merged_df.columns) != len(DBCAN_EXPECTED_COLUMNS):
        raise ValueError(
            "Unexpected dbCAN_seq overview structure. Expected six columns: "
            f"{', '.join(DBCAN_EXPECTED_COLUMNS)}; found {len(merged_df.columns)}."
        )

    merged_df.columns = DBCAN_EXPECTED_COLUMNS
    merged_df = merged_df.drop(columns=["dbcan_NumOfTools"])
    merged_df["dbcan_HMMER"] = (
        merged_df["dbcan_HMMER"].astype("string").str.split("(", n=1).str[0]
    )
    print(f"{get_time()} dbCAN overview: {merged_df.shape}")
    return merged_df


def _with_id_column(df):
    if df.empty and len(df.columns) == 0:
        raise ValueError("Annotation table has no columns.")
    result = df.copy()
    result.rename(columns={result.columns[0]: "ID"}, inplace=True)
    if result.columns.duplicated().any():
        duplicates = result.columns[result.columns.duplicated()].tolist()
        raise ValueError(f"Annotation table has duplicate column names: {duplicates}")
    return result


def get_new_anno_df(file_path) -> pd.DataFrame:
    df = _with_id_column(pd.read_csv(file_path, sep="\t"))
    print(f"{get_time()} new annotation: {df.shape}")
    print(f"{get_time()} new annotation columns: {df.columns}, the first column will be used as ID")
    return df


def _rename_conflicting_columns(old_columns, new_anno_df):
    new_anno_df = _with_id_column(new_anno_df)
    replaced_columns = [
        column for column in new_anno_df.columns if column != "ID" and column in old_columns
    ]
    if replaced_columns:
        print(
            f"{get_time()} Warning: replacing existing annotation columns with incoming "
            f"values: {replaced_columns}"
        )
    return new_anno_df, replaced_columns


def _write_provenance(new_conn, provenance, match_stats):
    provenance = provenance or {}
    new_conn.execute(
        """
        CREATE TABLE IF NOT EXISTS annotation_update_metadata (
            update_time TEXT NOT NULL,
            update_mode TEXT NOT NULL,
            source_name TEXT,
            source_url TEXT,
            old_id_count INTEGER NOT NULL,
            new_id_count INTEGER NOT NULL,
            matched_id_count INTEGER NOT NULL,
            match_rate_old REAL NOT NULL,
            match_rate_new REAL NOT NULL
        )
        """
    )
    new_conn.execute(
        """
        INSERT INTO annotation_update_metadata (
            update_time, update_mode, source_name, source_url, old_id_count,
            new_id_count, matched_id_count, match_rate_old, match_rate_new
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            get_time(),
            provenance.get("update_mode", "exact_id_merge"),
            provenance.get("source_name"),
            provenance.get("source_url"),
            match_stats["old_n"],
            match_stats["new_n"],
            match_stats["matched_n"],
            match_stats["match_rate_old"],
            match_stats["match_rate_new"],
        ),
    )


def create_new_database(old_db_path, new_db_path, new_anno_df, match_stats=None, provenance=None):
    """Create an updated database without replacing existing annotation fields."""
    if match_stats is None:
        match_stats = check_table_match(old_db_path, new_anno_df)
    with sqlite3.connect(old_db_path) as conn, sqlite3.connect(new_db_path) as new_conn:
        print(f"{get_time()} open id2annotation table...")
        id2annotation = pd.read_sql_query("SELECT * FROM id2annotation", conn)
        new_anno_df, replaced_columns = _rename_conflicting_columns(
            id2annotation.columns, new_anno_df
        )
        if replaced_columns:
            id2annotation = id2annotation.drop(columns=replaced_columns)

        print(f"{get_time()} merge id2annotation table...")
        merged_df = pd.merge(
            id2annotation,
            new_anno_df,
            on="ID",
            how="left",
            validate="one_to_one",
        ).fillna("-")
        merged_df.set_index("ID", inplace=True)
        print(f"{get_time()} write new id2annotation table to new database...")
        merged_df.to_sql("id2annotation", new_conn, if_exists="replace", index=True)

        id2taxa = pd.read_sql_query("SELECT * FROM id2taxa", conn)
        id2taxa.set_index("ID", inplace=True)
        print(f"{get_time()} write id2taxa table to new database...")
        id2taxa.to_sql("id2taxa", new_conn, if_exists="replace", index=True)
        _write_provenance(new_conn, provenance, match_stats)

    print(f"{get_time()} Done!")


def check_table_match(old_db_path, new_df):
    """Validate exact protein-ID overlap and return overlap statistics."""
    new_df = _with_id_column(new_df)
    with sqlite3.connect(old_db_path) as conn:
        old_df = pd.read_sql_query("SELECT ID FROM id2annotation", conn)

    old_ids = set(old_df["ID"].dropna().astype(str))
    new_ids = set(new_df["ID"].dropna().astype(str))
    matched_ids = old_ids & new_ids
    old_n = len(old_ids)
    new_n = len(new_ids)
    matched_n = len(matched_ids)
    stats = {
        "old_n": old_n,
        "new_n": new_n,
        "matched_n": matched_n,
        "match_rate_old": matched_n / old_n if old_n else 0.0,
        "match_rate_new": matched_n / new_n if new_n else 0.0,
    }
    print(
        f"{get_time()} ID overlap (exact match): old_n={old_n}, new_n={new_n}, "
        f"matched_n={matched_n}, match_rate_old={stats['match_rate_old']:.2%}, "
        f"match_rate_new={stats['match_rate_new']:.2%}"
    )
    if matched_n == 0:
        raise ValueError(
            "The old database and new annotation table have zero matching protein IDs. "
            "Built-in dbCAN_seq annotations are merged by exact protein ID; they do not "
            "perform sequence similarity annotation."
        )
    if stats["match_rate_old"] < LOW_MATCH_RATE:
        print(
            f"{get_time()} Warning: only {stats['match_rate_old']:.2%} of old database "
            "protein IDs match the incoming annotation table."
        )
    return stats


def get_built_in_df(built_in_db_name) -> pd.DataFrame:
    if built_in_db_name == "CAZy":
        print(f"{get_time()} CAZy is not supported yet!")
        return None
    try:
        url = DBCAN_SEQ_URLS[built_in_db_name]
    except KeyError as error:
        raise ValueError(f"Invalid built-in database name: {built_in_db_name}") from error

    save_dir = os.path.join(os.path.expanduser("~"), "MetaX")
    return merge_dbcan(download_file(url, save_dir))


def run_db_update(update_type, tsv_path, old_db_path, new_db_path, built_in_db_name=None):
    try:
        provenance = {"update_mode": "exact_id_merge"}
        if update_type == "built-in":
            new_anno_df = get_built_in_df(built_in_db_name)
            provenance.update(
                source_name=f"dbCAN_seq {built_in_db_name.removeprefix('dbCAN ').strip('()')}",
                source_url=DBCAN_SEQ_URLS.get(built_in_db_name),
            )
        elif update_type == "custom":
            new_anno_df = get_new_anno_df(tsv_path)
            provenance["source_name"] = os.path.basename(tsv_path)
        else:
            raise ValueError(f"Invalid type: {update_type}")

        match_stats = check_table_match(old_db_path, new_anno_df)
        create_new_database(
            old_db_path,
            new_db_path,
            new_anno_df,
            match_stats,
            provenance,
        )
        return True
    except Exception as error:
        print(f"{get_time()} Error: {error}")
        print(f"{get_time()} Failed!")
        raise


if __name__ == "__main__":
    print(f"{get_time()} Start...")
    run_db_update(
        update_type="built-in",
        tsv_path=None,
        old_db_path="MetaX-human-gut-new.db",
        new_db_path="1.0.db",
        built_in_db_name="dbCAN (HUMAN GUT)",
    )
