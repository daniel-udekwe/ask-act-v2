"""Calibrated crossing probability at the decision deadline, per Ask or Act scenario.

Runs the Ask or Act offline simulator (unchanged code from the repository) with a
threshold policy whose band is disabled, so the robot never commits early: it
drives and observes until the pedestrian is at the deadline (0.6 m ahead). The
smoothed, calibrated probability at that first deadline step is recorded, with
the scenario's ground-truth intent.

Seed block: fleet development pool s = 4000-4099 in each condition block
(10000 * condition index + s); 4000-4099 was never used by Ask or Act.
The fleet final pool 8000-8099 is reserved and not touched here.

Usage:
  python scripts/extract_deadline_probs.py --aoa <repo> --model <intent_model.pkl>
Writes results/deadline_probs.csv.
"""
import argparse
import os
import sys

import pandas as pd


class Deadline(Exception):
    pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aoa", default="/home/claude/daniel-udekwe/turtlebot3-ask_or_act")
    ap.add_argument("--model", default="/home/claude/aoa_data/predictor/intent_model.pkl")
    ap.add_argument("--conditions", nargs="+", default=["nominal", "noisy"])
    ap.add_argument("--seed-start", type=int, default=4000)
    ap.add_argument("--seeds", type=int, default=100)
    ap.add_argument("--out", default="results/deadline_probs.csv")
    args = ap.parse_args()

    sys.path.insert(0, args.aoa)
    from generate_scenarios import CONDITIONS, ENVS, FAMILIES, build
    from policy import AskOrActPolicy, load_predictor
    from simulate_policies import simulate

    ASK_DIST = 0.6

    class ProbeAtDeadline(AskOrActPolicy):
        def decide(self, t, robot_x):
            out = super().decide(t, robot_x)
            if self.decisions:
                _, _, p, _, _, ahead, oy = self.decisions[-1]
                if ahead <= ASK_DIST and p != "":
                    self.probe = dict(t_deadline=t, p=float(p), dist_to_line=oy)
                    raise Deadline
            return out

    variants = {"raw": ("raw", None), "isotonic": ("isotonic", "recal"),
                "isotonic_dw": ("isotonic_dw", "recal")}
    cond_index = {c: i for i, c in enumerate(CONDITIONS)}
    rows = []
    for cond in args.conditions:
        preds = {v: load_predictor(args.model, "mlp", kind, cond if which else "nominal")
                 for v, (kind, which) in variants.items()}
        base = 10000 * cond_index[cond]
        for env in ENVS:
            for family, intent in FAMILIES:
                for seed in range(base + args.seed_start, base + args.seed_start + args.seeds):
                    label = build(env, family, intent, seed, cond)
                    for v, (model, cal) in preds.items():
                        pol = ProbeAtDeadline("threshold", model, cal, p_low=-1.0, p_high=2.0,
                                              true_intent=label["intent"])
                        pol.probe = None
                        try:
                            simulate(label, pol, CONDITIONS[cond]["noise"], 1.5, 1.0, 1.0)
                        except Deadline:
                            pass
                        rows.append(dict(scenario=label["id"], condition=cond, family=family,
                                         intent=intent, crossing=int(intent == "crossing"),
                                         ambiguous=label["ambiguous"], seed=seed, calibration=v,
                                         reached_deadline=pol.probe is not None,
                                         **(pol.probe or {})))
        print(cond, "done", flush=True)
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    df.to_csv(args.out, index=False)
    print(df.groupby(["condition", "calibration"]).agg(
        n=("scenario", "size"), reached=("reached_deadline", "mean"), mean_p=("p", "mean")))


if __name__ == "__main__":
    main()
