"""
=============================================================================
DIAGRAM GENERATOR: ARCHITECTURE & PROCESS FLOW IMAGES
Module: generate_diagram_images.py
-----------------------------------------------------------------------------
Generates publication-quality high-resolution PNG image files (300 DPI):
  1. architecture_diagram.png - 9-Layer System Architecture
  2. process_flow_diagram.png - End-to-End Execution Sequence Flow

Outputs are saved in the current directory and can be directly inserted into
the thesis document, presentation slides, or patent application.
=============================================================================
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set crisp rendering styles
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 9


def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(14, 18), dpi=300)
    ax.axis("off")
    fig.patch.set_facecolor("#0b0f19")

    # Title
    ax.text(
        0.5, 0.98,
        "CLOUD GUARDIAN: 9-LAYER SYSTEM ARCHITECTURE",
        fontsize=18, fontweight="bold", color="#00d4ff", ha="center", va="top"
    )
    ax.text(
        0.5, 0.965,
        "Quantum-Optimized Cloud Incident Response & Federated Threat Intelligence Pipeline",
        fontsize=11, color="#a0aec0", ha="center", va="top"
    )

    layers = [
        ("Layer 0: Preprocessing & Cache Manager", [
            "Raw Edge-IIoTset Logs → Median Imputation → IQR Outlier Clip (1.5x)",
            "log1p Compression → StandardScaler Normalization → Variance Filter",
            "Output: Shared Fitted Scaler Cache (preprocessor_cache.pkl)"
        ], "#1e293b", "#38bdf8", 0.88),

        ("Layer 1: Telemetry Ingestion & Sharding", [
            "14 Attack-Vector Categories (DDoS_UDP, SQLi, PortScan, Ransomware, Backdoor, XSS, etc.)",
            "Non-IID Data Partitioning across Simulated IoT Edge Shards"
        ], "#1e293b", "#818cf8", 0.78),

        ("Layer 2: Federated ML Threat Detection", [
            "Local Edge Node Training: Lightweight TCN-Attention Classifier (Data locked locally)",
            "Global Server Aggregation: FedAvg / FedProx / SCAFFOLD + Top-k Sparsification",
            "Output: Threat Probabilities (s_i) per resource [0.0, 1.0]"
        ], "#1e293b", "#34d399", 0.68),

        ("Layer 3: Asset Context & Compliance Aggregation", [
            "Threat Dimensions: Severity & Attack Velocity",
            "Asset & Business: Criticality, SLA Priority (CRITICAL/HIGH/MED), Recovery Cost",
            "Compliance Engine: GDPR, HIPAA, PCI-DSS Flag Verification"
        ], "#1e293b", "#fbbf24", 0.58),

        ("Layer 4: Detection Confidence Evaluation", [
            "Detection Confidence + Sensor Reliability + Evidence Quality",
            "Overall Confidence Score (c_i) & Confidence Tiers (HIGH / MODERATE / LOW)",
            "Confidence-Gated Action Space: Low confidence restricts high-disruption actions"
        ], "#1e293b", "#f87171", 0.48),

        ("Layer 5: Adaptive Constraints & Context Synthesizer", [
            "Feasible Action Matrix (Per-Resource Capability Filtering e.g. PLC/Medical Device)",
            "C-I-A Importance Profiles (Confidentiality, Integrity, Availability ratings)",
            "Constraint Matrix (Required & Forbidden Policy Rules) + Decision Stability Penalty (Δ=0.15)"
        ], "#1e293b", "#c084fc", 0.38),

        ("Layer 6: Decision Optimization Engine (QUBO / QAOA)", [
            "Formulates Context-Constrained Binary QUBO Objective H(x)",
            "Quantum Solvers: Qiskit QAOA Simulator (AerSampler) & Exact NumPy Diagonalization",
            "Classical Baselines: PuLP Integer Linear Programming (ILP) & Budgeted Greedy"
        ], "#1e293b", "#38bdf8", 0.28),

        ("Layer 7 & 8: Response Utility, Orchestration & Explainability", [
            "Multi-Attribute Net Utility Scoring (Containment Gain vs Business & Downtime Cost)",
            "Automated Response Plan Execution (Network Isolation, Credential Rotation, IP Blocking)",
            "Explainable Rationale Engine: Human-readable selection & rejection reasons"
        ], "#1e293b", "#4ade80", 0.18),

        ("Layer 9: Rich EMA Feedback Learning System", [
            "Incident Outcome Logging (Success, Containment Time, Downtime, False Positives)",
            "Exponential Moving Average (EMA) Rolling Metrics per Action Type",
            "Adaptive Weight Calibration for Future Optimization Rounds"
        ], "#1e293b", "#f472b6", 0.08),
    ]

    for title, details, bg_color, border_color, y_pos in layers:
        # Drawing Box
        rect = patches.FancyBboxPatch(
            (0.08, y_pos), 0.84, 0.08,
            boxstyle="round,pad=0.01,rounding_size=0.015",
            facecolor=bg_color, edgecolor=border_color, linewidth=2.0
        )
        ax.add_patch(rect)

        # Title Text
        ax.text(0.11, y_pos + 0.065, title, fontsize=11, fontweight="bold", color=border_color, va="top")

        # Detail Lines
        for idx, line in enumerate(details):
            ax.text(0.12, y_pos + 0.045 - idx * 0.016, f"• {line}", fontsize=8.5, color="#e2e8f0", va="top")

        # Arrow down (except last box)
        if y_pos > 0.10:
            arrow = patches.FancyArrowPatch(
                (0.5, y_pos), (0.5, y_pos - 0.02),
                arrowstyle="-|>", mutation_scale=12, color=border_color, linewidth=1.5
            )
            ax.add_patch(arrow)

    plt.tight_layout()
    out_path = "architecture_diagram.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"[OK] Generated: {os.path.abspath(out_path)}")


def create_process_flow_diagram():
    fig, ax = plt.subplots(figsize=(16, 11), dpi=300)
    ax.axis("off")
    fig.patch.set_facecolor("#0b0f19")

    # Title
    ax.text(
        0.5, 0.96,
        "CLOUD GUARDIAN: 9-LAYER END-TO-END PROCESS FLOW",
        fontsize=16, fontweight="bold", color="#00d4ff", ha="center", va="top"
    )
    ax.text(
        0.5, 0.93,
        "End-to-End Incident Response and Feedback Process Flow (Layers 0 through 9)",
        fontsize=10, color="#a0aec0", ha="center", va="top"
    )

    # Top Row: Steps 1 - 5
    top_steps = [
        ("Step 1: Telemetry", "Layer 1 Raw Telemetry\nIngestion & Sharding", "#1e293b", "#38bdf8", 0.03),
        ("Step 2: Preprocess", "Layer 0 Preprocessing\n(Shared Scaler)", "#1e293b", "#818cf8", 0.22),
        ("Step 3: Detection", "Layer 2 Threat Detection\nThreat Probability (s_i)", "#1e293b", "#34d399", 0.41),
        ("Step 4: Confidence", "Layer 4 Confidence &\nAction Gating (c_i)", "#1e293b", "#f87171", 0.60),
        ("Step 5: Synthesis", "Layer 5 Context &\nConstraint Matrix", "#1e293b", "#c084fc", 0.79),
    ]

    for title, label, bg, border, x_pos in top_steps:
        box = patches.FancyBboxPatch(
            (x_pos, 0.58), 0.17, 0.22,
            boxstyle="round,pad=0.01,rounding_size=0.02",
            facecolor=bg, edgecolor=border, linewidth=2.0
        )
        ax.add_patch(box)
        ax.text(x_pos + 0.085, 0.76, title, fontsize=9.5, fontweight="bold", color=border, ha="center", va="top")
        ax.text(x_pos + 0.085, 0.68, label, fontsize=8.5, color="#ffffff", ha="center", va="top")

        if x_pos < 0.75:
            arrow = patches.FancyArrowPatch(
                (x_pos + 0.17, 0.69), (x_pos + 0.19, 0.69),
                arrowstyle="-|>", mutation_scale=14, color="#38bdf8", linewidth=2.0
            )
            ax.add_patch(arrow)

    # Connect Step 5 down to Step 6
    down_arr = patches.FancyArrowPatch(
        (0.875, 0.58), (0.875, 0.43),
        arrowstyle="-|>", mutation_scale=14, color="#c084fc", linewidth=2.0
    )
    ax.add_patch(down_arr)

    # Bottom Row: Steps 6 - 9 (Right to Left)
    bot_steps = [
        ("Step 6: Optimization", "Layer 6 Decision Engine\nQUBO / QAOA / ILP / Greedy", "#1e293b", "#38bdf8", 0.79),
        ("Step 7: Utility Evaluation", "Layer 7 Response Model\nMulti-Attribute Utility", "#1e293b", "#fbbf24", 0.54),
        ("Step 8: Orchestration", "Layer 8 Containment\nExecution & Explainability", "#1e293b", "#4ade80", 0.29),
        ("Step 9: EMA Feedback", "Layer 9 Feedback Learner\nOutcome Logging & Weights", "#1e293b", "#f472b6", 0.04),
    ]

    for title, label, bg, border, x_pos in bot_steps:
        box = patches.FancyBboxPatch(
            (x_pos, 0.18), 0.21, 0.22,
            boxstyle="round,pad=0.01,rounding_size=0.02",
            facecolor=bg, edgecolor=border, linewidth=2.0
        )
        ax.add_patch(box)
        ax.text(x_pos + 0.105, 0.36, title, fontsize=9.5, fontweight="bold", color=border, ha="center", va="top")
        ax.text(x_pos + 0.105, 0.28, label, fontsize=8.5, color="#ffffff", ha="center", va="top")

        if x_pos > 0.10:
            arrow = patches.FancyArrowPatch(
                (x_pos, 0.29), (x_pos - 0.04, 0.29),
                arrowstyle="-|>", mutation_scale=14, color="#4ade80", linewidth=2.0
            )
            ax.add_patch(arrow)

    # Feedback Loop Arrow from Step 9 back up to Step 5 Synthesis
    feedback_arr = patches.FancyArrowPatch(
        (0.145, 0.40), (0.875, 0.56),
        connectionstyle="arc3,rad=0.35",
        arrowstyle="-|>", mutation_scale=14, color="#f472b6", linewidth=2.0, linestyle="--"
    )
    ax.add_patch(feedback_arr)
    ax.text(0.50, 0.51, "Updated Utility Weights (Feedback Loop)", fontsize=9, fontweight="bold", color="#f472b6", ha="center")

    plt.tight_layout()
    out_path = "process_flow_diagram.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"[OK] Generated: {os.path.abspath(out_path)}")


if __name__ == "__main__":
    create_architecture_diagram()
    create_process_flow_diagram()
