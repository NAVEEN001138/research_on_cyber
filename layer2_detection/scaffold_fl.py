"""
=============================================================================
SCAFFOLD FEDERATED LEARNING ALGORITHM
Module: scaffold_fl.py
-----------------------------------------------------------------------------
Implements SCAFFOLD (Stochastic Controlled Averaging for Federated Learning).
Uses client and server control variates (c_k and c) to correct client drift
caused by non-IID data distribution skew across heterogeneous IoT Edge devices.
=============================================================================
"""

import copy
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from typing import Dict, List, Tuple


class SCAFFOLDClient:
    """SCAFFOLD Local Edge Node Client with Control Variate Corrections."""
    def __init__(self, client_id: int, X_local: np.ndarray, y_local: np.ndarray):
        self.client_id = client_id
        self.X_local = X_local
        self.y_local = y_local
        self.sample_count = len(y_local)
        self.c_client = None  # Client control variate dict

    def train_scaffold_round(
        self,
        global_model: nn.Module,
        c_global: Dict[str, torch.Tensor],
        epochs: int = 2,
        lr: float = 0.01,
        batch_size: int = 32
    ) -> Tuple[Dict[str, torch.Tensor], Dict[str, torch.Tensor], float]:
        if self.sample_count == 0:
            return global_model.state_dict(), {}, 0.0

        local_model = copy.deepcopy(global_model)
        local_model.train()
        global_weights = copy.deepcopy(global_model.state_dict())

        # Initialize client control variate if first round
        if self.c_client is None:
            self.c_client = {k: torch.zeros_like(v, dtype=torch.float32) for k, v in global_weights.items()}

        optimizer = optim.SGD(local_model.parameters(), lr=lr)


        dataset = TensorDataset(
            torch.tensor(self.X_local, dtype=torch.float32),
            torch.tensor(self.y_local, dtype=torch.long)
        )
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        total_loss = 0.0
        steps = 0

        for _ in range(epochs):
            for bx, by in loader:
                optimizer.zero_grad()
                out = local_model(bx)
                loss = F.cross_entropy(out, by)
                loss.backward()

                # SCAFFOLD Control Variate Gradient Correction: g = g - c_k + c
                with torch.no_grad():
                    for name, param in local_model.named_parameters():
                        if param.grad is not None and name in self.c_client:
                            param.grad = param.grad - self.c_client[name] + c_global[name]

                optimizer.step()
                total_loss += loss.item()
                steps += 1

        avg_loss = total_loss / max(1, steps)
        local_weights = local_model.state_dict()

        # Update client control variate c_client_new = c_client - c_global + 1/(K*lr) * (w_global - w_local)
        K_steps = max(1, steps)
        c_client_new = {}
        delta_c_client = {}

        for k in global_weights.keys():
            c_c = self.c_client[k]
            c_g = c_global[k]
            w_g = global_weights[k]
            w_l = local_weights[k]

            c_new = c_c - c_g + (w_g - w_l) / (K_steps * lr)
            delta_c = c_new - c_c

            c_client_new[k] = c_new
            delta_c_client[k] = delta_c

        self.c_client = c_client_new
        return copy.deepcopy(local_weights), delta_c_client, avg_loss


class SCAFFOLDServer:
    """SCAFFOLD Central Server with Global Control Variate Maintenance."""
    def __init__(self, global_model: nn.Module):
        self.global_model = copy.deepcopy(global_model)
        self.c_global = {k: torch.zeros_like(v, dtype=torch.float32) for k, v in global_model.state_dict().items()}

    def aggregate(
        self,
        client_weights: List[Dict[str, torch.Tensor]],
        client_delta_c: List[Dict[str, torch.Tensor]],
        sample_counts: List[int],
        trust_weights: Optional[List[float]] = None
    ):
        num_clients = len(client_weights)
        if num_clients == 0:
            return copy.deepcopy(self.global_model.state_dict())

        # Compute effective aggregation weights combining sample counts and trust scores
        if trust_weights is not None and len(trust_weights) == num_clients:
            raw_weights = [sample_counts[i] * max(0.0, float(trust_weights[i])) for i in range(num_clients)]
            total_w = sum(raw_weights)
            if total_w > 0:
                agg_weights = [w / total_w for w in raw_weights]
            else:
                agg_weights = [1.0 / num_clients for _ in range(num_clients)]
        else:
            total_samples = sum(sample_counts)
            agg_weights = [sample_counts[i] / total_samples for i in range(num_clients)]

        # 1. Update Global Model Weights
        new_global_weights = {}
        for k in client_weights[0].keys():
            if not client_weights[0][k].is_floating_point():
                new_global_weights[k] = client_weights[0][k].clone()
                continue
            weight_sum = torch.zeros_like(client_weights[0][k], dtype=torch.float32)
            for i in range(num_clients):
                weight_sum += agg_weights[i] * client_weights[i][k].float()
            new_global_weights[k] = weight_sum.to(client_weights[0][k].dtype)

        self.global_model.load_state_dict(new_global_weights)

        # 2. Update Global Control Variate c_global = c_global + sum(agg_weights[i] * delta_c_k)
        if num_clients > 0 and len(client_delta_c) > 0:
            for k in self.c_global.keys():
                if not self.c_global[k].is_floating_point():
                    continue
                delta_sum = torch.zeros_like(self.c_global[k], dtype=torch.float32)
                for i in range(num_clients):
                    if k in client_delta_c[i] and client_delta_c[i][k].is_floating_point():
                        delta_sum += agg_weights[i] * client_delta_c[i][k].float()
                self.c_global[k] = self.c_global[k] + delta_sum

        return copy.deepcopy(self.global_model.state_dict())

