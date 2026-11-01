# Epoch-level evaluation with real calibrated probabilities

Development pool only (scenario seeds 4000-4099, 500 epochs per cell). Collisions are per crossing robot, with 95% Wilson intervals.

## Probabilities at the deadline

ECE of the probability at the deadline (one value per scenario).

| Condition | Calibration | Scenarios | ECE at deadline | Share in ask band |
| --- | --- | --- | --- | --- |
| nominal | isotonic | 701 | 0.136 | 0.78 |
| nominal | isotonic_dw | 701 | 0.087 | 0.82 |
| nominal | raw | 701 | 0.183 | 0.77 |
| noisy | isotonic | 708 | 0.190 | 0.81 |
| noisy | isotonic_dw | 708 | 0.120 | 0.96 |
| noisy | raw | 708 | 0.248 | 0.61 |

## Outcomes by solver and calibration

| Condition | N | Layout | Calibration | Solver | Collisions (%) | 95% CI | Questions / epoch | Unnecessary stops / epoch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nominal | 6 | none | isotonic | exact | 33.3 | [31.1, 35.5] | 2.00 | 0.38 |
| nominal | 6 | none | isotonic | greedy | 33.0 | [30.9, 35.3] | 2.00 | 0.39 |
| nominal | 6 | none | isotonic | independent_rule | 3.2 | [2.4, 4.1] | 2.00 | 0.92 |
| nominal | 6 | none | isotonic_dw | exact | 6.8 | [5.7, 8.1] | 2.00 | 0.89 |
| nominal | 6 | none | isotonic_dw | greedy | 6.8 | [5.7, 8.1] | 2.00 | 0.90 |
| nominal | 6 | none | isotonic_dw | independent_rule | 0.6 | [0.3, 1.1] | 2.00 | 1.03 |
| nominal | 6 | none | raw | exact | 41.2 | [38.9, 43.6] | 2.00 | 0.25 |
| nominal | 6 | none | raw | greedy | 41.3 | [39.0, 43.6] | 2.00 | 0.25 |
| nominal | 6 | none | raw | independent_rule | 4.5 | [3.6, 5.6] | 2.00 | 0.90 |
| nominal | 6 | single | isotonic | exact | 46.2 | [43.9, 48.6] | 1.99 | 0.17 |
| nominal | 6 | single | isotonic | greedy | 33.0 | [30.9, 35.3] | 2.00 | 0.39 |
| nominal | 6 | single | isotonic | independent_rule | 3.2 | [2.4, 4.1] | 2.00 | 0.92 |
| nominal | 6 | single | isotonic_dw | exact | 36.6 | [34.4, 38.9] | 2.00 | 0.32 |
| nominal | 6 | single | isotonic_dw | greedy | 6.8 | [5.7, 8.1] | 2.00 | 0.90 |
| nominal | 6 | single | isotonic_dw | independent_rule | 0.6 | [0.3, 1.1] | 2.00 | 1.03 |
| nominal | 6 | single | raw | exact | 49.7 | [47.4, 52.1] | 1.96 | 0.13 |
| nominal | 6 | single | raw | greedy | 41.3 | [39.0, 43.6] | 2.00 | 0.25 |
| nominal | 6 | single | raw | independent_rule | 4.5 | [3.6, 5.6] | 2.00 | 0.90 |
| nominal | 6 | tjunction | isotonic | exact | 43.8 | [41.4, 46.1] | 1.99 | 0.20 |
| nominal | 6 | tjunction | isotonic | greedy | 33.0 | [30.9, 35.3] | 2.00 | 0.39 |
| nominal | 6 | tjunction | isotonic | independent_rule | 3.2 | [2.4, 4.1] | 2.00 | 0.92 |
| nominal | 6 | tjunction | isotonic_dw | exact | 34.2 | [32.0, 36.5] | 2.00 | 0.38 |
| nominal | 6 | tjunction | isotonic_dw | greedy | 6.8 | [5.7, 8.1] | 2.00 | 0.90 |
| nominal | 6 | tjunction | isotonic_dw | independent_rule | 0.6 | [0.3, 1.1] | 2.00 | 1.03 |
| nominal | 6 | tjunction | raw | exact | 47.2 | [44.9, 49.5] | 1.98 | 0.19 |
| nominal | 6 | tjunction | raw | greedy | 41.3 | [39.0, 43.6] | 2.00 | 0.25 |
| nominal | 6 | tjunction | raw | independent_rule | 4.5 | [3.6, 5.6] | 2.00 | 0.90 |
| nominal | 8 | none | isotonic | exact | 27.9 | [26.1, 29.8] | 3.00 | 0.55 |
| nominal | 8 | none | isotonic | greedy | 27.7 | [25.9, 29.6] | 3.00 | 0.54 |
| nominal | 8 | none | isotonic | independent_rule | 2.4 | [1.8, 3.1] | 3.00 | 1.20 |
| nominal | 8 | none | isotonic_dw | exact | 5.2 | [4.4, 6.2] | 3.00 | 1.13 |
| nominal | 8 | none | isotonic_dw | greedy | 5.2 | [4.4, 6.2] | 3.00 | 1.17 |
| nominal | 8 | none | isotonic_dw | independent_rule | 0.6 | [0.3, 1.0] | 3.00 | 1.35 |
| nominal | 8 | none | raw | exact | 36.7 | [34.7, 38.6] | 3.00 | 0.35 |
| nominal | 8 | none | raw | greedy | 36.7 | [34.7, 38.6] | 3.00 | 0.35 |
| nominal | 8 | none | raw | independent_rule | 3.4 | [2.7, 4.2] | 3.00 | 1.18 |
| nominal | 8 | single | isotonic | exact | 43.4 | [41.4, 45.4] | 2.99 | 0.15 |
| nominal | 8 | single | isotonic | greedy | 27.7 | [25.9, 29.6] | 3.00 | 0.54 |
| nominal | 8 | single | isotonic | independent_rule | 2.4 | [1.8, 3.1] | 3.00 | 1.20 |
| nominal | 8 | single | isotonic_dw | exact | 37.1 | [35.2, 39.1] | 3.00 | 0.32 |
| nominal | 8 | single | isotonic_dw | greedy | 5.2 | [4.4, 6.2] | 3.00 | 1.17 |
| nominal | 8 | single | isotonic_dw | independent_rule | 0.6 | [0.3, 1.0] | 3.00 | 1.35 |
| nominal | 8 | single | raw | exact | 46.1 | [44.1, 48.2] | 2.95 | 0.11 |
| nominal | 8 | single | raw | greedy | 36.7 | [34.7, 38.6] | 3.00 | 0.35 |
| nominal | 8 | single | raw | independent_rule | 3.4 | [2.7, 4.2] | 3.00 | 1.18 |
| nominal | 8 | tjunction | isotonic | exact | 42.7 | [40.7, 44.7] | 2.99 | 0.18 |
| nominal | 8 | tjunction | isotonic | greedy | 27.7 | [25.9, 29.6] | 3.00 | 0.54 |
| nominal | 8 | tjunction | isotonic | independent_rule | 2.4 | [1.8, 3.1] | 3.00 | 1.20 |
| nominal | 8 | tjunction | isotonic_dw | exact | 34.7 | [32.8, 36.7] | 3.00 | 0.38 |
| nominal | 8 | tjunction | isotonic_dw | greedy | 5.2 | [4.4, 6.2] | 3.00 | 1.17 |
| nominal | 8 | tjunction | isotonic_dw | independent_rule | 0.6 | [0.3, 1.0] | 3.00 | 1.35 |
| nominal | 8 | tjunction | raw | exact | 44.7 | [42.6, 46.7] | 2.97 | 0.16 |
| nominal | 8 | tjunction | raw | greedy | 36.7 | [34.7, 38.6] | 3.00 | 0.35 |
| nominal | 8 | tjunction | raw | independent_rule | 3.4 | [2.7, 4.2] | 3.00 | 1.18 |
| noisy | 6 | none | isotonic | exact | 56.1 | [53.7, 58.4] | 2.00 | 0.19 |
| noisy | 6 | none | isotonic | greedy | 56.1 | [53.7, 58.4] | 2.00 | 0.19 |
| noisy | 6 | none | isotonic | independent_rule | 18.0 | [16.2, 19.8] | 2.00 | 1.19 |
| noisy | 6 | none | isotonic_dw | exact | 42.9 | [40.6, 45.2] | 2.00 | 0.53 |
| noisy | 6 | none | isotonic_dw | greedy | 43.1 | [40.8, 45.4] | 2.00 | 0.53 |
| noisy | 6 | none | isotonic_dw | independent_rule | 1.9 | [1.4, 2.7] | 2.00 | 1.63 |
| noisy | 6 | none | raw | exact | 52.2 | [49.9, 54.6] | 1.96 | 0.29 |
| noisy | 6 | none | raw | greedy | 52.2 | [49.9, 54.6] | 1.96 | 0.29 |
| noisy | 6 | none | raw | independent_rule | 32.4 | [30.2, 34.6] | 1.96 | 0.78 |
| noisy | 6 | single | isotonic | exact | 60.4 | [58.1, 62.7] | 1.99 | 0.09 |
| noisy | 6 | single | isotonic | greedy | 56.1 | [53.7, 58.4] | 2.00 | 0.19 |
| noisy | 6 | single | isotonic | independent_rule | 18.0 | [16.2, 19.8] | 2.00 | 1.19 |
| noisy | 6 | single | isotonic_dw | exact | 55.1 | [52.7, 57.4] | 2.00 | 0.23 |
| noisy | 6 | single | isotonic_dw | greedy | 43.1 | [40.8, 45.4] | 2.00 | 0.53 |
| noisy | 6 | single | isotonic_dw | independent_rule | 1.9 | [1.4, 2.7] | 2.00 | 1.63 |
| noisy | 6 | single | raw | exact | 57.3 | [55.0, 59.6] | 1.88 | 0.19 |
| noisy | 6 | single | raw | greedy | 52.2 | [49.9, 54.6] | 1.96 | 0.29 |
| noisy | 6 | single | raw | independent_rule | 32.4 | [30.2, 34.6] | 1.96 | 0.78 |
| noisy | 6 | tjunction | isotonic | exact | 59.4 | [57.1, 61.7] | 2.00 | 0.12 |
| noisy | 6 | tjunction | isotonic | greedy | 56.1 | [53.7, 58.4] | 2.00 | 0.19 |
| noisy | 6 | tjunction | isotonic | independent_rule | 18.0 | [16.2, 19.8] | 2.00 | 1.19 |
| noisy | 6 | tjunction | isotonic_dw | exact | 53.0 | [50.7, 55.4] | 2.00 | 0.29 |
| noisy | 6 | tjunction | isotonic_dw | greedy | 43.1 | [40.8, 45.4] | 2.00 | 0.53 |
| noisy | 6 | tjunction | isotonic_dw | independent_rule | 1.9 | [1.4, 2.7] | 2.00 | 1.63 |
| noisy | 6 | tjunction | raw | exact | 54.9 | [52.6, 57.3] | 1.95 | 0.22 |
| noisy | 6 | tjunction | raw | greedy | 52.2 | [49.9, 54.6] | 1.96 | 0.29 |
| noisy | 6 | tjunction | raw | independent_rule | 32.4 | [30.2, 34.6] | 1.96 | 0.78 |
| noisy | 8 | none | isotonic | exact | 52.7 | [50.6, 54.7] | 3.00 | 0.16 |
| noisy | 8 | none | isotonic | greedy | 52.8 | [50.7, 54.8] | 3.00 | 0.17 |
| noisy | 8 | none | isotonic | independent_rule | 16.3 | [14.8, 17.9] | 3.00 | 1.53 |
| noisy | 8 | none | isotonic_dw | exact | 37.8 | [35.9, 39.8] | 3.00 | 0.65 |
| noisy | 8 | none | isotonic_dw | greedy | 37.9 | [35.9, 39.9] | 3.00 | 0.66 |
| noisy | 8 | none | isotonic_dw | independent_rule | 1.8 | [1.4, 2.5] | 3.00 | 2.02 |
| noisy | 8 | none | raw | exact | 47.6 | [45.6, 49.7] | 2.96 | 0.31 |
| noisy | 8 | none | raw | greedy | 47.6 | [45.6, 49.7] | 2.96 | 0.31 |
| noisy | 8 | none | raw | independent_rule | 30.4 | [28.6, 32.4] | 2.96 | 0.93 |
| noisy | 8 | single | isotonic | exact | 57.9 | [55.8, 59.9] | 2.98 | 0.06 |
| noisy | 8 | single | isotonic | greedy | 52.8 | [50.7, 54.8] | 3.00 | 0.17 |
| noisy | 8 | single | isotonic | independent_rule | 16.3 | [14.8, 17.9] | 3.00 | 1.53 |
| noisy | 8 | single | isotonic_dw | exact | 52.5 | [50.4, 54.5] | 3.00 | 0.21 |
| noisy | 8 | single | isotonic_dw | greedy | 37.9 | [35.9, 39.9] | 3.00 | 0.66 |
| noisy | 8 | single | isotonic_dw | independent_rule | 1.8 | [1.4, 2.5] | 3.00 | 2.02 |
| noisy | 8 | single | raw | exact | 55.2 | [53.1, 57.2] | 2.80 | 0.14 |
| noisy | 8 | single | raw | greedy | 47.6 | [45.6, 49.7] | 2.96 | 0.31 |
| noisy | 8 | single | raw | independent_rule | 30.4 | [28.6, 32.4] | 2.96 | 0.93 |
| noisy | 8 | tjunction | isotonic | exact | 57.2 | [55.2, 59.2] | 2.99 | 0.08 |
| noisy | 8 | tjunction | isotonic | greedy | 52.8 | [50.7, 54.8] | 3.00 | 0.17 |
| noisy | 8 | tjunction | isotonic | independent_rule | 16.3 | [14.8, 17.9] | 3.00 | 1.53 |
| noisy | 8 | tjunction | isotonic_dw | exact | 50.7 | [48.7, 52.8] | 3.00 | 0.27 |
| noisy | 8 | tjunction | isotonic_dw | greedy | 37.9 | [35.9, 39.9] | 3.00 | 0.66 |
| noisy | 8 | tjunction | isotonic_dw | independent_rule | 1.8 | [1.4, 2.5] | 3.00 | 2.02 |
| noisy | 8 | tjunction | raw | exact | 53.0 | [50.9, 55.0] | 2.88 | 0.19 |
| noisy | 8 | tjunction | raw | greedy | 47.6 | [45.6, 49.7] | 2.96 | 0.31 |
| noisy | 8 | tjunction | raw | independent_rule | 30.4 | [28.6, 32.4] | 2.96 | 0.93 |

## Paired comparisons (exploratory, McNemar exact, crossing robots only)

| Comparison | Condition | N | Layout | Only first collided | Only second collided | p |
| --- | --- | --- | --- | --- | --- | --- |
| independent rule vs exact (decision-aware) | nominal | 6 | none | 0 | 109 | 3.08e-33 |
| conventional vs decision-aware (exact) | nominal | 6 | none | 461 | 0 | 3.36e-139 |
| independent rule vs exact (decision-aware) | nominal | 6 | single | 0 | 629 | 8.98e-190 |
| conventional vs decision-aware (exact) | nominal | 6 | single | 224 | 57 | 1.43e-24 |
| independent rule vs exact (decision-aware) | nominal | 6 | tjunction | 0 | 587 | 3.95e-177 |
| conventional vs decision-aware (exact) | nominal | 6 | tjunction | 195 | 29 | 2.12e-31 |
| independent rule vs exact (decision-aware) | nominal | 8 | none | 0 | 108 | 6.16e-33 |
| conventional vs decision-aware (exact) | nominal | 8 | none | 524 | 0 | 3.64e-158 |
| independent rule vs exact (decision-aware) | nominal | 8 | single | 0 | 845 | 8.52e-255 |
| conventional vs decision-aware (exact) | nominal | 8 | single | 230 | 85 | 1.4e-16 |
| independent rule vs exact (decision-aware) | nominal | 8 | tjunction | 0 | 790 | 3.07e-238 |
| conventional vs decision-aware (exact) | nominal | 8 | tjunction | 256 | 73 | 5.69e-25 |
| independent rule vs exact (decision-aware) | noisy | 6 | none | 0 | 709 | 7.43e-214 |
| conventional vs decision-aware (exact) | noisy | 6 | none | 235 | 6 | 1.48e-61 |
| independent rule vs exact (decision-aware) | noisy | 6 | single | 0 | 920 | 2.26e-277 |
| conventional vs decision-aware (exact) | noisy | 6 | single | 126 | 33 | 5.27e-14 |
| independent rule vs exact (decision-aware) | noisy | 6 | tjunction | 0 | 885 | 7.75e-267 |
| conventional vs decision-aware (exact) | noisy | 6 | tjunction | 132 | 21 | 7.29e-21 |
| independent rule vs exact (decision-aware) | noisy | 8 | none | 0 | 824 | 1.79e-248 |
| conventional vs decision-aware (exact) | noisy | 8 | none | 341 | 1 | 7.66e-101 |
| independent rule vs exact (decision-aware) | noisy | 8 | single | 0 | 1160 | 0 |
| conventional vs decision-aware (exact) | noisy | 8 | single | 177 | 54 | 1.84e-16 |
| independent rule vs exact (decision-aware) | noisy | 8 | tjunction | 0 | 1120 | 0 |
| conventional vs decision-aware (exact) | noisy | 8 | tjunction | 196 | 48 | 2.08e-22 |

## How often the question budget binds

Share of epochs where more robots are in the ask band than the budget allows.

| condition   |   N | calibration   |   budget_binds |
|:------------|----:|:--------------|---------------:|
| noisy       |   6 | isotonic      |          0.978 |
| noisy       |   6 | isotonic_dw   |          1     |
| noisy       |   6 | raw           |          0.816 |
| noisy       |   8 | isotonic      |          0.996 |
| noisy       |   8 | isotonic_dw   |          1     |
| noisy       |   8 | raw           |          0.868 |
| nominal     |   6 | isotonic      |          0.982 |
| nominal     |   6 | isotonic_dw   |          0.992 |
| nominal     |   6 | raw           |          0.97  |
| nominal     |   8 | isotonic      |          0.998 |
| nominal     |   8 | isotonic_dw   |          0.998 |
| nominal     |   8 | raw           |          0.998 |
