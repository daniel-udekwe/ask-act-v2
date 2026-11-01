"""Build a fleet epoch (scenarios, labels and start offsets) exactly as the offline studies do.

Shared by run_fleet_gazebo.py and compare_fleet_validation.py so Gazebo and the offline
simulator see identical inputs.
"""
import numpy as np
import pandas as pd

DT = 0.05
LANE = 10.0        # m between lanes in the Gazebo world


def build_epoch(pool_csv, condition, N, seed, jitter=1.0):
    """Return (labels, shifts) for one epoch.

    labels : Ask or Act scenario labels (generate_scenarios.build), one per robot
    shifts : integer step offsets c_i (robot i's episode clock starts at global step c_i)
    """
    import generate_scenarios as gs                     # Ask or Act repository on sys.path
    pool = pd.read_csv(pool_csv)
    pool = pool[(pool.condition == condition) & pool.reached_deadline & (pool.calibration == "isotonic_dw")]
    pool = pool.drop_duplicates("scenario").reset_index(drop=True)
    rng = np.random.default_rng([seed, N])
    pick = pool.iloc[rng.choice(len(pool), size=N, replace=False)]
    u = rng.uniform(0, jitter, size=N)
    labels = [gs.build("cafe", r.family, r.intent, int(r.seed), condition) for r in pick.itertuples()]
    shifts = [int(round((ui - td) / DT)) for ui, td in zip(u, pick.t_deadline)]
    return labels, shifts


def start_delays(shifts, base=2.0):
    """Gazebo start delay per robot after the common go signal (>= 2 s, so 2 s of observation fits)."""
    m = min(shifts)
    return [base + (c - m) * DT for c in shifts]


def band(kappa, C=100.0, tau_s=10.0, tau_a=1.5):
    """Per-robot cost-model band (go below lo, stop above hi), as in scripts/pareto.py."""
    ask = tau_a + kappa
    return min(ask / C, tau_s / (C + tau_s)), max(1.0 - ask / tau_s, tau_s / (C + tau_s))
