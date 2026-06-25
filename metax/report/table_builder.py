from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

if TYPE_CHECKING:
    from .workflow import ReportContext


VALID_TAXA_LEVELS = {"d", "p", "c", "o", "f", "g", "s", "m", "l"}
DEFAULT_ALL_TAXA_LEVELS = ["d", "p", "c", "o", "f", "g", "s"]
DEFAULT_EXCLUDED_FUNCTION_COLUMNS = {
    "protein_id",
    "EC_DE",
    "EC_AN",
    "EC_CC",
    "EC_CA",
    "KEGG_Pathway",
    "KEGG_ko",
    "None_func",
}
REPORT_DEFAULT_FUNCTION_PRIORITY = ("KEGG_ko_name", "KEGG_ko")
REPORT_DEFAULT_ADDITIONAL_FUNCTIONS = ("Gene",)


class TableBuilder:
    def __init__(self, context: "ReportContext"):
        self.context = context
        self.config = context.config
        self.tfa = context.tfa

    def build_all(self) -> None:
        self.context.logger.info("Generating report tables")
        self.context.function_columns = self.resolve_function_columns()
        self.context.taxa_levels = self.resolve_taxa_levels()

        if self.config.tables.generate_taxa_tables:
            self.build_taxa_tables()
        if self.config.tables.generate_function_tables:
            self.build_function_tables()
        if self.config.tables.generate_otf_tables:
            self.build_otf_tables()

        self.build_qc_tables()

    def resolve_taxa_levels(self) -> list[str]:
        taxa_levels = self.config.tables.taxa_levels
        if taxa_levels == ["all"]:
            return DEFAULT_ALL_TAXA_LEVELS
        invalid = [level for level in taxa_levels if level not in VALID_TAXA_LEVELS]
        if invalid:
            raise ValueError(f"Invalid taxa level(s): {invalid}. Valid levels: {sorted(VALID_TAXA_LEVELS)}")
        return taxa_levels

    def resolve_function_columns(self) -> list[str]:
        available = [
            item
            for item in (self.tfa.func_list or [])
            if item in self.tfa.original_df.columns and f"{item}_prop" in self.tfa.original_df.columns
        ]
        if self.config.tables.function_columns == "auto":
            selected = self._resolve_auto_report_function_columns(available)
        else:
            requested = list(self.config.tables.function_columns)
            missing = [item for item in requested if item not in available]
            if missing:
                raise ValueError(
                    f"Requested function column(s) not found or missing *_prop column: {missing}. "
                    f"Available function columns: {available}"
                )
            selected = requested

        main_function = self.config.analysis.main_function
        if main_function:
            if main_function not in available:
                raise ValueError(f"main_function [{main_function}] is not available. Available: {available}")
            selected = [main_function] + [item for item in selected if item != main_function]

        if not selected:
            self.context.registry.add_warning(
                "No usable function annotation columns were detected.",
                "TableBuilder",
                details={
                    "requested_function_columns": self.config.tables.function_columns,
                    "available_function_columns": available,
                },
            )
        return selected

    def _resolve_auto_report_function_columns(self, available: list[str]) -> list[str]:
        selected: list[str] = []
        if REPORT_DEFAULT_FUNCTION_PRIORITY[0] in available:
            selected.append(REPORT_DEFAULT_FUNCTION_PRIORITY[0])
        elif REPORT_DEFAULT_FUNCTION_PRIORITY[1] in available:
            selected.append(REPORT_DEFAULT_FUNCTION_PRIORITY[1])
            self.context.registry.add_warning(
                "Function column [KEGG_ko_name] was not available; using [KEGG_ko] for the KEGG report default.",
                "TableBuilder",
                details={
                    "requested_default": "KEGG_ko_name",
                    "fallback": "KEGG_ko",
                    "available_function_columns": available,
                },
            )
        else:
            self.context.registry.add_warning(
                "Neither [KEGG_ko_name] nor [KEGG_ko] was available for the KEGG report default.",
                "TableBuilder",
                details={
                    "requested_defaults": list(REPORT_DEFAULT_FUNCTION_PRIORITY),
                    "available_function_columns": available,
                },
            )

        for func_name in REPORT_DEFAULT_ADDITIONAL_FUNCTIONS:
            if func_name in available and func_name not in selected:
                selected.append(func_name)

        if selected:
            return selected

        fallback = [item for item in available if item not in DEFAULT_EXCLUDED_FUNCTION_COLUMNS]
        if fallback:
            self.context.registry.add_warning(
                f"Using fallback function annotation columns because report defaults were unavailable: {fallback}",
                "TableBuilder",
                details={
                    "fallback_function_columns": fallback,
                    "available_function_columns": available,
                },
            )
            return fallback
        return available

    def build_taxa_tables(self) -> None:
        kwargs = self._preprocess_kwargs()
        for level in self.context.taxa_levels:
            path = self.context.paths.taxa_tables_dir / f"taxa_table_{level}.tsv"
            try:
                df = self.tfa._create_taxa_table_only_from_otf(level=level, **kwargs)
                df = df.drop(
                    columns=["peptide_num", "unit_peptide_num", "bare_sequence_num"],
                    errors="ignore",
                )
                self._save_table(df, path)
                self._register_table(
                    "taxa",
                    f"taxa_{level}",
                    path,
                    df,
                    f"Taxa abundance - {taxa_level_label(level)} level",
                    f"Abundance summarized by {taxa_level_label(level)}.",
                    df_type="taxa",
                    taxa_level=level,
                )
            except Exception as exc:
                self.context.logger.exception("Failed to generate taxa table for level %s", level)
                self.context.registry.add_warning(
                    f"Taxa table for level [{level}] failed: {exc}",
                    "TableBuilder",
                    details=self._warning_details(
                        table_type="taxa",
                        taxa_level=level,
                        function_column=None,
                        error=exc,
                    ),
                )

    def build_function_tables(self) -> None:
        kwargs = self._preprocess_kwargs()
        for func_name in self.context.function_columns:
            safe_name = safe_filename(func_name)
            path = self.context.paths.function_tables_dir / f"function_table_{safe_name}.tsv"
            try:
                df = self.tfa._create_func_table_only_from_otf(
                    func_name=func_name,
                    func_threshold=1.0,
                    keep_unknow_func=self.config.tables.keep_unknown_func,
                    split_func=self.config.tables.split_func,
                    split_func_params={
                        "split_by": self.config.tables.split_by,
                        "share_intensity": self.config.tables.share_intensity,
                    },
                    **kwargs,
                )
                df = df.drop(
                    columns=["peptide_num", "unit_peptide_num", "bare_sequence_num"],
                    errors="ignore",
                )
                self._save_table(df, path)
                self._register_table(
                    "function",
                    f"function_{safe_name}",
                    path,
                    df,
                    f"Function abundance - {func_name}",
                    f"Abundance summarized by the {func_name} annotation.",
                    df_type="func",
                    function_column=func_name,
                )
            except Exception as exc:
                self.context.logger.exception("Failed to generate function table for %s", func_name)
                self.context.registry.add_warning(
                    f"Function table for [{func_name}] failed: {exc}",
                    "TableBuilder",
                    details=self._warning_details(
                        table_type="function",
                        taxa_level=None,
                        function_column=func_name,
                        error=exc,
                    ),
                )

    def build_otf_tables(self) -> None:
        kwargs = self._preprocess_kwargs()
        protein_saved = False
        for level in self.context.taxa_levels:
            for func_name in self.context.function_columns:
                safe_name = safe_filename(func_name)
                path = self.context.paths.otf_tables_dir / f"otf_table_{level}_{safe_name}.tsv"
                try:
                    self.tfa.set_func(func_name)
                    self.tfa.set_multi_tables(
                        level=level,
                        keep_unknow_func=self.config.tables.keep_unknown_func,
                        sum_protein=self.config.tables.generate_protein_table and not protein_saved,
                        sum_protein_params={
                            "method": "anti-razor",
                            "by_sample": False,
                            "rank_method": "unique_counts",
                            "greedy_method": "heap",
                            "peptide_num_threshold": self.config.preprocessing.otf_peptide_num_threshold,
                        },
                        split_func=self.config.tables.split_func,
                        split_func_params={
                            "split_by": self.config.tables.split_by,
                            "share_intensity": self.config.tables.share_intensity,
                        },
                        taxa_and_func_only_from_otf=False,
                        func_threshold=1.0,
                        **kwargs,
                    )
                    if self.config.tables.generate_protein_table and not protein_saved:
                        self._save_protein_table()
                        protein_saved = True

                    df = self.tfa.get_df("taxa_func")
                    self._save_table(df, path)
                    self._register_table(
                        "otf",
                        f"otf_{level}_{safe_name}",
                        path,
                        df,
                        f"Taxa-function links - {taxa_level_label(level)} and {func_name}",
                        f"OTF abundance linking {taxa_level_label(level)} taxa to {func_name} functions.",
                        df_type="taxa-func",
                        taxa_level=level,
                        function_column=func_name,
                    )
                except Exception as exc:
                    self.context.logger.exception("Failed to generate OTF table for %s / %s", level, func_name)
                    self.context.registry.add_warning(
                        f"OTF table for level [{level}] and function [{func_name}] failed: {exc}",
                        "TableBuilder",
                        details=self._warning_details(
                            table_type="otf",
                            taxa_level=level,
                            function_column=func_name,
                            error=exc,
                        ),
                    )

    def build_qc_tables(self) -> None:
        self.context.logger.info("Generating QC tables")
        sample_qc = self._build_sample_qc()
        sample_qc_path = self.context.paths.qc_tables_dir / "sample_qc.tsv"
        sample_qc.to_csv(sample_qc_path, sep="\t", index=False)
        self._register_table(
            "qc",
            "sample_qc",
            sample_qc_path,
            sample_qc.set_index("sample") if "sample" in sample_qc.columns else sample_qc,
            "Sample quality summary",
            "Per-sample intensity totals, feature counts, and missingness.",
        )

        for table_type in ["taxa", "function", "otf"]:
            df = self._first_table_df(table_type)
            prevalence = self._build_feature_prevalence(df)
            path = self.context.paths.qc_tables_dir / f"feature_prevalence_{table_type}.tsv"
            prevalence.to_csv(path, sep="\t", index=False)
            self._register_table(
                "qc",
                f"feature_prevalence_{table_type}",
                path,
                prevalence.set_index("feature_id") if "feature_id" in prevalence.columns else prevalence,
                f"Feature prevalence - {table_type}",
                f"How often features are detected across samples in the first {table_type} result.",
            )

    def _build_sample_qc(self) -> pd.DataFrame:
        sample_list = list(self.tfa.sample_list or [])
        original_matrix = self.tfa.original_df[sample_list].apply(pd.to_numeric, errors="coerce")
        group_map = self._sample_group_map()

        data: dict[str, Any] = {
            "sample": sample_list,
            "group": [group_map.get(sample, "All") for sample in sample_list],
            "total_intensity": [original_matrix[sample].sum(skipna=True) for sample in sample_list],
        }

        for table_type in ["taxa", "function", "otf"]:
            df = self._first_table_df(table_type)
            counts, missing = self._sample_feature_metrics(df, sample_list)
            data[f"nonzero_feature_count_{table_type}"] = counts
            data[f"missing_fraction_{table_type}"] = missing

        return pd.DataFrame(data)

    def _build_feature_prevalence(self, df: pd.DataFrame | None) -> pd.DataFrame:
        columns = [
            "feature_id",
            "mean_intensity",
            "median_intensity",
            "nonzero_sample_count",
            "prevalence",
        ]
        sample_list = list(self.tfa.sample_list or [])
        if df is None or df.empty:
            return pd.DataFrame(columns=columns)

        matrix = df[[sample for sample in sample_list if sample in df.columns]].apply(pd.to_numeric, errors="coerce")
        nonzero = matrix.fillna(0) != 0
        result = pd.DataFrame(
            {
                "feature_id": self._feature_ids(df),
                "mean_intensity": matrix.mean(axis=1, skipna=True).values,
                "median_intensity": matrix.median(axis=1, skipna=True).values,
                "nonzero_sample_count": nonzero.sum(axis=1).values,
                "prevalence": nonzero.mean(axis=1).values,
            }
        )

        group_meta = self.config.analysis.group_meta
        if group_meta and group_meta in self.tfa.meta_df.columns:
            for group, samples in self.tfa.meta_df.groupby(group_meta)["Sample"]:
                valid_samples = [sample for sample in samples.tolist() if sample in matrix.columns]
                if valid_samples:
                    result[f"prevalence_{safe_filename(str(group))}"] = nonzero[valid_samples].mean(axis=1).values
        return result

    def _sample_feature_metrics(self, df: pd.DataFrame | None, sample_list: list[str]) -> tuple[list[int], list[float]]:
        if df is None or df.empty:
            return [0 for _ in sample_list], [1.0 for _ in sample_list]
        matrix = df[[sample for sample in sample_list if sample in df.columns]].apply(pd.to_numeric, errors="coerce")
        counts: list[int] = []
        missing: list[float] = []
        for sample in sample_list:
            if sample not in matrix.columns:
                counts.append(0)
                missing.append(1.0)
                continue
            values = matrix[sample]
            counts.append(int((values.fillna(0) != 0).sum()))
            missing.append(float(((values.isna()) | (values == 0)).mean()))
        return counts, missing

    def _save_protein_table(self) -> None:
        protein_df = self.tfa.get_df("protein")
        path = self.context.paths.protein_tables_dir / "protein_table.tsv"
        self._save_table(protein_df, path)
        self._register_table(
            "protein",
            "protein",
            path,
            protein_df,
            "Protein abundance",
            "Protein-level abundance summarized during OTF table generation.",
            df_type="protein",
        )

    def _save_table(self, df: pd.DataFrame, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, sep="\t", index=True)

    def _register_table(
        self,
        table_type: str,
        key: str,
        path: Path,
        df: pd.DataFrame,
        title: str,
        description: str,
        **metadata: Any,
    ) -> None:
        artifact = {
            "key": key,
            "path": path,
            "title": title,
            "description": description,
            "df": df.copy(),
            "table_type": table_type,
            **metadata,
        }
        self.context.generated_tables.setdefault(table_type, []).append(artifact)
        self.context.registry.add_table(key, path, title=title, description=description)
        self.context.logger.info("Generated table: %s", path)

    def _first_table_df(self, table_type: str) -> pd.DataFrame | None:
        items = self.context.generated_tables.get(table_type, [])
        if not items:
            return None
        return items[0]["df"]

    def _sample_group_map(self) -> dict[str, str]:
        group_meta = self.config.analysis.group_meta
        if not group_meta or group_meta not in self.tfa.meta_df.columns:
            return {sample: "All" for sample in self.tfa.sample_list or []}
        return dict(zip(self.tfa.meta_df["Sample"], self.tfa.meta_df[group_meta].astype(str)))

    def _feature_ids(self, df: pd.DataFrame) -> list[str]:
        if isinstance(df.index, pd.MultiIndex):
            return [" | ".join(str(part) for part in index) for index in df.index]
        return [str(index) for index in df.index]

    def _preprocess_kwargs(self) -> dict[str, Any]:
        preprocessing = self.config.preprocessing
        return {
            "outlier_params": {
                "detect_method": preprocessing.outlier_detect_method,
                "handle_method": preprocessing.outlier_handle_method,
                "detection_by_group": preprocessing.detection_by_group,
                "handle_by_group": preprocessing.handle_by_group,
            },
            "data_preprocess_params": {
                "normalize_method": preprocessing.normalize_method,
                "transform_method": preprocessing.transform_method,
                "batch_meta": preprocessing.batch_meta,
                "processing_order": ["transform", "normalize", "batch"],
            },
            "peptide_num_threshold": {
                "taxa": preprocessing.taxa_peptide_num_threshold,
                "func": preprocessing.func_peptide_num_threshold,
                "taxa_func": preprocessing.otf_peptide_num_threshold,
            },
            "quant_method": preprocessing.quant_method,
        }

    def _warning_details(
        self,
        table_type: str,
        taxa_level: str | None,
        function_column: str | None,
        error: Exception,
    ) -> dict[str, Any]:
        preprocessing = self.config.preprocessing
        details: dict[str, Any] = {
            "table_type": table_type,
            "taxa_level": taxa_level,
            "function_column": function_column,
            "error": str(error),
            "quant_method": preprocessing.quant_method,
            "outlier_detect_method": preprocessing.outlier_detect_method,
            "outlier_handle_method": preprocessing.outlier_handle_method,
            "normalize_method": preprocessing.normalize_method,
            "transform_method": preprocessing.transform_method,
            "taxa_peptide_num_threshold": preprocessing.taxa_peptide_num_threshold,
            "func_peptide_num_threshold": preprocessing.func_peptide_num_threshold,
            "otf_peptide_num_threshold": preprocessing.otf_peptide_num_threshold,
            "split_func": self.config.tables.split_func,
            "split_by": self.config.tables.split_by,
            "keep_unknown_func": self.config.tables.keep_unknown_func,
        }
        return {key: value for key, value in details.items() if value is not None and value != ""}


def safe_filename(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return safe.strip("._") or "unnamed"


def taxa_level_label(level: str) -> str:
    labels = {
        "d": "domain",
        "p": "phylum",
        "c": "class",
        "o": "order",
        "f": "family",
        "g": "genus",
        "s": "species",
        "m": "genome",
        "l": "life",
    }
    return labels.get(level, level)
