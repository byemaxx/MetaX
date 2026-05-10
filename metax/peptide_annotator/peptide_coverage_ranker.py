"""Rank targets by their contribution to peptide coverage.

This module is intentionally target-agnostic. A target can be a genome,
protein, or any other entity stored in a delimited column. For each peptide,
the target column lists one or more targets that can explain that peptide.

The ranker orders targets with one of the supported ranking strategies, then
computes how many unique peptides are cumulatively covered as targets are
added in ranked order.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd
from tqdm import tqdm

__all__ = ["PeptideCoverageRanker", "GenomeRank"]


class PeptideCoverageRanker:
    """Rank targets and calculate cumulative peptide coverage.

    Parameters
    ----------
    df:
        Input peptide table. Each row represents a peptide observation.
    peptide_column:
        Column containing the peptide sequence or peptide identifier.
    target_column:
        Delimited column containing targets that can explain the peptide.
        Typical examples are ``Proteins`` and ``Genomes``.
    target_separator:
        Separator used inside ``target_column``.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        peptide_column: str,
        target_column: str,
        target_separator: str,
    ) -> None:
        self.peptide_column = peptide_column
        self.target_column = target_column
        self.target_separator = target_separator
        self.df = self._drop_empty_targets(df, target_column)

        self.df_results_by_rank: pd.DataFrame | None = None
        self.target_to_peptides: dict[str, set[str]] | None = None
        self.df_combined: pd.DataFrame | None = None

    @staticmethod
    def _split_targets(targets_raw: object, target_separator: str) -> list[str]:
        """Split a delimited target value and discard empty target IDs."""
        if pd.isna(targets_raw):
            return []
        return [
            target.strip()
            for target in str(targets_raw).split(target_separator)
            if target.strip()
        ]

    @staticmethod
    def _drop_empty_targets(df: pd.DataFrame, target_column: str) -> pd.DataFrame:
        """Remove rows where the target column is missing or empty."""
        target_values = df[target_column]
        keep_mask = target_values.notna() & target_values.astype(str).str.strip().ne("")
        removed_count = int((~keep_mask).sum())
        if removed_count > 0:
            print(f"Removing {removed_count} rows with empty targets in [{target_column}]")
            df = df.loc[keep_mask].copy()
            print(f"After removing empty targets: {df.shape}")
        return df

    def _create_target_to_peptides(
        self,
        df: pd.DataFrame,
        peptide_column: str,
        target_column: str,
        target_separator: str,
    ) -> dict[str, set[str]]:
        """Create a mapping from each target to the peptides it covers."""
        peptide_targets_df = df.loc[:, [peptide_column, target_column]]
        target_to_peptides: defaultdict[str, set[str]] = defaultdict(set)

        for peptide, targets_raw in tqdm(
            peptide_targets_df.itertuples(index=False, name=None),
            total=peptide_targets_df.shape[0],
            desc="Creating target to peptides mapping",
        ):
            for target in self._split_targets(targets_raw, target_separator):
                target_to_peptides[target].add(str(peptide))

        self.target_to_peptides = target_to_peptides
        return target_to_peptides

    def _get_distinct_targets(
        self,
        df: pd.DataFrame,
        target_column: str,
        target_separator: str,
    ) -> pd.DataFrame:
        """Count peptides that map to exactly one target.

        The returned table includes every observed target. Targets without
        target-specific peptides receive ``distinct_count = 0`` so they can
        still participate in later ranking and metadata joins.
        """
        target_lists = df[target_column].apply(
            lambda targets_raw: self._split_targets(targets_raw, target_separator)
        )

        all_targets = sorted({target for targets in target_lists for target in targets})
        single_target_rows = target_lists[target_lists.apply(len).eq(1)]
        distinct_targets = single_target_rows.apply(lambda targets: targets[0])

        df_distinct = (
            distinct_targets.value_counts()
            .rename_axis(target_column)
            .reset_index(name="distinct_count")
        )
        df_all_targets = pd.DataFrame({target_column: all_targets})

        df_distinct = df_all_targets.merge(df_distinct, on=target_column, how="left")
        df_distinct["distinct_count"] = df_distinct["distinct_count"].fillna(0).astype(int)
        return df_distinct.sort_values("distinct_count", ascending=False).reset_index(drop=True)

    def _calculate_peptide_counts(self) -> pd.DataFrame:
        """Count all unique peptides covered by each target."""
        if self.target_to_peptides is None:
            raise ValueError("Please call _create_target_to_peptides() first")

        peptide_counts = {
            target: len(peptides)
            for target, peptides in self.target_to_peptides.items()
        }
        df_peptide_counts = pd.DataFrame(
            list(peptide_counts.items()),
            columns=[self.target_column, "peptide_count"],
        )
        return df_peptide_counts.sort_values(
            by="peptide_count",
            ascending=False,
        ).reset_index(drop=True)

    def _calculate_target_coverage(
        self,
        target_rank_list: list[str],
        target_to_peptides: dict[str, set[str]],
    ) -> pd.DataFrame:
        """Calculate cumulative peptide coverage for a ranked target list."""
        unique_peptides: set[str] = set()
        cumulative_counts: list[int] = []
        added_counts: list[int] = []

        for target in target_rank_list:
            peptides = target_to_peptides[target]
            previous_count = len(unique_peptides)
            unique_peptides.update(peptides)
            cumulative_counts.append(len(unique_peptides))
            added_counts.append(len(unique_peptides) - previous_count)

        df_results_by_rank = pd.DataFrame(
            {
                self.target_column: target_rank_list,
                "cumulative_peptides": cumulative_counts,
                "added_peptides": added_counts,
            }
        )
        if df_results_by_rank.empty:
            df_results_by_rank["coverage_ratio"] = pd.Series(dtype=float)
        else:
            df_results_by_rank["coverage_ratio"] = (
                df_results_by_rank["cumulative_peptides"] / len(unique_peptides)
            )
        return df_results_by_rank

    def _calculate_turning_point(
        self,
        df_results_by_rank: pd.DataFrame,
        window_size: int = 20,
        std_threshold: float = 1,
    ) -> int | None:
        """Estimate the point where cumulative coverage starts to plateau."""
        rolling_std = df_results_by_rank["cumulative_peptides"].rolling(window=window_size).std()
        threshold = rolling_std.mean() * std_threshold
        turning_point_idx = (
            rolling_std[rolling_std < threshold].index[0]
            if (rolling_std < threshold).any()
            else None
        )

        print(f"Turning point index: {turning_point_idx}")
        return turning_point_idx

    def _calculate_combined_rank(
        self,
        df_target_distinct: pd.DataFrame,
        df_peptide_counts: pd.DataFrame,
        distinct_w: float = 0.9,
        peptide_w: float = 0.1,
    ) -> pd.DataFrame:
        """Rank targets by weighted distinct-peptide and total-peptide scores."""
        df = (
            pd.merge(
                df_target_distinct[[self.target_column, "distinct_count"]],
                df_peptide_counts[[self.target_column, "peptide_count"]],
                on=self.target_column,
                how="outer",
            )
            .fillna(0)
        )

        distinct_log = np.log1p(df["distinct_count"])
        distinct_min, distinct_max = distinct_log.min(), distinct_log.max()
        if distinct_max > distinct_min:
            df["distinct_norm"] = (distinct_log - distinct_min) / (distinct_max - distinct_min)
        else:
            df["distinct_norm"] = 0.0

        peptide_min, peptide_max = df["peptide_count"].min(), df["peptide_count"].max()
        if peptide_max > peptide_min:
            df["peptide_norm"] = (df["peptide_count"] - peptide_min) / (peptide_max - peptide_min)
        else:
            df["peptide_norm"] = 0.0

        df["combined_score"] = (
            distinct_w * df["distinct_norm"] + peptide_w * df["peptide_norm"]
        )

        df_sorted = df.sort_values("combined_score", ascending=False).reset_index(drop=True)
        self.df_combined = df_sorted
        return df_sorted

    @staticmethod
    def _get_cutoff_index(
        df_results_by_rank: pd.DataFrame,
        target_coverage: float | None,
    ) -> int | None:
        """Return the first row index meeting the requested coverage cutoff."""
        if target_coverage is None or df_results_by_rank.empty:
            return None
        matched = df_results_by_rank.index[df_results_by_rank["coverage_ratio"] >= target_coverage]
        if len(matched) == 0:
            return int(df_results_by_rank.index[-1])
        return int(matched[0])

    def get_ranked_coverage_df(
        self,
        rank_method: str = "combined",
        weight_distinct: float = 0.9,
        weight_peptide: float = 0.1,
        iters: int = 1,
        target_coverage: float | None = None,
        stop_when_selected_stable: bool = False,
    ) -> pd.DataFrame:
        """Return ranked targets with cumulative peptide coverage metrics.

        ``rank_method`` can be:
        - ``distinct_number``: rank by peptides assigned to exactly one target.
        - ``peptide_number``: rank by all peptides covered by each target.
        - ``combined``: rank by a weighted score from both metrics.

        When ``iters`` is greater than one, targets are re-ranked by the number
        of newly added peptides after each coverage pass. This is useful for
        choosing a compact target set for a requested coverage cutoff.
        """
        print(f"Calculating target coverage using [{rank_method}] method")

        target_to_peptides = self._create_target_to_peptides(
            self.df,
            self.peptide_column,
            self.target_column,
            self.target_separator,
        )
        df_target_distinct = self._get_distinct_targets(
            self.df,
            self.target_column,
            self.target_separator,
        )
        df_peptide_counts = self._calculate_peptide_counts()

        df_rank_meta = pd.merge(
            df_target_distinct[[self.target_column, "distinct_count"]],
            df_peptide_counts[[self.target_column, "peptide_count"]],
            on=self.target_column,
            how="outer",
        ).fillna(0)
        df_rank_meta["distinct_count"] = df_rank_meta["distinct_count"].astype(int)
        df_rank_meta["peptide_count"] = df_rank_meta["peptide_count"].astype(int)
        df_rank_meta["combined_score"] = 0.0

        if rank_method == "distinct_number":
            target_rank_list = df_target_distinct[self.target_column].tolist()
        elif rank_method == "peptide_number":
            target_rank_list = sorted(
                target_to_peptides.keys(),
                key=lambda target: len(target_to_peptides[target]),
                reverse=True,
            )
        elif rank_method == "combined":
            print(f"weight_distinct={weight_distinct}, weight_peptide={weight_peptide}")
            df_combined = self._calculate_combined_rank(
                df_target_distinct,
                df_peptide_counts,
                weight_distinct,
                weight_peptide,
            )
            target_rank_list = df_combined[self.target_column].tolist()
            df_rank_meta = df_combined[
                [self.target_column, "distinct_count", "peptide_count", "combined_score"]
            ].copy()
        else:
            raise ValueError("Invalid rank_method")

        distinct_count_map = dict(
            zip(df_rank_meta[self.target_column], df_rank_meta["distinct_count"])
        )
        peptide_count_map = dict(
            zip(df_rank_meta[self.target_column], df_rank_meta["peptide_count"])
        )
        combined_score_map = dict(
            zip(df_rank_meta[self.target_column], df_rank_meta["combined_score"])
        )

        print(f"Round 1/{iters} for [{self.target_column}] coverage...")
        df_results_by_rank = self._calculate_target_coverage(target_rank_list, target_to_peptides)
        previous_selected_targets: frozenset[str] | None = None

        for i in range(1, iters):
            print(f"Round {i + 1}/{iters} for [{self.target_column}] coverage...")
            cutoff_index = self._get_cutoff_index(df_results_by_rank, target_coverage)
            current_selected_targets = (
                frozenset(df_results_by_rank.loc[:cutoff_index, self.target_column].tolist())
                if cutoff_index is not None
                else None
            )
            if (
                stop_when_selected_stable
                and current_selected_targets is not None
                and current_selected_targets == previous_selected_targets
            ):
                print(f"Selected [{self.target_column}] set stabilized at round {i}; stop reranking")
                break

            rerank_df = df_results_by_rank.copy()
            rerank_df["distinct_count"] = (
                rerank_df[self.target_column].map(distinct_count_map).fillna(0)
            )
            rerank_df["peptide_count"] = (
                rerank_df[self.target_column].map(peptide_count_map).fillna(0)
            )
            rerank_df["combined_score"] = (
                rerank_df[self.target_column].map(combined_score_map).fillna(0.0)
            )
            rerank_df.sort_values(
                by=["added_peptides", "distinct_count", "peptide_count", "combined_score"],
                ascending=[False, False, False, False],
                inplace=True,
                kind="mergesort",
            )
            new_target_rank_list = rerank_df[self.target_column].tolist()
            df_results_by_rank = self._calculate_target_coverage(
                new_target_rank_list,
                target_to_peptides,
            )
            previous_selected_targets = current_selected_targets

        df_results_by_rank = pd.merge(
            df_results_by_rank,
            df_rank_meta[[self.target_column, "distinct_count", "peptide_count"]],
            on=self.target_column,
            how="left",
        )
        df_results_by_rank.rename(
            columns={
                "distinct_count": "distinct_peptides_count",
                "peptide_count": "all_peptide_count",
            },
            inplace=True,
        )

        df_results_by_rank["rank"] = range(1, len(df_results_by_rank) + 1)
        cols = ["rank"] + [col for col in df_results_by_rank.columns if col != "rank"]
        df_results_by_rank = df_results_by_rank[cols]

        self.df_results_by_rank = df_results_by_rank
        return df_results_by_rank

    def get_rank_list_by_distinct_number(self) -> list[str]:
        """Return targets ordered by distinct peptide count."""
        df_target_distinct = self._get_distinct_targets(
            self.df,
            self.target_column,
            self.target_separator,
        )
        return df_target_distinct[self.target_column].tolist()

    def get_rank_list_by_peptide_number(self) -> list[str]:
        """Return targets ordered by the number of covered peptides."""
        if self.target_to_peptides is None:
            self._create_target_to_peptides(
                self.df,
                self.peptide_column,
                self.target_column,
                self.target_separator,
            )
        if self.target_to_peptides is None:
            return []
        return sorted(
            self.target_to_peptides.keys(),
            key=lambda target: len(self.target_to_peptides[target]),
            reverse=True,
        )

    def get_turning_point(
        self,
        df_results_by_rank: pd.DataFrame | None = None,
        window_size: int = 20,
        std_threshold: float = 1,
    ) -> int | None:
        """Estimate the plateau point for a ranked coverage table."""
        if df_results_by_rank is None:
            df_results_by_rank = self.df_results_by_rank
        if df_results_by_rank is None:
            raise ValueError("Please call get_ranked_coverage_df() first")

        return self._calculate_turning_point(df_results_by_rank, window_size, std_threshold)

    def get_rank_covre_df(
        self,
        genome_rank_method: str = "combined",
        weight_distinct: float = 0.9,
        weight_peptide: float = 0.1,
        iters: int = 1,
        target_coverage: float | None = None,
        stop_when_selected_stable: bool = False,
    ) -> pd.DataFrame:
        """Backward-compatible wrapper for the old misspelled method name."""
        return self.get_ranked_coverage_df(
            rank_method=genome_rank_method,
            weight_distinct=weight_distinct,
            weight_peptide=weight_peptide,
            iters=iters,
            target_coverage=target_coverage,
            stop_when_selected_stable=stop_when_selected_stable,
        )


class GenomeRank(PeptideCoverageRanker):
    """Backward-compatible alias for the old genome-specific class name."""

    def __init__(
        self,
        df: pd.DataFrame,
        peptide_column: str,
        genome_column: str,
        genome_separator: str,
    ) -> None:
        super().__init__(
            df=df,
            peptide_column=peptide_column,
            target_column=genome_column,
            target_separator=genome_separator,
        )

    @property
    def genome_column(self) -> str:
        """Old attribute name for ``target_column``."""
        return self.target_column

    @property
    def genome_separator(self) -> str:
        """Old attribute name for ``target_separator``."""
        return self.target_separator


if __name__ == "__main__":
    extracted_columns = ["Stripped.Sequence", "Genomes"]
    dft = pd.read_csv(
        "DIANN/temp/annotated_peptide_table.tsv",
        sep="\t",
        usecols=extracted_columns,
    )
    ranker = PeptideCoverageRanker(dft, "Stripped.Sequence", "Genomes", ";")
    df_ranked = ranker.get_ranked_coverage_df(rank_method="combined")
    ranker.get_turning_point()
    df_ranked.to_csv("DIANN/temp/genome_ranked.tsv", sep="\t", index=False)
