"""
=============================================================================
REPRODUCIBILITY & GLOBAL SEEDING HELPER
Module: utils/seeding.py
-----------------------------------------------------------------------------
Guarantees strict trial-level determinism across Python random, NumPy,
PyTorch CPU and CUDA runtimes.
=============================================================================
"""

import os
import random
import numpy as np
import torch


def set_seed(seed: int = 42) -> None:
    """
    Sets global deterministic random seeds across Python, NumPy, and PyTorch.
    Called at the beginning of every experimental trial and round evaluation.
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    # Enforce deterministic PyTorch algorithms where feasible
    try:
        torch.use_deterministic_algorithms(True)
    except Exception:
        # Fallback if deterministic algorithm is not implemented for specific sparse/custom op
        pass
