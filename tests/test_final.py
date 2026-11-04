"""Checks for the frozen final-analysis helpers."""
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, "scripts")]
fcl = pytest.importorskip("final_closed_loop")
fst = pytest.importorskip("fleet_final_stats")


def test_band_matches_development_rules():
    assert fcl.band(1.5) == pytest.approx((0.03, 0.7))
    lo, hi = fcl.band(1.5, 0.9)                      # dev_alpha_aware.band
    assert lo == pytest.approx(3 / 90) and hi == pytest.approx(7 / 20)
    g = 10 / 110
    assert fcl.band(6.7, 0.9) == pytest.approx((g, g))  # band closes: never ask


def test_method_sets():
    conf = [m[0] for m in fcl.methods("confirmatory", 6)]
    assert conf == ["rule_matched", "joint", "rule_a_matched", "joint_a"]
    expl = fcl.methods("exploratory", 8)
    names = [m[0] for m in expl]
    assert len(names) == len(set(names)) == 33
    m = dict((x[0], x) for x in expl)
    assert m["rule_matched"][2] == 6.15 and m["rule_a_matched"][2] == 6.20
    assert m["joint_budget"][4] == 3 and m["joint_budget"][3] == 0.0
    assert m["joint_misspec"][5] == 1.0 and m["joint_misspec"][6] == 0.9


def test_holm_and_intervals():
    assert np.allclose(fst.holm([0.01, 0.04, 0.03, 0.2]), [0.04, 0.09, 0.09, 0.2])
    lo, hi = fst.clopper_pearson(20, 20)
    assert hi == 1.0 and lo == pytest.approx(0.8316, abs=1e-4)
    n01, n10, p = fst.mcnemar(np.array([0, 0, 1, 1]), np.array([0, 1, 1, 0]))
    assert (n01, n10) == (1, 1) and p == 1.0
