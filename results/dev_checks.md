# Development checks after the probability fix (3 November 2026)

## Fixed band [0.2, 0.8] (`scripts/dev_band_check.py`, N = 6, 200 epochs, seeds 4 950 000+)

| condition | calibration | crossing robots | collisions | questions/epoch | delay (s) |
|---|---|---|---|---|---|
| noisy | conventional | 706 | 0 | 6.00 | 3.05 |
| noisy | decision-aware | 706 | 0 | 5.95 | 3.17 |
| nominal | conventional | 715 | 0 | 4.50 | 2.55 |
| nominal | decision-aware | 715 | 0 | 4.62 | 2.56 |

## Answer accuracy 0.9 (`scripts/dev_alpha_check.py`, N = 6 noisy, 200 epochs, seeds 4 960 000+)

The joint solver still assumes α = 1 here.

| calibration | method | crossing robots | collisions | questions/epoch | delay (s) |
|---|---|---|---|---|---|
| conventional | rule κ = 5.95 | 690 | 0 | 2.42 | 5.26 |
| conventional | joint | 690 | 8 | 2.44 | 3.93 |
| decision-aware | rule κ = 5.95 | 690 | 0 | 2.04 | 6.80 |
| decision-aware | joint | 690 | 7 | 2.11 | 3.97 |

Collision detection check: robots that never stop hit all 120 of 120 crossing pedestrians.
