"""Post-hoc analyses requested in review (NOT pre-registered; run after the final results).

Stages (all noisy/nominal tracking, decision-aware calibration):
  match   development seeds only: kappa* for the alpha-aware per-robot rule under the symmetric
          operator-error model with per-question answers (results/posthoc/match_sym.csv)
  alpha   final seeds 8 100 000 + e, e < 1000, N = 6 and 8, nominal and noisy, answers correct
          with probability 0.9 drawn independently per question:
            joint_a_pq / rule_a_pq           pre-registered cost model and kappa*
            joint_sym / rule_sym_matched     symmetric operator-error model, re-matched kappa*
            joint_sym_eps<e>                 symmetric model + per-robot collision-risk cap e
          (results/posthoc/alpha.csv.gz)
  deadline final seeds, N = 6 and 8, noisy, perfect answers: the joint solver (kappa = q = 1.5)
          and the same solver with no queue term (q = 0) for kappa in a grid. With q = 0 the
          problem separates, so each robot applies the per-robot cost rule, but at its deadline and
          inside the joint execution mode. This separates the gain of deciding at the deadline from
          the gain of coordinating questions (results/posthoc/deadline.csv.gz)
  grid    final seeds, e < 300, N = 6, noisy: answer accuracy x collision-to-stop cost ratio,
          joint solver (kappa = 1.5, q = 1.5) and per-robot rule (kappa = 1.5), symmetric model,
          per-question answers (results/posthoc/grid.csv.gz)

Symmetric operator-error model: a crossing pedestrian is reported as not crossing with
probability 1 - alpha (the robot drives on: collision risk), and a non-crossing pedestrian is
reported as crossing with probability 1 - alpha (the robot yields: one unnecessary stop):
  L(ask) = tau_a + kappa + (1 - alpha) [C p + tau_s (1 - p)].
Risk cap: an action is allowed only if its collision probability (go: p; ask: p (1 - alpha);
stop: 0) is at most eps; this fixes variables and keeps the problem a QUBO.
"""
import argparse, itertools, os, sys, time
from multiprocessing import Pool
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import final_closed_loop as F
from fleet_qubo.fleet_sim import run_fleet, make_policy_class, DT

TAU_S, TAU_A, Q, KAPPA = 10.0, 1.5, 1.5, 1.5
OUT = os.path.join(ROOT, "results", "posthoc")
_TABLES = {}


def table(n):
    if n not in _TABLES:
        _TABLES[n] = np.array(list(itertools.product(range(3), repeat=n)), dtype=np.int8)
    return _TABLES[n]


def unary(p, C, kappa, alpha, model):
    p = np.asarray(p, float)
    ask = TAU_A + kappa + C * p * (1 - alpha)
    if model == "symmetric":
        ask = ask + TAU_S * (1 - p) * (1 - alpha)
    return np.stack([C * p, TAU_S * (1 - p), ask], axis=1)


def solver(C, kappa, q, alpha, model, eps=None):
    def solve(ps, idx):
        ps = np.asarray(ps, float); n = len(ps)
        U = unary(ps, C, kappa, alpha, model)
        A = table(n)
        cost = U[np.arange(n), A].sum(axis=1)
        k = (A == 2).sum(axis=1); cost = cost + q * k * (k - 1) / 2
        if eps is not None:
            risk = np.stack([ps, np.zeros(n), ps * (1 - alpha)], axis=1)
            ok = (risk[np.arange(n), A] <= eps).all(axis=1)
            cost = np.where(ok, cost, np.inf)
        return list(A[int(np.argmin(cost))])
    return solve


def band(C, kappa, alpha, model):
    ask, gs = TAU_A + kappa, TAU_S / (C + TAU_S)
    if model == "symmetric":
        lo = (ask + (1 - alpha) * TAU_S) / (alpha * C + (1 - alpha) * TAU_S)
        hi = (alpha * TAU_S - ask) / (alpha * TAU_S + (1 - alpha) * C)
    else:
        lo, hi = ask / (C * alpha), (TAU_S - ask) / (TAU_S + C * (1 - alpha))
    return (lo, hi) if lo < hi else (gs, gs)


def methods(stage, N, kstar_sym=None, alpha=0.9, C=100.0):
    if stage == "alpha":
        m = [("joint_a_pq", "joint", dict(C=C, kappa=KAPPA, q=Q, alpha=alpha, model="collision_only")),
             ("rule_a_pq", "rule", dict(C=C, kappa=F.KAPPA_STAR_A[N], alpha=alpha, model="collision_only")),
             ("joint_sym", "joint", dict(C=C, kappa=KAPPA, q=Q, alpha=alpha, model="symmetric")),
             ("rule_sym_matched", "rule", dict(C=C, kappa=kstar_sym[N], alpha=alpha, model="symmetric"))]
        m += [(f"joint_sym_eps{e:g}", "joint", dict(C=C, kappa=KAPPA, q=Q, alpha=alpha, model="symmetric", eps=e))
              for e in (0.005, 0.01, 0.02)]
        return m
    if stage == "grid":
        return [("joint_sym", "joint", dict(C=C, kappa=KAPPA, q=Q, alpha=alpha, model="symmetric")),
                ("rule_sym", "rule", dict(C=C, kappa=KAPPA, alpha=alpha, model="symmetric"))]
    if stage == "deadline":
        return [("joint", "joint", dict(C=C, kappa=KAPPA, q=Q, alpha=1.0, model="collision_only"))] + \
               [(f"deadline_k{k:g}", "joint", dict(C=C, kappa=k, q=0.0, alpha=1.0, model="collision_only"))
                for k in (0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0)]
    if stage == "match":
        return [("joint_sym", "joint", dict(C=C, kappa=KAPPA, q=Q, alpha=alpha, model="symmetric"))] + \
               [(f"rule_sym_k{k:g}", "rule", dict(C=C, kappa=k, alpha=alpha, model="symmetric"))
                for k in (3.0, 4.0, 4.5, 5.0, 5.25, 5.5, 5.75, 6.0, 6.25, 6.5)]


def task(args):
    stage, cond, epochs, N, pool_path, seed0, cfg = args
    import generate_scenarios as gs, ped_traj, policy as aoa_policy, simulate_policies as sp
    FP = make_policy_class(aoa_policy.AskOrActPolicy)
    env = dict(build_trajectory=ped_traj.build_trajectory, pose_at=ped_traj.pose_at, ROBOT=gs.ROBOT, COLLISION_DIST=sp.COLLISION_DIST)
    model, calib = aoa_policy.load_predictor(F.MODEL, "mlp", "isotonic_dw", cond)
    pool = pd.read_csv(pool_path)
    pool = pool[(pool.condition == cond) & pool.reached_deadline & (pool.calibration == "isotonic_dw")].drop_duplicates("scenario").reset_index(drop=True)
    noise = gs.CONDITIONS[cond]["noise"]
    rows = []
    for e in epochs:
        rng = np.random.default_rng([seed0 + e, N])
        pick = pool.iloc[rng.choice(len(pool), size=N, replace=False)]
        u = rng.uniform(0, 1.0, size=N)
        labs = [gs.build("cafe", r.family, r.intent, int(r.seed), cond) for r in pick.itertuples()]
        shifts = [int(round((ui - td) / DT)) for ui, td in zip(u, pick.t_deadline)]
        for name, kind, kw in methods(stage, N, cfg.get("kstar"), cfg.get("alpha", 0.9), cfg.get("C", 100.0)):
            if kind == "joint":
                pols = [FP(model, calib, mode="joint", true_intent=l["intent"]) for l in labs]
                out, _, _ = run_fleet(labs, pols, noise, shifts, env, answer_accuracy=kw["alpha"], answer_seed=seed0 + e,
                                      joint=solver(kw["C"], kw["kappa"], kw["q"], kw["alpha"], kw["model"], kw.get("eps")))
            else:
                lo, hi = band(kw["C"], kw["kappa"], kw["alpha"], kw["model"])
                pols = [FP(model, calib, mode="independent", true_intent=l["intent"], p_low=lo, p_high=hi) for l in labs]
                out, _, _ = run_fleet(labs, pols, noise, shifts, env, answer_accuracy=kw["alpha"], answer_seed=seed0 + e)
            for i, (o, l) in enumerate(zip(out, labs)):
                rows.append(dict(stage=stage, N=N, condition=cond, epoch=e, robot=i, scenario=l["id"], method=name,
                                 alpha=kw["alpha"], C=kw["C"], crossing=int(l["intent"] == "crossing"),
                                 collision=int(o["collision"]), n_asks=o["n_asks"], delay=o["delay"],
                                 fallback=int(o["fallback"]), stopped_time=o["stopped_time"], action=o["action"]))
    return rows


def run(jobs, out, workers):
    rows = []
    if os.path.exists(out):
        old = pd.read_csv(out); rows = old.to_dict("records")
        done = set(zip(old.N, old.condition, old.alpha, old.C, old.epoch))
        jobs = [j for j in jobs if not all((j[3], j[1], j[6].get("alpha", 0.9), j[6].get("C", 100.0), e) in done for e in j[2])]
    print(f"{len(jobs)} jobs -> {out}", flush=True)
    t0 = time.time()
    with Pool(workers) as p:
        for i, r in enumerate(p.imap_unordered(task, jobs)):
            rows += r
            pd.DataFrame(rows).to_csv(out, index=False)
            print(f"{i + 1}/{len(jobs)} jobs, {time.time() - t0:.0f} s", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["match", "alpha", "grid", "deadline"])
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    dev_pool = os.path.join(ROOT, "results", "deadline_probs.csv")
    fin_pool = os.path.join(ROOT, "results", "final", "deadline_probs.csv")
    chunks = lambda n, c: [list(range(s, min(s + c, n))) for s in range(0, n, c)]
    if a.stage == "match":
        jobs = [("match", "noisy", ep, N, dev_pool, 4_990_000, {}) for N in (6, 8) for ep in chunks(500, 50)]
        out = os.path.join(OUT, "match_raw.csv.gz"); run(jobs, out, a.workers)
        d = pd.read_csv(out)
        s = d.groupby(["N", "method", "epoch"]).n_asks.sum().groupby(["N", "method"]).mean().rename("q").reset_index()
        rows = []
        for N in (6, 8):
            x = s[s.N == N]; jq = x[x.method == "joint_sym"].q.iloc[0]
            r = x[x.method.str.startswith("rule")].assign(k=lambda z: z.method.str[10:].astype(float)).sort_values("q")
            rows.append(dict(N=N, joint_q=jq, kappa_star=float(np.interp(jq, r.q, r.k))))
            print(r.to_string(), "\njoint", jq)
        pd.DataFrame(rows).to_csv(os.path.join(OUT, "match_sym.csv"), index=False); print(pd.DataFrame(rows))
    elif a.stage == "alpha":
        ks = pd.read_csv(os.path.join(OUT, "match_sym.csv")).set_index("N").kappa_star.to_dict()
        jobs = [("alpha", c, ep, N, fin_pool, 8_100_000, {"kstar": ks}) for N in (6, 8) for c in ("noisy", "nominal") for ep in chunks(1000, 50)]
        run(jobs, os.path.join(OUT, "alpha.csv.gz"), a.workers)
    elif a.stage == "deadline":
        jobs = [("deadline", "noisy", ep, N, fin_pool, 8_100_000, {"alpha": 1.0}) for N in (6, 8) for ep in chunks(1000, 50)]
        run(jobs, os.path.join(OUT, "deadline.csv.gz"), a.workers)
    else:
        jobs = [("grid", "noisy", ep, 6, fin_pool, 8_100_000, {"alpha": al, "C": TAU_S * r})
                for al in (0.8, 0.85, 0.9, 0.95, 1.0) for r in (2.5, 5.0, 10.0, 20.0, 50.0) for ep in chunks(300, 150)]
        run(jobs, os.path.join(OUT, "grid.csv.gz"), a.workers)


if __name__ == "__main__":
    main()
