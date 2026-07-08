from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

import numpy as np
import pandas as pd

from .table_builder import safe_filename

if TYPE_CHECKING:
    from .workflow import ReportContext


class StatsBuilder:
    """Run the same statistical backend used by the MetaX GUI."""

    def __init__(self, context: "ReportContext"):
        self.context = context
        self.config = context.config
        self.tfa = context.tfa

    def run_all(self) -> None:
        group_meta = self.config.analysis.group_meta
        control_group = self.config.analysis.control_group
        diff_method = str(self.config.statistics.diff_method).lower()
        if diff_method == "gui_dunnett":
            diff_method = "dunnett"
        if diff_method not in {"limma", "dunnett"}:
            raise ValueError(
                f"Unsupported statistics.diff_method [{self.config.statistics.diff_method}]. "
                "Supported methods are: limma, dunnett."
            )
        if self.config.statistics.run_deseq2:
            configured_method = str(self.config.statistics.diff_method).lower()
            method_label = "limma via InMoose" if configured_method == "limma" else "MetaX GUI Dunnett"
            self.context.registry.add_warning(
                "DESeq2 analysis was requested, but it is not implemented in Auto Report. "
                f"Group-vs-control results will use the configured backend: {method_label}.",
                "StatsBuilder",
                details={
                    "requested_method": "DESeq2",
                    "configured_group_vs_control_backend": method_label,
                    "run_deseq2": self.config.statistics.run_deseq2,
                },
            )
        if not group_meta:
            self.context.logger.info("Skipping statistics because no group_meta is configured.")
            return
        if group_meta not in self.tfa.meta_df.columns:
            raise ValueError(f"group_meta [{group_meta}] is not in metadata columns.")

        self.tfa.set_group(group_meta)
        groups = self._valid_group_names()
        if len(groups) < 2:
            self.context.registry.add_warning(
                f"Too few groups for statistical testing in [{group_meta}].",
                "StatsBuilder",
                details={
                    "group_meta": group_meta,
                    "groups": groups,
                    "required_groups": "at least 2",
                },
            )
            return

        for table_type in ["taxa", "function", "otf"]:
            for artifact in self.context.generated_tables.get(table_type, []):
                with self._activate_gui_table(artifact, transform_for_stats=True) as df_type:
                    if self.config.statistics.run_anova and len(groups) > 2:
                        self._run_gui_anova(table_type, artifact, df_type, groups)
                    elif self.config.statistics.run_ttest and len(groups) == 2:
                        self._run_gui_ttest(table_type, artifact, df_type, groups)
                    if control_group and self.config.statistics.run_group_vs_control:
                        if diff_method == "limma":
                            self._run_limma(table_type, artifact, groups, str(control_group))
                        else:
                            self._run_gui_dunnett(table_type, artifact, df_type, groups, str(control_group))

    def _run_limma(
        self,
        table_type: str,
        artifact: dict,
        groups: list[str],
        control_group: str,
    ) -> None:
        if control_group not in groups:
            raise ValueError(f"control_group [{control_group}] is not present in configured groups.")
        comparison_groups = [group for group in groups if group != control_group]
        if not comparison_groups:
            return
        try:
            result = self.tfa.CrossTest.get_stats_limma_against_control(
                df=artifact["df"].copy(),
                control_group=control_group,
                group_list=list(comparison_groups),
                log2_transform=True,
                zero_to_nan=False,
                concat_sample_to_result=True,
            )
        except Exception as exc:
            raise RuntimeError(
                f"limma via InMoose failed for [{artifact['title']}]. "
                "Install/repair the limma backend or explicitly set statistics.diff_method to dunnett. "
                f"Original error: {exc}"
            ) from exc

        if result is None or result.empty:
            self.context.registry.add_warning(
                f"limma returned no group-vs-control results for [{artifact['title']}].",
                "StatsBuilder",
                details=self._warning_details(
                    artifact,
                    analysis="limma",
                    groups=groups,
                    control=control_group,
                    reason="empty result",
                ),
            )
            return
        if not isinstance(result.columns, pd.MultiIndex):
            if len(comparison_groups) != 1:
                raise ValueError("limma against-control output did not identify comparison groups.")
            result = pd.concat({comparison_groups[0]: result}, axis=1)

        available_groups = set(str(item) for item in result.columns.get_level_values(0))
        for group in comparison_groups:
            if group not in available_groups:
                self.context.registry.add_warning(
                    f"limma did not return comparison [{group} vs {control_group}] for [{artifact['title']}].",
                    "StatsBuilder",
                )
                continue
            pair_df = result[group].copy()
            pair_df.insert(0, "control", control_group)
            pair_df.insert(0, "group", group)
            pair_df = self._with_feature_id(pair_df)
            preferred = [
                "feature_id",
                "group",
                "control",
                "baseMean",
                "log2FoldChange",
                "stat",
                "pvalue",
                "padj",
            ]
            pair_df = pair_df[
                [name for name in preferred if name in pair_df.columns]
                + [name for name in pair_df.columns if name not in preferred]
            ]
            required = {"log2FoldChange", "pvalue", "padj"}
            missing = sorted(required - set(pair_df.columns))
            if missing:
                raise ValueError(f"limma result is missing required columns: {missing}")
            safe_group = safe_filename(group)
            safe_control = safe_filename(control_group)
            path = self._stats_dir(table_type) / (
                f"{safe_filename(artifact['key'])}_{safe_group}_vs_{safe_control}.tsv"
            )
            self._save_stat(
                key=f"{artifact['key']}_{safe_group}_vs_{safe_control}",
                path=path,
                df=pair_df,
                title=f"{group} vs {control_group} - {artifact['title']}",
                description=(
                    "limma via InMoose on log2(x + 1)-transformed abundance. "
                    "Appended sample abundance columns contain log2(x + 1)-transformed values."
                ),
                analysis="group_vs_control",
                table_type=table_type,
                source_key=artifact["key"],
                index=False,
                backend="limma_inmoose",
                group=group,
                control=control_group,
            )

    def _run_gui_anova(self, table_type: str, artifact: dict, df_type: str, groups: list[str]) -> None:
        if len(groups) <= 2:
            self.context.registry.add_warning(
                f"ANOVA skipped for [{artifact['title']}] because MetaX GUI ANOVA requires more than two groups.",
                "StatsBuilder",
                details=self._warning_details(
                    artifact,
                    analysis="anova",
                    groups=groups,
                    reason="requires more than two groups",
                ),
            )
            return

        try:
            result = self.tfa.CrossTest.get_stats_anova(group_list=list(groups), df_type=df_type)
        except Exception as exc:
            self.context.logger.exception("GUI ANOVA failed for %s", artifact["key"])
            self.context.registry.add_warning(
                f"GUI ANOVA failed for [{artifact['title']}]: {exc}",
                "StatsBuilder",
                details=self._warning_details(
                    artifact,
                    analysis="anova",
                    groups=groups,
                    error=exc,
                ),
            )
            return

        path = self._stats_dir(table_type) / f"{safe_filename(artifact['key'])}_anova.tsv"
        self._save_stat(
            key=f"{artifact['key']}_anova",
            path=path,
            df=result,
            title=f"ANOVA - {artifact['title']}",
            description="MetaX GUI ANOVA result generated with CrossTest.get_stats_anova.",
            analysis="anova",
            table_type=table_type,
            source_key=artifact["key"],
            index=True,
            backend="metax_gui",
        )

    def _run_gui_ttest(self, table_type: str, artifact: dict, df_type: str, groups: list[str]) -> None:
        if len(groups) != 2:
            return

        try:
            result = self.tfa.CrossTest.get_stats_ttest(group_list=list(groups), df_type=df_type)
        except Exception as exc:
            self.context.logger.exception("GUI t-test failed for %s", artifact["key"])
            self.context.registry.add_warning(
                f"GUI t-test failed for [{artifact['title']}]: {exc}",
                "StatsBuilder",
                details=self._warning_details(
                    artifact,
                    analysis="ttest",
                    groups=groups,
                    error=exc,
                ),
            )
            return

        path = self._stats_dir(table_type) / f"{safe_filename(artifact['key'])}_ttest.tsv"
        self._save_stat(
            key=f"{artifact['key']}_ttest",
            path=path,
            df=result,
            title=f"T-test - {artifact['title']}",
            description="MetaX GUI t-test result generated with CrossTest.get_stats_ttest on log2(x + 1) abundance.",
            analysis="ttest",
            table_type=table_type,
            source_key=artifact["key"],
            index=True,
            backend="metax_gui",
        )

    def _run_gui_dunnett(
        self,
        table_type: str,
        artifact: dict,
        df_type: str,
        groups: list[str],
        control_group: str,
    ) -> None:
        if control_group not in groups:
            raise ValueError(f"control_group [{control_group}] is not present in configured groups.")
        comparison_groups = [group for group in groups if group != control_group]
        if not comparison_groups:
            self.context.registry.add_warning(
                f"Dunnett comparison skipped for [{artifact['title']}] because no non-control groups were available.",
                "StatsBuilder",
                details=self._warning_details(
                    artifact,
                    analysis="dunnett",
                    groups=groups,
                    control=control_group,
                    reason="no non-control groups",
                ),
            )
            return

        try:
            result = self.tfa.CrossTest.get_stats_dunnett_test(
                control_group=control_group,
                group_list=list(groups),
                df_type=df_type,
            )
        except Exception as exc:
            self.context.logger.exception("GUI Dunnett test failed for %s", artifact["key"])
            self.context.registry.add_warning(
                f"GUI Dunnett test failed for [{artifact['title']}]: {exc}",
                "StatsBuilder",
                details=self._warning_details(
                    artifact,
                    analysis="dunnett",
                    groups=groups,
                    control=control_group,
                    error=exc,
                ),
            )
            return

        raw_path = self._stats_dir(table_type) / f"{safe_filename(artifact['key'])}_dunnett.tsv"
        self._save_stat(
            key=f"{artifact['key']}_dunnett",
            path=raw_path,
            df=result,
            title=f"Dunnett test - {artifact['title']}",
            description="MetaX GUI group-vs-control result generated with CrossTest.get_stats_dunnett_test.",
            analysis="dunnett_all",
            table_type=table_type,
            source_key=artifact["key"],
            index=True,
            backend="metax_gui",
            control=control_group,
        )

        matrix = self._matrix_from_table(self._log2_for_stats(artifact["df"]))
        if matrix is None or matrix.empty:
            self.context.registry.add_warning(
                f"Pairwise Dunnett summaries skipped for [{artifact['title']}] because no numeric matrix was available.",
                "StatsBuilder",
                details=self._warning_details(
                    artifact,
                    analysis="pairwise_dunnett_summary",
                    groups=groups,
                    control=control_group,
                    reason="no numeric sample matrix",
                ),
            )
            return

        for group in comparison_groups:
            pair_df = self._dunnett_pair_summary(result, matrix, group, control_group)
            safe_group = safe_filename(group)
            safe_control = safe_filename(control_group)
            path = self._stats_dir(table_type) / f"{safe_filename(artifact['key'])}_{safe_group}_vs_{safe_control}.tsv"
            self._save_stat(
                key=f"{artifact['key']}_{safe_group}_vs_{safe_control}",
                path=path,
                df=pair_df,
                title=f"{group} vs {control_group} - {artifact['title']}",
                description=(
                    "Report-friendly pairwise summary derived from the MetaX GUI Dunnett result on log2(x + 1) abundance. "
                    "p_value/q_value/statistic come from CrossTest; log2FC is the difference between mean log2 abundances."
                ),
                analysis="group_vs_control",
                table_type=table_type,
                source_key=artifact["key"],
                index=False,
                backend="metax_gui",
                group=group,
                control=control_group,
                raw_stat_key=f"{artifact['key']}_dunnett",
            )

    def _dunnett_pair_summary(
        self,
        dunnett_df: pd.DataFrame,
        matrix: pd.DataFrame,
        group: str,
        control: str,
    ) -> pd.DataFrame:
        if not isinstance(dunnett_df.columns, pd.MultiIndex) or group not in dunnett_df.columns.get_level_values(0):
            raise ValueError(f"Dunnett result does not contain group [{group}].")

        group_samples = [sample for sample in self.tfa.get_sample_list_in_a_group(group) if sample in matrix.columns]
        control_samples = [sample for sample in self.tfa.get_sample_list_in_a_group(control) if sample in matrix.columns]
        p_values = pd.to_numeric(dunnett_df[(group, "pvalue")], errors="coerce")
        q_values = pd.to_numeric(dunnett_df[(group, "padj")], errors="coerce")
        statistic = pd.to_numeric(dunnett_df[(group, "statistic")], errors="coerce")

        rows = []
        for feature_id in matrix.index:
            group_values = matrix.loc[feature_id, group_samples].dropna()
            control_values = matrix.loc[feature_id, control_samples].dropna()
            mean_group = float(group_values.mean()) if len(group_values) else np.nan
            mean_control = float(control_values.mean()) if len(control_values) else np.nan
            median_group = float(group_values.median()) if len(group_values) else np.nan
            median_control = float(control_values.median()) if len(control_values) else np.nan
            log2fc = float(mean_group - mean_control)
            p_value = float(p_values.loc[feature_id]) if feature_id in p_values.index and pd.notna(p_values.loc[feature_id]) else np.nan
            q_value = float(q_values.loc[feature_id]) if feature_id in q_values.index and pd.notna(q_values.loc[feature_id]) else np.nan
            stat_value = float(statistic.loc[feature_id]) if feature_id in statistic.index and pd.notna(statistic.loc[feature_id]) else np.nan
            significant = bool(
                pd.notna(q_value)
                and q_value <= self.config.statistics.alpha
                and abs(log2fc) >= self.config.statistics.log2fc_cutoff
            )
            direction = "not_significant"
            if significant and log2fc > 0:
                direction = "up"
            elif significant and log2fc < 0:
                direction = "down"
            rows.append(
                {
                    "feature_id": feature_id,
                    "group": group,
                    "control": control,
                    "n_group": int(len(group_values)),
                    "n_control": int(len(control_values)),
                    "mean_group": mean_group,
                    "mean_control": mean_control,
                    "median_group": median_group,
                    "median_control": median_control,
                    "log2FC": log2fc,
                    "p_value": p_value,
                    "q_value": q_value,
                    "t_statistic": stat_value,
                    "test_method": f"MetaX GUI Dunnett test on log2(x + {self.config.statistics.pseudo_count}) abundance",
                    "significant": significant,
                    "direction": direction,
                }
            )
        return pd.DataFrame(rows)

    @contextmanager
    def _activate_gui_table(self, artifact: dict, transform_for_stats: bool = False) -> Iterator[str]:
        df_type = artifact.get("df_type")
        if df_type not in {"taxa", "func", "taxa-func"}:
            raise ValueError(f"Unsupported table type for GUI statistics: {artifact.get('key')}")

        old_state = {
            "taxa_df": getattr(self.tfa, "taxa_df", None),
            "func_df": getattr(self.tfa, "func_df", None),
            "taxa_func_df": getattr(self.tfa, "taxa_func_df", None),
            "func_name": getattr(self.tfa, "func_name", None),
            "taxa_level": getattr(self.tfa, "taxa_level", None),
        }
        table_df = self._log2_for_stats(artifact["df"]) if transform_for_stats else artifact["df"].copy()
        try:
            if df_type == "taxa":
                self.tfa.taxa_df = table_df
                if artifact.get("taxa_level"):
                    self.tfa.taxa_level = artifact["taxa_level"]
            elif df_type == "func":
                self.tfa.func_df = table_df
                if artifact.get("function_column"):
                    self.tfa.func_name = artifact["function_column"]
            elif df_type == "taxa-func":
                self.tfa.taxa_func_df = table_df
                if artifact.get("function_column"):
                    self.tfa.func_name = artifact["function_column"]
                if artifact.get("taxa_level"):
                    self.tfa.taxa_level = artifact["taxa_level"]
            yield df_type
        finally:
            for attr, value in old_state.items():
                setattr(self.tfa, attr, value)

    def _save_stat(
        self,
        key: str,
        path: Path,
        df: pd.DataFrame,
        title: str,
        description: str,
        analysis: str,
        table_type: str,
        source_key: str,
        index: bool,
        backend: str,
        group: str | None = None,
        control: str | None = None,
        raw_stat_key: str | None = None,
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        output_df = self._with_feature_id(df)
        output_df.to_csv(path, sep="\t", index=False)
        self.context.registry.add_stat(key, path, title=title, description=description)
        sample_value_transform = "log2(x + 1)" if backend == "limma_inmoose" else None
        if sample_value_transform:
            self.context.registry.stats[-1]["sample_value_transform"] = sample_value_transform
        self.context.generated_stats.append(
            {
                "key": key,
                "path": path,
                "title": title,
                "description": description,
                "df": output_df.copy() if analysis == "group_vs_control" else df.copy(),
                "analysis": analysis,
                "table_type": table_type,
                "source_key": source_key,
                "group": group,
                "control": control,
                "backend": backend,
                "sample_value_transform": sample_value_transform,
                "raw_stat_key": raw_stat_key,
            }
        )
        self.context.logger.info("Generated statistics: %s", path)

    def _with_feature_id(self, df: pd.DataFrame) -> pd.DataFrame:
        output = df.copy()
        if isinstance(output.columns, pd.MultiIndex):
            output.columns = [
                "__".join(str(part) for part in column if str(part))
                for column in output.columns
            ]
        if "feature_id" in output.columns:
            return output
        output.insert(0, "feature_id", self._feature_labels(output))
        return output

    def _valid_group_names(self) -> list[str]:
        group_names = sorted(set(str(group) for group in self.tfa.get_meta_list(self.tfa.meta_name)))
        valid_groups = []
        for group in group_names:
            try:
                if self.tfa.get_sample_list_in_a_group(group):
                    valid_groups.append(group)
            except Exception:
                continue
        return valid_groups

    def _matrix_from_table(self, df: pd.DataFrame) -> pd.DataFrame | None:
        sample_cols = [sample for sample in self.tfa.sample_list or [] if sample in df.columns]
        if not sample_cols:
            return None
        matrix = df[sample_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
        matrix = matrix.loc[(matrix != 0).any(axis=1)]
        return matrix

    def _log2_for_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        sample_cols = [sample for sample in self.tfa.sample_list or [] if sample in df.columns]
        transformed = df.copy()
        if not sample_cols:
            return transformed
        values = transformed[sample_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
        transformed[sample_cols] = np.log2(values + self.config.statistics.pseudo_count)
        return transformed

    def _feature_labels(self, df: pd.DataFrame) -> list[str]:
        if isinstance(df.index, pd.MultiIndex):
            return [" | ".join(str(part) for part in index) for index in df.index]
        return [str(index) for index in df.index]

    def _stats_dir(self, table_type: str) -> Path:
        if table_type == "taxa":
            return self.context.paths.taxa_stats_dir
        if table_type == "function":
            return self.context.paths.function_stats_dir
        if table_type == "otf":
            return self.context.paths.otf_stats_dir
        return self.context.paths.stats_dir

    def _warning_details(
        self,
        artifact: dict,
        analysis: str,
        groups: list[str] | None = None,
        control: str | None = None,
        reason: str | None = None,
        error: Exception | None = None,
    ) -> dict[str, object]:
        details: dict[str, object] = {
            "analysis": analysis,
            "table_key": artifact.get("key"),
            "table_title": artifact.get("title"),
            "table_type": artifact.get("table_type"),
            "taxa_level": artifact.get("taxa_level"),
            "function_column": artifact.get("function_column"),
            "groups": groups,
            "control_group": control or self.config.analysis.control_group,
            "group_meta": self.config.analysis.group_meta,
            "alpha": self.config.statistics.alpha,
            "log2fc_cutoff": self.config.statistics.log2fc_cutoff,
            "pseudo_count": self.config.statistics.pseudo_count,
            "transform": f"log2(x + {self.config.statistics.pseudo_count})",
            "reason": reason,
            "error": str(error) if error else None,
        }
        return {key: value for key, value in details.items() if value is not None and value != ""}


def _bh_fdr(p_values: np.ndarray) -> np.ndarray:
    p_values = np.asarray(p_values, dtype=float)
    q_values = np.full_like(p_values, np.nan, dtype=float)
    valid = np.isfinite(p_values)
    if not valid.any():
        return q_values
    valid_indices = np.where(valid)[0]
    valid_p = p_values[valid]
    order = np.argsort(valid_p)
    ranked = valid_p[order]
    n = len(ranked)
    adjusted = ranked * n / np.arange(1, n + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    adjusted = np.clip(adjusted, 0, 1)
    q_values[valid_indices[order]] = adjusted
    return q_values
