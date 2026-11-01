# Closed-loop study, month 3 (exploratory, development seeds)

N = 6 robots per epoch, 1000 paired epochs per cell, one operator answering serially (1.5 s per question), deadlines within a 1 s window. Cost model C = 100. Collisions are per crossing robot, with 95% Wilson intervals.

| Condition | Calibration | Method | Collisions (%) | 95% CI | Questions / epoch | Unanswered (cautious fallback) / epoch | Mean delay (s) | Stopped with non-crosser (s) | Congestion (s / epoch) | Held for epoch (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| noisy | raw | independent | 31.7 | [30.1, 33.3] | 3.66 | 0.26 | 2.28 | 2.05 | 5.37 | 0.00 |
| noisy | raw | independent_costband | 1.3 | [1.0, 1.8] | 5.58 | 0.74 | 3.46 | 3.55 | 12.28 | 0.00 |
| noisy | raw | joint_free | 1.3 | [0.9, 1.7] | 5.58 | 0.70 | 3.42 | 3.75 | 13.03 | 0.27 |
| noisy | raw | joint_none | 7.4 | [6.6, 8.4] | 2.00 | 0.00 | 3.80 | 4.86 | 11.63 | 0.27 |
| noisy | raw | joint_queue | 5.2 | [4.5, 6.0] | 3.28 | 0.07 | 3.70 | 4.54 | 11.92 | 0.27 |
| noisy | raw | joint_single | 11.9 | [10.8, 13.0] | 2.00 | 0.00 | 3.59 | 4.56 | 10.26 | 0.27 |
| noisy | isotonic | independent | 18.0 | [16.8, 19.4] | 4.82 | 0.52 | 2.78 | 2.77 | 8.28 | 0.00 |
| noisy | isotonic | independent_costband | 0.3 | [0.2, 0.6] | 5.90 | 0.84 | 3.47 | 3.62 | 12.72 | 0.00 |
| noisy | isotonic | joint_free | 0.3 | [0.2, 0.6] | 5.90 | 0.79 | 3.46 | 3.81 | 13.50 | 0.27 |
| noisy | isotonic | joint_none | 0.7 | [0.5, 1.1] | 2.00 | 0.00 | 4.11 | 5.32 | 13.61 | 0.27 |
| noisy | isotonic | joint_queue | 0.6 | [0.4, 0.9] | 3.19 | 0.04 | 3.95 | 4.93 | 13.44 | 0.27 |
| noisy | isotonic | joint_single | 0.9 | [0.6, 1.3] | 2.00 | 0.00 | 4.10 | 5.29 | 13.52 | 0.27 |
| noisy | isotonic_dw | independent | 2.2 | [1.7, 2.7] | 5.74 | 0.78 | 3.39 | 3.50 | 12.09 | 0.00 |
| noisy | isotonic_dw | independent_costband | 0.3 | [0.2, 0.6] | 5.88 | 0.82 | 3.48 | 3.63 | 12.72 | 0.00 |
| noisy | isotonic_dw | joint_free | 0.3 | [0.2, 0.6] | 5.88 | 0.78 | 3.47 | 3.83 | 13.50 | 0.27 |
| noisy | isotonic_dw | joint_none | 1.2 | [0.9, 1.7] | 2.00 | 0.00 | 4.07 | 5.25 | 13.37 | 0.27 |
| noisy | isotonic_dw | joint_queue | 1.2 | [0.9, 1.7] | 2.88 | 0.01 | 3.95 | 4.97 | 13.18 | 0.27 |
| noisy | isotonic_dw | joint_single | 1.7 | [1.3, 2.2] | 2.00 | 0.00 | 4.06 | 5.23 | 13.23 | 0.27 |
| nominal | raw | independent | 4.0 | [3.3, 4.7] | 4.68 | 0.28 | 2.78 | 2.19 | 8.40 | 0.00 |
| nominal | raw | independent_costband | 0.0 | [0.0, 0.1] | 5.71 | 0.78 | 3.48 | 3.64 | 12.53 | 0.00 |
| nominal | raw | joint_free | 0.0 | [0.0, 0.1] | 5.71 | 0.77 | 3.48 | 3.93 | 13.64 | 0.35 |
| nominal | raw | joint_none | 0.0 | [0.0, 0.1] | 2.00 | 0.00 | 3.51 | 4.00 | 11.04 | 0.35 |
| nominal | raw | joint_queue | 0.0 | [0.0, 0.1] | 2.93 | 0.02 | 3.52 | 4.03 | 11.45 | 0.35 |
| nominal | raw | joint_single | 0.0 | [0.0, 0.2] | 2.00 | 0.00 | 3.41 | 3.78 | 10.33 | 0.35 |
| nominal | isotonic | independent | 3.1 | [2.6, 3.7] | 4.77 | 0.29 | 2.78 | 2.18 | 8.48 | 0.00 |
| nominal | isotonic | independent_costband | 0.0 | [0.0, 0.1] | 5.09 | 0.39 | 2.98 | 2.52 | 9.67 | 0.00 |
| nominal | isotonic | joint_free | 0.0 | [0.0, 0.1] | 5.09 | 0.39 | 3.00 | 2.82 | 10.54 | 0.35 |
| nominal | isotonic | joint_none | 0.5 | [0.3, 0.8] | 2.00 | 0.00 | 3.34 | 3.64 | 10.04 | 0.35 |
| nominal | isotonic | joint_queue | 0.5 | [0.3, 0.8] | 2.66 | 0.00 | 3.30 | 3.53 | 10.07 | 0.35 |
| nominal | isotonic | joint_single | 0.8 | [0.5, 1.1] | 2.00 | 0.00 | 3.31 | 3.58 | 9.84 | 0.35 |
| nominal | isotonic_dw | independent | 1.0 | [0.7, 1.4] | 4.96 | 0.34 | 2.89 | 2.36 | 9.18 | 0.00 |
| nominal | isotonic_dw | independent_costband | 0.0 | [0.0, 0.1] | 5.09 | 0.39 | 2.98 | 2.52 | 9.67 | 0.00 |
| nominal | isotonic_dw | joint_free | 0.0 | [0.0, 0.1] | 5.09 | 0.39 | 3.00 | 2.82 | 10.54 | 0.35 |
| nominal | isotonic_dw | joint_none | 0.0 | [0.0, 0.1] | 2.00 | 0.00 | 3.40 | 3.75 | 10.48 | 0.35 |
| nominal | isotonic_dw | joint_queue | 0.0 | [0.0, 0.1] | 1.97 | 0.00 | 3.42 | 3.80 | 10.51 | 0.35 |
| nominal | isotonic_dw | joint_single | 0.0 | [0.0, 0.2] | 2.00 | 0.00 | 3.38 | 3.70 | 10.31 | 0.35 |

## Paired comparisons

McNemar exact on collisions of crossing robots; Wilcoxon signed-rank on per-robot delay.

| Comparison | Condition | Calibration | Only first collided | Only second collided | p (collisions) | Mean delay difference (s) | p (delay) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| independent vs joint_single | nominal | raw | 134 | 0 | 9.18e-41 | -0.63 | 4.14e-55 |
| independent vs joint_single | nominal | isotonic | 79 | 0 | 3.31e-24 | -0.54 | 7.25e-39 |
| independent vs joint_single | nominal | isotonic_dw | 34 | 0 | 1.16e-10 | -0.49 | 1.51e-20 |
| independent_costband vs joint_none | nominal | raw | 0 | 0 | 1 | -0.03 | 5.06e-33 |
| independent_costband vs joint_none | nominal | isotonic | 0 | 16 | 3.05e-05 | -0.37 | 0.000178 |
| independent_costband vs joint_none | nominal | isotonic_dw | 0 | 0 | 1 | -0.42 | 5.08e-09 |
| independent_costband vs joint_queue | nominal | raw | 0 | 0 | 1 | -0.04 | 3.07e-31 |
| independent_costband vs joint_queue | nominal | isotonic | 0 | 16 | 3.05e-05 | -0.32 | 0.00461 |
| independent_costband vs joint_queue | nominal | isotonic_dw | 0 | 0 | 1 | -0.44 | 8.37e-11 |
| independent_costband vs joint_free (early commits) | nominal | isotonic | 0 | 0 | 1 | -0.02 | 0.0096 |
| independent_costband vs joint_free (early commits) | nominal | isotonic_dw | 0 | 0 | 1 | -0.02 | 0.0096 |
| joint_free vs joint_queue (coordination) | nominal | isotonic | 0 | 16 | 3.05e-05 | -0.30 | 6.27e-52 |
| joint_free vs joint_queue (coordination) | nominal | isotonic_dw | 0 | 0 | 1 | -0.42 | 6.04e-96 |
| joint_none vs joint_single | nominal | isotonic_dw | 0 | 1 | 1 | +0.02 | 9.54e-11 |
| conventional vs decision-aware (independent) | nominal | both | 71 | 0 | 8.47e-22 | -0.12 | 5.8e-43 |
| conventional vs decision-aware (joint_single) | nominal | both | 26 | 0 | 2.98e-08 | -0.07 | 8.06e-16 |
| independent vs joint_single | noisy | raw | 671 | 0 | 2.04e-202 | -1.31 | 2.54e-296 |
| independent vs joint_single | noisy | isotonic | 581 | 0 | 2.53e-175 | -1.32 | 2.43e-226 |
| independent vs joint_single | noisy | isotonic_dw | 16 | 0 | 3.05e-05 | -0.67 | 4.94e-13 |
| independent_costband vs joint_none | noisy | raw | 2 | 209 | 1.36e-59 | -0.33 | 0.0149 |
| independent_costband vs joint_none | noisy | isotonic | 0 | 13 | 0.000244 | -0.64 | 1.41e-07 |
| independent_costband vs joint_none | noisy | isotonic_dw | 0 | 31 | 9.31e-10 | -0.59 | 2.79e-05 |
| independent_costband vs joint_queue | noisy | raw | 2 | 133 | 4.22e-37 | -0.23 | 1.3e-08 |
| independent_costband vs joint_queue | noisy | isotonic | 0 | 9 | 0.00391 | -0.48 | 0.4 |
| independent_costband vs joint_queue | noisy | isotonic_dw | 0 | 31 | 9.31e-10 | -0.47 | 0.549 |
| independent_costband vs joint_free (early commits) | noisy | isotonic | 0 | 0 | 1 | +0.01 | 6.88e-43 |
| independent_costband vs joint_free (early commits) | noisy | isotonic_dw | 0 | 0 | 1 | +0.01 | 1.46e-41 |
| joint_free vs joint_queue (coordination) | noisy | isotonic | 0 | 9 | 0.00391 | -0.49 | 2.38e-94 |
| joint_free vs joint_queue (coordination) | noisy | isotonic_dw | 0 | 31 | 9.31e-10 | -0.48 | 1.81e-87 |
| joint_none vs joint_single | noisy | isotonic_dw | 0 | 15 | 6.1e-05 | +0.02 | 1.69e-08 |
| conventional vs decision-aware (independent) | noisy | both | 538 | 0 | 2.22e-162 | -0.61 | 1.73e-213 |
| conventional vs decision-aware (joint_single) | noisy | both | 0 | 27 | 1.49e-08 | +0.04 | 1.35e-09 |

## Joint actions at the deadline

0 = go, 1 = stop, 2 = ask.

|                                            |     0 |     1 |     2 |
|:-------------------------------------------|------:|------:|------:|
| ('joint_queue', 'noisy', 'isotonic')       | 0.004 | 0.464 | 0.532 |
| ('joint_queue', 'noisy', 'isotonic_dw')    | 0.014 | 0.505 | 0.481 |
| ('joint_queue', 'noisy', 'raw')            | 0.058 | 0.396 | 0.547 |
| ('joint_queue', 'nominal', 'isotonic')     | 0.132 | 0.425 | 0.443 |
| ('joint_queue', 'nominal', 'isotonic_dw')  | 0.113 | 0.56  | 0.328 |
| ('joint_queue', 'nominal', 'raw')          | 0.072 | 0.439 | 0.489 |
| ('joint_single', 'noisy', 'isotonic')      | 0.008 | 0.658 | 0.333 |
| ('joint_single', 'noisy', 'isotonic_dw')   | 0.019 | 0.648 | 0.333 |
| ('joint_single', 'noisy', 'raw')           | 0.127 | 0.54  | 0.333 |
| ('joint_single', 'nominal', 'isotonic')    | 0.14  | 0.527 | 0.333 |
| ('joint_single', 'nominal', 'isotonic_dw') | 0.119 | 0.548 | 0.333 |
| ('joint_single', 'nominal', 'raw')         | 0.115 | 0.552 | 0.333 |

## Collisions by scenario family (crossing robots, %, all calibrations pooled)

|                                     |   clear_cross |   hesitant |   late_turn |   slow_cross |
|:------------------------------------|--------------:|-----------:|------------:|-------------:|
| ('noisy', 'independent')            |          26.2 |        7.8 |        26   |          8.5 |
| ('noisy', 'independent_costband')   |           1.3 |        0.4 |         0.5 |          0.4 |
| ('noisy', 'joint_free')             |           1.3 |        0.3 |         0.5 |          0.4 |
| ('noisy', 'joint_none')             |           2.9 |        1.8 |         4.4 |          3.3 |
| ('noisy', 'joint_queue')            |           2.1 |        1.6 |         3.5 |          2.1 |
| ('noisy', 'joint_single')           |           5.2 |        2.3 |         7.2 |          4.3 |
| ('nominal', 'independent')          |           4.4 |        0   |         6.1 |          0   |
| ('nominal', 'independent_costband') |           0   |        0   |         0   |          0   |
| ('nominal', 'joint_free')           |           0   |        0   |         0   |          0   |
| ('nominal', 'joint_none')           |           0   |        0   |         0.6 |          0   |
| ('nominal', 'joint_queue')          |           0   |        0   |         0.6 |          0   |
| ('nominal', 'joint_single')         |           0.3 |        0   |         0.8 |          0   |
