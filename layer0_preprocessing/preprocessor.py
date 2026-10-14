"""
=============================================================================
LAYER 0: DATA PREPROCESSING
Module: preprocessor.py
-----------------------------------------------------------------------------
Problem Solved:
  Provides a reproducible, fit → transform preprocessing pipeline that runs
  on raw EDGE IIoT feature matrices BEFORE they reach Layer 1 (Telemetry).

  Fixes the root causes of inconsistent FL accuracy:
    1. Mixed-type / hex-string columns   → coerced to float
    2. Missing values filled naively     → median imputation per column
    3. Heavy-tailed / extreme outliers   → IQR-based clipping
    4. Different feature magnitudes      → log1p compression + StandardScaler
    5. Zero-variance / constant columns  → dropped before training
    6. Each FL client normalising independently → ONE shared fitted scaler

Pipeline (in order):
  [1] Coerce to numeric (hex strings, mixed types)
  [2] Median imputation  (NaN → column median, or 0 if all-NaN)
  [3] IQR outlier clipping  (values outside Q1–1.5·IQR … Q3+1.5·IQR)
  [4] log1p(|x|) compression  (handles heavy-tailed protocol counters)
  [5] StandardScaler  (zero mean, unit variance)
  [6] Variance filter  (drop near-constant columns)

Inputs:  pd.DataFrame or np.ndarray of raw feature values
Outputs: np.ndarray of cleaned, normalised floats + preprocessing stats dict
=============================================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple

from config import OUTLIER_IQR_FACTOR, MIN_VARIANCE_THRESHOLD, TOP_K_FEATURES


class DataPreprocessor:
    """
    Stateful fit → transform preprocessing pipeline for EDGE IIoT features.

    Usage
    -----
    On training data (fit once, shared across all FL clients):
        preprocessor = DataPreprocessor()
        X_clean = preprocessor.fit_transform(df_or_array, feature_cols)

    On any new data (attack CSVs, test sets, FL client shards):
        X_clean = preprocessor.transform(df_or_array)

    The fitted state (medians, IQR bounds, scaler mean/std, kept columns)
    should be saved with cache_manager.save_preprocessor() after fitting.
    """

    def __init__(
        self,
        iqr_factor: float = OUTLIER_IQR_FACTOR,
        variance_threshold: float = MIN_VARIANCE_THRESHOLD,
        top_k: int = TOP_K_FEATURES,
    ):
        self.iqr_factor = iqr_factor
        self.variance_threshold = variance_threshold
        self.top_k = top_k

        # Fitted state (set during fit_transform / fit)
        self._is_fitted: bool = False
        self._feature_cols: List[str] = []
        self._kept_indices: np.ndarray = np.array([], dtype=int)
        self._medians: np.ndarray = np.array([])
        self._clip_lower: np.ndarray = np.array([])
        self._clip_upper: np.ndarray = np.array([])
        self._scale_mean: np.ndarray = np.array([])
        self._scale_std: np.ndarray = np.array([])

        # Diagnostic stats from the last fit
        self.fit_stats: Dict = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fit_transform(
        self,
        data: "pd.DataFrame | np.ndarray",
        feature_cols: Optional[List[str]] = None,
    ) -> np.ndarray:
        """Fit on data and return the transformed array."""
        X_raw = self._to_float_array(data, feature_cols)
        X_out = self._fit(X_raw)
        return X_out

    def transform(
        self,
        data: "pd.DataFrame | np.ndarray",
        feature_cols: Optional[List[str]] = None,
    ) -> np.ndarray:
        """Transform new data using already-fitted parameters."""
        if not self._is_fitted:
            raise RuntimeError(
                "DataPreprocessor has not been fitted yet. "
                "Call fit_transform() first."
            )
        X_raw = self._to_float_array(data, feature_cols)
        return self._transform(X_raw)

    def fit(
        self,
        data: "pd.DataFrame | np.ndarray",
        feature_cols: Optional[List[str]] = None,
    ) -> "DataPreprocessor":
        """Fit without returning the transformed array (chainable)."""
        X_raw = self._to_float_array(data, feature_cols)
        self._fit(X_raw)
        return self

    @property
    def n_features_out(self) -> int:
        """Number of output features after the variance filter."""
        return int(self._kept_indices.shape[0])

    @property
    def kept_feature_names(self) -> List[str]:
        """Names of kept features (if feature_cols was provided at fit time)."""
        if not self._feature_cols:
            return [f"feature_{i}" for i in self._kept_indices.tolist()]
        return [self._feature_cols[i] if i < len(self._feature_cols) else f"feature_{i}" for i in self._kept_indices.tolist()]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _to_float_array(
        self,
        data: "pd.DataFrame | np.ndarray",
        feature_cols: Optional[List[str]] = None,
    ) -> np.ndarray:
        """Coerce input to a float64 numpy array (Step 1)."""
        if isinstance(data, pd.DataFrame):
            if feature_cols:
                available = [c for c in feature_cols if c in data.columns]
                self._feature_cols = available
                df = data[available].copy()
            else:
                self._feature_cols = list(data.columns)
                df = data.copy()

            # Coerce every column to numeric (hex strings → NaN → handled next)
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            return df.to_numpy(dtype=float)

        # Already an array
        arr = np.asarray(data, dtype=float)
        if arr.ndim == 1:
            arr = arr.reshape(-1, 1)
        return arr

    def _fit(self, X: np.ndarray) -> np.ndarray:
        """Run the full fit + transform pipeline, record fitted state."""
        n_rows, n_cols = X.shape
        stats: Dict = {"n_rows_fit": n_rows, "n_cols_input": n_cols}

        # Step 2 — Median imputation
        medians = np.nanmedian(X, axis=0)
        medians = np.where(np.isnan(medians), 0.0, medians)   # fallback for all-NaN cols
        nan_counts = int(np.isnan(X).sum())
        stats["nan_cells_imputed"] = nan_counts
        for j in range(n_cols):
            mask = np.isnan(X[:, j])
            X[mask, j] = medians[j]
        self._medians = medians

        # Step 3 — IQR outlier clipping
        q1 = np.percentile(X, 25, axis=0)
        q3 = np.percentile(X, 75, axis=0)
        iqr = q3 - q1
        clip_lo = q1 - self.iqr_factor * iqr
        clip_hi = q3 + self.iqr_factor * iqr
        n_clipped = int(np.sum((X < clip_lo) | (X > clip_hi)))
        X = np.clip(X, clip_lo, clip_hi)
        self._clip_lower = clip_lo
        self._clip_upper = clip_hi
        stats["outlier_cells_clipped"] = n_clipped

        # Step 4 — log1p compression
        X = np.log1p(np.abs(X))
        X = np.nan_to_num(X, nan=0.0, posinf=100.0, neginf=0.0)

        # Step 5 — StandardScaler
        mean = X.mean(axis=0)
        std  = X.std(axis=0)
        std  = np.where(std < 1e-12, 1.0, std)   # avoid divide-by-zero
        X    = (X - mean) / std
        self._scale_mean = mean
        self._scale_std  = std

        # Step 6 — Variance filter (on the scaled array)
        variances = X.var(axis=0)
        kept = np.where(variances >= self.variance_threshold)[0]

        # Apply top-K cap
        if self.top_k > 0 and len(kept) > self.top_k:
            top_var_idx = np.argsort(variances[kept])[::-1][: self.top_k]
            kept = kept[top_var_idx]

        stats["n_cols_dropped_low_variance"] = n_cols - len(kept)
        stats["n_features_out"] = len(kept)

        # Class imbalance info is computed externally (requires labels)
        self._kept_indices = kept
        self.fit_stats = stats
        self._is_fitted = True

        return X[:, kept]

    def _transform(self, X: np.ndarray) -> np.ndarray:
        """Apply fitted pipeline to new data (no re-fitting)."""
        n_cols_in = X.shape[1] if X.ndim == 2 else 1

        # Step 2 — Impute using fitted medians (pad/trim if column count differs)
        medians = self._medians
        if len(medians) != n_cols_in:
            medians = np.resize(medians, n_cols_in)
        for j in range(n_cols_in):
            mask = np.isnan(X[:, j])
            X[mask, j] = medians[j]

        # Step 3 — Clip using fitted bounds
        lo = np.resize(self._clip_lower, n_cols_in)
        hi = np.resize(self._clip_upper, n_cols_in)
        X  = np.clip(X, lo, hi)

        # Step 4 — log1p
        X = np.log1p(np.abs(X))
        X = np.nan_to_num(X, nan=0.0, posinf=100.0, neginf=0.0)

        # Step 5 — Standardise using fitted mean/std
        mean = np.resize(self._scale_mean, n_cols_in)
        std  = np.resize(self._scale_std,  n_cols_in)
        X    = (X - mean) / std

        # Step 6 — Select kept columns
        kept = self._kept_indices
        kept = kept[kept < n_cols_in]   # safety guard for shape mismatches
        if len(kept) == 0:
            return X
        return X[:, kept]


def compute_class_balance(y: np.ndarray) -> Dict:
    """
    Returns a dict with class counts and the imbalance ratio.
    Used to populate meta['class_balance'] in data_loader.
    """
    if len(y) == 0:
        return {"normal": 0, "attack": 0, "imbalance_ratio": None}
    normal  = int(np.sum(y == 0))
    attack  = int(np.sum(y == 1))
    ratio   = round(normal / attack, 2) if attack > 0 else None
    return {
        "normal":          normal,
        "attack":          attack,
        "attack_rate_pct": round(100.0 * attack / len(y), 2),
        "imbalance_ratio": ratio,   # normal:attack  e.g. 3.2 means 3.2x more normal
    }
