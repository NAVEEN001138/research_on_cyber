"""
=============================================================================
IMBALANCE-AWARE STATISTICAL & CLASSIFICATION METRICS
Module: utils/metrics.py
-----------------------------------------------------------------------------
Computes complete, honest evaluation metrics for imbalanced cybersecurity
datasets (~84% attack in Edge-IIoTset, ~93% normal in WUSTL-IIoT-2021).
Never derives one metric from another; computes all directly from predictions.
=============================================================================
"""

import numpy as np
import scipy.stats as stats
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    matthews_corrcoef,
    roc_auc_score,
    average_precision_score,
    confusion_matrix
)


def compute_comprehensive_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_scores: np.ndarray
) -> dict:
    """
    Computes imbalance-aware metric dictionary from ground truth, binary predictions,
    and positive class continuous probabilities.
    
    Args:
        y_true: True binary labels (0 or 1)
        y_pred: Predicted discrete labels (0 or 1)
        y_scores: Continuous probabilities / softmax scores for class 1
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    y_scores = np.asarray(y_scores, dtype=float)

    acc = float(accuracy_score(y_true, y_pred))
    bal_acc = float(balanced_accuracy_score(y_true, y_pred))
    macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    mcc = float(matthews_corrcoef(y_true, y_pred))

    # Per-class precision, recall, f1
    p_per_class = precision_score(y_true, y_pred, average=None, zero_division=0)
    r_per_class = recall_score(y_true, y_pred, average=None, zero_division=0)
    f1_per_class = f1_score(y_true, y_pred, average=None, zero_division=0)

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

    # ROC-AUC and PR-AUC
    try:
        roc_auc = float(roc_auc_score(y_true, y_scores))
    except Exception:
        roc_auc = 0.5

    try:
        pr_auc = float(average_precision_score(y_true, y_scores))
    except Exception:
        pr_auc = float(np.mean(y_true))

    # Sanity check for constant class prediction
    if roc_auc < 0.55:
        print("\n" + "!" * 75)
        print("  [LOUD WARNING] MODEL IS PREDICTING A CONSTANT CLASS (ROC-AUC < 0.55)")
        print(f"  ROC-AUC: {roc_auc:.4f} | Balanced Acc: {bal_acc:.4f} | Accuracy: {acc:.4f}")
        print("!" * 75 + "\n")

    return {
        "accuracy": round(acc, 6),
        "balanced_accuracy": round(bal_acc, 6),
        "macro_f1": round(macro_f1, 6),
        "mcc": round(mcc, 6),
        "roc_auc": round(roc_auc, 6),
        "pr_auc": round(pr_auc, 6),
        "fpr": round(fpr, 6),
        "fnr": round(fnr, 6),
        "precision_normal": round(float(p_per_class[0]), 6) if len(p_per_class) > 0 else 0.0,
        "recall_normal": round(float(r_per_class[0]), 6) if len(r_per_class) > 0 else 0.0,
        "f1_normal": round(float(f1_per_class[0]), 6) if len(f1_per_class) > 0 else 0.0,
        "precision_attack": round(float(p_per_class[1]), 6) if len(p_per_class) > 1 else 0.0,
        "recall_attack": round(float(r_per_class[1]), 6) if len(r_per_class) > 1 else 0.0,
        "f1_attack": round(float(f1_per_class[1]), 6) if len(f1_per_class) > 1 else 0.0,
        "confusion_matrix": cm.tolist()
    }


def compute_seed_statistics(values: list) -> dict:
    """
    Computes mean, std, 95% Confidence Interval (t-distribution), min, max across trials.
    """
    n = len(values)
    if n == 0:
        return {}
    mean = float(np.mean(values))
    std = float(np.std(values, ddof=1)) if n > 1 else 0.0

    if n > 1 and std > 0:
        # 95% Confidence Interval using t-distribution
        ci_half = float(stats.t.ppf(0.975, df=n - 1) * (std / np.sqrt(n)))
    else:
        ci_half = 0.0

    return {
        "mean": round(mean, 6),
        "std": round(std, 6),
        "ci_95": round(ci_half, 6),
        "ci_lower": round(mean - ci_half, 6),
        "ci_upper": round(mean + ci_half, 6),
        "min": round(float(np.min(values)), 6),
        "max": round(float(np.max(values)), 6),
        "trials": [round(float(v), 6) for v in values]
    }


def compute_paired_comparison(a_trials: list, b_trials: list) -> dict:
    """
    Computes paired t-test and Wilcoxon signed-rank test between two methods across identical seeds.
    """
    a = np.array(a_trials, dtype=float)
    b = np.array(b_trials, dtype=float)

    diff = a - b
    res = {
        "mean_diff": round(float(np.mean(diff)), 6),
        "std_diff": round(float(np.std(diff, ddof=1)), 6) if len(diff) > 1 else 0.0,
    }

    if len(diff) >= 3 and not np.all(diff == 0):
        t_stat, p_val = stats.ttest_rel(a, b)
        res["t_stat"] = round(float(t_stat), 4)
        res["p_value_ttest"] = round(float(p_val), 6)
        try:
            w_stat, w_pval = stats.wilcoxon(diff)
            res["wilcoxon_stat"] = round(float(w_stat), 4)
            res["p_value_wilcoxon"] = round(float(w_pval), 6)
        except Exception:
            pass

    return res


import torch

@torch.no_grad()
def predict_in_batches(model, X, batch_size: int = 512):
    """Memory-safe inference. The attention layer allocates O(B x heads x L x L);
    evaluating a whole test set in one call peaks at GBs and was the cause of the
    2026-09-20 OOM crashes. Returns (preds, probs_of_class_1) as numpy arrays."""
    import numpy as np
    import torch.nn.functional as F
    was_training = model.training
    model.eval()
    preds, probs = [], []
    for i in range(0, len(X), batch_size):
        xb = torch.as_tensor(X[i:i + batch_size], dtype=torch.float32)
        lg = model(xb)
        probs.append(F.softmax(lg, dim=1)[:, 1].numpy())
        preds.append(torch.argmax(lg, dim=1).numpy())
    if was_training:
        model.train()
    return np.concatenate(preds), np.concatenate(probs)
