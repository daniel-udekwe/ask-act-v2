"""Paper figure (oblique 3D version of make_epoch_figure.py): one final confirmatory epoch (N = 6, noisy, decision-aware), drawn lane by lane.

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

INK2 = "#333333"; XC, NC = "#d0453a", "#1d8a5a"; ROBOTC = "#3a3a38"
# ---- oblique "3D" projection of the ground plane: screen = A @ (x, y) + (0, z)
from matplotlib.transforms import Affine2D
from matplotlib.patches import Polygon, Ellipse
SH, SY = 0.22, 0.62
A = np.array([[1.0, SH], [0.0, SY]])
def P(x, y, z=0.0):
    x, y = np.asarray(x, float), np.asarray(y, float)
    return x + SH * y, SY * y + z
def poly(ax, pts, z=0.0, **kw):
    xs, ys = P([p[0] for p in pts], [p[1] for p in pts], z)
    ax.add_patch(Polygon(np.c_[xs, ys], closed=True, **kw))
def quad_vertical(ax, x0, y0, x1, y1, h, **kw):
    a, b = P([x0, x1], [y0, y1]); ax.add_patch(Polygon([(a[0], b[0]), (a[1], b[1]), (a[1], b[1] + h), (a[0], b[0] + h)], closed=True, **kw))
def ground_tf(ax, z=0.0):
    return Affine2D(np.array([[1, SH, 0], [0, SY, z], [0, 0, 1]])) + ax.transData
def sprite3d(ax, x, y, heading_deg, alpha, size=0.85, lift=0.06):
    im = SPRITE.rotate(heading_deg - 90.0, expand=True, resample=Image.BICUBIC)
    w = size * im.width / SPRITE.width; h = size * im.height / SPRITE.width
    sx, sy = P(x + 0.07, y - 0.07)
    ax.add_patch(Ellipse((sx, sy), 0.62, 0.62 * SY, fc="black", alpha=0.10 * alpha + 0.04, lw=0, zorder=3))
    ax.imshow(np.asarray(im), extent=(x - w / 2, x + w / 2, y - h / 2, y + h / 2), alpha=alpha, zorder=4,
              interpolation="lanczos", interpolation_stage="rgba", transform=ground_tf(ax, lift))
ROBOT_IMG = Image.open(os.path.join(ROOT, "paper", "assets", "turtlebot3_rgba.png")).convert("RGBA")
def robot3d(ax, x, y, h=0.85):
    """TurtleBot3 Burger drawn upright at ground point (x, y); not to scale (enlarged for visibility)."""
    cx, cy = P(x, y)
    w = h * ROBOT_IMG.width / ROBOT_IMG.height
    ax.add_patch(Ellipse((cx + 0.05, cy - 0.02), 1.1 * w, 1.1 * w * SY, fc="black", alpha=0.18, lw=0, zorder=3))
    ax.imshow(np.asarray(ROBOT_IMG), extent=(cx - w / 2, cx + w / 2, cy - 0.12 * h, cy + 0.88 * h), zorder=6, interpolation="lanczos", interpolation_stage="rgba")

X0, X1, Y0, Y1 = -3.45, 1.25, -2.85, 2.9
fig = plt.figure(figsize=(7.2, 5.9))
gsp = fig.add_gridspec(3, 3, height_ratios=[1, 1, 0.7], hspace=0.42, wspace=0.03)
order = np.argsort([-s for s in shifts])
for n, i in enumerate(order):
    ax = fig.add_subplot(gsp[n // 3, n % 3]); lab = labs[i]
    cx, cy = P([X0, X1, X0, X1], [Y0, Y0, Y1, Y1])
    ax.set_xlim(cx.min() - 0.05, cx.max() + 0.05); ax.set_ylim(cy.min() - 0.12, cy.max() + 0.25); ax.set_aspect("equal"); ax.axis("off")
    # floor with a 1 m grid
    poly(ax, [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)], fc="#f5f4ef", ec="#d9d7cf", lw=0.6, zorder=0)
    for gx in np.arange(-3, 1.01, 1.0):
        ax.plot(*P([gx, gx], [Y0, Y1]), color="#e4e2da", lw=0.5, zorder=0)
    for gy in np.arange(-2, 2.01, 1.0):
        ax.plot(*P([X0, X1], [gy, gy]), color="#e4e2da", lw=0.5, zorder=0)
    # walkway slab: front face, then top
    quad_vertical(ax, X0, -0.3, X1, -0.3, -0.07, fc="#c9c7c0", lw=0, zorder=1)
    poly(ax, [(X0, -0.3), (X1, -0.3), (X1, 0.35), (X0, 0.35)], fc="#e6e5e0", ec="#cfcdc5", lw=0.5, zorder=1)
    traj = ped_traj.build_trajectory(lab["start"], lab["plan"], lab["human_speed"]); ts = [s[0] for s in traj]
    px = -lab["start"][0]
    poly(ax, [(px - 1.0, -0.3), (px - 0.6, -0.3), (px - 0.6, 0.35), (px - 1.0, 0.35)], fc="#f6dfcc", lw=0, zorder=1)
    # deadline: a translucent vertical gate across the walkway
    quad_vertical(ax, px - 0.6, -0.3, px - 0.6, 0.35, 0.7, fc="#e08a4f", alpha=0.35, ec="#c0622d", lw=0.9, zorder=2)
    ax.annotate("", xy=P(1.2, 0.03), xytext=P(-2.9, 0.03), arrowprops=dict(arrowstyle="-|>", color=ROBOTC, lw=1.3, ls="--"), zorder=2)
    col = XC if lab["intent"] == "crossing" else NC
    T = np.linspace(0, ts[-1], 200)
    Q = np.array([ped_traj.pose_at(traj, ts, t)[:2] for t in T]); Q = Q[(Q[:, 1] > Y0) & (Q[:, 1] < Y1)]
    ax.plot(*P(-Q[:, 0], Q[:, 1]), "--", color=col, lw=1.4, zorder=2)
    ax.annotate("", xy=P(-Q[-1, 0], Q[-1, 1]), xytext=P(-Q[-6, 0], Q[-6, 1]), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.2))
    from epoch_marks import choose_marks, pause_point
    mk = choose_marks(ped_traj, traj, ts, ylim=(Y0 + 0.2, Y1 - 0.3))
    for k, (t, x, y, hd) in sorted(enumerate(mk), key=lambda q: -q[1][2]):     # far (larger y) first
        sprite3d(ax, x, y, hd, 0.35 + 0.65 * (k + 1) / len(mk))
        tx, ty = P(x - 0.5, y)
        ax.text(tx, ty, str(k + 1), fontsize=6, color=INK2, ha="right", va="center", zorder=7)
    pz = pause_point(ped_traj, traj, ts)
    if pz is not None:
        tx, ty = P(pz[0] + 0.5, pz[1])
        txt = f"pauses {pz[2]:.1f} s" + (",\nturns back" if lab["family"] == "hesitant" and lab["intent"] != "crossing" else "")
        ax.text(tx, ty, txt, fontsize=5.8, color=INK, ha="left", va="center", zorder=8,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.8))
    robot3d(ax, -2.9, 0.03)
    fam = lab["family"].replace("_", " ").replace("noncross", "non-cross")
    ax.set_title(f"R{n + 1}: {fam}, {lab['intent'].replace('_', ' ')}", fontsize=7.8, color=INK, pad=1)
    ja_, ra_ = (NAMES[jo[i]["action"]] if jo[i]["action"] >= 0 else "alone"), rule_action(rp[i], ro[i])
    ax.text(0.5, -0.02, f"$p$ = {deadline_p(jp[i]):.2f} at the deadline\njoint: {ja_.upper()} ({jo[i]['delay']:.1f} s)   rule: {ra_.upper()} ({ro[i]['delay']:.1f} s)",
            transform=ax.transAxes, fontsize=6.4, ha="center", va="top", color=INK)
    if n == 0:
        ax.text(*P(-2.9, 0.03, 0.98), "robot", fontsize=6.5, color=INK, ha="center", fontweight="bold", zorder=8)
        ax.text(*P(1.2, 0.55), "to goal", fontsize=6.5, color=ROBOTC, ha="right", zorder=8)
        ax.annotate("deadline\ngate", xy=P(px - 0.6, -0.3, 0.35), xytext=P(-3.3, -2.3, 0.0), fontsize=6, color="#a0522d",
                    ha="left", arrowprops=dict(arrowstyle="-", color="#a0522d", lw=0.7), zorder=8)
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
                    Line2D([], [], color=ROBOTC, ls="--", label="robot path"),
                    Rectangle((0, 0), 1, 1, fc="#f6dfcc", label="engaged: observe until the deadline"),
                    Rectangle((0, 0), 1, 1, fc="#e08a4f", alpha=0.35, ec="#c0622d", label="decision deadline (pedestrian 0.6 m ahead)")],
           loc="lower center", ncol=3, fontsize=7, bbox_to_anchor=(0.5, 0.0))
fig.subplots_adjust(top=0.97, bottom=0.15, left=0.12, right=0.99)
fig.savefig(os.path.join(OUT, "epoch_3d.pdf"), dpi=900); plt.close(fig)
print("written")
