import os
import sys

import numpy as np
import pandas as pd
import pytest

AOA = os.environ.get("AOA_REPO", "/home/claude/daniel-udekwe/turtlebot3-ask_or_act")
MODEL = os.environ.get("AOA_MODEL", "/home/claude/aoa_data/predictor/intent_model.pkl")
POOL = os.path.join(os.path.dirname(__file__), "..", "results", "deadline_probs.csv")
pytestmark = pytest.mark.skipif(not (os.path.isdir(AOA) and os.path.exists(MODEL)),
                                reason="needs the Ask or Act repository and a trained model")


@pytest.fixture(scope="module")
def aoa():
    sys.path.insert(0, AOA)
    import generate_scenarios as gs
    import policy
    import ped_traj
    import simulate_policies as sp
    from fleet_qubo.fleet_sim import make_policy_class
    return dict(gs=gs, policy=policy, sp=sp, FleetPolicy=make_policy_class(policy.AskOrActPolicy),
                env=dict(build_trajectory=ped_traj.build_trajectory, pose_at=ped_traj.pose_at,
                         ROBOT=gs.ROBOT, COLLISION_DIST=sp.COLLISION_DIST))


CASES = [("clear_cross", "crossing", "nominal", 4001), ("hesitant", "crossing", "noisy", 44003),
         ("hesitant", "not_crossing", "nominal", 4007), ("late_turn", "crossing", "noisy", 44011),
         ("wait_far", "not_crossing", "nominal", 4002), ("slow_cross", "crossing", "noisy", 44005)]


@pytest.mark.parametrize("family,intent,cond,seed", CASES)
@pytest.mark.parametrize("shift", [0, 37])
def test_single_robot_matches_ask_or_act(aoa, family, intent, cond, seed, shift):
    """One independent robot (any clock shift) reproduces simulate_policies.simulate()."""
    gs, sp = aoa["gs"], aoa["sp"]
    lab = gs.build("cafe", family, intent, seed, cond)
    model, cal = aoa["policy"].load_predictor(MODEL, "mlp", "isotonic_dw", cond)
    # reference: Ask or Act's own simulate() loop, driving the same (cache-fixed) policy class
    ref = sp.simulate(lab, aoa["FleetPolicy"](model, cal, mode="independent", true_intent=intent),
                      gs.CONDITIONS[cond]["noise"], 1.5, 1.0, 1.0)
    pol = aoa["FleetPolicy"](model, cal, mode="independent", true_intent=intent)
    out, _, _ = __import__("fleet_qubo.fleet_sim", fromlist=["run_fleet"]).run_fleet(
        [lab], [pol], gs.CONDITIONS[cond]["noise"], [shift], aoa["env"])
    for key in ("outcome", "delay", "min_dist", "collision", "n_asks", "stopped_time"):
        assert out[0][key] == ref[key], key


@pytest.mark.skipif(not os.path.exists(POOL), reason="needs results/deadline_probs.csv")
def test_joint_request_probability_matches_pool(aoa):
    """The probability a joint robot reports at its deadline equals the extracted pool value."""
    from fleet_qubo.fleet_sim import run_fleet
    gs = aoa["gs"]
    d = pd.read_csv(POOL)
    d = d[(d.calibration == "isotonic_dw") & d.reached_deadline & (d.condition == "noisy")].head(5)
    model, cal = aoa["policy"].load_predictor(MODEL, "mlp", "isotonic_dw", "noisy")
    seen = {}

    def joint(ps, idx):
        seen.update(dict(zip(idx, ps)))
        return [1] * len(ps)

    labs = [gs.build("cafe", r.family, r.intent, int(r.seed), "noisy") for r in d.itertuples()]
    pols = [aoa["FleetPolicy"](model, cal, mode="joint", true_intent=l["intent"]) for l in labs]
    shifts = [int(round(-t / 0.05)) for t in d.t_deadline]
    run_fleet(labs, pols, gs.CONDITIONS["noisy"]["noise"], shifts, aoa["env"], joint=joint)
    assert np.allclose([seen[i] for i in range(len(labs))], d.p.to_numpy(), atol=1e-4)


def test_probability_keeps_updating_after_history_fills(aoa):
    """Regression: Ask or Act's predict() froze once its 40-observation history was full."""
    gs, sp = aoa["gs"], aoa["sp"]
    lab = gs.build("cafe", "clear_cross", "crossing", 7000, "nominal")
    model, cal = aoa["policy"].load_predictor(MODEL, "mlp", "isotonic_dw", "nominal")
    pol = aoa["FleetPolicy"](model, cal, mode="independent", true_intent="crossing", p_low=-1.0, p_high=2.0)
    sp.simulate(lab, pol, 0.03, 1.5, 1.0, 1.0)
    ps = [d[2] for d in pol.decisions if d[2] != ""]
    assert len(set(ps)) > 5                      # the fixed policy's probability evolves
    orig = aoa["policy"].AskOrActPolicy("threshold", model, cal, true_intent="crossing", p_low=-1.0, p_high=2.0)
    sp.simulate(lab, orig, 0.03, 1.5, 1.0, 1.0)
    assert len({d[2] for d in orig.decisions if d[2] != ""}) == 1   # documents the original behaviour
