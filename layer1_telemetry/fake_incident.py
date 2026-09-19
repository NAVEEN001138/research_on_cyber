"""
=============================================================================
LAYER 1: TELEMETRY, EVENT COLLECTION & DATA LOADING
Module: fake_incident.py
-----------------------------------------------------------------------------
Problem Solved:
  Generates multi-resource cloud incident telemetry profiles (DDoS floods,
  port scanning, ransomware outbreaks, SQL injection exfiltration) for
  end-to-end testing and demonstration of the 9-layer quantum security pipeline.

Inputs:  Scenario profile key (e.g. 'ddos_flood', 'port_scan_recon', 'ransomware_outbreak', 'sql_injection_exfil').
Outputs: Scenario telemetry dictionary containing cloud resources and raw signal features.
=============================================================================
"""

SCENARIOS = {
    "ddos_flood": {
        "scenario": "Volumetric DDoS attack against web tier",
        "resources": [
            {
                "id": "ddos_flood-res-0",
                "name": "Frontend Web Server 1",
                "type": "ec2_instance",
                "raw_signal": {
                    "failed_logins": 5.0,
                    "unusual_outbound_bytes": 450_000.0,
                    "privilege_escalation_attempts": 0.0,
                },
            },
            {
                "id": "ddos_flood-res-1",
                "name": "Frontend Web Server 2",
                "type": "ec2_instance",
                "raw_signal": {
                    "failed_logins": 2.0,
                    "unusual_outbound_bytes": 380_000.0,
                    "privilege_escalation_attempts": 0.0,
                },
            },
            {
                "id": "ddos_flood-res-2",
                "name": "Load Balancer",
                "type": "load_balancer",
                "raw_signal": {
                    "failed_logins": 0.0,
                    "unusual_outbound_bytes": 890_000.0,
                    "privilege_escalation_attempts": 0.0,
                },
            },
            {
                "id": "ddos_flood-res-3",
                "name": "API Gateway",
                "type": "api_gateway",
                "raw_signal": {
                    "failed_logins": 12.0,
                    "unusual_outbound_bytes": 120_000.0,
                    "privilege_escalation_attempts": 1.0,
                },
            },
            {
                "id": "ddos_flood-res-4",
                "name": "Backend DB",
                "type": "rds_database",
                "raw_signal": {
                    "failed_logins": 1.0,
                    "unusual_outbound_bytes": 5_000.0,
                    "privilege_escalation_attempts": 0.0,
                },
            },
        ],
    },
    "port_scan_recon": {
        "scenario": "Port scanning & reconnaissance phase",
        "resources": [
            {
                "id": "port_scan_recon-res-0",
                "name": "Bastion Host",
                "type": "ec2_instance",
                "raw_signal": {
                    "failed_logins": 45.0,
                    "unusual_outbound_bytes": 15_000.0,
                    "privilege_escalation_attempts": 3.0,
                },
            },
            {
                "id": "port_scan_recon-res-1",
                "name": "Admin Workstation",
                "type": "ec2_instance",
                "raw_signal": {
                    "failed_logins": 30.0,
                    "unusual_outbound_bytes": 8_000.0,
                    "privilege_escalation_attempts": 4.0,
                },
            },
            {
                "id": "port_scan_recon-res-2",
                "name": "Internal Subnet Router",
                "type": "vpc_router",
                "raw_signal": {
                    "failed_logins": 0.0,
                    "unusual_outbound_bytes": 50_000.0,
                    "privilege_escalation_attempts": 0.0,
                },
            },
            {
                "id": "port_scan_recon-res-3",
                "name": "IAM Service Role",
                "type": "iam_role",
                "raw_signal": {
                    "failed_logins": 80.0,
                    "unusual_outbound_bytes": 1_000.0,
                    "privilege_escalation_attempts": 5.0,
                },
            },
        ],
    },
    "ransomware_outbreak": {
        "scenario": "Ransomware encryption & file host targeting",
        "resources": [
            {
                "id": "ransomware-res-0",
                "name": "File Storage Server",
                "type": "ec2_instance",
                "raw_signal": {
                    "failed_logins": 15.0,
                    "unusual_outbound_bytes": 950_000.0,
                    "privilege_escalation_attempts": 6.0,
                },
            },
            {
                "id": "ransomware-res-1",
                "name": "S3 Data Bucket",
                "type": "s3_bucket",
                "raw_signal": {
                    "failed_logins": 0.0,
                    "unusual_outbound_bytes": 1_200_000.0,
                    "privilege_escalation_attempts": 0.0,
                },
            },
            {
                "id": "ransomware-res-2",
                "name": "Domain Controller IAM",
                "type": "iam_role",
                "raw_signal": {
                    "failed_logins": 95.0,
                    "unusual_outbound_bytes": 20_000.0,
                    "privilege_escalation_attempts": 8.0,
                },
            },
        ],
    },
    "sql_injection_exfil": {
        "scenario": "Database SQL injection & data exfiltration",
        "resources": [
            {
                "id": "sqli-res-0",
                "name": "Production RDS MySQL DB",
                "type": "rds_database",
                "raw_signal": {
                    "failed_logins": 10.0,
                    "unusual_outbound_bytes": 750_000.0,
                    "privilege_escalation_attempts": 4.0,
                },
            },
            {
                "id": "sqli-res-1",
                "name": "Public E-Commerce Web API",
                "type": "api_gateway",
                "raw_signal": {
                    "failed_logins": 25.0,
                    "unusual_outbound_bytes": 600_000.0,
                    "privilege_escalation_attempts": 2.0,
                },
            },
        ],
    },
}

SCENARIO_PROFILES = {
    "ddos_flood": {
        "title": "Volumetric DDoS Attack",
        "description": "High-volume network traffic targeting web servers and load balancer.",
    },
    "port_scan_recon": {
        "title": "Port Scanning & Reconnaissance",
        "description": "Probe scans and brute-force attempts against bastion hosts and IAM roles.",
    },
    "ransomware_outbreak": {
        "title": "Ransomware & File Encryption",
        "description": "High file I/O, rapid encryption patterns, and credential dumping against file storage.",
    },
    "sql_injection_exfil": {
        "title": "SQL Injection & Data Exfiltration",
        "description": "Malicious payload injection targeting relational database backends and API gateways.",
    },
}


def generate_incident_scenario(n_assets: int = 4, seed: int = 42) -> dict:
    """
    Generates an incident scenario with n_assets cloud resources for solver benchmarks.
    Deterministic based on seed.
    """
    import random
    rng = random.Random(seed)
    resource_types = ["ec2_instance", "rds_database", "load_balancer", "api_gateway", "s3_bucket"]
    resources = []
    for i in range(n_assets):
        rtype = resource_types[i % len(resource_types)]
        resources.append({
            "id": f"asset_{i:03d}",
            "name": f"Resource-{rtype}-{i}",
            "type": rtype,
            "raw_signal": {
                "failed_logins": float(rng.randint(0, 50)),
                "unusual_outbound_bytes": float(rng.randint(1000, 1000000)),
                "privilege_escalation_attempts": float(rng.randint(0, 5))
            }
        })
    return {
        "scenario": f"Scalable Incident Scenario ({n_assets} assets)",
        "resources": resources
    }

