"""Shared helper for the epoch figures: which pedestrian positions to draw.

Positions are spaced along the walked path (at least STEP metres of walking apart, and at least
GAP metres from every position already drawn), so a pedestrian who pauses or walks slowly is not
drawn as a pile of overlapping figures. Returns (t, x, y, heading_deg) in the display frame
(x mirrored so the robot drives left to right), numbered later in time order.
"""
import numpy as np

STEP, GAP = 0.85, 0.6


def choose_marks(ped_traj, traj, ts, ylim=(-2.65, 2.6), max_marks=6, step=STEP, gap=GAP):
    T = np.arange(0, ts[-1] + 1e-9, 0.05)
    XY = np.array([ped_traj.pose_at(traj, ts, t)[:2] for t in T]) * np.array([-1, 1])
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(XY, axis=0).T))]
    marks, last_s = [], -np.inf
    for k, t in enumerate(T):
        x, y = XY[k]
        if not (ylim[0] < y < ylim[1]) or seg[k] - last_s < step:
            continue
        if any(np.hypot(x - mx, y - my) < gap for _, mx, my, _ in marks):
            continue
        j = min(k + 6, len(T) - 1)
        dx, dy = XY[j] - XY[k]
        head = np.degrees(np.arctan2(dy, dx)) if np.hypot(dx, dy) > 1e-3 else (marks[-1][3] if marks else 90.0)
        marks.append((t, x, y, head)); last_s = seg[k]
        if len(marks) == max_marks:
            break
    return marks


def pause_point(ped_traj, traj, ts, min_pause=0.8):
    """(x, y, duration) of the longest stop, in the display frame, or None."""
    T = np.arange(0, ts[-1] + 1e-9, 0.05)
    XY = np.array([ped_traj.pose_at(traj, ts, t)[:2] for t in T]) * np.array([-1, 1])
    still = np.r_[np.hypot(*np.diff(XY, axis=0).T) < 1e-4, False]
    best, run, start = None, 0, 0
    for k, s in enumerate(still):
        if s:
            if run == 0:
                start = k
            run += 1
        else:
            if run * 0.05 >= min_pause and (best is None or run > best[2]):
                best = (start, k, run)
            run = 0
    if best is None or best[0] == 0:
        return None
    x, y = XY[best[0]]
    return x, y, best[2] * 0.05
