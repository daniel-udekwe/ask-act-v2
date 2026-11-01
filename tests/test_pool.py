import os

import numpy as np
import pytest

from fleet_qubo.instances import GO, STOP, ASK
from fleet_qubo.pool import realized, ScenarioPool

POOL = os.path.join(os.path.dirname(__file__), "..", "results", "deadline_probs.csv")


def test_realized_outcomes():
    acts = np.array([GO, GO, STOP, STOP, ASK, ASK])
    cross = np.array([1, 0, 1, 0, 1, 0])
    r = realized(acts, cross)
    assert r == {"collisions": 1, "crossing": 3, "questions": 2, "unnecessary_stops": 1}


def test_wrong_answers_only_hurt_crossers():
    acts = np.full(1000, ASK)
    cross = np.zeros(1000)
    assert realized(acts, cross, alpha=0.5, rng=np.random.default_rng(0))["collisions"] == 0


@pytest.mark.skipif(not os.path.exists(POOL), reason="run extract_deadline_probs.py first")
def test_pool_paired_and_in_range():
    pool = ScenarioPool(POOL)
    assert set(pool.calibrations) == {"raw", "isotonic", "isotonic_dw"}
    for cond in ("nominal", "noisy"):
        rng = np.random.default_rng(1)
        scen = pool.draw(cond, 6, rng)
        ps = [pool.instance(cond, scen, c).p for c in pool.calibrations]
        assert all(len(p) == 6 and np.all((p >= 0) & (p <= 1)) for p in ps)
        # final-evaluation seeds (8000+) must never be in the development pool
    import pandas as pd
    seeds = pd.read_csv(POOL).seed.to_numpy() % 10000
    assert ((seeds >= 4000) & (seeds <= 4099)).all()
