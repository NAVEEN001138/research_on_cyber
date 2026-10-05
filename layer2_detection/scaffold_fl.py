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
from typing import Dict, List, Tuple, Optional


class SCAFFOLDClient:
    """SCAFFOLD Local Edge Node Client with Control Variate Corrections."""
    def __init__(self, client_id: int, X_local: np.ndarray, y_local: np.ndarray):
        self.client_id = client_id
        self.X_local = X_local
        self.y_local = y_local
        self.sample_count = len(y_local)
        self.c_client = None  # Client control variate dict (named_parameters only)

    def train_scaffold_round(
        self,
        global_model: nn.Module,
        c_global: Dict[str, torch.Tensor],
        local_steps: int = 20,
        lr: float = 0.01,
        batch_size: int = 32,
        epochs: Optional[int] = None
    ) -> Tuple[Dict[str, torch.Tensor], Dict[str, torch.Tensor], float]:
        if self.sample_count == 0:
            return copy.deepcopy(global_model.state_dict()), {}, 0.0

        local_model = copy.deepcopy(global_model)
        local_model.train()

        # Initialise client control variate with named_parameters() keys (Option II)
        if self.c_client is None:
            self.c_client = {
                name: torch.zeros_like(p.data, dtype=torch.float32)
                for name, p in local_model.named_parameters()
            }

        # Optimizer: plain SGD (no momentum)
        optimizer = optim.SGD(local_model.parameters(), lr=lr)

        dataset = TensorDataset(
            torch.tensor(self.X_local, dtype=torch.float32),
            torch.tensor(self.y_local, dtype=torch.long)
        )
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        loader_iter = iter(loader)

        total_loss = 0.0
        steps = local_steps

        for _ in range(steps):
            try:
                bx, by = next(loader_iter)
            except StopIteration:
                loader_iter = iter(loader)
                bx, by = next(loader_iter)

            optimizer.zero_grad()
            out = local_model(bx)
            loss = F.cross_entropy(out, by)
            loss.backward()

            # SCAFFOLD Control Variate Gradient Correction: g = g - c_i + c
            with torch.no_grad():
                for name, param in local_model.named_parameters():
                    if param.grad is not None and name in self.c_client and name in c_global:
                        param.grad = param.grad - self.c_client[name] + c_global[name]

            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / max(1, steps)
        local_weights = copy.deepcopy(local_model.state_dict())

        # Update client control variate using Option II (parameters only):
        # c_i⁺ = c_i − c + (w_global − w_local) / (K · lr)
        # Δc_i = c_i⁺ − c_i
        global_params = {name: p.data for name, p in global_model.named_parameters()}
        local_params = {name: p.data for name, p in local_model.named_parameters()}

        delta_c_client = {}
        c_client_new = {}
        denom = float(steps * lr)

        for name in self.c_client.keys():
            c_i = self.c_client[name]
            c = c_global[name]
            w_g = global_params[name]
            w_l = local_params[name]

            c_i_plus = c_i - c + (w_g - w_l) / denom
            delta_c = c_i_plus - c_i
            c_client_new[name] = c_i_plus.clone().detach()
            delta_c_client[name] = delta_c.clone().detach()

        self.c_client = c_client_new
        return local_weights, delta_c_client, avg_loss


class SCAFFOLDServer:
    """SCAFFOLD Central Server with Global Control Variate Maintenance."""
    def __init__(self, global_model: nn.Module, num_total_clients: int = 20):
        self.global_model = copy.deepcopy(global_model)
        self.num_total_clients = max(1, num_total_clients)
        # Initialise c with named_parameters() keys, not state_dict() keys
        self.c_global = {
            name: torch.zeros_like(param.data, dtype=torch.float32)
            for name, param in global_model.named_parameters()
        }

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

        # 2. Update Global Control Variate: c <- c + (1/N) * sum_{i in S} delta_c_i
        # where N is total number of clients
        if num_clients > 0 and len(client_delta_c) > 0:
            scale = 1.0 / float(self.num_total_clients)
            for k in self.c_global.keys():
                delta_sum = torch.zeros_like(self.c_global[k], dtype=torch.float32)
                for i in range(num_clients):
                    if k in client_delta_c[i] and client_delta_c[i][k].is_floating_point():
                        delta_sum += client_delta_c[i][k].float()
                self.c_global[k] = self.c_global[k] + scale * delta_sum

        return copy.deepcopy(self.global_model.state_dict())


