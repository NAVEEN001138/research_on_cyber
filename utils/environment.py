"""
=============================================================================
ENVIRONMENT CAPTURE UTILITY
Module: utils/environment.py
-----------------------------------------------------------------------------
Captures the execution hardware, CPU architecture, RAM, GPU, OS, and
dependency runtime versions for paper provenance and reproducibility.
=============================================================================
"""

import os
import sys
import json
import platform
import subprocess
import psutil
import torch
import qiskit


def capture_environment(output_path: str = "results/environment.json") -> dict:
    """
    Captures complete system specifications and writes to results/environment.json.
    """
    cpu_model = platform.processor()
    if sys.platform == "win32":
        try:
            out = subprocess.check_output(["wmic", "cpu", "get", "name"], text=True).strip()
            lines = [l.strip() for l in out.split("\n") if l.strip() and "Name" not in l]
            if lines:
                cpu_model = lines[0]
        except Exception:
            pass
    elif os.path.exists("/proc/cpuinfo"):
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        cpu_model = line.split(":", 1)[1].strip()
                        break
        except Exception:
            pass

    gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    cuda_version = torch.version.cuda if torch.cuda.is_available() else None

    env = {
        "cpu_model": cpu_model,
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "ram_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "gpu_name": gpu_name,
        "os": f"{platform.system()} {platform.release()} ({platform.version()})",
        "python_version": platform.python_version(),
        "torch_version": torch.__version__,
        "qiskit_version": qiskit.__version__,
        "torch_threads": torch.get_num_threads(),
        "cuda_version": cuda_version
    }

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(env, f, indent=2)

    return env


if __name__ == "__main__":
    env = capture_environment("results/environment.json")
    print("Environment captured successfully:")
    print(json.dumps(env, indent=2))
