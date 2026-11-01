"""Fleet epochs drawn from Ask or Act scenarios with real calibrated probabilities.

Each robot in an epoch is assigned one Ask or Act scenario that reaches the
decision deadline. The same scenarios are used for every calibrator (paired
design), so differences come only from the probabilities.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .instances import Instance, corridor_edges, default_budget, GO, STOP, ASK


class ScenarioPool:
    def __init__(self, path: str):
        d = pd.read_csv(path)
        d = d[d.reached_deadline]
        self.p = d.pivot_table(index=["condition", "scenario"], columns="calibration", values="p")
        meta = d.drop_duplicates(["condition", "scenario"]).set_index(["condition", "scenario"])
        self.meta = meta[["family", "intent", "crossing", "ambiguous"]]
        # keep only scenarios that reached the deadline under every calibrator
        self.p = self.p.dropna()
        self.calibrations = list(self.p.columns)

    def scenarios(self, condition: str) -> np.ndarray:
        return self.p.loc[condition].index.to_numpy()

    def draw(self, condition: str, N: int, rng: np.random.Generator) -> np.ndarray:
        return rng.choice(self.scenarios(condition), size=N, replace=False)

    def instance(self, condition: str, scenarios, calibration: str, layout: str = "none",
                 B: int | None = None, w: float = 2.0, v: float = 3.0, **cost) -> Instance:
        p = self.p.loc[condition].loc[list(scenarios), calibration].to_numpy(dtype=float)
        Ec, En = corridor_edges(len(p), layout, w=w, v=v)
        return Instance(p=p, B=default_budget(len(p)) if B is None else B, Ec=Ec, En=En,
                        name=f"{condition}_{calibration}_{layout}", **cost)

    def crossing(self, condition: str, scenarios) -> np.ndarray:
        return self.meta.loc[condition].loc[list(scenarios), "crossing"].to_numpy(dtype=int)


def realized(actions, crossing, alpha: float = 1.0, rng=None) -> dict:
    """Outcome of an epoch's actions against ground-truth intent.

    go & crossing         -> collision
    stop & not crossing   -> unnecessary stop
    ask                   -> question; follows the answer (truthful when alpha = 1)
    """
    actions = np.asarray(actions)
    crossing = np.asarray(crossing).astype(bool)
    asks = actions == ASK
    wrong = np.zeros_like(asks)
    if alpha < 1.0:
        rng = rng or np.random.default_rng(0)
        wrong = asks & (rng.random(len(actions)) > alpha)
    collide = ((actions == GO) & crossing) | (wrong & crossing)
    return {
        "collisions": int(collide.sum()),
        "crossing": int(crossing.sum()),
        "questions": int(asks.sum()),
        "unnecessary_stops": int(((actions == STOP) & ~crossing).sum()),
    }
