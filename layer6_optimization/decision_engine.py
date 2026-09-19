"""
=============================================================================
LAYER 6: DECISION OPTIMIZATION ENGINE
Module: decision_engine.py
-----------------------------------------------------------------------------
Problem Solved:
  Formulates incident response action selection as a Quadratic Unconstrained
  Binary Optimization (QUBO) problem and solves it using Qiskit QAOA or NumPy
  eigensolvers. Solves optimal action selection under resource, budget,
  confidence, policy, and decision stability constraints.

  Integrated Improvements:
    - Layer 4 Confidence weighting (threat score * confidence)
    - Layer 5 Adaptive constraints (feasible actions, forbidden/required actions)
    - Action Switching Penalty (prevents action oscillation between rounds)

Inputs:  Scenario, threat scores (s_i), max budget, constraints, confidences.
Outputs: Quantum objective value, optimal action plan dictionary, and binary variable mapping.
=============================================================================
"""

import math
import numpy as np
from typing import Dict, List, Tuple, Optional


try:
    from qiskit_optimization import QuadraticProgram
    from qiskit_optimization.algorithms import MinimumEigenOptimizer
    HAS_QISKIT_OPT = True
except ImportError:
    HAS_QISKIT_OPT = False
    class QuadraticProgram:
        def __init__(self, name: str = ""):
            self.name = name
            self.variables = []
        def binary_var(self, name: str):
            self.variables.append(name)
        def minimize(self, linear=None, quadratic=None):
            pass
    class MinimumEigenOptimizer:
        def __init__(self, min_eigen_solver=None):
            pass
        def solve(self, problem):
            pass

try:
    from qiskit_algorithms import QAOA, NumPyMinimumEigensolver
    from qiskit_algorithms.optimizers import COBYLA
    from qiskit_aer.primitives import Sampler as AerSampler
    HAS_QISKIT_ALG = True
except ImportError:
    HAS_QISKIT_ALG = False


from config import ACTIONS, COST_WEIGHTS, MAX_BUDGET, LAMBDA_PENALTY, QAOA_MAXITER, QAOA_REPS
from layer5_constraints.adaptive_constraints import OptimizationConstraints
from layer4_confidence.confidence_evaluator import ConfidenceScores


def action_cost(resource_type: str, action: str, cost_weights=COST_WEIGHTS) -> float:
    w1, w2, w3 = cost_weights
    base = ACTIONS.get(action, 0.1)

    if action == "isolate":
        business_impact = 0.9 if resource_type == "rds_database" else 0.5
        compliance_impact = 0.1
        downtime = 0.8
    elif action == "rotate_credentials":
        business_impact = 0.2
        compliance_impact = 0.1
        downtime = 0.1
    elif action == "block_ip":
        business_impact = 0.3
        compliance_impact = 0.2
        downtime = 0.05
    elif action == "disable_user":
        business_impact = 0.4
        compliance_impact = 0.3
        downtime = 0.2
    elif action == "snapshot_backup":
        business_impact = 0.1
        compliance_impact = 0.05
        downtime = 0.1
    elif action == "monitor":
        business_impact = 0.01
        compliance_impact = 0.0
        downtime = 0.0
    elif action == "increase_logging":
        business_impact = 0.05
        compliance_impact = 0.0
        downtime = 0.0
    else:
        business_impact = 0.2
        compliance_impact = 0.1
        downtime = 0.1

    return w1 * business_impact + w2 * compliance_impact + w3 * downtime


CORE_ACTIONS = ["isolate", "rotate_credentials", "block_ip", "disable_user"]


def build_qubo(
    scenario: dict,
    threat_scores: dict,
    max_budget: float = MAX_BUDGET,
    hard_budget: bool = False,
    action_subset: List[str] = None,
    constraints: Optional[OptimizationConstraints] = None,
    confidences: Optional[Dict[str, ConfidenceScores]] = None,
) -> Tuple[QuadraticProgram, dict]:
    qp = QuadraticProgram("incident_response")
    var_lookup = {}
    default_actions = action_subset or CORE_ACTIONS

    # Build binary decision variables per resource
    for r in scenario["resources"]:
        rid = r["id"]
        allowed = (
            constraints.feasible_actions.get(rid, default_actions)
            if constraints and constraints.feasible_actions
            else default_actions
        )
        allowed = [a for a in allowed if a in default_actions]
        for k in allowed:
            name = f"x_{rid}_{k}"
            qp.binary_var(name)
            var_lookup[(rid, k)] = name

    linear_terms = {}
    prev_plan = constraints.previous_plan if constraints else {}
    switching_pen = constraints.switching_penalty if constraints else 0.0

    for r in scenario["resources"]:
        rid = r["id"]
        s_i = threat_scores.get(rid, 0.5)
        
        # Incorporate Layer 4 Confidence weighting
        c_i = confidences[rid].overall_confidence if confidences and rid in confidences else 1.0
        effective_threat = s_i * c_i

        allowed = (
            constraints.feasible_actions.get(rid, default_actions)
            if constraints and constraints.feasible_actions
            else default_actions
        )
        allowed = [a for a in allowed if a in default_actions]

        for k in allowed:
            v = var_lookup[(rid, k)]
            r_type = r["type"]
            c_cost = action_cost(r_type, k)

            eff = ACTIONS.get(k, 0.5)
            linear_terms[v] = linear_terms.get(v, 0.0) - (effective_threat * eff) + (0.3 * c_cost)

            if prev_plan and rid in prev_plan:
                if prev_plan[rid] != k:
                    linear_terms[v] = linear_terms.get(v, 0.0) + switching_pen

    quadratic_terms = {}

    # Constraint 1: One-hot action constraint per resource
    for r in scenario["resources"]:
        rid = r["id"]
        allowed = (
            constraints.feasible_actions.get(rid, default_actions)
            if constraints and constraints.feasible_actions
            else default_actions
        )
        allowed = [a for a in allowed if a in default_actions]
        res_vars = [var_lookup[(rid, k)] for k in allowed if (rid, k) in var_lookup]

        for v in res_vars:
            linear_terms[v] = linear_terms.get(v, 0.0) - LAMBDA_PENALTY

        for idx1 in range(len(res_vars)):
            for idx2 in range(idx1 + 1, len(res_vars)):
                pair = (res_vars[idx1], res_vars[idx2])
                quadratic_terms[pair] = quadratic_terms.get(pair, 0.0) + 2 * LAMBDA_PENALTY

    # Constraint 2: Budget Constraint (Soft Quadratic Penalty)
    if not hard_budget and max_budget > 0:
        B = max_budget
        quad_penalty = LAMBDA_PENALTY / (B ** 2) if B > 0 else LAMBDA_PENALTY

        all_vars = []
        for r in scenario["resources"]:
            rid = r["id"]
            allowed = (
                constraints.feasible_actions.get(rid, default_actions)
                if constraints and constraints.feasible_actions
                else default_actions
            )
            allowed = [a for a in allowed if a in default_actions]
            for k in allowed:
                if (rid, k) in var_lookup:
                    all_vars.append((rid, k))

        for rid, k in all_vars:
            v1 = var_lookup[(rid, k)]
            r_type = next(res["type"] for res in scenario["resources"] if res["id"] == rid)
            c1 = action_cost(r_type, k)
            linear_terms[v1] = linear_terms.get(v1, 0.0) - 2 * quad_penalty * B * c1

        for idx1 in range(len(all_vars)):
            r1_id, k1 = all_vars[idx1]
            v1 = var_lookup[(r1_id, k1)]
            r1_type = next(res["type"] for res in scenario["resources"] if res["id"] == r1_id)
            c1 = action_cost(r1_type, k1)

            for idx2 in range(idx1, len(all_vars)):
                r2_id, k2 = all_vars[idx2]
                v2 = var_lookup[(r2_id, k2)]
                r2_type = next(res["type"] for res in scenario["resources"] if res["id"] == r2_id)
                c2 = action_cost(r2_type, k2)

                if idx1 == idx2:
                    linear_terms[v1] = linear_terms.get(v1, 0.0) + quad_penalty * (c1 ** 2)
                else:
                    pair = (v1, v2) if v1 < v2 else (v2, v1)
                    quadratic_terms[pair] = quadratic_terms.get(pair, 0.0) + 2 * quad_penalty * c1 * c2

    qp.minimize(linear=linear_terms, quadratic=quadratic_terms)

    # Optional Hard Inequality Constraint
    if hard_budget:
        budget_linear = {}
        for r in scenario["resources"]:
            rid = r["id"]
            allowed = (
                constraints.feasible_actions.get(rid, default_actions)
                if constraints and constraints.feasible_actions
                else default_actions
            )
            allowed = [a for a in allowed if a in default_actions]
            for k in allowed:
                if (rid, k) in var_lookup:
                    var = var_lookup[(rid, k)]
                    budget_linear[var] = action_cost(r["type"], k)
        qp.linear_constraint(linear=budget_linear, sense="<=", rhs=max_budget, name="hard_budget_limit")

    return qp, var_lookup


MAX_QAOA_VARS = 12


def solve_quantum(qp: QuadraticProgram, method: str = "numpy", seed: int = 42) -> dict:
    n_vars = len(qp.variables) if hasattr(qp, "variables") else 0
    if n_vars > MAX_QAOA_VARS:
        raise ValueError(f"QAOA simulator limit: {n_vars} vars > {MAX_QAOA_VARS}")

    if method == "numpy":
        solver = MinimumEigenOptimizer(NumPyMinimumEigensolver())
    elif method == "qaoa":
        optimizer = COBYLA(maxiter=QAOA_MAXITER)
        try:
            from qiskit.primitives import StatevectorSampler
            sampler = StatevectorSampler(default_shots=2048)
        except ImportError:
            sampler = AerSampler()
        qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=QAOA_REPS)
        solver = MinimumEigenOptimizer(qaoa)
    else:
        raise ValueError(f"Unknown solver method: {method}")

    result = solver.solve(qp)
    return {
        "x": result.x,
        "fval": result.fval,
        "variable_names": [v.name for v in qp.variables],
        "status": str(result.status),
    }



def decode_action_plan(qp: QuadraticProgram, var_lookup: dict, solve_result: dict) -> dict:
    x = solve_result["x"]
    var_names = solve_result["variable_names"]
    val_map = dict(zip(var_names, x))
    plan = {}

    resources = list(dict.fromkeys(r for (r, k) in var_lookup.keys()))
    for r in resources:
        best_action = None
        best_val = -1.0
        for (res_id, k), var_name in var_lookup.items():
            if res_id == r and var_name in val_map:
                if val_map[var_name] > best_val:
                    best_val = val_map[var_name]
                    best_action = k
        plan[r] = best_action or "monitor"

    return plan


def calculate_objective(plan: dict, scenario: dict, threat_scores: dict) -> float:
    val = 0.0
    for r in scenario["resources"]:
        rid = r["id"]
        action = plan.get(rid)
        if action:
            s_i = threat_scores.get(rid, 0.0)
            beta_k = ACTIONS.get(action, 0.0)
            c_ik = action_cost(r["type"], action)
            val += (-beta_k * s_i + c_ik)
    return val


def calculate_total_cost(plan: dict, scenario: dict) -> float:
    total = 0.0
    for r in scenario["resources"]:
        rid = r["id"]
        action = plan.get(rid)
        if action:
            total += action_cost(r["type"], action)
    return total


def is_budget_feasible(plan: dict, scenario: dict, max_budget: float) -> bool:
    return calculate_total_cost(plan, scenario) <= max_budget
