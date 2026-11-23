"""Post hoc: split the joint solver's delay saving into decision timing and coordination.

  decomposition  results/posthoc/deadline.csv.gz + results/final/closed_loop_exploratory.csv.gz
                 -> results/posthoc/decomposition.csv
  load           results/posthoc/load.csv.gz -> results/posthoc/load_summary.csv, paper/figures/load.pdf

A per-robot family (deadline rule or early rule, kappa swept) is compared with the joint solver at the
joint solver's question rate: the delay of each epoch is interpolated linearly between the two kappa
values whose question rates bracket the joint solver's; 95% intervals by paired bootstrap over epochs.
"""
import os, sys
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PH = os.path.join(ROOT, "results", "posthoc")
B = 5000


def epoch_table(d):
    return d.groupby(["method", "epoch"]).agg(q=("n_asks", "sum"), d=("delay", "mean"),
                                              fb=("fallback", "sum")).reset_index()


def at_rate(ep, prefix, jq):
    """Per-epoch delay (and fallbacks) of a kappa-swept family interpolated to question rate jq."""
    fam = ep[ep.method.str.startswith(prefix)]
    s = fam.groupby("method")[["q", "d"]].mean().sort_values("q")
    if not (s.q.min() <= jq <= s.q.max()):
        return None
    lo = s[s.q <= jq].iloc[-1]; hi = s[s.q >= jq].iloc[0]
    w = 0.0 if hi.q == lo.q else (jq - lo.q) / (hi.q - lo.q)
    P = fam.pivot(index="epoch", columns="method", values="d")
    F = fam.pivot(index="epoch", columns="method", values="fb")
    return (1 - w) * P[lo.name] + w * P[hi.name], (1 - w) * F[lo.name] + w * F[hi.name]


def boot(x, rng):
    x = np.asarray(x); m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(B)]
    return x.mean(), *np.quantile(m, [0.025, 0.975])


def decomposition():
    rng = np.random.default_rng(7)
    dl = pd.read_csv(os.path.join(PH, "deadline.csv.gz"))
    ex = pd.read_csv(os.path.join(ROOT, "results", "final", "closed_loop_exploratory.csv.gz"))
    ex = ex[(ex.calibration == "isotonic_dw") & ex.method.isin(["joint", "rule_matched"])]
    rows = []
    for cond in ("noisy", "nominal"):
        for N in (6, 8):
            ep = epoch_table(dl[(dl.N == N) & (dl.condition == cond)])
            J = ep[ep.method == "joint"].set_index("epoch"); jq = J.q.mean()
            D, _ = at_rate(ep, "deadline_k", jq)
            R = epoch_table(ex[(ex.N == N) & (ex.condition == cond)])
            Rm = R[R.method == "rule_matched"].set_index("epoch"); Jx = R[R.method == "joint"].set_index("epoch")
            # identical epochs; a few epochs differ through ties broken differently by the two exact solvers
            print(cond, N, "epochs with a different joint delay:", int((np.abs(Jx.d.values - J.d.values) > 1e-6).sum()))
            coord = boot(D - J.d, rng); timing = boot(Rm.d - D, rng)
            col = lambda x: x[x.crossing == 1].collision.sum()
            rows.append(dict(condition=cond, N=N, q_joint=jq, q_rule=Rm.q.mean(), delay_joint=J.d.mean(),
                             delay_deadline=D.mean(), delay_rule=Rm.d.mean(),
                             timing=timing[0], timing_lo=timing[1], timing_hi=timing[2],
                             coord=coord[0], coord_lo=coord[1], coord_hi=coord[2],
                             coll_joint=col(dl[(dl.N == N) & (dl.condition == cond) & (dl.method == "joint")]),
                             coll_deadline=col(dl[(dl.N == N) & (dl.condition == cond) & dl.method.str.startswith("deadline")])))
    out = pd.DataFrame(rows); out.to_csv(os.path.join(PH, "decomposition.csv"), index=False)
    print(out.round(3).to_string())


def load_summary(src, dst, rng):
    d = pd.read_csv(os.path.join(PH, src))
    rows = []
    for (ta, N), x in d.groupby(["tau_a", "N"]):
        ep = epoch_table(x)
        J = ep[ep.method == "joint"].set_index("epoch"); jq = J.q.mean()
        r = dict(tau_a=ta, N=N, q_joint=jq, delay_joint=J.d.mean(), fb_joint=J.fb.mean(),
                 coll_joint=x[(x.method == "joint") & (x.crossing == 1)].collision.sum(), epochs=len(J))
        for fam, pre in (("deadline", "deadline_k"), ("rule", "rule_k")):
            z = at_rate(ep, pre, jq)
            if z is None:
                r[f"delay_{fam}"] = np.nan; continue
            D, F = z; m, lo, hi = boot(D - J.d, rng)
            r.update({f"delay_{fam}": D.mean(), f"fb_{fam}": F.mean(), f"save_{fam}": m, f"save_{fam}_lo": lo, f"save_{fam}_hi": hi})
        rows.append(r)
    out = pd.DataFrame(rows); out.to_csv(os.path.join(PH, dst), index=False)
    print(src); print(out.round(3).to_string())
    return out


def load():
    """Fig.: timeout scaled with the service time (T = 3 tau_a, joint limited to 3 questions) when
    results/posthoc/load_timeout3.csv.gz exists; the fixed 5 s timeout is shown dashed in panel (a)."""
    rng = np.random.default_rng(11)
    fixed = load_summary("load.csv.gz", "load_summary.csv", rng)
    scaled = load_summary("load_timeout3.csv.gz", "load_timeout3_summary.csv", rng) \
        if os.path.exists(os.path.join(PH, "load_timeout3.csv.gz")) else None
    main = scaled if scaled is not None else fixed
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "serif", "font.size": 8, "pdf.fonttype": 42})
    INK, cols = "#2b2b29", {1.5: "#2a78d6", 3.0: "#eb6834", 4.5: "#1baf7a"}
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.6))
    for ta, g in main.groupby("tau_a"):
        g = g.sort_values("N"); c = cols[ta]; lab = rf"$\tau_a$ = {ta:g} s"
        axs[0].errorbar(g.N, g.save_deadline, yerr=[g.save_deadline - g.save_deadline_lo, g.save_deadline_hi - g.save_deadline],
                        color=c, marker="o", ms=3.5, lw=1.2, capsize=2, label=lab)
        if scaled is not None:
            f = fixed[fixed.tau_a == ta].sort_values("N")
            axs[0].plot(f.N, f.save_deadline, color=c, lw=0.9, ls=":", alpha=0.8)
        axs[1].errorbar(g.N, g.save_rule, yerr=[g.save_rule - g.save_rule_lo, g.save_rule_hi - g.save_rule],
                        color=c, marker="o", ms=3.5, lw=1.2, capsize=2)
        axs[2].plot(g.N, g.q_joint, color=c, marker="o", ms=3.5, lw=1.2)
        axs[2].plot(g.N, g.fb_deadline, color=c, marker="^", ms=3.5, lw=1.0, ls="--")
    if scaled is not None:
        axs[0].plot([], [], color=INK, lw=0.9, ls=":", label="timeout 5 s")
    axs[0].axhline(0, color="#8a8a85", lw=0.7)
    axs[0].set_title("(a) Coordination\n(deadline rule $-$ joint solver)", fontsize=7.8, color=INK)
    axs[1].set_title("(b) Timing and coordination\n(per-robot rule $-$ joint solver)", fontsize=7.8, color=INK)
    axs[2].set_title("(c) Questions per epoch (joint, solid)\nunanswered (deadline rule, dashed)", fontsize=7.8, color=INK)
    axs[0].set_ylabel("delay saved per robot (s)"); axs[2].set_ylabel("per epoch")
    for ax in axs:
        ax.set_xticks([6, 8, 12]); ax.set_xlabel("robots per epoch $N$"); ax.grid(alpha=0.25, lw=0.5)
    axs[0].legend(fontsize=6.5, frameon=False)
    fig.tight_layout(w_pad=1.0); fig.savefig(os.path.join(ROOT, "paper", "figures", "load.pdf")); plt.close(fig)


if __name__ == "__main__":
    {"decomposition": decomposition, "load": load}[sys.argv[1]]()
