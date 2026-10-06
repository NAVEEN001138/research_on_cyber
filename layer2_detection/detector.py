"""
=============================================================================
LAYER 2: THREAT DETECTION & FEDERATED EDGE AI
Module: detector.py
-----------------------------------------------------------------------------
Problem Solved:
  Computes threat probability scores (s_i) for cloud resources using Machine
  Learning (RandomForestClassifier). Solves threat identification based on
  3 aligned signals: failed logins, unusual outbound traffic, privilege escalation.

Inputs:  Raw signal features per cloud resource.
Outputs: Threat probability score s_i in [0, 1] per resource.
=============================================================================
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler

from config import FEATURE_NAMES
from layer1_telemetry.data_loader import build_training_dataset


class ThreatDetector:
    def __init__(self, seed: int = 0, use_real_data: bool = True, verbose: bool = True):
        self.seed = seed
        self.verbose = verbose
        self.training_meta: dict = {}
        self.model = RandomForestClassifier(n_estimators=200, random_state=seed)
        self.scaler = StandardScaler()
        self.feature_names = FEATURE_NAMES.copy()
        self._fit(use_real_data)

    def _synthetic_training_data(self, n_samples: int = 2000):
        rng = np.random.default_rng(self.seed)
        benign = rng.normal(loc=[3, 2000, 0], scale=[2, 1000, 0.3], size=(n_samples // 2, 3))
        malicious = rng.normal(loc=[25, 200_000, 2.5], scale=[10, 100_000, 1.2], size=(n_samples // 2, 3))
        X = np.vstack([benign, malicious])
        y = np.array([0] * (n_samples // 2) + [1] * (n_samples // 2))
        return np.clip(X, 0, None), y

    def _fit(self, use_real_data: bool):
        X, y = None, None

        if use_real_data:
            X, y, meta = build_training_dataset()
            self.training_meta = meta
            if len(y) > 0 and self.verbose:
                source = meta.get("source", "unknown")
                rows = meta.get("rows", len(y))
                pos = meta.get("positive_rate", y.mean())
                print(f"Training on {rows} rows from {source.upper()} (attack rate {pos:.1%})")
                if meta.get("attack_types"):
                    attacks_list = list(meta["attack_types"].keys()) if isinstance(meta["attack_types"], dict) else meta["attack_types"]
                    print(
                        f"  Attack classes: {', '.join(attacks_list[:6])}"
                        f"{'...' if len(attacks_list) > 6 else ''}"
                    )

        if X is None or len(y) == 0:
            if self.verbose:
                print("No dataset found, using synthetic training data")
            X, y = self._synthetic_training_data()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.seed,
            stratify=y if len(np.unique(y)) > 1 else None,
        )
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)
        self.model.fit(X_train, y_train)

        if self.verbose:
            y_pred = self.model.predict(X_test)
            print("\nModel Evaluation:")
            print(f"  Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
            print(f"  Precision: {precision_score(y_test, y_pred, zero_division=0):.4f}")
            print(f"  Recall:    {recall_score(y_test, y_pred, zero_division=0):.4f}")
            print(f"  F1 Score:  {f1_score(y_test, y_pred, zero_division=0):.4f}")

    def _resource_features(self, resource: dict) -> np.ndarray:
        raw = resource.get("raw_signal", {})
        values = [[raw.get(name, 0.0) for name in self.feature_names]]
        return self.scaler.transform(values)

    def score_resource(self, resource: dict) -> float:
        features = self._resource_features(resource)
        proba = self.model.predict_proba(features)[0]
        return float(proba[1])

    def score_scenario(self, scenario: dict) -> dict:
        return {r["id"]: self.score_resource(r) for r in scenario["resources"]}


if __name__ == "__main__":
    from layer1_telemetry.fake_incident import SCENARIOS

    detector = ThreatDetector()
    scores = detector.score_scenario(SCENARIOS["ddos_flood"])
    print("\nThreat Scores:")
    for rid, score in scores.items():
        print(f"  {rid}: {score:.3f}")
