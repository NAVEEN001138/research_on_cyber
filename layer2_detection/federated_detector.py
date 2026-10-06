"""
=============================================================================
LAYER 2: THREAT DETECTION & FEDERATED EDGE AI
Module: federated_detector.py
-----------------------------------------------------------------------------
Problem Solved:
  Detects cyber threats across heterogeneous IoT Edge devices without exposing
  sensitive raw telemetry to a central cloud server. Solves data privacy risks
  and reduces network bandwidth consumption using Federated Averaging (FedAvg).

Inputs:  Edge-IIoTset IoT network packet features (MQTT, Modbus, TCP/UDP, ARP).
Outputs: Federated threat probabilities (s_i) for downstream Quantum Engine.
=============================================================================
"""

import time
import copy
import platform
import psutil
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    log_loss, confusion_matrix, roc_curve, auc
)
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier

from layer1_telemetry.data_loader import (
    load_edge_iiot_dataset, partition_data_for_fl,
    load_mixed_attack_test, FEATURE_NAMES
)
from layer2_detection.local_clients.edge_client import PyTorchMLP, PyTorch1DCNN, IoTEdgeNodeClient
from layer2_detection.global_server.fedavg_server    import GlobalFedAvgServer
from layer2_detection.global_server.fedprox_server   import GlobalFedProxServer
from layer2_detection.global_server.fednova_server   import GlobalFedNovaServer
from layer2_detection.global_server.fedadam_server   import GlobalFedAdamServer
from layer2_detection.global_server.fedmedian_server import GlobalFedMedianServer

import random

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


def set_global_seed(seed: int = 42):
    """Sets global random seeds across python, numpy, and PyTorch for 100% deterministic reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    if HAS_TORCH:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def _safe_compute_metrics(y_true, probs, preds) -> Tuple[float, float, float]:
    probs = np.nan_to_num(probs, nan=0.5, posinf=1.0, neginf=0.0)
    probs = np.clip(probs, 1e-15, 1.0 - 1e-15)
    preds = np.nan_to_num(preds, nan=0).astype(int)
    acc = float(accuracy_score(y_true, preds))
    f1 = float(f1_score(y_true, preds, zero_division=0))
    try:
        l_loss = float(log_loss(y_true, probs, labels=[0, 1]))
    except Exception:
        l_loss = 0.5
    return acc, f1, l_loss


def compute_privacy_index(
    bytes_shared: int,
    total_data_bytes: int,
    architecture: str = "fl"
) -> float:
    """
    Privacy Index Formula:
      PI = 100 * (1 - bytes_shared / total_data_bytes)

    Interpretations:
      - FL (FedAvg): shares only model gradient updates (param_bytes * clients * rounds)
        → High PI because raw data never leaves the device.
      - Centralized DNN/RF: shares the full training dataset with the server
        → Low PI because all raw records are transmitted.
      - Local Isolated NN: shares nothing; PI = 100.

    Clipped to [0, 100].
    """
    if architecture == "isolated":
        return 100.0
    if total_data_bytes <= 0:
        return 50.0
    ratio = min(bytes_shared / total_data_bytes, 1.0)
    return round(max(0.0, (1.0 - ratio) * 100.0), 1)


def compute_per_class_metrics(y_true, y_pred, label_names=None) -> List[Dict]:
    """
    Compute per-class Precision, Recall, F1 for each unique label.
    Returns a list of dicts suitable for pd.DataFrame.
    """
    labels = sorted(np.unique(np.concatenate([y_true, y_pred])))
    if label_names is None:
        label_names = {0: "Normal Traffic", 1: "Attack Traffic"}
    rows = []
    for lbl in labels:
        name = label_names.get(int(lbl), f"Class {lbl}")
        prec = precision_score(y_true, y_pred, labels=[lbl], average="micro", zero_division=0)
        rec  = recall_score(y_true, y_pred, labels=[lbl], average="micro", zero_division=0)
        f1   = f1_score(y_true, y_pred, labels=[lbl], average="micro", zero_division=0)
        support = int(np.sum(np.array(y_true) == lbl))
        rows.append({
            "Class": name,
            "Precision": round(float(prec) * 100, 2),
            "Recall": round(float(rec) * 100, 2),
            "F1 Score": round(float(f1) * 100, 2),
            "Support (samples)": support
        })
    return rows


def get_hardware_info() -> str:
    """Returns a brief hardware descriptor for the experiment config panel."""
    try:
        cpu = platform.processor() or platform.machine()
        ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 1)
        return f"{cpu[:40]} | RAM: {ram_gb} GB"
    except Exception:
        return "CPU info unavailable"


class FederatedEdgeManager:
    def __init__(
        self,
        sample_size: int = 25_000,
        num_clients: int = 5,
        non_iid: bool = True,
        seed: int = 42
    ):
        self.seed = seed
        set_global_seed(seed)
        self.num_clients = num_clients
        self.non_iid = non_iid
        self.scaler = StandardScaler()
        
        self.X_raw, self.y, self.raw_df, self.meta = load_edge_iiot_dataset(
            sample_size=sample_size, seed=seed
        )
        n_test = int(len(self.y) * 0.2)
        rng = np.random.default_rng(seed)
        shuffled_indices = rng.permutation(len(self.y))
        
        self.test_idx = shuffled_indices[:n_test]
        self.train_idx = shuffled_indices[n_test:]

        if len(self.y) > 0:
            self.X_train = self.scaler.fit_transform(self.X_raw[self.train_idx])
            self.X_test = self.scaler.transform(self.X_raw[self.test_idx])
        else:
            self.X_train = self.X_raw[self.train_idx]
            self.X_test = self.X_raw[self.test_idx]

        self.y_train = self.y[self.train_idx]
        self.y_test = self.y[self.test_idx]

        self.client_partitions, self.client_histograms = partition_data_for_fl(
            self.X_train, self.y_train, num_clients=num_clients, alpha=0.5, seed=seed
        )

    def set_custom_splits(self, X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray):
        """Sets custom preprocessed zero-leakage splits and re-partitions client data."""
        self.X_train, self.y_train = X_train, y_train
        self.X_test, self.y_test = X_test, y_test
        self.client_partitions = partition_data_for_fl(
            self.X_train, self.y_train, num_clients=self.num_clients, non_iid=self.non_iid, seed=self.seed
        )


    def train_federated_fl(
        self,
        rounds: int = 10,
        epochs_per_round: int = 2,
        lr: float = 0.01
    ) -> Dict:
        start_time = time.time()
        input_dim = self.X_train.shape[1]
        round_history = []
        bytes_transferred = 0

        if HAS_TORCH:
            global_model = PyTorchMLP(input_dim)
            global_weights = copy.deepcopy(global_model.state_dict())
            server = GlobalFedAvgServer(global_weights)

            param_size = sum(p.numel() * p.element_size() for p in global_model.parameters())

            for r in range(1, rounds + 1):
                client_weights_list = []
                client_sizes = []

                for c_idx, (cX, cy) in enumerate(self.client_partitions):
                    if len(cy) == 0:
                        continue
                    
                    client_node = IoTEdgeNodeClient(c_idx, cX, cy, name=f"Node {c_idx+1}")
                    w_k, _ = client_node.train_local_epoch(global_weights, epochs=epochs_per_round, lr=lr)

                    client_weights_list.append(w_k)
                    client_sizes.append(len(cy))
                    bytes_transferred += 2 * param_size

                global_weights = server.aggregate_weights(client_weights_list, client_sizes)
                global_model.load_state_dict(global_weights)

                global_model.eval()
                with torch.no_grad():
                    logits = global_model(torch.tensor(self.X_test, dtype=torch.float32))
                    probs = torch.softmax(logits, dim=1)[:, 1].numpy()
                    preds = torch.argmax(logits, dim=1).numpy()

                acc, f1, l_loss = _safe_compute_metrics(self.y_test, probs, preds)
                round_history.append({
                    "round": r,
                    "accuracy": acc,
                    "f1_score": f1,
                    "loss": l_loss,
                    "total_bytes_mb": round(bytes_transferred / (1024 * 1024), 2)
                })

            self.final_fl_model = global_model
            final_acc = round_history[-1]["accuracy"]
            final_f1 = round_history[-1]["f1_score"]
            final_loss = round_history[-1]["loss"]
        else:
            global_mlp = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=1, random_state=self.seed)
            classes = np.array([0, 1])
            global_mlp.partial_fit(self.X_train[:10], self.y_train[:10], classes=classes)

            for r in range(1, rounds + 1):
                client_coefs = []
                client_intercepts = []
                client_sizes = []

                for cX, cy in self.client_partitions:
                    if len(cy) < 5 or len(np.unique(cy)) < 2:
                        continue
                    local_mlp = copy.deepcopy(global_mlp)
                    local_mlp.partial_fit(cX, cy)
                    client_coefs.append(local_mlp.coefs_)
                    client_intercepts.append(local_mlp.intercepts_)
                    client_sizes.append(len(cy))

                total_s = sum(client_sizes)
                if total_s > 0:
                    for l in range(len(global_mlp.coefs_)):
                        global_mlp.coefs_[l] = sum((client_sizes[k]/total_s) * client_coefs[k][l] for k in range(len(client_sizes)))
                        global_mlp.intercepts_[l] = sum((client_sizes[k]/total_s) * client_intercepts[k][l] for k in range(len(client_sizes)))

                preds = global_mlp.predict(self.X_test)
                probs = global_mlp.predict_proba(self.X_test)[:, 1]
                acc, f1, l_loss = _safe_compute_metrics(self.y_test, probs, preds)
                bytes_transferred += 50_000 * self.num_clients * 2

                round_history.append({
                    "round": r,
                    "accuracy": acc,
                    "f1_score": f1,
                    "loss": l_loss,
                    "total_bytes_mb": round(bytes_transferred / (1024 * 1024), 2)
                })

            self.final_fl_model = global_mlp
            final_acc = round_history[-1]["accuracy"]
            final_f1 = round_history[-1]["f1_score"]
            final_loss = round_history[-1]["loss"]

        total_time = time.time() - start_time
        # Privacy Index: FL only shares model weights (not raw data)
        total_data_bytes = self.X_train.nbytes
        privacy_score = compute_privacy_index(bytes_transferred, total_data_bytes, "fl")

        # Confusion matrix & per-class metrics on final round
        if HAS_TORCH:
            self.final_fl_model.eval()
            with torch.no_grad():
                logits_final = self.final_fl_model(torch.tensor(self.X_test, dtype=torch.float32))
                preds_final = torch.argmax(logits_final, dim=1).numpy()
                probs_final = torch.softmax(logits_final, dim=1)[:, 1].numpy()
        else:
            preds_final = self.final_fl_model.predict(self.X_test)
            probs_final = self.final_fl_model.predict_proba(self.X_test)[:, 1]

        cm = confusion_matrix(self.y_test, preds_final, labels=[0, 1]).tolist()
        try:
            fpr, tpr, _ = roc_curve(self.y_test, probs_final, pos_label=1)
            roc_auc = float(auc(fpr, tpr))
            roc_data = {"fpr": fpr.tolist(), "tpr": tpr.tolist(), "auc": roc_auc}
        except Exception:
            roc_data = {"fpr": [], "tpr": [], "auc": 0.0}

        per_class = compute_per_class_metrics(self.y_test, preds_final)

        exp_config = {
            "dataset": "Edge-IIoTset (ML-EdgeIIoT-dataset.csv)",
            "train_test_split": "80 / 20",
            "total_samples": len(self.y),
            "train_samples": len(self.y_train),
            "test_samples": len(self.y_test),
            "num_clients": self.num_clients,
            "aggregation": "FedAvg",
            "model": "PyTorch MLP (36→128→64→2)" if HAS_TORCH else "sklearn MLP (36→64→32→2)",
            "random_seed": self.seed,
            "non_iid": self.non_iid,
            "hardware": get_hardware_info()
        }

        return {
            "algorithm": "Federated Learning (FedAvg MLP)",
            "accuracy": float(final_acc),
            "f1_score": float(final_f1),
            "loss": float(final_loss),
            "time_sec": total_time,
            "network_mb": round(bytes_transferred / (1024 * 1024), 2),
            "network_note": "Model gradient updates only (no raw data transmitted)",
            "privacy_score": privacy_score,
            "privacy_note": "PI = 100 × (1 − model_bytes / training_data_bytes)",
            "history": round_history,
            "confusion_matrix": cm,
            "roc": roc_data,
            "per_class_metrics": per_class,
            "experiment_config": exp_config
        }

    def train_centralized_dnn(self) -> Dict:
        start_time = time.time()
        input_dim = self.X_train.shape[1]

        if HAS_TORCH:
            model = PyTorchMLP(input_dim)
            model.train()
            optimizer = optim.Adam(model.parameters(), lr=0.01)
            criterion = nn.CrossEntropyLoss()

            dataset = TensorDataset(torch.tensor(self.X_train, dtype=torch.float32), torch.tensor(self.y_train, dtype=torch.long))
            loader = DataLoader(dataset, batch_size=64, shuffle=True)

            for _ in range(5):
                for bx, by in loader:
                    optimizer.zero_grad()
                    out = model(bx)
                    loss = criterion(out, by)
                    loss.backward()
                    optimizer.step()

            model.eval()
            with torch.no_grad():
                logits = model(torch.tensor(self.X_test, dtype=torch.float32))
                probs = torch.softmax(logits, dim=1)[:, 1].numpy()
                preds = torch.argmax(logits, dim=1).numpy()
        else:
            mlp = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=20, random_state=self.seed)
            mlp.fit(self.X_train, self.y_train)
            preds = mlp.predict(self.X_test)
            probs = mlp.predict_proba(self.X_test)[:, 1]

        acc, f1, l_loss = _safe_compute_metrics(self.y_test, probs, preds)
        total_time = time.time() - start_time
        # DNN sends full training dataset to central server
        raw_bytes = self.X_train.nbytes
        privacy_score = compute_privacy_index(raw_bytes, raw_bytes, "centralized")

        return {
            "algorithm": "Centralized Deep NN (DNN)",
            "accuracy": float(acc),
            "f1_score": float(f1),
            "loss": float(l_loss),
            "time_sec": total_time,
            "network_mb": round(raw_bytes / (1024 * 1024), 2),
            "network_note": "Full training dataset transmitted to central server",
            "privacy_score": privacy_score,
            "privacy_note": "PI = 100 × (1 − raw_bytes / raw_bytes) → near 0 (all data exposed)"
        }

    def train_local_isolated_nn(self) -> Dict:
        start_time = time.time()
        cX, cy = self.client_partitions[0]
        input_dim = self.X_train.shape[1]

        if len(cy) == 0:
            return {"algorithm": "Local Isolated NN", "accuracy": 0.5, "f1_score": 0.0, "loss": 1.0, "time_sec": 0.1, "network_mb": 0.0, "privacy_score": 100.0}

        if HAS_TORCH:
            model = PyTorchMLP(input_dim)
            model.train()
            optimizer = optim.Adam(model.parameters(), lr=0.01)
            criterion = nn.CrossEntropyLoss()

            dataset = TensorDataset(torch.tensor(cX, dtype=torch.float32), torch.tensor(cy, dtype=torch.long))
            loader = DataLoader(dataset, batch_size=32, shuffle=True)

            for _ in range(5):
                for bx, by in loader:
                    optimizer.zero_grad()
                    out = model(bx)
                    loss = criterion(out, by)
                    loss.backward()
                    optimizer.step()

            model.eval()
            with torch.no_grad():
                logits = model(torch.tensor(self.X_test, dtype=torch.float32))
                probs = torch.softmax(logits, dim=1)[:, 1].numpy()
                preds = torch.argmax(logits, dim=1).numpy()
        else:
            mlp = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=20, random_state=self.seed)
            mlp.fit(cX, cy)
            preds = mlp.predict(self.X_test)
            probs = mlp.predict_proba(self.X_test)[:, 1]

        acc, f1, l_loss = _safe_compute_metrics(self.y_test, probs, preds)
        total_time = time.time() - start_time

        return {
            "algorithm": "Local Isolated NN (Single Node)",
            "accuracy": float(acc),
            "f1_score": float(f1),
            "loss": float(l_loss),
            "time_sec": total_time,
            "network_mb": 0.0,
            "network_note": "No data transmitted — fully local training",
            "privacy_score": 100.0,
            "privacy_note": "PI = 100 (no sharing whatsoever)"
        }

    def train_1d_cnn(self) -> Dict:
        start_time = time.time()
        input_dim = self.X_train.shape[1]

        if HAS_TORCH:
            model = PyTorch1DCNN(input_dim)
            model.train()
            optimizer = optim.Adam(model.parameters(), lr=0.01)
            criterion = nn.CrossEntropyLoss()

            dataset = TensorDataset(torch.tensor(self.X_train, dtype=torch.float32), torch.tensor(self.y_train, dtype=torch.long))
            loader = DataLoader(dataset, batch_size=64, shuffle=True)

            for _ in range(5):
                for bx, by in loader:
                    optimizer.zero_grad()
                    out = model(bx)
                    loss = criterion(out, by)
                    loss.backward()
                    optimizer.step()

            model.eval()
            with torch.no_grad():
                logits = model(torch.tensor(self.X_test, dtype=torch.float32))
                probs = torch.softmax(logits, dim=1)[:, 1].numpy()
                preds = torch.argmax(logits, dim=1).numpy()
        else:
            mlp = MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=20, random_state=self.seed)
            mlp.fit(self.X_train, self.y_train)
            preds = mlp.predict(self.X_test)
            probs = mlp.predict_proba(self.X_test)[:, 1]

        acc, f1, l_loss = _safe_compute_metrics(self.y_test, probs, preds)
        total_time = time.time() - start_time
        raw_bytes = self.X_train.nbytes
        privacy_score = compute_privacy_index(raw_bytes, raw_bytes, "centralized")

        return {
            "algorithm": "1D-CNN (Convolutional NN)",
            "accuracy": float(acc),
            "f1_score": float(f1),
            "loss": float(l_loss),
            "time_sec": total_time,
            "network_mb": round(raw_bytes / (1024 * 1024), 2),
            "network_note": "Full training dataset transmitted to central server",
            "privacy_score": privacy_score,
            "privacy_note": "PI = 100 × (1 − raw_bytes / raw_bytes) → near 0"
        }

    def train_baseline_rf(self) -> Dict:
        start_time = time.time()
        rf = RandomForestClassifier(n_estimators=100, random_state=self.seed)
        rf.fit(self.X_train, self.y_train)
        preds = rf.predict(self.X_test)
        probs = rf.predict_proba(self.X_test)[:, 1]

        acc, f1, l_loss = _safe_compute_metrics(self.y_test, probs, preds)
        total_time = time.time() - start_time

        # RF is centralized — it requires full training data on one machine.
        # Network MB = training data sent to server (same as centralized DNN).
        raw_bytes = self.X_train.nbytes
        privacy_score = compute_privacy_index(raw_bytes, raw_bytes, "centralized")

        return {
            "algorithm": "Baseline Random Forest",
            "accuracy": float(acc),
            "f1_score": float(f1),
            "loss": float(l_loss),
            "time_sec": total_time,
            "network_mb": round(raw_bytes / (1024 * 1024), 2),
            "network_note": "Full training dataset required on central server",
            "privacy_score": privacy_score,
            "privacy_note": "PI = 100 × (1 − raw_bytes / raw_bytes) → near 0"
        }

    # =========================================================================
    # FL Algorithm Variants
    # =========================================================================

    def train_fedprox(self, rounds: int = 10, epochs_per_round: int = 2,
                      lr: float = 0.01, mu: float = 0.01) -> Dict:
        """
        FedProx — Adds proximal regularisation μ‖w−w_global‖² to each client's
        loss, preventing drift on non-IID IoT edge data.
        """
        if not HAS_TORCH:
            return {"algorithm": "FedProx", "accuracy": 0.0, "f1_score": 0.0, "loss": 1.0,
                    "time_sec": 0.0, "network_mb": 0.0, "privacy_score": 97.0}
        start_time = time.time()
        input_dim = self.X_train.shape[1]
        global_model = PyTorchMLP(input_dim)
        global_weights = copy.deepcopy(global_model.state_dict())
        server = GlobalFedProxServer(global_weights, mu=mu)
        param_size = sum(p.numel() * p.element_size() for p in global_model.parameters())
        bytes_transferred = 0
        round_history = []

        for r in range(1, rounds + 1):
            client_weights_list, client_sizes = [], []
            for c_idx, (cX, cy) in enumerate(self.client_partitions):
                if len(cy) == 0:
                    continue
                client = IoTEdgeNodeClient(c_idx, cX, cy, name=f"Node {c_idx+1}")
                w_k, _ = client.train_local_epoch_prox(global_weights, epochs=epochs_per_round, lr=lr, mu=mu)
                client_weights_list.append(w_k)
                client_sizes.append(len(cy))
                bytes_transferred += 2 * param_size

            global_weights = server.aggregate_weights(client_weights_list, client_sizes)
            global_model.load_state_dict(global_weights)
            global_model.eval()
            with torch.no_grad():
                logits = global_model(torch.tensor(self.X_test, dtype=torch.float32))
                probs = torch.softmax(logits, dim=1)[:, 1].numpy()
                preds = torch.argmax(logits, dim=1).numpy()
            acc, f1, l_loss = _safe_compute_metrics(self.y_test, probs, preds)
            round_history.append({"round": r, "accuracy": acc, "f1_score": f1, "loss": l_loss})

        self.final_fl_model = global_model
        total_data_bytes = self.X_train.nbytes
        return {
            "algorithm": "FedProx",
            "accuracy": float(round_history[-1]["accuracy"]),
            "f1_score": float(round_history[-1]["f1_score"]),
            "loss": float(round_history[-1]["loss"]),
            "time_sec": time.time() - start_time,
            "network_mb": round(bytes_transferred / (1024 * 1024), 2),
            "network_note": "Model gradient updates only (proximal-regularised)",
            "privacy_score": compute_privacy_index(bytes_transferred, total_data_bytes, "fl"),
            "privacy_note": "PI = 100 × (1 − model_bytes / training_data_bytes)",
            "history": round_history,
            "mu": mu,
        }

    def train_fednova(self, rounds: int = 10, epochs_per_round: int = 2,
                     lr: float = 0.01) -> Dict:
        """
        FedNova — Normalises client updates by local step count to fix objective
        inconsistency when IoT nodes have unequal dataset sizes.
        """
        if not HAS_TORCH:
            return {"algorithm": "FedNova", "accuracy": 0.0, "f1_score": 0.0, "loss": 1.0,
                    "time_sec": 0.0, "network_mb": 0.0, "privacy_score": 97.0}
        start_time = time.time()
        input_dim = self.X_train.shape[1]
        global_model = PyTorchMLP(input_dim)
        global_weights = copy.deepcopy(global_model.state_dict())
        server = GlobalFedNovaServer(global_weights)
        param_size = sum(p.numel() * p.element_size() for p in global_model.parameters())
        bytes_transferred = 0
        round_history = []

        for r in range(1, rounds + 1):
            finals, initials, sizes, steps = [], [], [], []
            for c_idx, (cX, cy) in enumerate(self.client_partitions):
                if len(cy) == 0:
                    continue
                client = IoTEdgeNodeClient(c_idx, cX, cy, name=f"Node {c_idx+1}")
                w_final, w_init, n_steps, _ = client.train_local_epoch_with_step_count(
                    global_weights, epochs=epochs_per_round, lr=lr
                )
                finals.append(w_final)
                initials.append(w_init)
                sizes.append(len(cy))
                steps.append(n_steps)
                bytes_transferred += 2 * param_size

            global_weights = server.aggregate_weights(finals, initials, sizes, steps)
            global_model.load_state_dict(global_weights)
            global_model.eval()
            with torch.no_grad():
                logits = global_model(torch.tensor(self.X_test, dtype=torch.float32))
                probs = torch.softmax(logits, dim=1)[:, 1].numpy()
                preds = torch.argmax(logits, dim=1).numpy()
            acc, f1, l_loss = _safe_compute_metrics(self.y_test, probs, preds)
            round_history.append({"round": r, "accuracy": acc, "f1_score": f1, "loss": l_loss})

        self.final_fl_model = global_model
        total_data_bytes = self.X_train.nbytes
        return {
            "algorithm": "FedNova",
            "accuracy": float(round_history[-1]["accuracy"]),
            "f1_score": float(round_history[-1]["f1_score"]),
            "loss": float(round_history[-1]["loss"]),
            "time_sec": time.time() - start_time,
            "network_mb": round(bytes_transferred / (1024 * 1024), 2),
            "network_note": "Normalised gradient updates (per-step)",
            "privacy_score": compute_privacy_index(bytes_transferred, total_data_bytes, "fl"),
            "privacy_note": "PI = 100 × (1 − model_bytes / training_data_bytes)",
            "history": round_history,
        }

    def train_fedadam(self, rounds: int = 10, epochs_per_round: int = 2,
                     lr: float = 0.01, server_lr: float = 0.01) -> Dict:
        """
        FedAdam — Applies server-side Adam optimiser on aggregated pseudo-gradients
        for faster convergence and better handling of non-IID noise.
        """
        if not HAS_TORCH:
            return {"algorithm": "FedAdam", "accuracy": 0.0, "f1_score": 0.0, "loss": 1.0,
                    "time_sec": 0.0, "network_mb": 0.0, "privacy_score": 97.0}
        start_time = time.time()
        input_dim = self.X_train.shape[1]
        global_model = PyTorchMLP(input_dim)
        global_weights = copy.deepcopy(global_model.state_dict())
        server = GlobalFedAdamServer(global_weights, server_lr=server_lr)
        param_size = sum(p.numel() * p.element_size() for p in global_model.parameters())
        bytes_transferred = 0
        round_history = []

        for r in range(1, rounds + 1):
            client_weights_list, client_sizes = [], []
            for c_idx, (cX, cy) in enumerate(self.client_partitions):
                if len(cy) == 0:
                    continue
                client = IoTEdgeNodeClient(c_idx, cX, cy, name=f"Node {c_idx+1}")
                w_k, _ = client.train_local_epoch(global_weights, epochs=epochs_per_round, lr=lr)
                client_weights_list.append(w_k)
                client_sizes.append(len(cy))
                bytes_transferred += 2 * param_size

            global_weights = server.aggregate_weights(client_weights_list, client_sizes)
            global_model.load_state_dict(global_weights)
            global_model.eval()
            with torch.no_grad():
                logits = global_model(torch.tensor(self.X_test, dtype=torch.float32))
                probs = torch.softmax(logits, dim=1)[:, 1].numpy()
                preds = torch.argmax(logits, dim=1).numpy()
            acc, f1, l_loss = _safe_compute_metrics(self.y_test, probs, preds)
            round_history.append({"round": r, "accuracy": acc, "f1_score": f1, "loss": l_loss})

        self.final_fl_model = global_model
        total_data_bytes = self.X_train.nbytes
        return {
            "algorithm": "FedAdam",
            "accuracy": float(round_history[-1]["accuracy"]),
            "f1_score": float(round_history[-1]["f1_score"]),
            "loss": float(round_history[-1]["loss"]),
            "time_sec": time.time() - start_time,
            "network_mb": round(bytes_transferred / (1024 * 1024), 2),
            "network_note": "Server-side Adam on aggregated pseudo-gradients",
            "privacy_score": compute_privacy_index(bytes_transferred, total_data_bytes, "fl"),
            "privacy_note": "PI = 100 × (1 − model_bytes / training_data_bytes)",
            "history": round_history,
            "server_lr": server_lr,
        }

    def train_fedmedian(self, rounds: int = 10, epochs_per_round: int = 2,
                       lr: float = 0.01) -> Dict:
        """
        FedMedian — Coordinate-wise median aggregation. Robust against Byzantine
        (poisoned/compromised) IoT edge clients.
        """
        if not HAS_TORCH:
            return {"algorithm": "FedMedian", "accuracy": 0.0, "f1_score": 0.0, "loss": 1.0,
                    "time_sec": 0.0, "network_mb": 0.0, "privacy_score": 97.0}
        start_time = time.time()
        input_dim = self.X_train.shape[1]
        global_model = PyTorchMLP(input_dim)
        global_weights = copy.deepcopy(global_model.state_dict())
        server = GlobalFedMedianServer(global_weights)
        param_size = sum(p.numel() * p.element_size() for p in global_model.parameters())
        bytes_transferred = 0
        round_history = []

        for r in range(1, rounds + 1):
            client_weights_list, client_sizes = [], []
            for c_idx, (cX, cy) in enumerate(self.client_partitions):
                if len(cy) == 0:
                    continue
                client = IoTEdgeNodeClient(c_idx, cX, cy, name=f"Node {c_idx+1}")
                w_k, _ = client.train_local_epoch(global_weights, epochs=epochs_per_round, lr=lr)
                client_weights_list.append(w_k)
                client_sizes.append(len(cy))
                bytes_transferred += 2 * param_size

            global_weights = server.aggregate_weights(client_weights_list, client_sizes)
            global_model.load_state_dict(global_weights)
            global_model.eval()
            with torch.no_grad():
                logits = global_model(torch.tensor(self.X_test, dtype=torch.float32))
                probs = torch.softmax(logits, dim=1)[:, 1].numpy()
                preds = torch.argmax(logits, dim=1).numpy()
            acc, f1, l_loss = _safe_compute_metrics(self.y_test, probs, preds)
            round_history.append({"round": r, "accuracy": acc, "f1_score": f1, "loss": l_loss})

        self.final_fl_model = global_model
        total_data_bytes = self.X_train.nbytes
        return {
            "algorithm": "FedMedian",
            "accuracy": float(round_history[-1]["accuracy"]),
            "f1_score": float(round_history[-1]["f1_score"]),
            "loss": float(round_history[-1]["loss"]),
            "time_sec": time.time() - start_time,
            "network_mb": round(bytes_transferred / (1024 * 1024), 2),
            "network_note": "Coordinate-wise median (Byzantine-robust)",
            "privacy_score": compute_privacy_index(bytes_transferred, total_data_bytes, "fl"),
            "privacy_note": "PI = 100 × (1 − model_bytes / training_data_bytes)",
            "history": round_history,
        }

    def run_full_fl_benchmark(self, rounds: int = 5) -> List[Dict]:
        """
        Runs all 5 FL algorithms on the SAME dataset split and returns
        a comparison list sorted by accuracy (descending).

        Use this to identify the best FL algorithm for your IoT threat
        detection task and justify the choice in your thesis.
        """
        results = []
        algorithms = [
            ("FedAvg",    lambda: self.train_federated_fl(rounds=rounds)),
            ("FedProx",   lambda: self.train_fedprox(rounds=rounds)),
            ("FedNova",   lambda: self.train_fednova(rounds=rounds)),
            ("FedAdam",   lambda: self.train_fedadam(rounds=rounds)),
            ("FedMedian", lambda: self.train_fedmedian(rounds=rounds)),
        ]
        for name, train_fn in algorithms:
            print(f"[FL Benchmark] Running {name}...")
            try:
                res = train_fn()
                results.append(res)
            except Exception as e:
                results.append({
                    "algorithm": name, "accuracy": 0.0, "f1_score": 0.0,
                    "loss": 1.0, "time_sec": 0.0, "network_mb": 0.0,
                    "privacy_score": 0.0, "error": str(e),
                })
        results.sort(key=lambda r: r.get("accuracy", 0.0), reverse=True)
        return results

    def run_full_benchmark(self, fl_rounds: int = 10) -> List[Dict]:
        print("Running Federated Learning (FedAvg)...")
        fl_res = self.train_federated_fl(rounds=fl_rounds)

        print("Running Centralized Deep NN...")
        dnn_res = self.train_centralized_dnn()

        print("Running Local Isolated NN...")
        loc_res = self.train_local_isolated_nn()

        print("Running 1D-CNN...")
        cnn_res = self.train_1d_cnn()

        print("Running Baseline Random Forest...")
        rf_res = self.train_baseline_rf()

        return [fl_res, dnn_res, loc_res, cnn_res, rf_res]

    def evaluate_on_individual_attack_csvs(self, sample_per_file: int = 2000) -> List[Dict]:
        """
        Evaluates the trained FL model individually against each specific raw attack CSV file.

        IMPORTANT: Uses load_mixed_attack_test() to create a 50/50 attack+normal test set
        for each file. This prevents the trivial '100% accuracy' artifact that occurs when
        test sets contain ONLY attack traffic (y=1 everywhere → any model predicting
        'always attack' scores 100%).

        Returns per-attack: accuracy, precision, recall, f1, confusion_matrix, ROC data.
        """
        from layer1_telemetry.data_loader import (
            list_available_raw_attack_files, load_mixed_attack_test
        )

        raw_files = list_available_raw_attack_files()
        csv_files = [f for f in raw_files if f["type"] == "CSV Log"]

        results = []
        for file_info in csv_files:
            fname = file_info["name"]
            # Mixed 50/50 test set: attack + normal traffic
            X_mix, y_mix, mix_meta = load_mixed_attack_test(
                fname, sample_size=sample_per_file, normal_fraction=0.5, seed=self.seed
            )

            if len(y_mix) == 0:
                continue

            X_scaled = self.scaler.transform(X_mix)

            if hasattr(self, "final_fl_model") and self.final_fl_model is not None:
                if HAS_TORCH and isinstance(self.final_fl_model, torch.nn.Module):
                    self.final_fl_model.eval()
                    with torch.no_grad():
                        logits = self.final_fl_model(torch.tensor(X_scaled, dtype=torch.float32))
                        probs = torch.softmax(logits, dim=1)[:, 1].numpy()
                        preds = torch.argmax(logits, dim=1).numpy()
                else:
                    preds = self.final_fl_model.predict(X_scaled)
                    probs = self.final_fl_model.predict_proba(X_scaled)[:, 1]
            else:
                preds = np.ones(len(y_mix), dtype=int)
                probs = np.full(len(y_mix), 0.75)

            acc, f1, l_loss = _safe_compute_metrics(y_mix, probs, preds)
            prec = float(precision_score(y_mix, preds, zero_division=0))
            rec  = float(recall_score(y_mix, preds, zero_division=0))

            cm = confusion_matrix(y_mix, preds, labels=[0, 1]).tolist()
            try:
                fpr, tpr, _ = roc_curve(y_mix, probs, pos_label=1)
                roc_auc = float(auc(fpr, tpr))
                roc_data = {"fpr": fpr.tolist(), "tpr": tpr.tolist(), "auc": roc_auc}
            except Exception:
                roc_data = {"fpr": [], "tpr": [], "auc": 0.0}

            clean_name = fname.replace("_attack.csv", "").replace("_", " ").replace("Attacks", "").strip()

            results.append({
                "attack_file": fname,
                "clean_name": clean_name.title(),
                "samples_tested": mix_meta.get("total", len(y_mix)),
                "attack_samples": mix_meta.get("attack_samples", 0),
                "normal_samples": mix_meta.get("normal_samples", 0),
                "test_composition": "50% attack + 50% normal",
                "accuracy_pct": round(acc * 100, 2),
                "precision_pct": round(prec * 100, 2),
                "recall_pct": round(rec * 100, 2),
                "f1_score_pct": round(f1 * 100, 2),
                "avg_threat_probability": round(float(probs.mean()), 3),
                "confusion_matrix": cm,
                "roc": roc_data,
                "status": "PASS" if acc >= 0.80 else "WARN"
            })

        return results

    def predict_threat_probability(self, sample_features: np.ndarray) -> float:
        scaled_x = self.scaler.transform(sample_features.reshape(1, -1))

        if hasattr(self, "final_fl_model") and self.final_fl_model is not None:
            if HAS_TORCH and isinstance(self.final_fl_model, torch.nn.Module):
                self.final_fl_model.eval()
                with torch.no_grad():
                    logits = self.final_fl_model(torch.tensor(scaled_x, dtype=torch.float32))
                    probs = torch.softmax(logits, dim=1)[0, 1].item()
                    return float(probs)
            else:
                probs = self.final_fl_model.predict_proba(scaled_x)[0, 1]
                return float(probs)

        return 0.75


class FederatedThreatDetector:
    def __init__(self, sample_size: int = 15_000, seed: int = 42):
        self.fl_manager = FederatedEdgeManager(sample_size=sample_size, seed=seed)
        self.fl_results = self.fl_manager.train_federated_fl(rounds=8)

    def score_resource(self, resource: dict) -> float:
        raw_signal = resource.get("raw_signal", {})
        feats = np.array([
            raw_signal.get("failed_logins", 0.0),
            raw_signal.get("unusual_outbound_bytes", 0.0),
            raw_signal.get("privilege_escalation_attempts", 0.0)
        ] + [0.0] * (self.fl_manager.X_train.shape[1] - 3))
        
        return self.fl_manager.predict_threat_probability(feats)

    def score_scenario(self, scenario: dict) -> Dict[str, float]:
        return {r["id"]: self.score_resource(r) for r in scenario["resources"]}
