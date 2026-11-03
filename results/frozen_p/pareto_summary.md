# Pareto study: operator load against safety and delay (month 4, development seeds)

500 paired epochs per point. Collisions are per crossing robot. Ask cost = 1.5 + κ.

## Frontier

|   N | condition   | calibration   |   kappa |    q | method             |   questions |   collisions_pct |   n_crossing |   delay_s |   fallbacks |
|----:|:------------|:--------------|--------:|-----:|:-------------------|------------:|-----------------:|-------------:|----------:|------------:|
|   6 | noisy       | isotonic      |     0.5 | 1.5  | joint κ=0.5 q=1.5  |       3.168 |            0.295 |         1696 |     3.96  |       0.032 |
|   6 | noisy       | isotonic      |     1   | 1.5  | joint κ=1 q=1.5    |       3.026 |            0.354 |         1696 |     3.988 |       0.018 |
|   6 | noisy       | isotonic      |     2   | 1.5  | joint κ=2 q=1.5    |       2.484 |            0.354 |         1696 |     4.085 |       0.006 |
|   6 | noisy       | isotonic      |     3   | 1.5  | joint κ=3 q=1.5    |       2.044 |            0.354 |         1696 |     4.138 |       0     |
|   6 | noisy       | isotonic      |     4   | 1.5  | joint κ=4 q=1.5    |       1.578 |            0.413 |         1696 |     4.218 |       0     |
|   6 | noisy       | isotonic      |     5   | 1.5  | joint κ=5 q=1.5    |       1.242 |            0.413 |         1696 |     4.272 |       0     |
|   6 | noisy       | isotonic      |     6   | 1.5  | joint κ=6 q=1.5    |       0.766 |            0.531 |         1696 |     4.398 |       0     |
|   6 | noisy       | isotonic      |     7   | 1.5  | joint κ=7 q=1.5    |       0.074 |            0.531 |         1696 |     4.627 |       0     |
|   6 | noisy       | isotonic      |     0.5 | 0    | joint κ=0.5 q=0    |       5.916 |            0.059 |         1696 |     3.47  |       0.822 |
|   6 | noisy       | isotonic      |     0.5 | 0.75 | joint κ=0.5 q=0.75 |       4.662 |            0.295 |         1696 |     3.712 |       0.436 |
|   6 | noisy       | isotonic      |     0.5 | 3    | joint κ=0.5 q=3    |       2.08  |            0.354 |         1696 |     4.113 |       0     |
|   6 | noisy       | isotonic      |     0.5 | 6    | joint κ=0.5 q=6    |       1.282 |            0.413 |         1696 |     4.255 |       0     |
|   6 | noisy       | isotonic      |     0.5 | 0    | indep κ=0.5        |       5.916 |            0.059 |         1696 |     3.454 |       0.838 |
|   6 | noisy       | isotonic      |     1   | 0    | indep κ=1          |       5.862 |            0.059 |         1696 |     3.466 |       0.826 |
|   6 | noisy       | isotonic      |     2   | 0    | indep κ=2          |       5.846 |            0.295 |         1696 |     3.465 |       0.826 |
|   6 | noisy       | isotonic      |     3   | 0    | indep κ=3          |       5.12  |            0.295 |         1696 |     3.701 |       0.57  |
|   6 | noisy       | isotonic      |     4   | 0    | indep κ=4          |       4.098 |            0.295 |         1696 |     4.007 |       0.302 |
|   6 | noisy       | isotonic      |     5   | 0    | indep κ=5          |       2.452 |            0.295 |         1696 |     4.588 |       0.052 |
|   6 | noisy       | isotonic      |     6   | 0    | indep κ=6          |       1.34  |            0.531 |         1696 |     4.975 |       0.01  |
|   6 | noisy       | isotonic      |     7   | 0    | indep κ=7          |       0.102 |            0.531 |         1696 |     5.554 |       0     |
|   6 | noisy       | isotonic_dw   |     0.5 | 1.5  | joint κ=0.5 q=1.5  |       2.91  |            0.884 |         1696 |     3.964 |       0.014 |
|   6 | noisy       | isotonic_dw   |     1   | 1.5  | joint κ=1 q=1.5    |       2.62  |            0.884 |         1696 |     4.007 |       0     |
|   6 | noisy       | isotonic_dw   |     2   | 1.5  | joint κ=2 q=1.5    |       2.152 |            1.002 |         1696 |     4.068 |       0     |
|   6 | noisy       | isotonic_dw   |     3   | 1.5  | joint κ=3 q=1.5    |       1.606 |            1.002 |         1696 |     4.182 |       0     |
|   6 | noisy       | isotonic_dw   |     4   | 1.5  | joint κ=4 q=1.5    |       1.142 |            1.002 |         1696 |     4.265 |       0     |
|   6 | noisy       | isotonic_dw   |     5   | 1.5  | joint κ=5 q=1.5    |       0.832 |            1.002 |         1696 |     4.342 |       0     |
|   6 | noisy       | isotonic_dw   |     6   | 1.5  | joint κ=6 q=1.5    |       0.286 |            1.002 |         1696 |     4.511 |       0     |
|   6 | noisy       | isotonic_dw   |     7   | 1.5  | joint κ=7 q=1.5    |       0.022 |            1.002 |         1696 |     4.612 |       0     |
|   6 | noisy       | isotonic_dw   |     0.5 | 0    | joint κ=0.5 q=0    |       5.906 |            0.059 |         1696 |     3.472 |       0.822 |
|   6 | noisy       | isotonic_dw   |     0.5 | 0.75 | joint κ=0.5 q=0.75 |       4.074 |            0.472 |         1696 |     3.792 |       0.26  |
|   6 | noisy       | isotonic_dw   |     0.5 | 3    | joint κ=0.5 q=3    |       1.966 |            1.002 |         1696 |     4.092 |       0     |
|   6 | noisy       | isotonic_dw   |     0.5 | 6    | joint κ=0.5 q=6    |       1     |            1.002 |         1696 |     4.289 |       0     |
|   6 | noisy       | isotonic_dw   |     0.5 | 0    | indep κ=0.5        |       5.906 |            0.059 |         1696 |     3.457 |       0.836 |
|   6 | noisy       | isotonic_dw   |     1   | 0    | indep κ=1          |       5.846 |            0.295 |         1696 |     3.465 |       0.826 |
|   6 | noisy       | isotonic_dw   |     2   | 0    | indep κ=2          |       5.168 |            0.295 |         1696 |     3.679 |       0.592 |
|   6 | noisy       | isotonic_dw   |     3   | 0    | indep κ=3          |       3.878 |            0.295 |         1696 |     4.077 |       0.254 |
|   6 | noisy       | isotonic_dw   |     4   | 0    | indep κ=4          |       2.814 |            1.002 |         1696 |     4.37  |       0.098 |
|   6 | noisy       | isotonic_dw   |     5   | 0    | indep κ=5          |       1.558 |            1.002 |         1696 |     4.842 |       0.018 |
|   6 | noisy       | isotonic_dw   |     6   | 0    | indep κ=6          |       0.346 |            1.002 |         1696 |     5.37  |       0     |
|   6 | noisy       | isotonic_dw   |     7   | 0    | indep κ=7          |       0.022 |            1.002 |         1696 |     5.547 |       0     |
|   6 | nominal     | isotonic      |     0.5 | 1.5  | joint κ=0.5 q=1.5  |       2.656 |            0.582 |         1718 |     3.292 |       0     |
|   6 | nominal     | isotonic      |     1   | 1.5  | joint κ=1 q=1.5    |       2.318 |            0.582 |         1718 |     3.315 |       0     |
|   6 | nominal     | isotonic      |     2   | 1.5  | joint κ=2 q=1.5    |       1.918 |            0.582 |         1718 |     3.329 |       0     |
|   6 | nominal     | isotonic      |     3   | 1.5  | joint κ=3 q=1.5    |       1.26  |            0.582 |         1718 |     3.394 |       0     |
|   6 | nominal     | isotonic      |     4   | 1.5  | joint κ=4 q=1.5    |       0.982 |            0.698 |         1718 |     3.418 |       0     |
|   6 | nominal     | isotonic      |     5   | 1.5  | joint κ=5 q=1.5    |       0.428 |            0.698 |         1718 |     3.482 |       0     |
|   6 | nominal     | isotonic      |     6   | 1.5  | joint κ=6 q=1.5    |       0.23  |            0.873 |         1718 |     3.491 |       0     |
|   6 | nominal     | isotonic      |     7   | 1.5  | joint κ=7 q=1.5    |       0.012 |            0.873 |         1718 |     3.548 |       0     |
|   6 | nominal     | isotonic      |     0.5 | 0    | joint κ=0.5 q=0    |       5.036 |            0     |         1718 |     3.003 |       0.396 |
|   6 | nominal     | isotonic      |     0.5 | 0.75 | joint κ=0.5 q=0.75 |       3.742 |            0.582 |         1718 |     3.14  |       0.092 |
|   6 | nominal     | isotonic      |     0.5 | 3    | joint κ=0.5 q=3    |       1.908 |            0.582 |         1718 |     3.328 |       0     |
|   6 | nominal     | isotonic      |     0.5 | 6    | joint κ=0.5 q=6    |       1.008 |            0.698 |         1718 |     3.393 |       0     |
|   6 | nominal     | isotonic      |     0.5 | 0    | indep κ=0.5        |       5.036 |            0     |         1718 |     2.959 |       0.364 |
|   6 | nominal     | isotonic      |     1   | 0    | indep κ=1          |       4.81  |            0.407 |         1718 |     2.965 |       0.308 |
|   6 | nominal     | isotonic      |     2   | 0    | indep κ=2          |       4.362 |            0.698 |         1718 |     3.095 |       0.238 |
|   6 | nominal     | isotonic      |     3   | 0    | indep κ=3          |       3.11  |            0.698 |         1718 |     3.644 |       0.044 |
|   6 | nominal     | isotonic      |     4   | 0    | indep κ=4          |       2.074 |            0.698 |         1718 |     4.079 |       0.008 |
|   6 | nominal     | isotonic      |     5   | 0    | indep κ=5          |       0.502 |            0.698 |         1718 |     4.772 |       0     |
|   6 | nominal     | isotonic      |     6   | 0    | indep κ=6          |       0.264 |            0.99  |         1718 |     4.824 |       0     |
|   6 | nominal     | isotonic      |     7   | 0    | indep κ=7          |       0.012 |            0.99  |         1718 |     4.962 |       0     |
|   6 | nominal     | isotonic_dw   |     0.5 | 1.5  | joint κ=0.5 q=1.5  |       1.968 |            0     |         1718 |     3.384 |       0     |
|   6 | nominal     | isotonic_dw   |     1   | 1.5  | joint κ=1 q=1.5    |       1.946 |            0     |         1718 |     3.397 |       0     |
|   6 | nominal     | isotonic_dw   |     2   | 1.5  | joint κ=2 q=1.5    |       1.132 |            0     |         1718 |     3.468 |       0     |
|   6 | nominal     | isotonic_dw   |     3   | 1.5  | joint κ=3 q=1.5    |       1.072 |            0     |         1718 |     3.467 |       0     |
|   6 | nominal     | isotonic_dw   |     4   | 1.5  | joint κ=4 q=1.5    |       0.498 |            0     |         1718 |     3.538 |       0     |
|   6 | nominal     | isotonic_dw   |     5   | 1.5  | joint κ=5 q=1.5    |       0.32  |            0     |         1718 |     3.554 |       0     |
|   6 | nominal     | isotonic_dw   |     6   | 1.5  | joint κ=6 q=1.5    |       0.234 |            0.291 |         1718 |     3.537 |       0     |
|   6 | nominal     | isotonic_dw   |     7   | 1.5  | joint κ=7 q=1.5    |       0.038 |            0.291 |         1718 |     3.65  |       0     |
|   6 | nominal     | isotonic_dw   |     0.5 | 0    | joint κ=0.5 q=0    |       5.036 |            0     |         1718 |     3.003 |       0.396 |
|   6 | nominal     | isotonic_dw   |     0.5 | 0.75 | joint κ=0.5 q=0.75 |       3.164 |            0     |         1718 |     3.331 |       0.046 |
|   6 | nominal     | isotonic_dw   |     0.5 | 3    | joint κ=0.5 q=3    |       1.134 |            0     |         1718 |     3.468 |       0     |
|   6 | nominal     | isotonic_dw   |     0.5 | 6    | joint κ=0.5 q=6    |       1     |            0     |         1718 |     3.47  |       0     |
|   6 | nominal     | isotonic_dw   |     0.5 | 0    | indep κ=0.5        |       5.036 |            0     |         1718 |     2.959 |       0.364 |
|   6 | nominal     | isotonic_dw   |     1   | 0    | indep κ=1          |       4.946 |            0     |         1718 |     2.991 |       0.348 |
|   6 | nominal     | isotonic_dw   |     2   | 0    | indep κ=2          |       3.502 |            0     |         1718 |     3.593 |       0.1   |
|   6 | nominal     | isotonic_dw   |     3   | 0    | indep κ=3          |       3.032 |            0     |         1718 |     3.768 |       0.05  |
|   6 | nominal     | isotonic_dw   |     4   | 0    | indep κ=4          |       0.574 |            0     |         1718 |     4.83  |       0     |
|   6 | nominal     | isotonic_dw   |     5   | 0    | indep κ=5          |       0.372 |            0     |         1718 |     4.916 |       0     |
|   6 | nominal     | isotonic_dw   |     6   | 0    | indep κ=6          |       0.272 |            0.407 |         1718 |     4.901 |       0     |
|   6 | nominal     | isotonic_dw   |     7   | 0    | indep κ=7          |       0.038 |            0.407 |         1718 |     5.07  |       0     |
|   8 | noisy       | isotonic      |     0.5 | 1.5  | joint κ=0.5 q=1.5  |       3.454 |            0.704 |         2274 |     4.147 |       0.11  |
|   8 | noisy       | isotonic      |     1   | 1.5  | joint κ=1 q=1.5    |       3.22  |            0.748 |         2274 |     4.149 |       0.068 |
|   8 | noisy       | isotonic      |     2   | 1.5  | joint κ=2 q=1.5    |       2.736 |            0.748 |         2274 |     4.192 |       0.022 |
|   8 | noisy       | isotonic      |     3   | 1.5  | joint κ=3 q=1.5    |       2.262 |            0.748 |         2274 |     4.217 |       0     |
|   8 | noisy       | isotonic      |     4   | 1.5  | joint κ=4 q=1.5    |       1.782 |            0.836 |         2274 |     4.27  |       0     |
|   8 | noisy       | isotonic      |     5   | 1.5  | joint κ=5 q=1.5    |       1.43  |            0.836 |         2274 |     4.294 |       0     |
|   8 | noisy       | isotonic      |     6   | 1.5  | joint κ=6 q=1.5    |       0.894 |            0.836 |         2274 |     4.402 |       0     |
|   8 | noisy       | isotonic      |     7   | 1.5  | joint κ=7 q=1.5    |       0.058 |            0.836 |         2274 |     4.637 |       0     |
|   8 | noisy       | isotonic      |     0.5 | 0    | joint κ=0.5 q=0    |       7.872 |            0.396 |         2274 |     3.568 |       1.406 |
|   8 | noisy       | isotonic      |     0.5 | 0.75 | joint κ=0.5 q=0.75 |       5.344 |            0.528 |         2274 |     3.918 |       0.602 |
|   8 | noisy       | isotonic      |     0.5 | 3    | joint κ=0.5 q=3    |       2.154 |            0.748 |         2274 |     4.215 |       0     |
|   8 | noisy       | isotonic      |     0.5 | 6    | joint κ=0.5 q=6    |       1.438 |            0.836 |         2274 |     4.293 |       0     |
|   8 | noisy       | isotonic      |     0.5 | 0    | indep κ=0.5        |       7.872 |            0.396 |         2274 |     3.583 |       1.454 |
|   8 | noisy       | isotonic      |     1   | 0    | indep κ=1          |       7.756 |            0.396 |         2274 |     3.603 |       1.432 |
|   8 | noisy       | isotonic      |     2   | 0    | indep κ=2          |       7.714 |            0.528 |         2274 |     3.609 |       1.43  |
|   8 | noisy       | isotonic      |     3   | 0    | indep κ=3          |       6.842 |            0.528 |         2274 |     3.815 |       1.092 |
|   8 | noisy       | isotonic      |     4   | 0    | indep κ=4          |       5.432 |            0.528 |         2274 |     4.123 |       0.632 |
|   8 | noisy       | isotonic      |     5   | 0    | indep κ=5          |       3.304 |            0.528 |         2274 |     4.657 |       0.176 |
|   8 | noisy       | isotonic      |     6   | 0    | indep κ=6          |       1.904 |            0.836 |         2274 |     4.962 |       0.04  |
|   8 | noisy       | isotonic      |     7   | 0    | indep κ=7          |       0.08  |            0.836 |         2274 |     5.571 |       0     |
|   8 | noisy       | isotonic_dw   |     0.5 | 1.5  | joint κ=0.5 q=1.5  |       3.128 |            0.967 |         2274 |     4.12  |       0.056 |
|   8 | noisy       | isotonic_dw   |     1   | 1.5  | joint κ=1 q=1.5    |       2.856 |            0.967 |         2274 |     4.141 |       0.01  |
|   8 | noisy       | isotonic_dw   |     2   | 1.5  | joint κ=2 q=1.5    |       2.362 |            0.967 |         2274 |     4.197 |       0     |
|   8 | noisy       | isotonic_dw   |     3   | 1.5  | joint κ=3 q=1.5    |       1.808 |            0.967 |         2274 |     4.259 |       0     |
|   8 | noisy       | isotonic_dw   |     4   | 1.5  | joint κ=4 q=1.5    |       1.284 |            0.967 |         2274 |     4.328 |       0     |
|   8 | noisy       | isotonic_dw   |     5   | 1.5  | joint κ=5 q=1.5    |       0.926 |            0.967 |         2274 |     4.393 |       0     |
|   8 | noisy       | isotonic_dw   |     6   | 1.5  | joint κ=6 q=1.5    |       0.318 |            0.967 |         2274 |     4.53  |       0     |
|   8 | noisy       | isotonic_dw   |     7   | 1.5  | joint κ=7 q=1.5    |       0.026 |            0.967 |         2274 |     4.631 |       0     |
|   8 | noisy       | isotonic_dw   |     0.5 | 0    | joint κ=0.5 q=0    |       7.844 |            0.396 |         2274 |     3.57  |       1.394 |
|   8 | noisy       | isotonic_dw   |     0.5 | 0.75 | joint κ=0.5 q=0.75 |       4.616 |            0.792 |         2274 |     3.988 |       0.396 |
|   8 | noisy       | isotonic_dw   |     0.5 | 3    | joint κ=0.5 q=3    |       1.996 |            0.967 |         2274 |     4.232 |       0     |
|   8 | noisy       | isotonic_dw   |     0.5 | 6    | joint κ=0.5 q=6    |       1     |            0.967 |         2274 |     4.376 |       0     |
|   8 | noisy       | isotonic_dw   |     0.5 | 0    | indep κ=0.5        |       7.844 |            0.396 |         2274 |     3.589 |       1.45  |
|   8 | noisy       | isotonic_dw   |     1   | 0    | indep κ=1          |       7.714 |            0.528 |         2274 |     3.609 |       1.43  |
|   8 | noisy       | isotonic_dw   |     2   | 0    | indep κ=2          |       6.886 |            0.528 |         2274 |     3.802 |       1.12  |
|   8 | noisy       | isotonic_dw   |     3   | 0    | indep κ=3          |       5.134 |            0.528 |         2274 |     4.199 |       0.53  |
|   8 | noisy       | isotonic_dw   |     4   | 0    | indep κ=4          |       3.84  |            0.967 |         2274 |     4.442 |       0.254 |
|   8 | noisy       | isotonic_dw   |     5   | 0    | indep κ=5          |       2.198 |            0.967 |         2274 |     4.869 |       0.066 |
|   8 | noisy       | isotonic_dw   |     6   | 0    | indep κ=6          |       0.422 |            0.967 |         2274 |     5.408 |       0.002 |
|   8 | noisy       | isotonic_dw   |     7   | 0    | indep κ=7          |       0.026 |            0.967 |         2274 |     5.571 |       0     |
|   8 | nominal     | isotonic      |     0.5 | 1.5  | joint κ=0.5 q=1.5  |       2.876 |            0.304 |         2299 |     3.474 |       0.002 |
|   8 | nominal     | isotonic      |     1   | 1.5  | joint κ=1 q=1.5    |       2.546 |            0.304 |         2299 |     3.502 |       0     |
|   8 | nominal     | isotonic      |     2   | 1.5  | joint κ=2 q=1.5    |       1.982 |            0.304 |         2299 |     3.52  |       0     |
|   8 | nominal     | isotonic      |     3   | 1.5  | joint κ=3 q=1.5    |       1.418 |            0.304 |         2299 |     3.543 |       0     |
|   8 | nominal     | isotonic      |     4   | 1.5  | joint κ=4 q=1.5    |       1.012 |            0.435 |         2299 |     3.548 |       0     |
|   8 | nominal     | isotonic      |     5   | 1.5  | joint κ=5 q=1.5    |       0.526 |            0.435 |         2299 |     3.589 |       0     |
|   8 | nominal     | isotonic      |     6   | 1.5  | joint κ=6 q=1.5    |       0.262 |            0.652 |         2299 |     3.592 |       0     |
|   8 | nominal     | isotonic      |     7   | 1.5  | joint κ=7 q=1.5    |       0.014 |            0.652 |         2299 |     3.644 |       0     |
|   8 | nominal     | isotonic      |     0.5 | 0    | joint κ=0.5 q=0    |       6.764 |            0     |         2299 |     3.121 |       0.756 |
|   8 | nominal     | isotonic      |     0.5 | 0.75 | joint κ=0.5 q=0.75 |       4.304 |            0.304 |         2299 |     3.359 |       0.154 |
|   8 | nominal     | isotonic      |     0.5 | 3    | joint κ=0.5 q=3    |       1.966 |            0.304 |         2299 |     3.52  |       0     |
|   8 | nominal     | isotonic      |     0.5 | 6    | joint κ=0.5 q=6    |       1.016 |            0.435 |         2299 |     3.538 |       0     |
|   8 | nominal     | isotonic      |     0.5 | 0    | indep κ=0.5        |       6.764 |            0     |         2299 |     3.121 |       0.78  |
|   8 | nominal     | isotonic      |     1   | 0    | indep κ=1          |       6.448 |            0.348 |         2299 |     3.123 |       0.68  |
|   8 | nominal     | isotonic      |     2   | 0    | indep κ=2          |       5.866 |            0.652 |         2299 |     3.251 |       0.546 |
|   8 | nominal     | isotonic      |     3   | 0    | indep κ=3          |       4.096 |            0.652 |         2299 |     3.827 |       0.132 |
|   8 | nominal     | isotonic      |     4   | 0    | indep κ=4          |       2.688 |            0.652 |         2299 |     4.233 |       0.038 |
|   8 | nominal     | isotonic      |     5   | 0    | indep κ=5          |       0.64  |            0.652 |         2299 |     4.88  |       0.002 |
|   8 | nominal     | isotonic      |     6   | 0    | indep κ=6          |       0.306 |            1     |         2299 |     4.929 |       0     |
|   8 | nominal     | isotonic      |     7   | 0    | indep κ=7          |       0.014 |            1     |         2299 |     5.051 |       0     |
|   8 | nominal     | isotonic_dw   |     0.5 | 1.5  | joint κ=0.5 q=1.5  |       2.028 |            0     |         2299 |     3.576 |       0.002 |
|   8 | nominal     | isotonic_dw   |     1   | 1.5  | joint κ=1 q=1.5    |       2.006 |            0     |         2299 |     3.579 |       0.002 |
|   8 | nominal     | isotonic_dw   |     2   | 1.5  | joint κ=2 q=1.5    |       1.222 |            0     |         2299 |     3.605 |       0     |
|   8 | nominal     | isotonic_dw   |     3   | 1.5  | joint κ=3 q=1.5    |       1.102 |            0     |         2299 |     3.599 |       0     |
|   8 | nominal     | isotonic_dw   |     4   | 1.5  | joint κ=4 q=1.5    |       0.606 |            0     |         2299 |     3.643 |       0     |
|   8 | nominal     | isotonic_dw   |     5   | 1.5  | joint κ=5 q=1.5    |       0.384 |            0     |         2299 |     3.651 |       0     |
|   8 | nominal     | isotonic_dw   |     6   | 1.5  | joint κ=6 q=1.5    |       0.306 |            0     |         2299 |     3.64  |       0     |
|   8 | nominal     | isotonic_dw   |     7   | 1.5  | joint κ=7 q=1.5    |       0.048 |            0     |         2299 |     3.751 |       0     |
|   8 | nominal     | isotonic_dw   |     0.5 | 0    | joint κ=0.5 q=0    |       6.764 |            0     |         2299 |     3.121 |       0.756 |
|   8 | nominal     | isotonic_dw   |     0.5 | 0.75 | joint κ=0.5 q=0.75 |       3.614 |            0     |         2299 |     3.524 |       0.102 |
|   8 | nominal     | isotonic_dw   |     0.5 | 3    | joint κ=0.5 q=3    |       1.208 |            0     |         2299 |     3.602 |       0     |
|   8 | nominal     | isotonic_dw   |     0.5 | 6    | joint κ=0.5 q=6    |       1.002 |            0     |         2299 |     3.6   |       0     |
|   8 | nominal     | isotonic_dw   |     0.5 | 0    | indep κ=0.5        |       6.764 |            0     |         2299 |     3.121 |       0.78  |
|   8 | nominal     | isotonic_dw   |     1   | 0    | indep κ=1          |       6.638 |            0     |         2299 |     3.153 |       0.764 |
|   8 | nominal     | isotonic_dw   |     2   | 0    | indep κ=2          |       4.6   |            0     |         2299 |     3.789 |       0.248 |
|   8 | nominal     | isotonic_dw   |     3   | 0    | indep κ=3          |       3.986 |            0     |         2299 |     3.958 |       0.164 |
|   8 | nominal     | isotonic_dw   |     4   | 0    | indep κ=4          |       0.702 |            0     |         2299 |     4.949 |       0.002 |
|   8 | nominal     | isotonic_dw   |     5   | 0    | indep κ=5          |       0.492 |            0     |         2299 |     5.017 |       0.002 |
|   8 | nominal     | isotonic_dw   |     6   | 0    | indep κ=6          |       0.366 |            0.348 |         2299 |     4.998 |       0.002 |
|   8 | nominal     | isotonic_dw   |     7   | 0    | indep κ=7          |       0.048 |            0.348 |         2299 |     5.166 |       0     |

## Matched question rate

Each joint point against the per-robot rule with the nearest question rate (McNemar exact on crossing robots, development seeds, exploratory).

|   N | condition   | calibration   | joint              |   joint_questions | matched_rule   |   rule_questions |   joint_collisions_pct |   rule_collisions_pct |   only_joint_collided |   only_rule_collided |     p |   joint_delay |   rule_delay |
|----:|:------------|:--------------|:-------------------|------------------:|:---------------|-----------------:|-----------------------:|----------------------:|----------------------:|---------------------:|------:|--------------:|-------------:|
|   6 | noisy       | isotonic      | joint κ=0.5 q=1.5  |             3.168 | indep κ=5      |            2.452 |                  0.295 |                 0.295 |                     0 |                    0 | 1     |         3.96  |        4.588 |
|   6 | noisy       | isotonic      | joint κ=1 q=1.5    |             3.026 | indep κ=5      |            2.452 |                  0.354 |                 0.295 |                     1 |                    0 | 1     |         3.988 |        4.588 |
|   6 | noisy       | isotonic      | joint κ=2 q=1.5    |             2.484 | indep κ=5      |            2.452 |                  0.354 |                 0.295 |                     1 |                    0 | 1     |         4.085 |        4.588 |
|   6 | noisy       | isotonic      | joint κ=3 q=1.5    |             2.044 | indep κ=5      |            2.452 |                  0.354 |                 0.295 |                     1 |                    0 | 1     |         4.138 |        4.588 |
|   6 | noisy       | isotonic      | joint κ=4 q=1.5    |             1.578 | indep κ=6      |            1.34  |                  0.413 |                 0.531 |                     0 |                    2 | 0.5   |         4.218 |        4.975 |
|   6 | noisy       | isotonic      | joint κ=5 q=1.5    |             1.242 | indep κ=6      |            1.34  |                  0.413 |                 0.531 |                     0 |                    2 | 0.5   |         4.272 |        4.975 |
|   6 | noisy       | isotonic      | joint κ=6 q=1.5    |             0.766 | indep κ=6      |            1.34  |                  0.531 |                 0.531 |                     0 |                    0 | 1     |         4.398 |        4.975 |
|   6 | noisy       | isotonic      | joint κ=7 q=1.5    |             0.074 | indep κ=7      |            0.102 |                  0.531 |                 0.531 |                     0 |                    0 | 1     |         4.627 |        5.554 |
|   6 | noisy       | isotonic      | joint κ=0.5 q=0    |             5.916 | indep κ=0.5    |            5.916 |                  0.059 |                 0.059 |                     0 |                    0 | 1     |         3.47  |        3.454 |
|   6 | noisy       | isotonic      | joint κ=0.5 q=0.75 |             4.662 | indep κ=3      |            5.12  |                  0.295 |                 0.295 |                     0 |                    0 | 1     |         3.712 |        3.701 |
|   6 | noisy       | isotonic      | joint κ=0.5 q=3    |             2.08  | indep κ=5      |            2.452 |                  0.354 |                 0.295 |                     1 |                    0 | 1     |         4.113 |        4.588 |
|   6 | noisy       | isotonic      | joint κ=0.5 q=6    |             1.282 | indep κ=6      |            1.34  |                  0.413 |                 0.531 |                     0 |                    2 | 0.5   |         4.255 |        4.975 |
|   6 | noisy       | isotonic_dw   | joint κ=0.5 q=1.5  |             2.91  | indep κ=4      |            2.814 |                  0.884 |                 1.002 |                     0 |                    2 | 0.5   |         3.964 |        4.37  |
|   6 | noisy       | isotonic_dw   | joint κ=1 q=1.5    |             2.62  | indep κ=4      |            2.814 |                  0.884 |                 1.002 |                     0 |                    2 | 0.5   |         4.007 |        4.37  |
|   6 | noisy       | isotonic_dw   | joint κ=2 q=1.5    |             2.152 | indep κ=5      |            1.558 |                  1.002 |                 1.002 |                     0 |                    0 | 1     |         4.068 |        4.842 |
|   6 | noisy       | isotonic_dw   | joint κ=3 q=1.5    |             1.606 | indep κ=5      |            1.558 |                  1.002 |                 1.002 |                     0 |                    0 | 1     |         4.182 |        4.842 |
|   6 | noisy       | isotonic_dw   | joint κ=4 q=1.5    |             1.142 | indep κ=5      |            1.558 |                  1.002 |                 1.002 |                     0 |                    0 | 1     |         4.265 |        4.842 |
|   6 | noisy       | isotonic_dw   | joint κ=5 q=1.5    |             0.832 | indep κ=6      |            0.346 |                  1.002 |                 1.002 |                     0 |                    0 | 1     |         4.342 |        5.37  |
|   6 | noisy       | isotonic_dw   | joint κ=6 q=1.5    |             0.286 | indep κ=6      |            0.346 |                  1.002 |                 1.002 |                     0 |                    0 | 1     |         4.511 |        5.37  |
|   6 | noisy       | isotonic_dw   | joint κ=7 q=1.5    |             0.022 | indep κ=7      |            0.022 |                  1.002 |                 1.002 |                     0 |                    0 | 1     |         4.612 |        5.547 |
|   6 | noisy       | isotonic_dw   | joint κ=0.5 q=0    |             5.906 | indep κ=0.5    |            5.906 |                  0.059 |                 0.059 |                     0 |                    0 | 1     |         3.472 |        3.457 |
|   6 | noisy       | isotonic_dw   | joint κ=0.5 q=0.75 |             4.074 | indep κ=3      |            3.878 |                  0.472 |                 0.295 |                     3 |                    0 | 0.25  |         3.792 |        4.077 |
|   6 | noisy       | isotonic_dw   | joint κ=0.5 q=3    |             1.966 | indep κ=5      |            1.558 |                  1.002 |                 1.002 |                     0 |                    0 | 1     |         4.092 |        4.842 |
|   6 | noisy       | isotonic_dw   | joint κ=0.5 q=6    |             1     | indep κ=5      |            1.558 |                  1.002 |                 1.002 |                     0 |                    0 | 1     |         4.289 |        4.842 |
|   6 | nominal     | isotonic      | joint κ=0.5 q=1.5  |             2.656 | indep κ=3      |            3.11  |                  0.582 |                 0.698 |                     0 |                    2 | 0.5   |         3.292 |        3.644 |
|   6 | nominal     | isotonic      | joint κ=1 q=1.5    |             2.318 | indep κ=4      |            2.074 |                  0.582 |                 0.698 |                     0 |                    2 | 0.5   |         3.315 |        4.079 |
|   6 | nominal     | isotonic      | joint κ=2 q=1.5    |             1.918 | indep κ=4      |            2.074 |                  0.582 |                 0.698 |                     0 |                    2 | 0.5   |         3.329 |        4.079 |
|   6 | nominal     | isotonic      | joint κ=3 q=1.5    |             1.26  | indep κ=5      |            0.502 |                  0.582 |                 0.698 |                     0 |                    2 | 0.5   |         3.394 |        4.772 |
|   6 | nominal     | isotonic      | joint κ=4 q=1.5    |             0.982 | indep κ=5      |            0.502 |                  0.698 |                 0.698 |                     2 |                    2 | 1     |         3.418 |        4.772 |
|   6 | nominal     | isotonic      | joint κ=5 q=1.5    |             0.428 | indep κ=5      |            0.502 |                  0.698 |                 0.698 |                     2 |                    2 | 1     |         3.482 |        4.772 |
|   6 | nominal     | isotonic      | joint κ=6 q=1.5    |             0.23  | indep κ=6      |            0.264 |                  0.873 |                 0.99  |                     0 |                    2 | 0.5   |         3.491 |        4.824 |
|   6 | nominal     | isotonic      | joint κ=7 q=1.5    |             0.012 | indep κ=7      |            0.012 |                  0.873 |                 0.99  |                     0 |                    2 | 0.5   |         3.548 |        4.962 |
|   6 | nominal     | isotonic      | joint κ=0.5 q=0    |             5.036 | indep κ=0.5    |            5.036 |                  0     |                 0     |                     0 |                    0 | 1     |         3.003 |        2.959 |
|   6 | nominal     | isotonic      | joint κ=0.5 q=0.75 |             3.742 | indep κ=2      |            4.362 |                  0.582 |                 0.698 |                     0 |                    2 | 0.5   |         3.14  |        3.095 |
|   6 | nominal     | isotonic      | joint κ=0.5 q=3    |             1.908 | indep κ=4      |            2.074 |                  0.582 |                 0.698 |                     0 |                    2 | 0.5   |         3.328 |        4.079 |
|   6 | nominal     | isotonic      | joint κ=0.5 q=6    |             1.008 | indep κ=5      |            0.502 |                  0.698 |                 0.698 |                     2 |                    2 | 1     |         3.393 |        4.772 |
|   6 | nominal     | isotonic_dw   | joint κ=0.5 q=1.5  |             1.968 | indep κ=3      |            3.032 |                  0     |                 0     |                     0 |                    0 | 1     |         3.384 |        3.768 |
|   6 | nominal     | isotonic_dw   | joint κ=1 q=1.5    |             1.946 | indep κ=3      |            3.032 |                  0     |                 0     |                     0 |                    0 | 1     |         3.397 |        3.768 |
|   6 | nominal     | isotonic_dw   | joint κ=2 q=1.5    |             1.132 | indep κ=4      |            0.574 |                  0     |                 0     |                     0 |                    0 | 1     |         3.468 |        4.83  |
|   6 | nominal     | isotonic_dw   | joint κ=3 q=1.5    |             1.072 | indep κ=4      |            0.574 |                  0     |                 0     |                     0 |                    0 | 1     |         3.467 |        4.83  |
|   6 | nominal     | isotonic_dw   | joint κ=4 q=1.5    |             0.498 | indep κ=4      |            0.574 |                  0     |                 0     |                     0 |                    0 | 1     |         3.538 |        4.83  |
|   6 | nominal     | isotonic_dw   | joint κ=5 q=1.5    |             0.32  | indep κ=6      |            0.272 |                  0     |                 0.407 |                     0 |                    7 | 0.016 |         3.554 |        4.901 |
|   6 | nominal     | isotonic_dw   | joint κ=6 q=1.5    |             0.234 | indep κ=6      |            0.272 |                  0.291 |                 0.407 |                     0 |                    2 | 0.5   |         3.537 |        4.901 |
|   6 | nominal     | isotonic_dw   | joint κ=7 q=1.5    |             0.038 | indep κ=7      |            0.038 |                  0.291 |                 0.407 |                     0 |                    2 | 0.5   |         3.65  |        5.07  |
|   6 | nominal     | isotonic_dw   | joint κ=0.5 q=0    |             5.036 | indep κ=0.5    |            5.036 |                  0     |                 0     |                     0 |                    0 | 1     |         3.003 |        2.959 |
|   6 | nominal     | isotonic_dw   | joint κ=0.5 q=0.75 |             3.164 | indep κ=3      |            3.032 |                  0     |                 0     |                     0 |                    0 | 1     |         3.331 |        3.768 |
|   6 | nominal     | isotonic_dw   | joint κ=0.5 q=3    |             1.134 | indep κ=4      |            0.574 |                  0     |                 0     |                     0 |                    0 | 1     |         3.468 |        4.83  |
|   6 | nominal     | isotonic_dw   | joint κ=0.5 q=6    |             1     | indep κ=4      |            0.574 |                  0     |                 0     |                     0 |                    0 | 1     |         3.47  |        4.83  |
|   8 | noisy       | isotonic      | joint κ=0.5 q=1.5  |             3.454 | indep κ=5      |            3.304 |                  0.704 |                 0.528 |                     4 |                    0 | 0.125 |         4.147 |        4.657 |
|   8 | noisy       | isotonic      | joint κ=1 q=1.5    |             3.22  | indep κ=5      |            3.304 |                  0.748 |                 0.528 |                     5 |                    0 | 0.062 |         4.149 |        4.657 |
|   8 | noisy       | isotonic      | joint κ=2 q=1.5    |             2.736 | indep κ=5      |            3.304 |                  0.748 |                 0.528 |                     5 |                    0 | 0.062 |         4.192 |        4.657 |
|   8 | noisy       | isotonic      | joint κ=3 q=1.5    |             2.262 | indep κ=6      |            1.904 |                  0.748 |                 0.836 |                     0 |                    2 | 0.5   |         4.217 |        4.962 |
|   8 | noisy       | isotonic      | joint κ=4 q=1.5    |             1.782 | indep κ=6      |            1.904 |                  0.836 |                 0.836 |                     0 |                    0 | 1     |         4.27  |        4.962 |
|   8 | noisy       | isotonic      | joint κ=5 q=1.5    |             1.43  | indep κ=6      |            1.904 |                  0.836 |                 0.836 |                     0 |                    0 | 1     |         4.294 |        4.962 |
|   8 | noisy       | isotonic      | joint κ=6 q=1.5    |             0.894 | indep κ=7      |            0.08  |                  0.836 |                 0.836 |                     0 |                    0 | 1     |         4.402 |        5.571 |
|   8 | noisy       | isotonic      | joint κ=7 q=1.5    |             0.058 | indep κ=7      |            0.08  |                  0.836 |                 0.836 |                     0 |                    0 | 1     |         4.637 |        5.571 |
|   8 | noisy       | isotonic      | joint κ=0.5 q=0    |             7.872 | indep κ=0.5    |            7.872 |                  0.396 |                 0.396 |                     0 |                    0 | 1     |         3.568 |        3.583 |
|   8 | noisy       | isotonic      | joint κ=0.5 q=0.75 |             5.344 | indep κ=4      |            5.432 |                  0.528 |                 0.528 |                     0 |                    0 | 1     |         3.918 |        4.123 |
|   8 | noisy       | isotonic      | joint κ=0.5 q=3    |             2.154 | indep κ=6      |            1.904 |                  0.748 |                 0.836 |                     0 |                    2 | 0.5   |         4.215 |        4.962 |
|   8 | noisy       | isotonic      | joint κ=0.5 q=6    |             1.438 | indep κ=6      |            1.904 |                  0.836 |                 0.836 |                     0 |                    0 | 1     |         4.293 |        4.962 |
|   8 | noisy       | isotonic_dw   | joint κ=0.5 q=1.5  |             3.128 | indep κ=4      |            3.84  |                  0.967 |                 0.967 |                     0 |                    0 | 1     |         4.12  |        4.442 |
|   8 | noisy       | isotonic_dw   | joint κ=1 q=1.5    |             2.856 | indep κ=5      |            2.198 |                  0.967 |                 0.967 |                     0 |                    0 | 1     |         4.141 |        4.869 |
|   8 | noisy       | isotonic_dw   | joint κ=2 q=1.5    |             2.362 | indep κ=5      |            2.198 |                  0.967 |                 0.967 |                     0 |                    0 | 1     |         4.197 |        4.869 |
|   8 | noisy       | isotonic_dw   | joint κ=3 q=1.5    |             1.808 | indep κ=5      |            2.198 |                  0.967 |                 0.967 |                     0 |                    0 | 1     |         4.259 |        4.869 |
|   8 | noisy       | isotonic_dw   | joint κ=4 q=1.5    |             1.284 | indep κ=6      |            0.422 |                  0.967 |                 0.967 |                     0 |                    0 | 1     |         4.328 |        5.408 |
|   8 | noisy       | isotonic_dw   | joint κ=5 q=1.5    |             0.926 | indep κ=6      |            0.422 |                  0.967 |                 0.967 |                     0 |                    0 | 1     |         4.393 |        5.408 |
|   8 | noisy       | isotonic_dw   | joint κ=6 q=1.5    |             0.318 | indep κ=6      |            0.422 |                  0.967 |                 0.967 |                     0 |                    0 | 1     |         4.53  |        5.408 |
|   8 | noisy       | isotonic_dw   | joint κ=7 q=1.5    |             0.026 | indep κ=7      |            0.026 |                  0.967 |                 0.967 |                     0 |                    0 | 1     |         4.631 |        5.571 |
|   8 | noisy       | isotonic_dw   | joint κ=0.5 q=0    |             7.844 | indep κ=0.5    |            7.844 |                  0.396 |                 0.396 |                     0 |                    0 | 1     |         3.57  |        3.589 |
|   8 | noisy       | isotonic_dw   | joint κ=0.5 q=0.75 |             4.616 | indep κ=3      |            5.134 |                  0.792 |                 0.528 |                     6 |                    0 | 0.031 |         3.988 |        4.199 |
|   8 | noisy       | isotonic_dw   | joint κ=0.5 q=3    |             1.996 | indep κ=5      |            2.198 |                  0.967 |                 0.967 |                     0 |                    0 | 1     |         4.232 |        4.869 |
|   8 | noisy       | isotonic_dw   | joint κ=0.5 q=6    |             1     | indep κ=6      |            0.422 |                  0.967 |                 0.967 |                     0 |                    0 | 1     |         4.376 |        5.408 |
|   8 | nominal     | isotonic      | joint κ=0.5 q=1.5  |             2.876 | indep κ=4      |            2.688 |                  0.304 |                 0.652 |                     0 |                    8 | 0.008 |         3.474 |        4.233 |
|   8 | nominal     | isotonic      | joint κ=1 q=1.5    |             2.546 | indep κ=4      |            2.688 |                  0.304 |                 0.652 |                     0 |                    8 | 0.008 |         3.502 |        4.233 |
|   8 | nominal     | isotonic      | joint κ=2 q=1.5    |             1.982 | indep κ=4      |            2.688 |                  0.304 |                 0.652 |                     0 |                    8 | 0.008 |         3.52  |        4.233 |
|   8 | nominal     | isotonic      | joint κ=3 q=1.5    |             1.418 | indep κ=5      |            0.64  |                  0.304 |                 0.652 |                     0 |                    8 | 0.008 |         3.543 |        4.88  |
|   8 | nominal     | isotonic      | joint κ=4 q=1.5    |             1.012 | indep κ=5      |            0.64  |                  0.435 |                 0.652 |                     3 |                    8 | 0.227 |         3.548 |        4.88  |
|   8 | nominal     | isotonic      | joint κ=5 q=1.5    |             0.526 | indep κ=5      |            0.64  |                  0.435 |                 0.652 |                     3 |                    8 | 0.227 |         3.589 |        4.88  |
|   8 | nominal     | isotonic      | joint κ=6 q=1.5    |             0.262 | indep κ=6      |            0.306 |                  0.652 |                 1     |                     0 |                    8 | 0.008 |         3.592 |        4.929 |
|   8 | nominal     | isotonic      | joint κ=7 q=1.5    |             0.014 | indep κ=7      |            0.014 |                  0.652 |                 1     |                     0 |                    8 | 0.008 |         3.644 |        5.051 |
|   8 | nominal     | isotonic      | joint κ=0.5 q=0    |             6.764 | indep κ=0.5    |            6.764 |                  0     |                 0     |                     0 |                    0 | 1     |         3.121 |        3.121 |
|   8 | nominal     | isotonic      | joint κ=0.5 q=0.75 |             4.304 | indep κ=3      |            4.096 |                  0.304 |                 0.652 |                     0 |                    8 | 0.008 |         3.359 |        3.827 |
|   8 | nominal     | isotonic      | joint κ=0.5 q=3    |             1.966 | indep κ=4      |            2.688 |                  0.304 |                 0.652 |                     0 |                    8 | 0.008 |         3.52  |        4.233 |
|   8 | nominal     | isotonic      | joint κ=0.5 q=6    |             1.016 | indep κ=5      |            0.64  |                  0.435 |                 0.652 |                     3 |                    8 | 0.227 |         3.538 |        4.88  |
|   8 | nominal     | isotonic_dw   | joint κ=0.5 q=1.5  |             2.028 | indep κ=4      |            0.702 |                  0     |                 0     |                     0 |                    0 | 1     |         3.576 |        4.949 |
|   8 | nominal     | isotonic_dw   | joint κ=1 q=1.5    |             2.006 | indep κ=4      |            0.702 |                  0     |                 0     |                     0 |                    0 | 1     |         3.579 |        4.949 |
|   8 | nominal     | isotonic_dw   | joint κ=2 q=1.5    |             1.222 | indep κ=4      |            0.702 |                  0     |                 0     |                     0 |                    0 | 1     |         3.605 |        4.949 |
|   8 | nominal     | isotonic_dw   | joint κ=3 q=1.5    |             1.102 | indep κ=4      |            0.702 |                  0     |                 0     |                     0 |                    0 | 1     |         3.599 |        4.949 |
|   8 | nominal     | isotonic_dw   | joint κ=4 q=1.5    |             0.606 | indep κ=4      |            0.702 |                  0     |                 0     |                     0 |                    0 | 1     |         3.643 |        4.949 |
|   8 | nominal     | isotonic_dw   | joint κ=5 q=1.5    |             0.384 | indep κ=6      |            0.366 |                  0     |                 0.348 |                     0 |                    8 | 0.008 |         3.651 |        4.998 |
|   8 | nominal     | isotonic_dw   | joint κ=6 q=1.5    |             0.306 | indep κ=6      |            0.366 |                  0     |                 0.348 |                     0 |                    8 | 0.008 |         3.64  |        4.998 |
|   8 | nominal     | isotonic_dw   | joint κ=7 q=1.5    |             0.048 | indep κ=7      |            0.048 |                  0     |                 0.348 |                     0 |                    8 | 0.008 |         3.751 |        5.166 |
|   8 | nominal     | isotonic_dw   | joint κ=0.5 q=0    |             6.764 | indep κ=0.5    |            6.764 |                  0     |                 0     |                     0 |                    0 | 1     |         3.121 |        3.121 |
|   8 | nominal     | isotonic_dw   | joint κ=0.5 q=0.75 |             3.614 | indep κ=3      |            3.986 |                  0     |                 0     |                     0 |                    0 | 1     |         3.524 |        3.958 |
|   8 | nominal     | isotonic_dw   | joint κ=0.5 q=3    |             1.208 | indep κ=4      |            0.702 |                  0     |                 0     |                     0 |                    0 | 1     |         3.602 |        4.949 |
|   8 | nominal     | isotonic_dw   | joint κ=0.5 q=6    |             1.002 | indep κ=4      |            0.702 |                  0     |                 0     |                     0 |                    0 | 1     |         3.6   |        4.949 |

## Joint against the per-robot frontier, interpolated at the same question rate

Delay saved = per-robot delay minus joint delay (s per robot); collision difference = joint minus per-robot (percentage points).

|                               |   points |   delay_saved_mean |   delay_saved_min |   delay_saved_max |   col_diff_mean_pp |   col_diff_max_pp |
|:------------------------------|---------:|-------------------:|------------------:|------------------:|-------------------:|------------------:|
| (6, 'noisy', 'isotonic')      |       11 |              0.508 |            -0.016 |             0.845 |             -0.021 |             0.059 |
| (6, 'noisy', 'isotonic_dw')   |       12 |              0.584 |            -0.015 |             0.935 |              0     |             0.177 |
| (6, 'nominal', 'isotonic')    |       12 |              0.87  |            -0.044 |             1.413 |             -0.085 |             0     |
| (6, 'nominal', 'isotonic_dw') |       12 |              1.007 |            -0.044 |             1.42  |             -0.037 |             0     |
| (8, 'noisy', 'isotonic')      |       11 |              0.588 |             0.016 |             0.897 |              0.039 |             0.201 |
| (8, 'noisy', 'isotonic_dw')   |       12 |              0.654 |             0.019 |             0.94  |              0.007 |             0.088 |
| (8, 'nominal', 'isotonic')    |       12 |              0.946 |             0.001 |             1.408 |             -0.296 |             0     |
| (8, 'nominal', 'isotonic_dw') |       12 |              1.071 |             0.001 |             1.415 |             -0.083 |             0     |
