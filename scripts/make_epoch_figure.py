"""Paper figure: one final confirmatory epoch (N = 6, noisy, decision-aware), drawn lane by lane.

Each panel is one robot's lane: robot path, decision-deadline zone, the pedestrian's path with
numbered positions every 1.5 s, the calibrated probability at the deadline, and the action
chosen by the joint solver and by the matched per-robot rule. A bottom panel shows the operator's
queue under each method. The epoch is picked automatically (first epoch in which the two methods
differ for at least two robots and the joint solver asks); outcomes equal the confirmatory run.
"""
import os, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
exec(open(os.path.join(ROOT, "scripts", "make_paper_figures.py")).read().split("# Fig. 2")[0])
import final_closed_loop as F
import generate_scenarios as gs, ped_traj, policy as aoa_policy, simulate_policies as sp
from fleet_qubo.fleet_sim import run_fleet, make_policy_class, DT

R, OUT = os.path.join(ROOT, "results", "final"), os.path.join(ROOT, "paper", "figures")
N, SEED, COND, CAL = 6, 8_100_000, "noisy", "isotonic_dw"
FP = make_policy_class(aoa_policy.AskOrActPolicy)
env = dict(build_trajectory=ped_traj.build_trajectory, pose_at=ped_traj.pose_at, ROBOT=gs.ROBOT, COLLISION_DIST=sp.COLLISION_DIST)
model, calib = aoa_policy.load_predictor(F.MODEL, "mlp", CAL, COND)
pool = pd.read_csv(os.path.join(R, "deadline_probs.csv"))
pool = pool[(pool.condition == COND) & pool.reached_deadline & (pool.calibration == "isotonic_dw")].drop_duplicates("scenario").reset_index(drop=True)
noise = gs.CONDITIONS[COND]["noise"]

from PIL import Image
SPRITE = Image.open(os.path.join(ROOT, "paper", "assets", "pedestrian.png")).convert("RGBA")
def sprite(ax, x, y, heading_deg, alpha, size=0.72):
    """Top-down pedestrian (faces +y in the image) at (x, y), rotated to the walking heading."""
    im = SPRITE.rotate(heading_deg - 90.0, expand=True, resample=Image.BICUBIC)
    w = size * im.width / SPRITE.width; h = size * im.height / SPRITE.width
    ax.imshow(np.asarray(im), extent=(x - w / 2, x + w / 2, y - h / 2, y + h / 2), alpha=alpha, zorder=3, interpolation="bilinear")
NAMES = {0: "go", 1: "stop", 2: "ask", -1: "decided alone"}


def run(e):
    rng = np.random.default_rng([SEED + e, N])
    pick = pool.iloc[rng.choice(len(pool), size=N, replace=False)]
    u = rng.uniform(0, 1.0, size=N)
    labs = [gs.build("cafe", r.family, r.intent, int(r.seed), COND) for r in pick.itertuples()]
    shifts = [int(round((ui - td) / DT)) for ui, td in zip(u, pick.t_deadline)]
    jp = [FP(model, calib, mode="joint", true_intent=l["intent"]) for l in labs]
    jo, _, _ = run_fleet(labs, jp, noise, shifts, env, joint=F.solver(F.KAPPA, F.Q, None, 1.0))
    lo, hi = F.band(F.KAPPA_STAR[N])
    rp = [FP(model, calib, mode="independent", true_intent=l["intent"], p_low=lo, p_high=hi) for l in labs]
    ro, _, _ = run_fleet(labs, rp, noise, shifts, env)
    return labs, shifts, jp, jo, rp, ro


def deadline_p(pol):
    for d in pol.decisions:
        if d[2] != "" and float(d[5]) <= 0.6:
            return float(d[2])
    return np.nan


def rule_action(pol, o):
    return "ask" if o["n_asks"] else ("stop" if o["stopped_time"] > 0 else "go")


conf = pd.read_csv(os.path.join(R, "closed_loop_confirmatory.csv.gz"))
for e in range(200):
    labs, shifts, jp, jo, rp, ro = run(e)
    ja = [NAMES[o["action"]] for o in jo]; ra = [rule_action(p, o) for p, o in zip(rp, ro)]
    fams = {l["family"] for l in labs}
    if sum(a != b for a, b in zip(ja, ra)) >= 2 and "ask" in ja and fams & {"hesitant", "late_turn"} and \
            len({l["intent"] for l in labs}) == 2:
        break
# consistency with the frozen confirmatory run
c = conf[(conf.N == N) & (conf.epoch == e)]
for m, outs in (("joint", jo), ("rule_matched", ro)):
    cc = c[c.method == m].sort_values("robot")
    assert list(cc.delay) == [o["delay"] for o in outs] and list(cc.n_asks) == [o["n_asks"] for o in outs], m
print("epoch", e, [l["id"] for l in labs])

INK2 = "#333333"; XC, NC = "#d0453a", "#1d8a5a"
fig = plt.figure(figsize=(7.2, 8.0))
gsp = fig.add_gridspec(3, 3, height_ratios=[1, 1, 0.42], hspace=0.32, wspace=0.05)
order = np.argsort([-s for s in shifts])           # robots in order of reaching their deadline
for n, i in enumerate(order):
    ax = fig.add_subplot(gsp[n // 3, n % 3]); lab = labs[i]
    ax.set_xlim(-3.45, 1.15); ax.set_ylim(-2.85, 2.95); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((-3.45, -0.25), 4.6, 0.5, color="#ececea", lw=0, zorder=0))
    ax.annotate("", xy=(1.1, 0.05), xytext=(-2.9, 0.05), arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.2, ls="--"))
    ax.add_patch(Circle((-2.9, 0.05), 0.17, fc="white", ec=BLUE, lw=1.5, zorder=3))
    ax.add_patch(Circle((-2.9, 0.05), 0.07, fc=BLUE, lw=0, zorder=4))
    traj = ped_traj.build_trajectory(lab["start"], lab["plan"], lab["human_speed"]); ts = [s[0] for s in traj]
    px = -lab["start"][0]                                   # pedestrian's position along the robot's line
    ax.add_patch(Rectangle((px - 1.0, -0.25), 0.4, 0.5, color="#f6dfcc", lw=0, zorder=0))
    ax.plot([px - 0.6, px - 0.6], [-0.32, 0.42], color="#c0622d", lw=1.6, zorder=2)
    col = XC if lab["intent"] == "crossing" else NC
    T = np.linspace(0, ts[-1], 200)
    P = np.array([ped_traj.pose_at(traj, ts, t)[:2] for t in T])
    ax.plot(-P[:, 0], P[:, 1], "--", color=col, lw=1.4, zorder=2)
    ax.annotate("", xy=(-P[-1, 0], P[-1, 1]), xytext=(-P[-6, 0], P[-6, 1]), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.2))
    from epoch_marks import choose_marks, pause_point
    mk = choose_marks(ped_traj, traj, ts)
    for k, (t, x, y, hd) in enumerate(mk):
        sprite(ax, x, y, hd, 0.35 + 0.65 * (k + 1) / len(mk))
        ax.text(x - 0.42, y + 0.02, str(k + 1), fontsize=6, color=INK2, ha="right", va="center")
    pz = pause_point(ped_traj, traj, ts)
    if pz is not None:
        txt = f"pauses {pz[2]:.1f} s" + (",\nturns back" if lab["family"] == "hesitant" and lab["intent"] != "crossing" else "")
        ax.text(pz[0] + 0.45, pz[1], txt, fontsize=5.8, color=INK, ha="left", va="center",
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.8))
    fam = lab["family"].replace("_", " ").replace("noncross", "non-cross")
    ax.set_title(f"R{n + 1}: {fam}, {lab['intent'].replace('_', ' ')}", fontsize=7.8, color=INK, pad=2)
    jtxt = f"joint: {NAMES[jo[i]['action']].upper()}" if jo[i]["action"] >= 0 else "joint: decided alone"
    ja_, ra_ = (NAMES[jo[i]["action"]] if jo[i]["action"] >= 0 else "alone"), rule_action(rp[i], ro[i])
    ax.text(0.5, -0.015, f"$p$ = {deadline_p(jp[i]):.2f} at the deadline\njoint: {ja_.upper()} ({jo[i]['delay']:.1f} s)   rule: {ra_.upper()} ({ro[i]['delay']:.1f} s)",
            transform=ax.transAxes, fontsize=6.4, ha="center", va="top", color=INK)
    if n == 0:
        ax.text(-2.9, 0.45, "robot", fontsize=6.5, color=INK, ha="center", fontweight="bold")
        ax.text(1.1, 0.4, "to goal", fontsize=6.5, color=BLUE, ha="right")
        ax.annotate("deadline\n(0.6 m)", xy=(px - 0.6, -0.3), xytext=(-3.35, -1.2), fontsize=6, color="#a0522d",
                    ha="left", arrowprops=dict(arrowstyle="-", color="#a0522d", lw=0.7))
# operator queue
ax = fig.add_subplot(gsp[2, :])
for row, (name, pols, outs) in enumerate((("Matched rule", rp, ro), ("Joint solver", jp, jo))):
    asks = sorted((a["t"] + shifts[i] * DT, n + 1) for n, i in enumerate(order) for a in pols[i].asks)
    free = -np.inf
    for t, r in asks:
        start = max(t, free); free = start + 1.5
        ax.add_patch(FancyBboxPatch((start, row - 0.3), 1.45, 0.6, boxstyle="round,pad=0,rounding_size=0.08",
                                    fc=[ORANGE, BLUE][row], ec="white", lw=1, alpha=0.9))
        ax.text(start + 0.72, row, f"R{r}", ha="center", va="center", fontsize=6.5, color="white")
        if start > t + 1e-6:
            ax.plot([t, start], [row, row], color=GRAY, lw=1, ls=":")
            ax.plot(t, row, "|", color=GRAY, ms=6)
ax.set_yticks([0, 1], ["Matched rule", "Joint solver"]); ax.set_ylim(-0.6, 1.6)
ax.set_xlabel("Time (s); boxes are questions being answered (1.5 s each), dotted lines waiting")
ax.set_title("Operator queue in this epoch", fontsize=8.5, color=INK); ax.grid(axis="y", visible=False)
from matplotlib.lines import Line2D
fig.legend(handles=[Line2D([], [], color=XC, ls="--", label="pedestrian crosses"),
                    Line2D([], [], color=NC, ls="--", label="pedestrian does not cross"),
                    Line2D([], [], color=BLUE, ls="--", label="robot path"),
                    Rectangle((0, 0), 1, 1, fc="#f6dfcc", label="engaged: observe until the deadline")],
           loc="lower center", ncol=4, fontsize=7, bbox_to_anchor=(0.5, 0.0))
fig.subplots_adjust(top=0.97, bottom=0.08, left=0.12, right=0.99)
fig.savefig(os.path.join(OUT, "epoch.pdf")); plt.close(fig)
print("written")
