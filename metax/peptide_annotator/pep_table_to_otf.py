# This script is used to annotate peptides with their corresponding proteins of a Table.
# input: peptide_table
# output: peptide_table with an additional column of proteins

# main steps:
# 1. load peptide_table and preprocess if necessary
# 2. annotate peptides with proteins
# 3. reduce proteins by genome ranking
# 4. save the annotated peptide_table or transfer to OTF annotator

#TODO:
# 1. add mutiple prefix options for intensity columns
# 2. add refine samples name function. e.g. D:/path/to/file/xxx.raw -> xxx


import sqlite3
import json
import os
import sys
import pathlib
import concurrent.futures
import time
import subprocess
import tempfile
from collections import defaultdict
from typing import Optional, Iterable

import pandas as pd
from tqdm import tqdm


def _ensure_project_root_on_syspath() -> None:
    """Allow running this file directly as a script.

    When executing `python metax/peptide_annotator/pep_table_to_otf.py`, Python sets
    `sys.path[0]` to the script directory (metax/peptide_annotator), so `import metax`
    fails because the project root is not on sys.path.

    Adding the repo root enables absolute imports like `metax.peptide_annotator...`.
    """
    if __package__:
        return

    this_file = pathlib.Path(__file__).resolve()
    repo_root = this_file.parents[2]  # .../MetaX
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)


_ensure_project_root_on_syspath()

# NOTE: Avoid importing GUI/Matplotlib-related modules at import-time.
# This file can be imported inside multiprocessing workers on Windows; importing
# Qt/Matplotlib backends there can trigger repeated backend initialization or
# even crashes. We import these lazily where needed.

def query_peptide_proteins(db_file, peptide_list, 
                           chunk_size=10000, 
                           removed_genomes_set:set|None = None,
                           selected_genomes_set:set|None = None):
    """
    Query peptide to protein mapping from a database with progress tracking.

    Args:
        db_file (str): The file path to the SQLite database.
        peptide_list (list of str): A list of peptide sequences to query.
        chunk_size (int): The number of peptides to query in one batch (default: 10000).
        removed_genomes_set (set[str] | None): Genomes to exclude. None means no exclusion; empty set means exclude nothing.
        selected_genomes_set (set[str] | None): Genomes to include. None means no inclusion filter; empty set means include none.

    Note:
        If a genome appears in both selected and removed sets, removal takes precedence.
        
    Returns:
        dict: A dictionary mapping peptide sequences to a semicolon-separated string of proteins.
    """
    peptide_proteins = {}

    # if set is empty, treat as no filtering
    sel_set = set(selected_genomes_set) if selected_genomes_set else None
    rm_set = set(removed_genomes_set) if removed_genomes_set else None

    # 冲突处理：同时在 selected 与 removed 中的基因组，按“移除优先”
    if sel_set is not None and rm_set is not None:
        conflict = sel_set & rm_set
        if conflict:
            print(f"Warning: {len(conflict)} genomes appear in both selected and removed sets; removal takes precedence.")
            sel_set -= rm_set

    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        # limit chunk size based on SQLite max variable number
        try:
            cursor.execute("PRAGMA max_variable_number;")
            row = cursor.fetchone()
            max_vars = int(row[0]) if row and row[0] else 999
        except Exception:
            max_vars = 999
        chunk_size = max(1, min(chunk_size, max_vars))

        for i in tqdm(range(0, len(peptide_list), chunk_size), desc="Querying database in chunks"):
            chunk = peptide_list[i:i + chunk_size]
            query = "SELECT peptide, proteins FROM peptide_proteins WHERE peptide IN ({})".format(
                ','.join(['?'] * len(chunk))
            )
            cursor.execute(query, chunk)
            rows = cursor.fetchall()

            for peptide, proteins_json in rows:
                try:
                    proteins = json.loads(proteins_json)
                except json.JSONDecodeError:
                    peptide_proteins[peptide] = ""
                    continue

                # returning empty if no proteins found
                if not proteins or not isinstance(proteins, list):
                    peptide_proteins[peptide] = ""
                    continue

                # filtering by selected/removed genomes
                if sel_set is not None:
                    proteins = [p for p in proteins if p.split('_', 1)[0] in sel_set]
                if rm_set is not None:
                    proteins = [p for p in proteins if p.split('_', 1)[0] not in rm_set]

                peptide_proteins[peptide] = ';'.join(proteins) if proteins else ""

    return peptide_proteins


# =========================
# Digested genome folder mode
# =========================
def _infer_digest_columns(columns: Iterable[str]) -> tuple[str, str]:
    """Infer peptide/protein columns from a digested-genome TSV header.

    The digested genome TSVs are expected to contain at least:
    - a peptide sequence column (e.g. Peptide / Sequence)
    - a protein id column (e.g. Protein / protein_id)

    This function is intentionally permissive because different digest pipelines
    may output different column names.
    """
    cols = [str(c) for c in columns]
    lower = {c.lower(): c for c in cols}

    peptide_candidates = [
        "peptide",
        "sequence",
        "base sequence",
        "stripped.sequence",
        "peptide sequence",
    ]
    protein_candidates = [
        "protein",
        "proteins",
        "protein_id",
        "protein id",
        "proteinid",
        "parent protein",
        "accession",
        "protein accession",
    ]

    peptide_col = None
    for k in peptide_candidates:
        if k in lower:
            peptide_col = lower[k]
            break

    protein_col = None
    for k in protein_candidates:
        if k in lower:
            protein_col = lower[k]
            break

    if peptide_col is None or protein_col is None:
        raise ValueError(
            "Cannot infer peptide/protein columns from digested TSV. "
            f"Found columns: {cols}. "
            "Please make sure each digested genome TSV contains both peptide and protein id columns "
            "(e.g. 'Peptide' + 'Protein' or 'Sequence' + 'protein_id')."
        )
    return peptide_col, protein_col


def _resolve_digest_columns_once(
    first_file: str,
    sep: str = "\t",
    digested_peptide_col: str | None = None,
    digested_protein_col: str | None = None,
) -> tuple[str, str]:
    """Resolve digested TSV peptide/protein column names once (all files share the same format).

    Priority:
    1) Use user-provided column names if given (validate against header when possible)
    2) Otherwise infer from header via _infer_digest_columns
    3) If inference fails, fallback to positional default: col0=protein, col1=peptide

    Returns:
        (peptide_col, protein_col)
    """
    header = pd.read_csv(first_file, sep=sep, nrows=0)
    cols = [str(c) for c in header.columns]
    if len(cols) < 2:
        raise ValueError(f"Digested genome TSV must have at least 2 columns: {first_file}")

    # If provided, trust them but validate against header
    pep = digested_peptide_col
    pro = digested_protein_col
    if pep or pro:
        if pep and pep not in cols:
            print(f"[DigestedScan] Warning: peptide column '{pep}' not in header; will try inference/fallback")
            pep = None
        if pro and pro not in cols:
            print(f"[DigestedScan] Warning: protein column '{pro}' not in header; will try inference/fallback")
            pro = None

        if pep and pro:
            return pep, pro

    # Infer (only for missing ones)
    try:
        inferred_pep, inferred_pro = _infer_digest_columns(cols)
    except Exception:
        inferred_pep, inferred_pro = None, None

    pep = pep or inferred_pep
    pro = pro or inferred_pro

    if pep and pro:
        return pep, pro

    # Final fallback: positional default (protein first, peptide second)
    fallback_pro = cols[0]
    fallback_pep = cols[1]
    print(
        "[DigestedScan] Warning: cannot infer digested columns; "
        f"falling back to positional default protein='{fallback_pro}', peptide='{fallback_pep}'"
    )
    return fallback_pep, fallback_pro


def _normalize_protein_ids(
    genome_id: str,
    protein_value: str,
    protein_genome_separator: str = "_",
) -> list[str]:
    """Normalize protein IDs to the MetaX convention: genomeId + separator + proteinId.

    If the protein already looks like it starts with '{genome_id}{sep}', keep it.
    Supports multi-protein fields separated by ';'.
    """
    if protein_value is None:
        return []
    protein_value = str(protein_value).strip()
    if not protein_value or protein_value.lower() == "nan":
        return []

    proteins = [p.strip() for p in protein_value.split(";") if p.strip()]
    out: list[str] = []
    prefix = f"{genome_id}{protein_genome_separator}"
    for p in proteins:
        if p.startswith(prefix):
            out.append(p)
        else:
            out.append(prefix + p)
    return out


def _process_digested_genome_batch_for_mapping(
    file_paths: list[str],
    peptide_set: set[str],
    removed_genomes_set: Optional[set[str]],
    selected_genomes_set: Optional[set[str]],
    protein_genome_separator: str,
    digested_peptide_col: str,
    digested_protein_col: str,
    sep: str = "\t",
    chunksize: int = 500_000,
) -> dict[str, set[str]]:
    """Process a batch of digested genome TSVs and return peptide->proteins mapping."""
    mapping: dict[str, set[str]] = defaultdict(set)

    for file_path in file_paths:
        genome_id = pathlib.Path(file_path).stem

        if removed_genomes_set is not None and genome_id in removed_genomes_set:
            continue
        if selected_genomes_set is not None and genome_id not in selected_genomes_set:
            continue

        try:
            for chunk in pd.read_csv(
                file_path,
                sep=sep,
                usecols=[digested_peptide_col, digested_protein_col],
                dtype={digested_peptide_col: "string", digested_protein_col: "string"},
                chunksize=chunksize,
                engine="c",
            ):
                peptide_col = digested_peptide_col
                protein_col = digested_protein_col

                chunk = chunk.dropna(subset=[peptide_col, protein_col])
                if chunk.empty:
                    continue

                hit = chunk[chunk[peptide_col].astype(str).isin(peptide_set)]
                if hit.empty:
                    continue

                for pep, pro in zip(hit[peptide_col].astype(str), hit[protein_col].astype(str)):
                    for pid in _normalize_protein_ids(
                        genome_id=genome_id,
                        protein_value=pro,
                        protein_genome_separator=protein_genome_separator,
                    ):
                        mapping[pep].add(pid)

        except Exception:
            # keep the batch robust: a single bad file should not kill the whole mapping
            continue

    return mapping


def query_peptide_proteins_from_digested_genome_folders(
    digested_genome_folders: str | list[str],
    peptide_list: list[str],
    removed_genomes_set: set[str] | None = None,
    selected_genomes_set: set[str] | None = None,
    protein_genome_separator: str = "_",
    sep: str = "\t",
    n_jobs: int | None = None,
    digested_peptide_col: str | None = None,
    digested_protein_col: str | None = None,
    parallel_backend: str = "thread",
) -> tuple[dict[str, str], str, str]:
    """Build peptide->proteins mapping by scanning digested genome TSV files directly.

    该模式用于替代预先构建 SQLite 的 peptide_to_protein 数据库：
    - 输入为一个或多个 digested genome 文件夹（每个文件夹下 *.tsv 为一个 genome）
    - 逐文件扫描，只保留出现在 peptide_list 中的 peptides
    - 输出与 DB 模式一致：{peptide: 'genome_protein;genome_protein;...'}
    """
    t0 = time.time()
    folders = [digested_genome_folders] if isinstance(digested_genome_folders, str) else list(digested_genome_folders)
    valid_folders: list[str] = []
    for folder in folders:
        if folder and os.path.isdir(folder):
            valid_folders.append(folder)

    if not valid_folders:
        raise ValueError(f"No valid digested genome folders found: {folders}")

    all_files: list[str] = []
    for folder in valid_folders:
        all_files.extend([str(p) for p in pathlib.Path(folder).glob("*.tsv")])

    if not all_files:
        raise ValueError(f"No '*.tsv' digested genome files found in: {valid_folders}")

    # Resolve digested column names once (assume all genome TSVs share the same header)
    resolved_pep_col, resolved_pro_col = _resolve_digest_columns_once(
        first_file=all_files[0],
        sep=sep,
        digested_peptide_col=digested_peptide_col,
        digested_protein_col=digested_protein_col,
    )

    print(f"[DigestedScan] Folders: {len(valid_folders)}")
    for f in valid_folders:
        print(f"[DigestedScan]  - {f}")
    print(f"[DigestedScan] Genome TSV files: {len(all_files)}")
    print(f"[DigestedScan] Using columns: peptide='{resolved_pep_col}', protein='{resolved_pro_col}'")

    peptide_set = {str(p) for p in peptide_list if isinstance(p, str) and p}
    if not peptide_set:
        # keep return type stable
        return {}, "", ""

    rm_set = set(removed_genomes_set) if removed_genomes_set else None
    sel_set = set(selected_genomes_set) if selected_genomes_set else None
    if rm_set is not None and sel_set is not None:
        sel_set -= rm_set

    if n_jobs is None:
        n_jobs = max(1, (os.cpu_count() or 1) - 1)

    print(f"[DigestedScan] n_jobs={n_jobs}, peptides_to_query={len(peptide_set)}")

    # create batches to reduce overhead (ref: cal_genome_socer.py)
    batch_count = max(1, n_jobs * 4)
    batches: list[list[str]] = [all_files[i::batch_count] for i in range(batch_count)]
    batches = [b for b in batches if b]

    print(f"[DigestedScan] Batches: {len(batches)} (batch_count={batch_count})")

    parallel_backend = (parallel_backend or "thread").strip().lower()
    if parallel_backend not in {"thread", "process"}:
        raise ValueError("parallel_backend must be 'thread' or 'process'")

    merged: dict[str, set[str]] = defaultdict(set)
    # Default is thread for GUI stability.
    # If you run from CLI and want max CPU, set parallel_backend='process'.
    Executor = (
        concurrent.futures.ProcessPoolExecutor
        if parallel_backend == "process"
        else concurrent.futures.ThreadPoolExecutor
    )

    with Executor(max_workers=n_jobs) as executor:
        futures = [
            executor.submit(
                _process_digested_genome_batch_for_mapping,
                batch,
                peptide_set,
                rm_set,
                sel_set,
                protein_genome_separator,
                resolved_pep_col,
                resolved_pro_col,
                sep,
            )
            for batch in batches
        ]

        for fut in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Scanning digested genomes"):
            part = fut.result()
            for pep, proteins in part.items():
                merged[pep].update(proteins)

    # to the same output format as DB query
    out: dict[str, str] = {}
    for pep in peptide_list:
        proteins = sorted(merged.get(str(pep), set()))
        out[str(pep)] = ";".join(proteins) if proteins else ""

    hit_cnt = sum(1 for v in out.values() if v)
    elapsed = time.time() - t0
    print(f"[DigestedScan] Done. Mapped peptides: {hit_cnt}/{len(peptide_list)}. Time: {elapsed:.2f}s")
    return out, resolved_pep_col, resolved_pro_col


class peptideProteinsMapper:
    def __init__(
                 self,
                 peptide_table_path,
                 db_path: str | None = None,
                 digested_genome_folders: str | list[str] | None = None,
                 digested_peptide_col: str | None = None,
                 digested_protein_col: str | None = None,
                 removed_genomes_set:set|None = None,
                 selected_genomes_set:set|None = None,
                 table_separator='\t',
                 peptide_col='Sequence', 
                 intensity_col_prefix='Intensity',
                 genome_cutoff_rank:int|None= None,   # if set, it will only get the top N genomes, otherwise use genome_peptide_coverage_cutoff
                 genome_peptide_coverage_cutoff:float|None = 0.97,
                 protein_peptide_coverage_cutoff:float|None = 1.0,
                 output_path=None,
                 temp_dir=None,
                 stop_after_genome_ranking=False,
                 continue_base_on_annotaied_peptide_table=False, # use genome annotated peptide table to continue the process, skip querying proteins
                 turn_point_method='auto', # 'auto', 'coverage', 'rank', or 'distinct_count'
                 turn_point_distinct_cutoff=3, # cutoff value for distinct_count method
                 protein_genome_separator: str = "_",
                 n_jobs: int | None = None,
                 digested_parallel_backend: str = "subprocess",
                 genome_list: Iterable[str] | None = None,
                 ):

        self.peptide_table_path = peptide_table_path
        self.db_file = db_path
        self.digested_genome_folders = digested_genome_folders
        self.digested_peptide_col = digested_peptide_col
        self.digested_protein_col = digested_protein_col
        self.removed_genomes_set = removed_genomes_set
        self.selected_genomes_set = selected_genomes_set
        self.genome_list = self._normalize_genome_list(genome_list)
        self.table_separator = table_separator
        self.peptide_col = peptide_col
        self.intensity_col_prefix = intensity_col_prefix
        self.genome_cutoff_rank = genome_cutoff_rank 
        self.genome_peptide_coverage_cutoff = genome_peptide_coverage_cutoff
        self.protein_peptide_coverage_cutoff = protein_peptide_coverage_cutoff
        self.output_path = output_path
        self.temp_dir = None
        self.stop_after_genome_ranking = stop_after_genome_ranking
        self.continue_base_on_annotaied_peptide_table = continue_base_on_annotaied_peptide_table
        self.turn_point_method = turn_point_method # 'auto', 'coverage', 'rank', or 'distinct_count'
        self.turn_point_distinct_cutoff = turn_point_distinct_cutoff # cutoff value for distinct_count method
        self.protein_genome_separator = protein_genome_separator
        self.n_jobs = n_jobs
        self.digested_parallel_backend = digested_parallel_backend
        
        self.has_intensity = False
        self.protein_ranked_table = None
        self.genome_ranked_table = None
        self.final_peptide_table = None
        
        self.selected_proteins_num = 0
        self.selected_genomes_num = 0
        self.original_peptides_before_mapping = 0
        self.peptides_after_mapping = 0
        self.removed_peptides_no_matched = 0
        
        self.set_temp_dir(temp_dir)
        self.peptide_table = self.load_peptide_table()

    @staticmethod
    def _log_save(df: pd.DataFrame, path: str, desc: str) -> None:
        try:
            rows = len(df)
        except Exception:
            rows = "Unknown"
        print(f"[Save...] {desc}: {path} (rows={rows})")

    @staticmethod
    def _normalize_genome_list(genome_list: Iterable[str] | None) -> list[str] | None:
        if genome_list is None:
            return None

        raw_items = genome_list.split(";") if isinstance(genome_list, str) else list(genome_list)
        cleaned: list[str] = []
        seen: set[str] = set()
        for item in raw_items:
            if item is None:
                continue
            genome = str(item).strip()
            if not genome or genome in seen:
                continue
            seen.add(genome)
            cleaned.append(genome)
        return cleaned

    @staticmethod
    def _collect_genomes_from_df(df: pd.DataFrame) -> set[str]:
        if 'Genomes' not in df.columns:
            return set()

        genomes: set[str] = set()
        for value in df['Genomes'].dropna():
            value_str = str(value).strip()
            if not value_str or value_str.lower() == 'nan':
                continue
            for genome in value_str.split(';'):
                genome = genome.strip()
                if genome:
                    genomes.add(genome)
        return genomes

    def _get_selected_genome_list(
        self,
        df: pd.DataFrame,
        genome_list: Iterable[str] | None = None,
    ) -> list[str]:
        effective_genome_list = (
            self._normalize_genome_list(genome_list)
            if genome_list is not None
            else self.genome_list
        )

        if effective_genome_list is None:
            return self.calculate_genome_list(df, turn_point_method=self.turn_point_method)

        if not effective_genome_list:
            print("Warning: genome_list is provided but empty; no genomes will be selected.")
            self.selected_genomes_num = 0
            return []

        available_genomes = self._collect_genomes_from_df(df)
        selected_genomes_list = list(effective_genome_list)

        if available_genomes:
            missing = [g for g in selected_genomes_list if g not in available_genomes]
            selected_genomes_list = [g for g in selected_genomes_list if g in available_genomes]
            if missing:
                preview = ', '.join(missing[:10])
                suffix = "..." if len(missing) > 10 else ""
                print(
                    f"Warning: {len(missing)} genomes in genome_list are not found in annotated peptides "
                    f"and will be ignored: {preview}{suffix}"
                )

        print(
            f"Using provided genome_list, skip calculate_genome_list(). "
            f"Selected genomes: [{len(selected_genomes_list)}]"
        )
        self.selected_genomes_num = len(selected_genomes_list)
        return selected_genomes_list
    
    def load_peptide_table(self):
        print("Loading peptide table...")
        
        header_df = pd.read_csv(self.peptide_table_path, sep=self.table_separator, nrows=0)
        self._check_columns(header_df.columns)
        
        required_cols = [self.peptide_col]
        intensity_cols = [col for col in header_df.columns if col.startswith(self.intensity_col_prefix)]
        
        if self.continue_base_on_annotaied_peptide_table:
            required_cols.extend(['Genomes', 'Proteins'])
        
        required_cols.extend(intensity_cols)
        
        # only print first 10 columns if too many
        print(f"Reading columns: {required_cols[:10]}{'...' if len(required_cols) > 10 else ''}")
        
        self.peptide_table = pd.read_csv(self.peptide_table_path, sep=self.table_separator, usecols=required_cols)
        
        if intensity_cols:
            self.has_intensity = True
            print("Intensity columns found, will be kept in the output and used for genome ranking")
            self.sum_duplicates_peptides()
        else:
            print("Warning: Intensity columns not found")
            raise ValueError(f"The intensity columns you specified:[{self.intensity_col_prefix}] are not in the peptide_table, please check!")
        
        return self.peptide_table
    
    def _check_columns(self, columns):
        """Check if the necessary columns are in the peptide table."""
        if self.continue_base_on_annotaied_peptide_table:
            print("Continue base on annotated peptide table")
            print(f"Check if all the necessary columns are in the peptide table\
                \nPeptide column: [{self.peptide_col}]\
                \nIntensity columns prefix: [{self.intensity_col_prefix}]\
                \nGenomes column: [Genomes]\
                \nProteins column: [Proteins]")
            for col in [self.peptide_col, 'Genomes', 'Proteins']:
                if col not in columns:
                    raise ValueError(f"The peptide table should have a column named '{col}'")
        else:
            print(f"Check if all the necessary columns are in the peptide table\
                \nPeptide column: [{self.peptide_col}]\
                \nIntensity columns prefix: [{self.intensity_col_prefix}]")
            if self.peptide_col not in columns:
                raise ValueError(f"The peptide column you specified:[{self.peptide_col}] is not in the peptide_table, please check!")

        if not any([col.startswith(self.intensity_col_prefix) for col in columns]):
            raise ValueError(f"The intensity columns you specified:[{self.intensity_col_prefix}] are not in the peptide_table, please check!")

    def set_temp_dir(self, temp_dir):
        if temp_dir:
            # check if the temp dir valid
            temp_dir = pathlib.Path(temp_dir)
            if not temp_dir.is_dir():
                raise ValueError(f"Invalid temp dir path: {temp_dir}")
            self.temp_dir = temp_dir
            
        else:
            # create a temp dir in output path
            temp_dir = pathlib.Path(self.output_path).parent / 'metax_temp'
            temp_dir.mkdir(parents=True, exist_ok=True)
            self.temp_dir = temp_dir
    
    def sum_duplicates_peptides(self):
        # check if the peptides are unique, if not, combine the intensity columns, sum them up, if na , consider as 0
        # Get all intensity columns
        intensity_cols = [col for col in self.peptide_table.columns if col.startswith(self.intensity_col_prefix)]
        print(f"Found {len(intensity_cols)} intensity columns")

        # Check if peptides are unique
        duplicated_peptides = self.peptide_table[self.peptide_col].duplicated().sum()
        if duplicated_peptides > 0:
            print(f"Found {duplicated_peptides} duplicate peptide entries, combining their intensities")
            
            # Fill NA values with 0 in intensity columns
            self.peptide_table[intensity_cols] = self.peptide_table[intensity_cols].fillna(0)
            
            # Group by peptide and sum the intensity columns
            grouped_table = self.peptide_table.groupby(self.peptide_col)[intensity_cols].sum().reset_index()            
            
            # Get non-intensity columns
            non_intensity_cols = [col for col in self.peptide_table.columns 
                                    if not col.startswith(self.intensity_col_prefix) and col != self.peptide_col]
            
            # Keep the first occurrence of each peptide for other columns
            first_occurrence = self.peptide_table.drop_duplicates(subset=[self.peptide_col])[
                [self.peptide_col] + non_intensity_cols]
            
            # Merge back together
            self.peptide_table = pd.merge(grouped_table, first_occurrence, on=self.peptide_col)
            
            print(f"After combining duplicates: {len(self.peptide_table)} unique peptides")
        else:
            print("No duplicate peptides found, skipping combination of intensities")

    def annotate_peptides(self):
        """Annotate peptides with proteins.

        Two modes:
        1) SQLite DB mode (legacy): provide db_path with a peptide_proteins table.
        2) Folder mode (NEW): provide digested_genome_folders; scan digested genome TSVs directly.

        Folder mode is designed to avoid building peptide_to_protein.db in advance.
        """
        print("Start annotating peptides with proteins")
        
        unique_peptides = self.peptide_table[self.peptide_col].drop_duplicates().tolist()

        if self.digested_genome_folders is not None:
            print("Annotation mode: digested genome folders (no pre-built peptide DB needed)")
            backend = (self.digested_parallel_backend or "subprocess").strip().lower()
            if backend == "subprocess":
                peptide_proteins_dict, resolved_pep_col, resolved_pro_col = self._query_peptide_proteins_via_subprocess(
                    peptide_list=unique_peptides,
                )
            else:
                peptide_proteins_dict, resolved_pep_col, resolved_pro_col = query_peptide_proteins_from_digested_genome_folders(
                    digested_genome_folders=self.digested_genome_folders,
                    peptide_list=unique_peptides,
                    removed_genomes_set=self.removed_genomes_set,
                    selected_genomes_set=self.selected_genomes_set,
                    protein_genome_separator=self.protein_genome_separator,
                    # digested genome TSVs are generated by digestion pipelines and are expected to be tab-separated
                    sep="\t",
                    n_jobs=self.n_jobs,
                    digested_peptide_col=self.digested_peptide_col,
                    digested_protein_col=self.digested_protein_col,
                    parallel_backend=backend,
                )

            # cache the resolved columns (all digested files share the same format)
            self.digested_peptide_col = resolved_pep_col
            self.digested_protein_col = resolved_pro_col
        else:
            if not self.db_file:
                raise ValueError("Either db_path or digested_genome_folders must be provided for peptide->protein annotation")
            print("Annotation mode: SQLite peptide DB")
            peptide_proteins_dict = query_peptide_proteins(
                self.db_file,
                unique_peptides,
                removed_genomes_set=self.removed_genomes_set,
                selected_genomes_set=self.selected_genomes_set,
            )

        self.peptide_table["Proteins"] = self.peptide_table[self.peptide_col].map(peptide_proteins_dict)

        mapped_cnt = int(self.peptide_table["Proteins"].notna().sum())
        print(f"Mapped (non-null) Proteins rows: {mapped_cnt}/{len(self.peptide_table)}")

        original_count = len(self.peptide_table)
        self.original_peptides_before_mapping = original_count
        self.peptide_table = self.peptide_table[self.peptide_table["Proteins"].notna() & (self.peptide_table["Proteins"] != "")]
        removed_count = original_count - len(self.peptide_table)
        self.peptides_after_mapping = len(self.peptide_table)
        self.removed_peptides_no_matched = removed_count
        
        print(f"Original peptides: {original_count}, after filtering: {len(self.peptide_table)}")
        print(f"Removed peptides: {removed_count} due to no protein mapped in the database")

        return self.peptide_table

    def _query_peptide_proteins_via_subprocess(
        self,
        peptide_list: list[str],
    ) -> tuple[dict[str, str], str, str]:
        """Run digested scanning in an isolated subprocess (stable for GUI on Windows).

        The subprocess will:
        - read peptide list from a temporary file
        - scan digested genome TSVs using a process pool (full CPU)
        - write a mapping TSV + a metadata JSON

        Returns:
            (mapping_dict, resolved_peptide_col, resolved_protein_col)
        """
        if self.digested_genome_folders is None:
            raise ValueError("digested_genome_folders is required")
        if not peptide_list:
            return {}, "", ""

        folders = [self.digested_genome_folders] if isinstance(self.digested_genome_folders, str) else list(self.digested_genome_folders)
        folders = [f for f in folders if f]
        if not folders:
            raise ValueError("No digested_genome_folders provided")

        # Use a temp dir under the current temp_dir when available (keeps artifacts discoverable).
        base_tmp = None
        try:
            base_tmp = str(self.temp_dir)
        except Exception:
            base_tmp = None

        with tempfile.TemporaryDirectory(prefix="metax_digested_scan_", dir=base_tmp) as tmp:
            tmp_path = pathlib.Path(tmp)
            peptides_file = tmp_path / "peptides.txt"
            out_mapping = tmp_path / "mapping.tsv"
            out_meta = tmp_path / "meta.json"
            removed_file = tmp_path / "removed_genomes.txt"
            selected_file = tmp_path / "selected_genomes.txt"

            peptides_file.write_text("\n".join([str(p) for p in peptide_list if p]), encoding="utf-8")

            removed_arg = []
            if self.removed_genomes_set:
                removed_file.write_text("\n".join(sorted(set(self.removed_genomes_set))), encoding="utf-8")
                removed_arg = ["--removed-genomes-file", str(removed_file)]

            selected_arg = []
            if self.selected_genomes_set:
                selected_file.write_text("\n".join(sorted(set(self.selected_genomes_set))), encoding="utf-8")
                selected_arg = ["--selected-genomes-file", str(selected_file)]

            pep_col_arg = []
            if self.digested_peptide_col:
                pep_col_arg = ["--digested-peptide-col", str(self.digested_peptide_col)]

            pro_col_arg = []
            if self.digested_protein_col:
                pro_col_arg = ["--digested-protein-col", str(self.digested_protein_col)]

            n_jobs = 0 if self.n_jobs is None else int(self.n_jobs)

            # Ensure the subprocess can import `metax` even when launched from GUI.
            repo_root = pathlib.Path(__file__).resolve().parents[2]
            env = os.environ.copy()
            env["PYTHONPATH"] = str(repo_root) + os.pathsep + env.get("PYTHONPATH", "")
            # Avoid Windows locale (e.g., GBK) decode issues when capturing output.
            env.setdefault("PYTHONIOENCODING", "utf-8")

            cmd = [
                sys.executable,
                "-m",
                "metax.peptide_annotator.digested_scan_cli",
                "--folders",
                *[str(f) for f in folders],
                "--peptides-file",
                str(peptides_file),
                "--out-mapping-tsv",
                str(out_mapping),
                "--out-meta-json",
                str(out_meta),
                "--sep",
                "\t",
                "--n-jobs",
                str(n_jobs),
                "--protein-genome-separator",
                str(self.protein_genome_separator),
                *pep_col_arg,
                *pro_col_arg,
                *removed_arg,
                *selected_arg,
            ]

            print(f"[DigestedScan/Subprocess] Launch: {' '.join(cmd[:6])} ...")

            # Stream output back to current stdout for visibility.
            creationflags = 0
            try:
                creationflags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
            except Exception:
                creationflags = 0

            proc = subprocess.Popen(
                cmd,
                cwd=str(repo_root),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                creationflags=creationflags,
            )

            last_lines: list[str] = []
            assert proc.stdout is not None
            for line in proc.stdout:
                print(line.rstrip("\n"))
                last_lines.append(line)
                if len(last_lines) > 50:
                    last_lines = last_lines[-50:]

            rc = proc.wait()
            if rc != 0:
                tail = "".join(last_lines[-20:])
                raise RuntimeError(f"Digested scan subprocess failed (exit={rc}). Last output:\n{tail}")

            if not out_mapping.is_file():
                raise RuntimeError("Digested scan subprocess finished but mapping.tsv not found")
            if not out_meta.is_file():
                raise RuntimeError("Digested scan subprocess finished but meta.json not found")

            meta = {}
            try:
                meta = json.loads(out_meta.read_text(encoding="utf-8"))
            except Exception:
                meta = {}

            resolved_pep_col = str(meta.get("resolved_digested_peptide_col", ""))
            resolved_pro_col = str(meta.get("resolved_digested_protein_col", ""))

            df_map = pd.read_csv(out_mapping, sep="\t", dtype={"Peptide": "string", "Proteins": "string"})
            mapping = dict(zip(df_map["Peptide"].astype(str), df_map["Proteins"].fillna("").astype(str)))

            return mapping, resolved_pep_col, resolved_pro_col

    def extract_genome_col(self, df):
        def extract_genome(proteins):
            if proteins in [None, '', 'NaN']:
                return ''
            proteins = proteins.split(';')
            genomes = []
            for protein in proteins:
                genome = protein.split('_')[0]
                genomes.append(genome)
            genomes = list(set(genomes))
            return ';'.join(genomes)

        df['Genomes'] = df['Proteins'].apply(extract_genome)
        return df
        
    def _update_cutoff_parameters_for_reporting(self, turn_point_method):
        if turn_point_method.lower() == 'auto':
            self.genome_cutoff_rank = "N/A"
            self.turn_point_distinct_cutoff = "N/A"
            self.genome_peptide_coverage_cutoff = "N/A"
        elif turn_point_method.lower() == 'coverage':
            self.genome_cutoff_rank = "N/A"
            self.turn_point_distinct_cutoff = "N/A"
        elif turn_point_method.lower() == 'rank':
            self.turn_point_distinct_cutoff = "N/A"
            self.genome_peptide_coverage_cutoff = "N/A"
        elif turn_point_method.lower() == 'distinct_count':
            self.genome_cutoff_rank = "N/A"
            self.genome_peptide_coverage_cutoff = "N/A"
        else:
            # warning already raised in calculate_genome_list
            pass
        
    def calculate_genome_list(self, df, turn_point_method="auto") -> list[str]:
        ''' 
        INPUT: df with columns: Peptide, Proteins, Genomes, Intensity*
        OUTPUT: list of selected genomes based on the turning point method
        Parameters for turning point methods:
        - auto: automatically calculate the turning point based on the coverage_ratio curve (default)
        - coverage: select genomes until the coverage_ratio reaches a specified cutoff (e.g. 0.97)
        - rank: select top N genomes based on the combined score ranking (e.g. top 10)
        - distinct_count: select genomes with at least N distinct peptides (e.g. 3)
        '''
        from metax.peptide_annotator.get_genome_rank import GenomeRank
        gr = GenomeRank(df = df, 
                                 peptide_column = self.peptide_col,
                                 genome_column = 'Genomes',
                                 genome_separator = ';')
        df_results_rank = gr.get_rank_covre_df(genome_rank_method='combined', 
                                                           weight_distinct=1, weight_peptide=0)
        df_weights = gr.df_combined[['Genomes', 'distinct_norm', 'peptide_norm', 'combined_score']]
        df_results_rank = df_results_rank.merge(df_weights, on='Genomes', how='left')
        # svaing the genome ranking table to temp dir
        # df_results_rank.to_csv(f'{self.output_path.replace(".tsv", "_genome_ranked.tsv")}', sep='\t', index=False)
        genome_rank_path = f'{self.temp_dir}/genome_ranked.tsv'
        self._log_save(df_results_rank, genome_rank_path, "genome_ranked")
        t0 = time.time()
        df_results_rank.to_csv(genome_rank_path, sep='\t', index=False)
        print(f"[Save] genome_ranked done in {time.time() - t0:.2f}s")
        self.genome_ranked_table = df_results_rank
        
        if turn_point_method.lower() == 'auto':
            window_size = 20
            std_threshold = 1
            print(f"Calculating turning point by rolling window: window_size={window_size}, std_threshold={std_threshold}")
            cutoff_index = gr._calculate_turning_point(df_results_rank, window_size, std_threshold)

        elif turn_point_method.lower() == 'coverage':
            if type(self.genome_peptide_coverage_cutoff) not in [float, int] or not (0 < self.genome_peptide_coverage_cutoff < 1): # type: ignore
                self.genome_peptide_coverage_cutoff = 0.97
                print(f"Warning: Invalid genome_peptide_coverage_cutoff: {self.genome_peptide_coverage_cutoff}, should be between 0 and 1. Using default value: 0.97")
                
            print(f"Calculating turning point by percentage cutoff: {self.genome_peptide_coverage_cutoff}")
            cutoff_index = df_results_rank[df_results_rank['coverage_ratio'] >= self.genome_peptide_coverage_cutoff].index[0]
            
        elif turn_point_method.lower() == 'rank' and type(self.genome_cutoff_rank) is int: 
            # make sure rank is less than total genomes, unless use Auto
            if self.genome_cutoff_rank > df_results_rank.shape[0]:
                raise ValueError(f"genome_cutoff_rank: {self.genome_cutoff_rank} is larger than total genomes found: {df_results_rank.shape[0]}, please check!")
            print(f"Get top {self.genome_cutoff_rank} genomes by rank")
            cutoff_index = self.genome_cutoff_rank - 1
            
        elif turn_point_method.lower() == 'distinct_count':
            cutoff_value = self.turn_point_distinct_cutoff
            print(f"Get top genomes with at least {cutoff_value} distinct peptides")
            cutoff_index = df_results_rank[df_results_rank['distinct_peptides_count'] >= cutoff_value].index[-1]
            
        else:
            raise ValueError(f"Invalid turn_point_method: {turn_point_method}, should be 'auto', 'coverage', 'rank', or 'distinct_count'")
        
        # Store the actually used parameters for reporting, set unused ones to 'N/A'
        self._update_cutoff_parameters_for_reporting(turn_point_method)
        
        selected_genomes = df_results_rank.loc[:cutoff_index]
        selected_genomes_list = selected_genomes['Genomes'].tolist()
        print(f'Original genomes: [{df_results_rank.shape[0]}]')
        print(f"The number of selected genomes: [{len(selected_genomes_list)}].\nThe last genome with coverage_ratio: {selected_genomes.iloc[-1]['coverage_ratio']}")
        self.selected_genomes_num = len(selected_genomes_list)
        
        return selected_genomes_list
    
    def calculate_protein_list(self, df):
        print("reducing proteins by genome ranking")
        from metax.peptide_annotator.get_genome_rank import GenomeRank
        gr = GenomeRank(df = df,
                                    peptide_column = self.peptide_col,
                                    genome_column = 'Proteins',
                                    genome_separator = ';')
        df_results_rank = gr.get_rank_covre_df(genome_rank_method='combined', iters=3)
        self.protein_ranked_table = df_results_rank
        cutoff_index = df_results_rank[df_results_rank['coverage_ratio'] >= self.protein_peptide_coverage_cutoff].index[0]
        selected_proteins = df_results_rank.loc[:cutoff_index]
        selected_proteins_list = selected_proteins['Proteins'].tolist()
        print(f'Original proteins: [{df_results_rank.shape[0]}]')
        print(f"The number of selected proteins: [{len(selected_proteins_list)}].\nThe last protein with coverage_ratio: {selected_proteins.iloc[-1]['coverage_ratio']}")
        self.selected_proteins_num = len(selected_proteins_list)
        
        return selected_proteins_list

    def reduce_proteins_by_genome(self, df, selected_genomes_list):
        print("Filtering proteins by selected genomes")
        original_peptides = df.shape[0]

        selected_genomes_set = set(selected_genomes_list)
        df['Proteins'] = df['Proteins'].astype(str).str.split(';')
        df['Proteins'] = df['Proteins'].apply(lambda proteins: ';'.join([p for p in proteins if p.split('_')[0] in selected_genomes_set]))
        
        df = df[df['Proteins'] != '']
        
        print(f"Original peptides: {original_peptides}, after filtering: {df.shape[0]}")
        print(f"Removed peptides: {original_peptides - df.shape[0]}, due to no protein left after filtering by selected genomes")
        print("-" * 20)

        if 'Genomes' in df.columns:
            df = df.drop(columns=['Genomes'])

        return df
    
    def reduce_proteins_by_mini_proteins_list(self, df, selected_proteins_list):
        print("Filtering proteins by selected proteins")
        original_peptides = df.shape[0]

        selected_proteins_set = set(selected_proteins_list)  
        df['Proteins'] = df['Proteins'].astype(str).str.split(';')
        df['Proteins'] = df['Proteins'].apply(lambda proteins: ';'.join([p for p in proteins if p in selected_proteins_set]))

        df = df[df['Proteins'] != '']
        
        print(f"Original peptides: {original_peptides}, after filtering: {df.shape[0]}")
        print("-" * 20)
        
        return df


    def process_peptides_to_proteins(self, genome_list: Iterable[str] | None = None):# main function workflow
        if self.continue_base_on_annotaied_peptide_table:
            self.run_base_on_annotaied_peptide_table(genome_list=genome_list)
            return

        self.annotate_peptides()
        self.extract_genome_col(self.peptide_table)
        
        if self.stop_after_genome_ranking:
            print("Stopped after genome ranking")
            self.final_peptide_table = self.peptide_table
            self._get_selected_genome_list(self.peptide_table, genome_list=genome_list)
            #save the annotated peptide table to output path
            self._log_save(self.peptide_table, self.output_path, "annotated_peptide_table")
            t0 = time.time()
            self.peptide_table.to_csv(self.output_path, sep='\t', index=False)
            print(f"[Save] annotated_peptide_table done in {time.time() - t0:.2f}s")
            return
        else:
            #save the annotated peptide table to temp dir
            annotated_tmp_path = f'{self.temp_dir}/annotated_peptide_table.tsv'
            self._log_save(self.peptide_table, annotated_tmp_path, "annotated_peptide_table(temp)")
            t0 = time.time()
            self.peptide_table.to_csv(annotated_tmp_path, sep='\t', index=False)
            print(f"[Save] annotated_peptide_table(temp) done in {time.time() - t0:.2f}s")
            self.run_base_on_annotaied_peptide_table(genome_list=genome_list)


    def run_base_on_annotaied_peptide_table(self, genome_list: Iterable[str] | None = None):
        selected_genomes_list = self._get_selected_genome_list(self.peptide_table, genome_list=genome_list)
        self.final_peptide_table = self.reduce_proteins_by_genome(self.peptide_table, selected_genomes_list)
        selected_proteins_list = self.calculate_protein_list(self.final_peptide_table)
        self.final_peptide_table = self.reduce_proteins_by_mini_proteins_list(self.final_peptide_table, selected_proteins_list)
        return self.final_peptide_table


    def all_in_one(self, 
                   taxafunc_anno_db_path,
                   lca_threshold = 1,
                   genome_mode = True, 
                   distinct_genome_threshold = 1, # usually 3
                   exclude_protein_startwith = None, #Usually 'REV_;XXX_' 
                   protein_genome_separator = '_',
                   genome_list: Iterable[str] | None = None,
                   ): # run peptide to OTF
        
        if self.continue_base_on_annotaied_peptide_table:
            self.run_base_on_annotaied_peptide_table(genome_list=genome_list)
        else:
            self.process_peptides_to_proteins(genome_list=genome_list)
        
        # collect additional running information
        additional_running_info = {
            "peptideProteinsMapper": "Peptides directly annotated with proteins from a database",
            "Run time": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            "peptide_mapping_mode": "digested_genome_folders" if self.digested_genome_folders is not None else "sqlite_db",
            "peptide_mapping_db": self.db_file,
            "digested_genome_folders": self.digested_genome_folders,
            "digested_scan_n_jobs": self.n_jobs,
            "peptide_col": self.peptide_col,
            "intensity_col_prefix": self.intensity_col_prefix,
            "protein_genome_separator": protein_genome_separator,
            "original_peptides_before_mapping": self.original_peptides_before_mapping,
            "peptides_after_mapping": self.peptides_after_mapping,
            "removed_peptides_no_matched": self.removed_peptides_no_matched,
            "genome_peptide_coverage_cutoff": self.genome_peptide_coverage_cutoff,
            "protein_peptide_coverage_cutoff": self.protein_peptide_coverage_cutoff,
            "turn_point_method": self.turn_point_method,
            "turn_point_distinct_cutoff": self.turn_point_distinct_cutoff,
            "genome_cutoff_rank": self.genome_cutoff_rank if self.turn_point_method.lower() in ['rank', 'distinct_count'] else "N/A",
            "total_genomes_found": len(self.genome_ranked_table) if self.genome_ranked_table is not None else "Unknown",
            "selected_genomes_num": self.selected_genomes_num,
            "total_proteins_found": len(self.protein_ranked_table) if self.protein_ranked_table is not None else "Unknown",
            "selected_proteins_num": self.selected_proteins_num,
            "continue_base_on_annotated_peptide_table": self.continue_base_on_annotaied_peptide_table,
            "stop_after_genome_ranking": self.stop_after_genome_ranking,
            "original_peptide_count": len(self.peptide_table) if hasattr(self, 'peptide_table') else "Unknown",
            "final_peptide_count": len(self.final_peptide_table) if hasattr(self, 'final_peptide_table') else "Unknown",
        }
        

        from metax.peptide_annotator.peptable_annotator import PeptideAnnotator
        annotator = PeptideAnnotator(
            db_path=taxafunc_anno_db_path,
            peptide_path=None,
            peptide_df=self.final_peptide_table,
            output_path=self.output_path,
            threshold=lca_threshold,
            genome_mode=genome_mode,
            protein_separator=';',
            protein_genome_separator= protein_genome_separator,
            protein_col='Proteins',
            peptide_col=self.peptide_col,
            sample_col_prefix=self.intensity_col_prefix,
            distinct_genome_threshold=distinct_genome_threshold,
            exclude_protein_startwith = exclude_protein_startwith,
            additional_running_info=additional_running_info
        )
        annotator.run_annotate()
        print("OTF annotation finished")
        
        
if __name__ == "__main__":
    # Local manual test entrypoint.
    # Put your test inputs under `.local_tests/` (not tracked by git) to avoid
    # committing machine-specific absolute paths.
    peptide_table_path = ".local_tests/report.pr_test.tsv"
    db_path = ".local_tests/peptide_to_protein.db"  # optional (SQLite mode)
    digested_genome_folders = [
        ".local_tests/digested_genomes",  # folder mode (preferred)
    ]
    
    ## test process_peptides_to_proteins
    # output_path = "anntated_report.pr_matrix.tsv"
    # peptide_mapper = peptideProteinsMapper(peptide_table_path=peptide_table_path, db_path=db_path, output_path=output_path,
    #                                        peptide_col='Stripped.Sequence', intensity_col_prefix="D:", table_separator='\t',
    #                                        genome_cutoff_rank=None,
    #                                         genome_peptide_coverage_cutoff=0.98, protein_peptide_coverage_cutoff=1,
    #                                         stop_after_genome_ranking=True, turn_point_method="Coverage",
    #                                         continue_base_on_annotaied_peptide_table=False)
    # peptide_mapper.process_peptides_to_proteins()
    # peptide_mapper.final_peptide_table.to_csv(output_path, sep='\t', index=False)
    # print("peptide annotation finished")
    
    # # test all_in_one
    taxafunc_anno_db_path = ".local_tests/MetaX_taxafunc.db"
    output_path = ".local_tests/OTF.tsv"
    
    # set of genomes to be removed
    removed_genomes_set = set()
    removed_genomes_file_path = ".local_tests/removed_genomes.txt"
    if not pathlib.Path(removed_genomes_file_path).is_file():
        print("No removed genomes file found, skip removing genomes")
    else:
        with open(removed_genomes_file_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    removed_genomes_set.add(line)
        print(len(removed_genomes_set), "genomes in the remove genome list")
    
    # set of genomes to be selected
    selected_mag_set = set()
    # selected_mag_file_path = '.local_tests/selected_genomes.txt'
    # if not pathlib.Path(selected_mag_file_path).is_file():
    #     print("No selected genomes file found, skip keeping selected genomes")
    # else:
    #     with open(selected_mag_file_path) as f:
    #         for line in f:
    #             line = line.strip()
    #             if line:
    #                 selected_mag_set.add(line)
    #     print(len(selected_mag_set), "genomes in the selected mags list")
    
    # initialize and run all in one
    peptide_mapper = peptideProteinsMapper(peptide_table_path=peptide_table_path, 
                                        #    db_path=db_path, 
                                           output_path=output_path,
                                           # use digested genome folders for peptide to protein mapping
                                           digested_genome_folders=digested_genome_folders,
                                           removed_genomes_set=removed_genomes_set, selected_genomes_set=selected_mag_set,
                                           peptide_col='Stripped.Sequence', intensity_col_prefix=r"E:", table_separator='\t',
                                           turn_point_method='coverage',
                                           genome_cutoff_rank=None,
                                           turn_point_distinct_cutoff=3,
                                           genome_peptide_coverage_cutoff=0.97, 
                                           protein_peptide_coverage_cutoff=1,
                                           continue_base_on_annotaied_peptide_table=False,
                                        #    stop_after_genome_ranking=True,
                                            genome_list=None
                                           )
    peptide_mapper.all_in_one(taxafunc_anno_db_path=taxafunc_anno_db_path)
    print("all in one finished")
