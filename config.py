"""Shared configuration for the 9-layer Cloud Guardian pipeline."""

# ─── Layer 0: Preprocessing ──────────────────────────────────────────────────
PREPROCESSING_CACHE_PATH = "layer0_preprocessing/preprocessor_cache.pkl"
OUTLIER_IQR_FACTOR       = 1.5    # Whisker width for IQR-based outlier clipping
MIN_VARIANCE_THRESHOLD   = 1e-6   # Drop columns whose variance is below this
TOP_K_FEATURES           = 36     # Maximum features to keep (0 = keep all passing variance filter)

# Layer 1: Telemetry & Event Collection
FEATURE_NAMES = [
    "failed_logins",
    "unusual_outbound_bytes",
    "privilege_escalation_attempts",
]

# Layer 7: Response Utility Model (base action effectiveness)
ACTIONS = {
    "isolate": 0.90,
    "rotate_credentials": 0.55,
    "block_ip": 0.50,
    "disable_user": 0.65,
    "snapshot_backup": 0.20,
    "monitor": 0.05,  # new for multi-step strategies
    "increase_logging": 0.10,  # new for multi-step strategies
}

# Layer 8: Response Orchestrator (multi-step strategy definitions)
RESPONSE_STRATEGIES = {
    "Strategy A": ["snapshot_backup", "block_ip", "rotate_credentials", "notify_soc"],
    "Strategy B": ["monitor", "increase_logging", "human_approval"],
}

# Layer 7: Response Utility Model (weights for utility components)
UTILITY_WEIGHTS = {
    "containment_effectiveness": 0.30,
    "business_impact": -0.25,
    "downtime": -0.20,
    "recovery_time": -0.10,
    "compliance_risk": -0.10,
    "analyst_effort": -0.03,
    "operational_cost": -0.02,
    "response_confidence": 0.0,
}

# Layer 6: Decision Optimization Engine
COST_WEIGHTS = (0.5, 0.3, 0.2)
MAX_BUDGET = 15.0
LAMBDA_PENALTY = 5.0

# Quantum simulator limits (each resource = 5 qubits; keep small on a laptop)
MAX_QUANTUM_RESOURCES = 2
QAOA_MAXITER = 8
QAOA_REPS = 1
QUANTUM_METHOD = "numpy"

# Layer 1: Data Loading
CLOUDTRAIL_TRAIN_SAMPLE = 50_000
ISCX_GLOB = "*ISCX*.csv"
ISCX_SAMPLE_PER_FILE = 8_000
ISCX_MAX_TOTAL = 50_000

# Layer 9: Feedback Learning
FEEDBACK_DATA_PATH = "feedback_data.json"
FEEDBACK_LEARNING_RATE = 0.1

# WUSTL-IIoT-2021 Feature Groups for Data Leakage Benchmark
WUSTL_FEATURE_GROUPS = {
    "label": "Target",
    "traffic": "Traffic",
    "g1_hosts_ports": ["SrcAddr", "DstAddr", "Sport", "Dport"],
    "g2_ipid": ["sIpId", "dIpId"],
    "g3_timestamps": ["StartTime", "LastTime"],
    "g4_fingerprints": ["sTtl", "dTtl", "sTos"],
    "semantic": [
        "Mean", "SrcPkts", "DstPkts", "TotPkts", "DstBytes", "SrcBytes", "TotBytes",
        "SrcLoad", "DstLoad", "Load", "SrcRate", "DstRate", "Rate", "SrcLoss",
        "DstLoss", "Loss", "pLoss", "SrcJitter", "DstJitter", "SIntPkt", "DIntPkt",
        "Proto", "Dur", "TcpRtt", "IdleTime", "Sum", "Min", "Max", "sDSb",
        "SAppBytes", "DAppBytes", "TotAppByte", "SynAck", "RunTime", "SrcJitAct", "DstJitAct"
    ]
}

