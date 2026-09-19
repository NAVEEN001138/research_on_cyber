# -*- coding: utf-8 -*-
"""
Full 9-Layer System Verification
Tests every layer individually then runs the integrated pipeline.
Run: python verify_system.py
"""
import sys
import time
import traceback
import os
import math
import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

PASS = "[PASS]"
FAIL = "[FAIL]"
results = {}

print("=" * 65)
print("  CLOUD GUARDIAN -- 9-LAYER SYSTEM VERIFICATION")
print("=" * 65)

# ─── LAYER 1: Telemetry ───────────────────────────────────────────
print("\n[ LAYER 1 ]  Telemetry & Data Ingestion")
try:
    from layer1_telemetry.fake_incident import SCENARIOS, SCENARIO_PROFILES
    assert "ddos_flood" in SCENARIOS and "port_scan_recon" in SCENARIOS
    assert len(SCENARIOS["ddos_flood"]["resources"]) == 5
    assert len(SCENARIOS["port_scan_recon"]["resources"]) == 4
    print(f"  Scenarios loaded   : {list(SCENARIOS.keys())}")

    from layer1_telemetry.data_loader import load_edge_iiot_dataset
    t0 = time.time()
    X, y, df, meta = load_edge_iiot_dataset(sample_size=2000)
    elapsed = time.time() - t0
    assert X is not None and len(X) > 0
    print(f"  Dataset loaded     : {len(X)} samples x {X.shape[1]} features  ({elapsed:.2f}s)")
    print(f"  Attack classes     : {len(meta.get('attack_counts', {}))} types")
    print(f"  {PASS} Layer 1 OK")
    results["Layer 1: Telemetry"] = PASS
except Exception as e:
    print(f"  {FAIL}: {e}")
    traceback.print_exc()
    results["Layer 1: Telemetry"] = FAIL

# ─── LAYER 2: Federated Detection ────────────────────────────────
print("\n[ LAYER 2 ]  Federated ML Threat Detection")
try:
    scenario = SCENARIOS["port_scan_recon"]

    from layer2_detection.detector import ThreatDetector
    det = ThreatDetector(verbose=False)
    scores = det.score_scenario(scenario)
    assert len(scores) == len(scenario["resources"])
    assert all(0.0 <= v <= 1.0 for v in scores.values())
    print(f"  Classical scores   : { {k[-5:]: round(v,3) for k,v in scores.items()} }")

    from layer2_detection.federated_detector import FederatedEdgeManager
    t0 = time.time()
    mgr = FederatedEdgeManager(sample_size=2000, num_clients=3, seed=42)
    fl_res = mgr.train_federated_fl(rounds=2)
    elapsed = time.time() - t0
    assert "accuracy" in fl_res
    print(f"  FL model accuracy  : {fl_res['accuracy']:.4f}  (f1={fl_res['f1_score']:.4f}, loss={fl_res['loss']:.4f})")
    print(f"  FL training time   : {elapsed:.2f}s  ({mgr.num_clients} clients)")
    print(f"  {PASS} Layer 2 OK")
    results["Layer 2: FL Detection"] = PASS
except Exception as e:
    print(f"  {FAIL}: {e}")
    traceback.print_exc()
    results["Layer 2: FL Detection"] = FAIL
    # Guarantee scores exist for downstream tests
    from layer2_detection.detector import ThreatDetector
    det = ThreatDetector(verbose=False)
    scores = det.score_scenario(SCENARIOS["port_scan_recon"])

# ─── LAYER 3: Context Aggregation ────────────────────────────────
print("\n[ LAYER 3 ]  Asset Context & Compliance Aggregation")
try:
    from layer3_context.context_aggregator import aggregate_context
    contexts = aggregate_context(scenario, scores)
    assert len(contexts) == len(scenario["resources"])
    sample = list(contexts.values())[0]
    assert hasattr(sample, "threat") and hasattr(sample, "business") and hasattr(sample, "compliance")
    print(f"  Resources ctx'd    : {len(contexts)}")
    print(f"  Sample context     : threat={sample.threat.threat_score:.3f}, sla={sample.business.sla_priority}, gdpr={sample.compliance.gdpr_applicable}")
    print(f"  {PASS} Layer 3 OK")
    results["Layer 3: Context"] = PASS
except Exception as e:
    print(f"  {FAIL}: {e}")
    traceback.print_exc()
    results["Layer 3: Context"] = FAIL

# ─── LAYER 4: Confidence Evaluation ──────────────────────────────
print("\n[ LAYER 4 ]  Detection Confidence Evaluation")
try:
    from layer4_confidence.confidence_evaluator import evaluate_confidence
    confidences = evaluate_confidence(scenario, scores)
    assert len(confidences) == len(scenario["resources"])
    sample = list(confidences.values())[0]
    assert 0.0 <= sample.detection_confidence <= 1.0
    assert 0.0 <= sample.overall_confidence <= 1.0
    print(f"  Resources eval'd   : {len(confidences)}")
    print(f"  Sample confidence  : detection={sample.detection_confidence:.3f}, sensor={sample.sensor_confidence:.3f}, overall={sample.overall_confidence:.3f}")
    print(f"  {PASS} Layer 4 OK")
    results["Layer 4: Confidence"] = PASS
except Exception as e:
    print(f"  {FAIL}: {e}")
    traceback.print_exc()
    results["Layer 4: Confidence"] = FAIL

# ─── LAYER 5: Adaptive Constraints ───────────────────────────────
print("\n[ LAYER 5 ]  Adaptive Budget & Policy Constraints")
try:
    from layer5_constraints.adaptive_constraints import generate_adaptive_constraints
    constraints = generate_adaptive_constraints(contexts, confidences, base_max_budget=5.0)
    assert hasattr(constraints, "max_budget") and constraints.max_budget > 0
    print(f"  Adaptive budget    : {constraints.max_budget:.3f}  (from base=5.0)")
    print(f"  Required actions   : {constraints.required_actions}")
    print(f"  Forbidden actions  : {constraints.forbidden_actions}")
    print(f"  {PASS} Layer 5 OK")
    results["Layer 5: Constraints"] = PASS
except Exception as e:
    print(f"  {FAIL}: {e}")
    traceback.print_exc()
    results["Layer 5: Constraints"] = FAIL

# ─── LAYER 6: Quantum Optimization ───────────────────────────────
print("\n[ LAYER 6 ]  QUBO/QAOA Quantum Decision Engine")
try:
    from layer6_optimization.decision_engine import (
        build_qubo, solve_quantum, decode_action_plan,
        calculate_objective, calculate_total_cost, is_budget_feasible
    )
    from layer6_optimization.baseline_greedy import solve_with_greedy, solve_with_greedy_budget, solve_with_ilp
    from config import QAOA_REPS, ACTIONS

    t0 = time.time()
    plan_g, obj_g = solve_with_greedy(scenario, scores)
    t_g = (time.time() - t0) * 1000

    t0 = time.time()
    plan_bg, obj_bg = solve_with_greedy_budget(scenario, scores, constraints.max_budget)
    t_bg = (time.time() - t0) * 1000

    t0 = time.time()
    plan_ilp, obj_ilp = solve_with_ilp(scenario, scores, constraints.max_budget)
    t_ilp = (time.time() - t0) * 1000

    q_scenario = {"scenario": scenario["scenario"], "resources": scenario["resources"][:2]}
    q_scores = {r["id"]: scores[r["id"]] for r in q_scenario["resources"]}
    qp, var_lookup = build_qubo(q_scenario, q_scores, constraints.max_budget, hard_budget=False)

    t0 = time.time()
    res_np = solve_quantum(qp, method="numpy")
    plan_np = decode_action_plan(qp, var_lookup, res_np)
    obj_np  = calculate_objective(plan_np, q_scenario, q_scores)
    t_np = (time.time() - t0) * 1000

    t0 = time.time()
    res_qaoa = solve_quantum(qp, method="qaoa", seed=42)
    plan_qaoa = decode_action_plan(qp, var_lookup, res_qaoa)
    obj_qaoa  = calculate_objective(plan_qaoa, q_scenario, q_scores)
    t_qaoa = time.time() - t0

    # Behavioral assertions: verify QUBO one-hot constraint is satisfied in decoded plan
    assert len(plan_np) == len(q_scenario["resources"]), "NumPy plan missing resources"
    assert all(r["id"] in plan_np for r in q_scenario["resources"]), "NumPy plan missing resource keys"
    assert all(action in ACTIONS for action in plan_np.values()), "NumPy plan selected invalid actions"

    assert len(plan_qaoa) == len(q_scenario["resources"]), "QAOA plan missing resources"
    assert all(r["id"] in plan_qaoa for r in q_scenario["resources"]), "QAOA plan missing resource keys"
    assert all(action in ACTIONS for action in plan_qaoa.values()), "QAOA plan selected invalid actions"
    assert obj_qaoa is not None and not np.isnan(obj_qaoa), "QAOA objective is NaN"

    print(f"  Greedy             : obj={obj_g:.3f}  {t_g:.1f}ms")
    print(f"  Greedy+Budget      : obj={obj_bg:.3f}  {t_bg:.1f}ms")
    print(f"  ILP (PuLP)         : obj={obj_ilp:.3f}  {t_ilp:.1f}ms  [BASELINE]")
    print(f"  NumPy Eigen (exact): obj={obj_np:.3f}  {t_np:.1f}ms  vars={qp.get_num_vars()}")
    print(f"  QAOA (reps={QAOA_REPS})      : obj={obj_qaoa:.3f}  {t_qaoa:.2f}s")
    print(f"  {PASS} Layer 6 OK (Behavioral one-hot and action feasibility verified)")
    results["Layer 6: Quantum"] = PASS
except Exception as e:
    print(f"  {FAIL}: {e}")
    traceback.print_exc()
    results["Layer 6: Quantum"] = FAIL
    plan_ilp = {}

# ─── LAYER 7: Utility Model ───────────────────────────────────────
print("\n[ LAYER 7 ]  Multi-Attribute Response Utility Model")
try:
    from layer7_utility.response_utility import calculate_all_action_utilities
    utilities = calculate_all_action_utilities(scenario, contexts, confidences)
    assert len(utilities) == len(scenario["resources"])
    sample_rid = scenario["resources"][0]["id"]
    sample_utils = utilities[sample_rid]
    best_action = max(sample_utils, key=lambda a: sample_utils[a].net_utility)
    print(f"  Resources scored   : {len(utilities)}")
    print(f"  Actions per res    : {len(sample_utils)}")
    print(f"  Best action [res-0]: {best_action}  (net_utility={sample_utils[best_action].net_utility:.3f})")
    print(f"  {PASS} Layer 7 OK")
    results["Layer 7: Utility"] = PASS
except Exception as e:
    print(f"  {FAIL}: {e}")
    traceback.print_exc()
    results["Layer 7: Utility"] = FAIL

# ─── LAYER 8: Execution ───────────────────────────────────────────
print("\n[ LAYER 8 ]  Response Orchestration & Execution")
try:
    from layer8_orchestration.executor import execute_plan, execute_strategy
    logs = execute_plan(plan_ilp)
    assert len(logs) == len(plan_ilp)
    assert all(log["status"] == "simulated_success" for log in logs)
    print(f"  Actions executed   : {len(logs)}")
    for log in logs:
        print(f"    {log['resource_id'][-5:]} -> {log['action']}  @ {log['timestamp']}")
    print(f"  {PASS} Layer 8 OK")
    results["Layer 8: Orchestration"] = PASS
except Exception as e:
    print(f"  {FAIL}: {e}")
    traceback.print_exc()
    results["Layer 8: Orchestration"] = FAIL

# ─── LAYER 9: Feedback ───────────────────────────────────────────
print("\n[ LAYER 9 ]  Post-Incident Feedback Learning")
try:
    from layer9_feedback.feedback_learner import FeedbackLearner
    learner = FeedbackLearner(data_path="test_feedback_tmp.json")
    w_before = learner.get_current_weights().copy()
    learner.record_feedback("v-001", "port_scan_recon", plan_ilp, successful=True, notes="verify")
    w_same = learner.get_current_weights()
    learner.record_feedback("v-002", "port_scan_recon", plan_ilp, successful=False, notes="verify-fail")
    w_changed = learner.get_current_weights()
    print(f"  Feedback records   : {len(learner.feedback_history)}")
    print(f"  Success->no change : {w_before == w_same}")
    print(f"  Failure->adapted   : {w_before != w_changed}")
    print(f"  Updated weights    : containment={w_changed.get('containment_effectiveness',0):.4f}")
    print(f"  {PASS} Layer 9 OK")
    results["Layer 9: Feedback"] = PASS
    os.remove("test_feedback_tmp.json")
except Exception as e:
    print(f"  {FAIL}: {e}")
    traceback.print_exc()
    results["Layer 9: Feedback"] = FAIL

# ─── INTEGRATED PIPELINE ─────────────────────────────────────────
print("\n[ PIPELINE ] Full Integrated 9-Layer Run (DDoS Flood)")
try:
    from pipeline import run_pipeline, comparison_table
    t0 = time.time()
    result = run_pipeline(
        SCENARIOS["ddos_flood"],
        max_budget=5.0,
        run_quantum=True,
        quantum_resources=2,
        quantum_method="numpy"
    )
    elapsed = time.time() - t0
    rows = comparison_table(result)
    print(f"  Total runtime      : {elapsed:.2f}s")
    print(f"  Threat scores      : { {k[-5:]: round(v,3) for k,v in result.threat_scores.items()} }")
    print(f"\n  {'Solver':<18} {'Objective':>10} {'Cost':>8} {'BudgetOK':>9} {'Gap vs ILP':>12}")
    print(f"  {'-'*62}")
    for row in rows:
        gap = f"{row['gap_vs_ilp_pct']:+.1f}%" if row['gap_vs_ilp_pct'] is not None else "baseline"
        ok  = "YES" if row["budget_ok"] else "NO"
        print(f"  {row['solver']:<18} {row['objective']:>10.3f} {row['cost']:>8.3f} {ok:>9} {gap:>12}")
    print(f"  {PASS} Integrated Pipeline OK")
    results["Integrated Pipeline"] = PASS
except Exception as e:
    print(f"  {FAIL}: {e}")
    traceback.print_exc()
    results["Integrated Pipeline"] = FAIL

# ─── SUMMARY ─────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  FINAL VERIFICATION SUMMARY")
print("=" * 65)
passed = sum(1 for v in results.values() if v == PASS)
total  = len(results)
for name, status in results.items():
    icon = ">>>" if status == PASS else "***"
    print(f"  {icon} {status}  {name}")
print(f"\n  Score: {passed}/{total} layers verified")
if passed == total:
    print("  *** ALL SYSTEMS GO -- Architecture working correctly! ***")
else:
    failed = [k for k, v in results.items() if v == FAIL]
    print(f"  *** ATTENTION: Failed -> {failed}")
print("=" * 65)
