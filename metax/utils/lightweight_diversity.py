"""Lightweight diversity and PCoA utilities for MetaX.

Portions of this module are adapted from scikit-bio.

Original project:
    scikit-bio
Original copyright:
    Copyright (c) 2013--, scikit-bio development team.
License:
    BSD-3-Clause. See licenses/scikit-bio-BSD-3-Clause.txt.

The implementation is intentionally limited to the diversity metrics and
ordination behavior used by MetaX, so MetaX does not require scikit-bio or its
BIOM-format runtime dependency during normal installation.
"""

from __future__ import annotations

from dataclasses import dataclass
from warnings import warn

import numpy as np
import pandas as pd
from scipy.linalg import eigh
from scipy.optimize import minimize_scalar
from scipy.spatial.distance import pdist, squareform


@dataclass
class PCoAResult:
    """Minimal PCoA result object compatible with MetaX plotting code."""

    samples: pd.DataFrame
    proportion_explained: pd.Series
    eigvals: pd.Series


def _validate_counts_vector(counts, cast_int: bool = False) -> np.ndarray:
    """Validate and normalize a one-dimensional counts vector."""
    arr = np.asarray(counts)
    if arr.ndim != 1:
        raise ValueError("Counts vector must be one-dimensional.")

    if cast_int:
        arr = arr.astype(int, copy=False)
    else:
        arr = arr.astype(float, copy=False)

    if np.any(np.isnan(arr)):
        raise ValueError("Counts vector cannot contain NaN values.")
    if np.any(arr < 0):
        raise ValueError("Counts vector cannot contain negative values.")

    return arr[arr != 0]


def observed_otus(counts) -> int:
    """Calculate the number of observed features."""
    counts = _validate_counts_vector(counts)
    return int(counts.size)


def shannon(counts, base: float | None = None) -> float:
    """Calculate Shannon entropy."""
    counts = _validate_counts_vector(counts)
    if counts.size == 0:
        return np.nan

    freqs = counts / counts.sum()
    entropy = -np.sum(freqs * np.log(freqs))
    if base is not None:
        entropy /= np.log(base)
    return float(entropy)


def dominance(counts, finite: bool = False) -> float:
    """Calculate Simpson's dominance index."""
    counts = _validate_counts_vector(counts)
    if counts.size == 0:
        return np.nan

    total = counts.sum()
    if finite:
        if total <= 1:
            return np.nan
        return float((counts * (counts - 1)).sum() / (total * (total - 1)))
    return float(((counts / total) ** 2).sum())


def simpson(counts, finite: bool = False) -> float:
    """Calculate Simpson's diversity index."""
    value = dominance(counts, finite=finite)
    return float(1 - value) if not np.isnan(value) else np.nan


def pielou_e(counts) -> float:
    """Calculate Pielou's evenness."""
    counts = _validate_counts_vector(counts)
    if counts.size <= 1:
        return np.nan
    return float(shannon(counts) / np.log(counts.size))


def chao1(counts) -> float:
    """Calculate the bias-corrected Chao1 richness estimator."""
    counts = _validate_counts_vector(counts, cast_int=True)
    observed = counts.size
    if observed == 0:
        return np.nan

    singles = np.sum(counts == 1)
    doubles = np.sum(counts == 2)
    return float(observed + singles * (singles - 1) / (2 * (doubles + 1)))


def menhinick(counts) -> float:
    """Calculate Menhinick's richness index."""
    counts = _validate_counts_vector(counts)
    if counts.size == 0:
        return np.nan
    return float(counts.size / np.sqrt(counts.sum()))


def mcintosh_d(counts) -> float:
    """Calculate McIntosh dominance index."""
    counts = _validate_counts_vector(counts)
    if counts.size == 0:
        return np.nan

    total = counts.sum()
    if total == 1:
        return np.nan
    u_value = np.sqrt((counts**2).sum())
    return float((total - u_value) / (total - np.sqrt(total)))


def mcintosh_e(counts) -> float:
    """Calculate McIntosh's evenness measure."""
    counts = _validate_counts_vector(counts)
    if counts.size == 0:
        return np.nan

    species = counts.size
    total = counts.sum()
    numerator = np.sqrt((counts * counts).sum())
    denominator = np.sqrt((total - species + 1) ** 2 + species - 1)
    if denominator == 0:
        return np.nan
    return float(numerator / denominator)


def fisher_alpha(counts) -> float:
    """Calculate Fisher's alpha by numerical optimization."""
    counts = _validate_counts_vector(counts, cast_int=True)
    if counts.size == 0:
        return 0.0

    total = counts.sum()
    species = counts.size
    if total == species:
        return np.inf

    def objective(alpha):
        if alpha <= 0:
            return np.inf
        return (alpha * np.log1p(total / alpha) - species) ** 2

    with np.errstate(invalid="ignore"):
        result = minimize_scalar(objective)
    if not result.success:
        raise RuntimeError("Optimizer failed to solve for Fisher's alpha.")
    return float(result.x)


def ace(counts, rare_threshold: int = 10) -> float:
    """Calculate the abundance-based coverage estimator.

    This implementation follows the scikit-bio ACE logic for abundance data.
    """
    counts = _validate_counts_vector(counts, cast_int=True)
    if counts.size == 0:
        return np.nan
    if rare_threshold < 1:
        raise ValueError("rare_threshold must be at least 1.")

    freq_counts = np.bincount(counts)
    if len(freq_counts) <= 1:
        return np.nan

    singles = freq_counts[1] if len(freq_counts) > 1 else 0
    rare_freqs = freq_counts[1 : rare_threshold + 1]
    abundant_freqs = freq_counts[rare_threshold + 1 :]

    rare_species = rare_freqs.sum()
    abundant_species = abundant_freqs.sum()
    rare_individuals = sum(i * rare_freqs[i - 1] for i in range(1, len(rare_freqs) + 1))

    if rare_species == 0:
        return float(abundant_species)
    if rare_individuals == 0:
        return float(abundant_species)
    if rare_individuals == singles:
        return np.nan

    coverage = 1 - singles / rare_individuals
    if coverage <= 0:
        return np.nan

    numerator = rare_species * sum(
        i * (i - 1) * rare_freqs[i - 1] for i in range(1, len(rare_freqs) + 1)
    )
    denominator = coverage * rare_individuals * (rare_individuals - 1)
    gamma = max(numerator / denominator - 1, 0) if denominator != 0 else 0

    return float(abundant_species + rare_species / coverage + singles / coverage * gamma)


ALPHA_DIVERSITY_METRICS = {
    "shannon": shannon,
    "simpson": simpson,
    "chao1": chao1,
    "observed_otus": observed_otus,
    "pielou_e": pielou_e,
    "fisher_alpha": fisher_alpha,
    "dominance": dominance,
    "menhinick": menhinick,
    "mcintosh_d": mcintosh_d,
    "mcintosh_e": mcintosh_e,
    "ace": ace,
}

BETA_DIVERSITY_METRIC_ALIASES = {
    "manhattan": "cityblock",
    "cityblock": "cityblock",
}

BINARY_BETA_DIVERSITY_METRICS = {
    "dice",
    "hamming",
    "jaccard",
    "rogerstanimoto",
    "russellrao",
    "sokalmichener",
    "sokalsneath",
    "yule",
}


def _normalize_beta_metric(metric: str) -> str:
    """Normalize user-facing metric names to SciPy-compatible names."""
    normalized = metric.strip().lower().replace(" ", "_").replace("-", "_")
    return BETA_DIVERSITY_METRIC_ALIASES.get(normalized, normalized)


def _dice_distance(u, v) -> float:
    """Calculate Dice dissimilarity on binary vectors.

    Two all-zero vectors are treated as identical and return 0.0. This avoids
    NaN values in the distance matrix and matches the expected behavior for
    absence-only comparisons in MetaX plots.
    """
    u = np.asarray(u, dtype=bool)
    v = np.asarray(v, dtype=bool)
    shared = np.logical_and(u, v).sum()
    total = u.sum() + v.sum()
    if total == 0:
        return 0.0
    return float(1 - (2 * shared / total))


def beta_diversity_to_dataframe(metric: str, data: pd.DataFrame) -> pd.DataFrame:
    """Calculate a beta-diversity distance matrix from a samples-by-features table."""
    if data.shape[0] < 2:
        raise ValueError("At least two samples are required for beta diversity.")

    metric = _normalize_beta_metric(metric)
    values = data.values

    if np.any(pd.isna(values)):
        raise ValueError("Input table for beta diversity cannot contain NaN values.")
    if np.any(values < 0):
        raise ValueError("Input table for beta diversity cannot contain negative values.")

    if metric in BINARY_BETA_DIVERSITY_METRICS:
        values = values > 0

    if metric == "dice":
        distances = pdist(values, metric=_dice_distance)
    else:
        distances = pdist(values, metric=metric)

    matrix = squareform(distances)
    if np.any(~np.isfinite(matrix)):
        raise ValueError(f"Metric '{metric}' produced non-finite distances and cannot be plotted.")

    return pd.DataFrame(matrix, index=data.index, columns=data.index)


def center_distance_matrix(distance_matrix: np.ndarray) -> np.ndarray:
    """Gower-center a distance matrix for PCoA."""
    matrix = np.asarray(distance_matrix, dtype=float)
    e_matrix = matrix * matrix / -2.0
    row_means = e_matrix.mean(axis=1, keepdims=True)
    col_means = e_matrix.mean(axis=0, keepdims=True)
    matrix_mean = e_matrix.mean()
    return e_matrix - row_means - col_means + matrix_mean


def pcoa(distance_matrix: pd.DataFrame | np.ndarray, warn_neg_eigval: float | bool = 0.01) -> PCoAResult:
    """Perform principal coordinate analysis on a distance matrix."""
    if isinstance(distance_matrix, pd.DataFrame):
        ids = list(distance_matrix.index)
        matrix = distance_matrix.values
    else:
        matrix = np.asarray(distance_matrix, dtype=float)
        ids = [str(i) for i in range(matrix.shape[0])]

    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("PCoA requires a square distance matrix.")
    if not np.allclose(matrix, matrix.T):
        raise ValueError("PCoA requires a symmetric distance matrix.")
    if np.any(~np.isfinite(matrix)):
        raise ValueError("PCoA requires a finite distance matrix.")

    centered = center_distance_matrix(matrix)
    eigvals, eigvecs = eigh(centered)

    eigvals = np.where(np.isclose(eigvals, 0), 0, eigvals)
    order = np.argsort(eigvals)[::-1]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]

    if warn_neg_eigval and eigvals[-1] < 0:
        threshold = 0 if warn_neg_eigval is True else eigvals[0] * float(warn_neg_eigval)
        if -eigvals[-1] > threshold:
            warn(
                "The PCoA result contains large negative eigenvalues, which may "
                "suggest result inaccuracy for this distance matrix.",
                RuntimeWarning,
            )

    positive_mask = eigvals >= 0
    eigvals = np.where(positive_mask, eigvals, 0)
    eigvecs = eigvecs * positive_mask

    total = eigvals.sum()
    if total == 0:
        proportions = np.zeros_like(eigvals)
    else:
        proportions = eigvals / total

    coordinates = eigvecs * np.sqrt(eigvals)
    axis_labels = [f"PC{i}" for i in range(1, len(eigvals) + 1)]

    return PCoAResult(
        samples=pd.DataFrame(coordinates, index=ids, columns=axis_labels),
        proportion_explained=pd.Series(proportions, index=axis_labels),
        eigvals=pd.Series(eigvals, index=axis_labels),
    )
