"""System-architecture overview figure (paper/figures/architecture.pdf)."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "paper", "assets")
BLUE, ORANGE, AQUA, GRAY, INK, PALE = "#2a78d6", "#eb6834", "#1baf7a", "#8a8a85", "#2b2b29", "#f3f3f0"
plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "mathtext.fontset": "dejavuserif", "font.size": 8, "pdf.fonttype": 42})
ROBOT = np.asarray(Image.open(os.path.join(A, "turtlebot3_rgba.png")).convert("RGBA"))
WORKER = np.asarray(Image.open(os.path.join(A, "worker_front_rgba.png")).convert("RGBA"))
OPER = np.asarray(Image.open(os.path.join(A, "operator_rgba.png")).convert("RGBA"))


def img(ax, arr, x, y, h, z=3):
    w = h * arr.shape[1] / arr.shape[0]
    ax.imshow(arr, extent=(x - w / 2, x + w / 2, y, y + h), zorder=z, interpolation="lanczos")


def box(ax, x, y, w, h, fc, ec, lw=0.9, r=0.12, z=1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, zorder=z))


def arrow(ax, p, q, col=INK, lw=1.1, rad=0.0, ls="-", z=2):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=9, color=col, lw=lw, ls=ls,
                                 connectionstyle=f"arc3,rad={rad}", zorder=z, shrinkA=0, shrinkB=0))


fig, ax = plt.subplots(figsize=(7.2, 3.15))
ax.set_xlim(0, 15); ax.set_ylim(0, 6.6); ax.set_aspect("equal"); ax.axis("off")

# ---- robots, each in its own lane --------------------------------------------------------
ax.text(2.3, 6.35, "Robot fleet (one lane each)", ha="center", va="center", fontsize=8.5, color=INK, weight="bold")
lanes = [(5.05, "1", 0.08, "go"), (3.35, "2", 0.46, "ask"), (1.15, "N", 0.81, "yield")]
acol = {"go": AQUA, "ask": BLUE, "yield": ORANGE}
for y, k, p, act in lanes:
    ax.add_patch(Rectangle((0.15, y - 0.12), 4.3, 0.24, fc="#e4e4e0", ec="none", zorder=0))
    ax.plot([0.15, 4.45], [y, y], color="white", lw=0.8, ls=(0, (4, 3)), zorder=0.5)
    img(ax, ROBOT, 0.85, y - 0.1, 0.95)
    img(ax, WORKER, 3.25, y - 0.1, 1.15)
    ax.annotate("", xy=(3.25, y - 0.05), xytext=(3.9, y + 0.55),
                arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=0.8, ls=(0, (2, 1.5)), mutation_scale=7), zorder=2)
    ax.text(0.2, y + 0.98, f"$R_{{{k}}}$", fontsize=8, color=INK, va="center")
    ax.text(1.55, y + 0.62, f"$p_{{{k}}} = {p:.2f}$", fontsize=7.5, color=INK, va="center")
    ax.text(1.55, y + 0.25, act, fontsize=7.5, color=acol[act], va="center", weight="bold")
ax.text(2.3, 2.45, r"$\vdots$", ha="center", va="center", fontsize=11, color=GRAY)

# ---- coordinator ---------------------------------------------------------------------
cx, cw = 5.35, 4.3
box(ax, cx, 0.35, cw, 5.65, PALE, GRAY, r=0.18)
ax.text(cx + cw / 2, 6.35, "Fleet coordinator", ha="center", va="center", fontsize=8.5, color=INK, weight="bold")
steps = [(4.7, "Decision epoch", "robots reaching their deadlines\nwithin 1 s hold and report $p_i$"),
         (3.25, "QUBO, 2N binaries", r"$\sum_i$ unary costs$(p_i)$ $+\ q\,k(k-1)/2$" "\n" r"$+\ \lambda\,$(no ask-and-stop)"),
         (1.8, "Solver", "exact search in the loop;\nQAOA benchmarked offline"),
         (0.75, None, r"actions $a_i, s_i$: go, yield or ask")]
for y, t, body in steps:
    if t is None:
        ax.text(cx + cw / 2, y, body, ha="center", va="center", fontsize=7.3, color=INK)
        continue
    box(ax, cx + 0.25, y - 0.55, cw - 0.5, 1.12, "white", GRAY, lw=0.7, r=0.1, z=1.5)
    ax.text(cx + cw / 2, y + 0.3, t, ha="center", va="center", fontsize=7.6, color=INK, weight="bold", zorder=3)
    ax.text(cx + cw / 2, y - 0.17, body, ha="center", va="center", fontsize=6.9, color=INK, zorder=3, linespacing=1.15)
for y0, y1 in ((4.15, 3.82), (2.7, 2.37), (1.25, 0.98)):
    arrow(ax, (cx + cw / 2, y0), (cx + cw / 2, y1), col=GRAY, lw=0.9)

# robots <-> coordinator: probability in, action out
for y, k, p, act in lanes:
    arrow(ax, (4.5, y + 0.62), (cx, y + 0.62), col=INK, lw=0.9)
    arrow(ax, (cx, y + 0.2), (4.5, y + 0.2), col=acol[act], lw=1.3)
ax.text(4.92, 5.05 + 0.75, "$p_i$", fontsize=7.5, color=INK, ha="center", va="bottom")
ax.text(4.92, 5.05 + 0.05, "action", fontsize=6.6, color=INK, ha="center", va="top")

# ---- operator ---------------------------------------------------------------------------
ox = 13.25
ax.text(12.6, 6.35, "Remote operator", ha="center", va="center", fontsize=8.5, color=INK, weight="bold")
img(ax, OPER, ox, 2.55, 2.75)
ax.text(10.95, 4.45, "FIFO queue", fontsize=7.3, color=INK, ha="center")
for i, lab in enumerate(("$R_2$", "$R_5$", "$R_7$")):
    x = 11.5 - i * 0.58
    box(ax, x - 0.25, 3.6, 0.5, 0.5, "white", BLUE, lw=1.0, r=0.08, z=2)
    ax.text(x, 3.85, lab, ha="center", va="center", fontsize=6.8, color=BLUE, zorder=3)
arrow(ax, (cx + cw - 0.25, 1.8), (10.25, 3.55), col=BLUE, lw=1.1)
ax.text(10.0, 2.45, "questions\n(robots\nthat ask)", fontsize=7, color=BLUE, ha="left", va="center", linespacing=1.15)
arrow(ax, (11.78, 3.85), (12.15, 3.85), col=BLUE, lw=1.0)
ax.text(ox - 0.2, 2.05, r"service time $\tau_a$ per question" "\n" r"answer correct w.p. $\alpha$", ha="center", va="top", fontsize=6.9, color=INK, linespacing=1.25)
# answer back to the asking robot (R2), routed below and left of the fleet
path = [(ox - 0.2, 1.2), (ox - 0.2, 0.1), (0.06, 0.1), (0.06, 2.85), (0.85, 2.85)]
ax.plot(*zip(*path), color=BLUE, lw=1.1, ls=(0, (3, 2)), zorder=2, solid_joinstyle="round")
arrow(ax, (0.85, 2.85), (0.85, 3.15), col=BLUE, lw=1.1)
ax.text(ox - 0.0, 0.7, "answer:\ncrossing or\nnot crossing", fontsize=7, color=BLUE, ha="left", va="center", linespacing=1.15)

fig.subplots_adjust(0.005, 0.005, 0.995, 0.995)
fig.savefig(os.path.join(ROOT, "paper", "figures", "architecture.pdf"), dpi=600)
fig.savefig(os.path.join(ROOT, "paper", "figures", "architecture_preview.png"), dpi=220)
