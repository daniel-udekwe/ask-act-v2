# Month-1 pilot (noiseless, development seeds 3000-3009)

## QAOA

Lift = probability QAOA puts on the optimum (or on feasible states) divided by that of uniform random sampling.

|   N | layout    | solver               |   depth |   qubits |   ground_state_ok |   p_opt |   lift_p_opt |   p_feasible |   lift_p_feas |   found_opt |   random_found_opt |   within_5pct |
|----:|:----------|:---------------------|--------:|---------:|------------------:|--------:|-------------:|-------------:|--------------:|------------:|-------------------:|--------------:|
|   4 | none      | qaoa_slack           |       1 |       10 |               1   |   0.015 |        3.981 |        0.688 |         2.404 |         1   |                1   |           1   |
|   4 | none      | qaoa_slack           |       2 |       10 |               1   |   0.034 |        9.391 |        0.879 |         3.084 |         1   |                1   |           1   |
|   4 | none      | qaoa_slack           |       3 |       10 |               1   |   0.058 |       16.085 |        0.919 |         3.266 |         1   |                1   |           1   |
|   4 | none      | qaoa_slack_cvar      |       1 |       10 |               1   |   0.018 |        5.198 |        0.616 |         2.224 |         1   |                1   |           1   |
|   4 | none      | qaoa_slack_cvar      |       2 |       10 |               1   |   0.046 |       13.635 |        0.772 |         2.783 |         1   |                1   |           1   |
|   4 | none      | qaoa_slack_cvar      |       3 |       10 |               1   |   0.077 |       22.128 |        0.838 |         2.987 |         1   |                1   |           1   |
|   4 | none      | qaoa_unbalanced      |       1 |        8 |               0.8 |   0.035 |        8.724 |        0.839 |         2.946 |         1   |                1   |           1   |
|   4 | none      | qaoa_unbalanced      |       2 |        8 |               0.8 |   0.08  |       16.975 |        0.926 |         3.366 |         1   |                1   |           1   |
|   4 | none      | qaoa_unbalanced      |       3 |        8 |               0.8 |   0.093 |       22.06  |        0.914 |         3.391 |         1   |                1   |           1   |
|   4 | none      | qaoa_unbalanced_cvar |       1 |        8 |               0.8 |   0.043 |       10.054 |        0.785 |         2.836 |         1   |                1   |           1   |
|   4 | none      | qaoa_unbalanced_cvar |       2 |        8 |               0.8 |   0.078 |       17.117 |        0.835 |         3.002 |         1   |                1   |           1   |
|   4 | none      | qaoa_unbalanced_cvar |       3 |        8 |               0.8 |   0.098 |       24.232 |        0.802 |         2.837 |         1   |                1   |           1   |
|   6 | none      | qaoa_slack           |       1 |       14 |               1   |   0.002 |        5.985 |        0.6   |         4.904 |         1   |                0.2 |           1   |
|   6 | none      | qaoa_slack           |       2 |       14 |               1   |   0.004 |        9.18  |        0.794 |         6.517 |         0.9 |                0.2 |           1   |
|   6 | none      | qaoa_slack           |       3 |       14 |               1   |   0.008 |       23.937 |        0.856 |         7.105 |         1   |                0.2 |           1   |
|   6 | none      | qaoa_slack_cvar      |       1 |       14 |               1   |   0.002 |        6.753 |        0.595 |         4.837 |         0.8 |                0.2 |           1   |
|   6 | none      | qaoa_slack_cvar      |       2 |       14 |               1   |   0.006 |       16.701 |        0.598 |         4.93  |         1   |                0.2 |           1   |
|   6 | none      | qaoa_slack_cvar      |       3 |       14 |               1   |   0.012 |       27.153 |        0.618 |         5.086 |         1   |                0.2 |           1   |
|   6 | none      | qaoa_unbalanced      |       1 |       12 |               0.9 |   0.006 |       25.141 |        0.732 |         5.798 |         1   |                0.1 |           1   |
|   6 | none      | qaoa_unbalanced      |       2 |       12 |               0.9 |   0.018 |       61.863 |        0.907 |         7.563 |         1   |                0.1 |           1   |
|   6 | none      | qaoa_unbalanced      |       3 |       12 |               0.9 |   0.034 |      129.445 |        0.898 |         7.449 |         1   |                0.1 |           1   |
|   6 | none      | qaoa_unbalanced_cvar |       1 |       12 |               0.9 |   0.008 |       31.98  |        0.667 |         5.391 |         1   |                0.1 |           1   |
|   6 | none      | qaoa_unbalanced_cvar |       2 |       12 |               0.9 |   0.024 |      102.148 |        0.784 |         6.903 |         1   |                0.1 |           1   |
|   6 | none      | qaoa_unbalanced_cvar |       3 |       12 |               0.9 |   0.041 |      159.969 |        0.737 |         6.207 |         1   |                0.1 |           1   |
|   6 | single    | qaoa_slack           |       1 |       14 |               1   |   0.002 |        7.799 |        0.636 |         5.223 |         0.8 |                0.2 |           1   |
|   6 | single    | qaoa_slack           |       2 |       14 |               1   |   0.003 |       12.795 |        0.816 |         6.701 |         1   |                0.2 |           1   |
|   6 | single    | qaoa_slack           |       3 |       14 |               1   |   0.005 |       17.808 |        0.877 |         7.271 |         1   |                0.2 |           1   |
|   6 | single    | qaoa_slack_cvar      |       1 |       14 |               1   |   0.002 |        8.584 |        0.639 |         5.248 |         0.9 |                0.2 |           1   |
|   6 | single    | qaoa_slack_cvar      |       2 |       14 |               1   |   0.004 |       13.735 |        0.69  |         5.742 |         1   |                0.2 |           1   |
|   6 | single    | qaoa_slack_cvar      |       3 |       14 |               1   |   0.006 |       15.999 |        0.731 |         6.169 |         1   |                0.2 |           1   |
|   6 | single    | qaoa_unbalanced      |       1 |       12 |               0.8 |   0.004 |       16.311 |        0.794 |         6.473 |         1   |                0.1 |           1   |
|   6 | single    | qaoa_unbalanced      |       2 |       12 |               0.8 |   0.01  |       25.888 |        0.89  |         7.65  |         0.9 |                0.1 |           0.9 |
|   6 | single    | qaoa_unbalanced      |       3 |       12 |               0.8 |   0.016 |       47.21  |        0.879 |         7.744 |         1   |                0.1 |           1   |
|   6 | single    | qaoa_unbalanced_cvar |       1 |       12 |               0.8 |   0.006 |       19.183 |        0.743 |         6.029 |         1   |                0.1 |           1   |
|   6 | single    | qaoa_unbalanced_cvar |       2 |       12 |               0.8 |   0.014 |       38.099 |        0.769 |         7.064 |         1   |                0.1 |           1   |
|   6 | single    | qaoa_unbalanced_cvar |       3 |       12 |               0.8 |   0.028 |      103.6   |        0.767 |         6.834 |         1   |                0.1 |           1   |
|   6 | tjunction | qaoa_slack           |       1 |       14 |               1   |   0.002 |        6.655 |        0.631 |         5.188 |         0.9 |                0.1 |           1   |
|   6 | tjunction | qaoa_slack           |       2 |       14 |               1   |   0.002 |        9.908 |        0.809 |         6.685 |         0.7 |                0.1 |           1   |
|   6 | tjunction | qaoa_slack           |       3 |       14 |               1   |   0.003 |       12.917 |        0.875 |         7.158 |         0.8 |                0.1 |           0.9 |
|   6 | tjunction | qaoa_slack_cvar      |       1 |       14 |               1   |   0.002 |        7.035 |        0.637 |         5.238 |         0.7 |                0.1 |           0.9 |
|   6 | tjunction | qaoa_slack_cvar      |       2 |       14 |               1   |   0.002 |       10.725 |        0.71  |         5.811 |         1   |                0.1 |           1   |
|   6 | tjunction | qaoa_slack_cvar      |       3 |       14 |               1   |   0.003 |       12.43  |        0.725 |         6.109 |         1   |                0.1 |           1   |
|   6 | tjunction | qaoa_unbalanced      |       1 |       12 |               0.9 |   0.003 |       12.602 |        0.778 |         6.374 |         1   |                0.2 |           1   |
|   6 | tjunction | qaoa_unbalanced      |       2 |       12 |               0.9 |   0.005 |       16.354 |        0.826 |         7.186 |         1   |                0.2 |           1   |
|   6 | tjunction | qaoa_unbalanced      |       3 |       12 |               0.9 |   0.006 |       22.76  |        0.815 |         7.357 |         1   |                0.2 |           1   |
|   6 | tjunction | qaoa_unbalanced_cvar |       1 |       12 |               0.9 |   0.003 |       13.198 |        0.751 |         6.235 |         1   |                0.2 |           1   |
|   6 | tjunction | qaoa_unbalanced_cvar |       2 |       12 |               0.9 |   0.005 |       16.83  |        0.771 |         7.089 |         1   |                0.2 |           1   |
|   6 | tjunction | qaoa_unbalanced_cvar |       3 |       12 |               0.9 |   0.012 |       41.298 |        0.723 |         6.132 |         1   |                0.2 |           1   |

## Classical baselines

Share of instances solved to optimality and median gap to the optimum.

|   N | layout    | solver           |   found_opt |   median_gap |   max_gap |   mean_time_s |
|----:|:----------|:-----------------|------------:|-------------:|----------:|--------------:|
|   4 | none      | cpsat            |         1   |       0      |    0      |        0.003  |
|   4 | none      | greedy           |         1   |       0      |    0      |        0      |
|   4 | none      | independent_rule |         0.9 |       0      |    0.168  |        0      |
|   4 | none      | sim_annealing    |         1   |       0      |    0      |        0.6792 |
|   6 | none      | cpsat            |         1   |       0      |    0      |        0.0017 |
|   6 | none      | greedy           |         1   |       0      |    0      |        0      |
|   6 | none      | independent_rule |         0.7 |       0      |    0.7396 |        0      |
|   6 | none      | sim_annealing    |         1   |       0      |    0      |        0.7569 |
|   6 | single    | cpsat            |         1   |       0      |    0      |        0.0028 |
|   6 | single    | greedy           |         0.5 |       0.0538 |    0.2921 |        0      |
|   6 | single    | independent_rule |         0.4 |       0.2265 |    1.2526 |        0      |
|   6 | single    | sim_annealing    |         0.8 |       0      |    0.0855 |        0.8218 |
|   6 | tjunction | cpsat            |         1   |       0      |    0      |        0.0031 |
|   6 | tjunction | greedy           |         0.7 |       0      |    0.2909 |        0      |
|   6 | tjunction | independent_rule |         0.6 |       0      |    0.8587 |        0      |
|   6 | tjunction | sim_annealing    |         0.6 |       0      |    0.1338 |        0.8126 |
