"""Dataset loaders, the shared seeded subsampling utility, and lazy accessors for
the two method implementations this repository does not redistribute (see the
README). Loading reproduces the companion paper's original preprocessing, so the
numbers here are comparable to the published ones. See results/PROTOCOL.md.
"""
import importlib
import os
import sys
import numpy as np
import pandas as pd
from sklearn.datasets import make_blobs
from sklearn.preprocessing import LabelEncoder, StandardScaler

# ─── Paths (resolved relative to this file, so the repo is relocatable) ─────
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(CODE_DIR)
DATA_DIR = os.path.join(REPO_ROOT, "data")
RESULTS_DIR = os.path.join(REPO_ROOT, "results")

sys.path.insert(0, CODE_DIR)


def normalizar_minmax(X):
    """Per-column min-max scaling to [0, 1], constant columns left unscaled.

    Reproduced from the companion paper so the loaders below do not depend on a
    module this repository does not ship.
    """
    X_min = X.min(axis=0)
    X_max = X.max(axis=0)
    rng = X_max - X_min
    rng[rng == 0] = 1
    return (X - X_min) / rng


# Imported lazily, so that everything not needing them still works.
_METHOD_SOURCES = {"hybrid_optimizer_c2": "hibrido_c2", "run_ga_c2": "ga_c2"}


def __getattr__(name):
    if name not in _METHOD_SOURCES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = _METHOD_SOURCES[name]
    try:
        return getattr(importlib.import_module(module), name)
    except ImportError:
        raise ImportError(
            f"{name}() lives in {module}.py, which this repository does not "
            f"redistribute (see README, 'Method implementations'). The paper's "
            f"numbers can still be verified from the committed raw results."
        ) from None

IRIS_CSV = os.path.join(DATA_DIR, "iris_dataset.csv")
HCV_CSV = os.path.join(DATA_DIR, "hcvdat0.csv")


# ─── Dataset loaders (mirrors experimentos_c2_paper1/run_heuristic_c2.py) ──
def get_iris():
    df = pd.read_csv(IRIS_CSV)
    features = [c for c in df.columns if df[c].dtype in [np.float64, np.int64]][:4]
    X_raw = df[features].values.astype(float)
    return normalizar_minmax(X_raw), "Iris (N=150, 4D)"


def get_hcv():
    df = pd.read_csv(HCV_CSV)
    df.dropna(inplace=True)
    le = LabelEncoder()
    df["Sex"] = le.fit_transform(df["Sex"])
    X_raw = df.values[:, 2:]
    scaler = StandardScaler()
    return scaler.fit_transform(X_raw), "HCV (N=589, 12D)"


def get_synthetic_2d():
    X_raw, _ = make_blobs(n_samples=1000, centers=5, n_features=2, random_state=42)
    return normalizar_minmax(X_raw), "Synthetic 2D (N=1000, 2D)"


DATASET_LOADERS = {
    "Iris": get_iris,
    "HCV": get_hcv,
    "Synthetic": get_synthetic_2d,
}


# ─── Subsampling utility (shared by exact / GA / proposed on sub-instances) ─
def subsample(X, n_sub, seed):
    """Deterministic subsample of n_sub rows. Used by all three methods, so a
    given (dataset, seed) yields the identical point set for each."""
    rng = np.random.default_rng(seed)
    n = len(X)
    if n_sub >= n:
        idx = np.arange(n)
    else:
        idx = rng.choice(n, size=n_sub, replace=False)
    return X[idx], idx


# Chosen empirically: ~5s per exact solve under networkx 3.6.1, scaling ~O(N^3).
EXACT_SUBSAMPLE_N = 300
EXACT_SUB_SEEDS = list(range(42, 52))  # 10 repetitions, seeds 42..51

if __name__ == "__main__":
    for name, fn in DATASET_LOADERS.items():
        X, desc = fn()
        print(name, desc, X.shape)
