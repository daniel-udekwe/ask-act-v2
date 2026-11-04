"""Check that this machine reproduces the reference closed-loop results before a long run.

Runs the exploratory method set for 2 development epochs (N = 6, noisy, decision-aware,
development pool, seeds 4 900 000+) and compares every robot's outcome with
results/repro_reference.csv, made in the original environment. Touches no final seeds.

Usage: python scripts/check_repro.py            (AOA_REPO=<Ask or Act checkout> if not the default)
       python scripts/check_repro.py --write    (original environment only: rewrite the reference)
"""
import os
import sys
import platform

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import final_closed_loop as F  # noqa: E402

REF = os.path.join(ROOT, "results", "repro_reference.csv")
COLS = ["collision", "n_asks", "delay", "fallback", "stopped_time", "held_s", "action"]


def main():
    import numpy, scipy, sklearn
    print(f"Python {platform.python_version()}, numpy {numpy.__version__}, scipy {scipy.__version__}, "
          f"pandas {pd.__version__}, scikit-learn {sklearn.__version__}")
    print(f"Ask or Act code: {F.AOA}")
    d = pd.DataFrame(F.task(("exploratory", "noisy", "isotonic_dw", [0, 1], 6,
                             os.path.join(ROOT, "results", "deadline_probs.csv"), 4_900_000, 1.0)))
    d = d[["method", "epoch", "robot", "scenario"] + COLS]
    if "--write" in sys.argv:
        d.to_csv(REF, index=False)
        print(f"wrote {len(d)} rows to {REF}")
        return
    ref = pd.read_csv(REF)
    m = ref.merge(d, on=["method", "epoch", "robot", "scenario"], suffixes=("_ref", ""))
    bad = [c for c in COLS if not (m[c].astype(float) - m[c + "_ref"].astype(float)).abs().le(1e-6).all()]
    if len(m) != len(ref) or bad:
        print(f"MISMATCH: {len(m)} of {len(ref)} rows matched; differing columns {bad}")
        sys.exit(1)
    print(f"OK: all {len(ref)} robot outcomes ({ref.method.nunique()} methods) match the reference.")


if __name__ == "__main__":
    main()
