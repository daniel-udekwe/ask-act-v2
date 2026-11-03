# Pareto study: operator load against safety and delay (month 4, development seeds)

500 paired epochs per point. Collisions are per crossing robot. Ask cost = 1.5 + κ.

## Frontier

|   N | condition   | calibration   |   kappa |    q | method             |   questions |   collisions_pct |   n_crossing |   delay_s |   fallbacks |
|----:|:------------|:--------------|--------:|-----:|:-------------------|------------:|-----------------:|-------------:|----------:|------------:|
|   6 | noisy       | isotonic      |     0.5 | 1.5  | joint κ=0.5 q=1.5  |       2.908 |                0 |         1696 |     3.691 |       0.014 |
|   6 | noisy       | isotonic      |     1   | 1.5  | joint κ=1 q=1.5    |       2.618 |                0 |         1696 |     3.692 |       0.002 |
|   6 | noisy       | isotonic      |     2   | 1.5  | joint κ=2 q=1.5    |       2.186 |                0 |         1696 |     3.763 |       0     |
|   6 | noisy       | isotonic      |     3   | 1.5  | joint κ=3 q=1.5    |       1.75  |                0 |         1696 |     3.846 |       0     |
|   6 | noisy       | isotonic      |     4   | 1.5  | joint κ=4 q=1.5    |       1.29  |                0 |         1696 |     3.995 |       0     |
|   6 | noisy       | isotonic      |     5   | 1.5  | joint κ=5 q=1.5    |       0.89  |                0 |         1696 |     4.156 |       0     |
|   6 | noisy       | isotonic      |     6   | 1.5  | joint κ=6 q=1.5    |       0.442 |                0 |         1696 |     4.394 |       0     |
|   6 | noisy       | isotonic      |     7   | 1.5  | joint κ=7 q=1.5    |       0.008 |                0 |         1696 |     4.684 |       0     |
|   6 | noisy       | isotonic      |     0.5 | 0    | joint κ=0.5 q=0    |       5.578 |                0 |         1696 |     3.458 |       0.768 |
|   6 | noisy       | isotonic      |     0.5 | 0.75 | joint κ=0.5 q=0.75 |       4.19  |                0 |         1696 |     3.618 |       0.382 |
|   6 | noisy       | isotonic      |     0.5 | 3    | joint κ=0.5 q=3    |       1.99  |                0 |         1696 |     3.821 |       0     |
|   6 | noisy       | isotonic      |     0.5 | 6    | joint κ=0.5 q=6    |       1.012 |                0 |         1696 |     4.115 |       0     |
|   6 | noisy       | isotonic      |     0.5 | 0    | indep κ=0.5        |       5.988 |                0 |         1696 |     3.392 |       0.802 |
|   6 | noisy       | isotonic      |     1   | 0    | indep κ=1          |       5.94  |                0 |         1696 |     3.389 |       0.78  |
|   6 | noisy       | isotonic      |     2   | 0    | indep κ=2          |       5.654 |                0 |         1696 |     3.42  |       0.776 |
|   6 | noisy       | isotonic      |     3   | 0    | indep κ=3          |       5.21  |                0 |         1696 |     3.566 |       0.73  |
|   6 | noisy       | isotonic      |     4   | 0    | indep κ=4          |       3.916 |                0 |         1696 |     3.722 |       0.182 |
|   6 | noisy       | isotonic      |     5   | 0    | indep κ=5          |       2.876 |                0 |         1696 |     4.157 |       0.046 |
|   6 | noisy       | isotonic      |     6   | 0    | indep κ=6          |       2.472 |                0 |         1696 |     5.105 |       0.016 |
|   6 | noisy       | isotonic      |     7   | 0    | indep κ=7          |       0.842 |                0 |         1696 |     6.332 |       0     |
|   6 | noisy       | isotonic_dw   |     0.5 | 1.5  | joint κ=0.5 q=1.5  |       2.46  |                0 |         1696 |     3.697 |       0     |
|   6 | noisy       | isotonic_dw   |     1   | 1.5  | joint κ=1 q=1.5    |       2.268 |                0 |         1696 |     3.749 |       0     |
|   6 | noisy       | isotonic_dw   |     2   | 1.5  | joint κ=2 q=1.5    |       1.8   |                0 |         1696 |     3.849 |       0     |
|   6 | noisy       | isotonic_dw   |     3   | 1.5  | joint κ=3 q=1.5    |       1.376 |                0 |         1696 |     3.972 |       0     |
|   6 | noisy       | isotonic_dw   |     4   | 1.5  | joint κ=4 q=1.5    |       0.96  |                0 |         1696 |     4.127 |       0     |
|   6 | noisy       | isotonic_dw   |     5   | 1.5  | joint κ=5 q=1.5    |       0.552 |                0 |         1696 |     4.327 |       0     |
|   6 | noisy       | isotonic_dw   |     6   | 1.5  | joint κ=6 q=1.5    |       0.08  |                0 |         1696 |     4.624 |       0     |
|   6 | noisy       | isotonic_dw   |     7   | 1.5  | joint κ=7 q=1.5    |       0.008 |                0 |         1696 |     4.684 |       0     |
|   6 | noisy       | isotonic_dw   |     0.5 | 0    | joint κ=0.5 q=0    |       5.488 |                0 |         1696 |     3.461 |       0.74  |
|   6 | noisy       | isotonic_dw   |     0.5 | 0.75 | joint κ=0.5 q=0.75 |       3.562 |                0 |         1696 |     3.633 |       0.21  |
|   6 | noisy       | isotonic_dw   |     0.5 | 3    | joint κ=0.5 q=3    |       1.778 |                0 |         1696 |     3.856 |       0     |
|   6 | noisy       | isotonic_dw   |     0.5 | 6    | joint κ=0.5 q=6    |       1     |                0 |         1696 |     4.117 |       0     |
|   6 | noisy       | isotonic_dw   |     0.5 | 0    | indep κ=0.5        |       5.95  |                0 |         1696 |     3.375 |       0.78  |
|   6 | noisy       | isotonic_dw   |     1   | 0    | indep κ=1          |       5.822 |                0 |         1696 |     3.389 |       0.778 |
|   6 | noisy       | isotonic_dw   |     2   | 0    | indep κ=2          |       5.458 |                0 |         1696 |     3.481 |       0.744 |
|   6 | noisy       | isotonic_dw   |     3   | 0    | indep κ=3          |       4.118 |                0 |         1696 |     3.651 |       0.236 |
|   6 | noisy       | isotonic_dw   |     4   | 0    | indep κ=4          |       3.072 |                0 |         1696 |     4.028 |       0.054 |
|   6 | noisy       | isotonic_dw   |     5   | 0    | indep κ=5          |       2.462 |                0 |         1696 |     4.823 |       0.028 |
|   6 | noisy       | isotonic_dw   |     6   | 0    | indep κ=6          |       1.938 |                0 |         1696 |     6.949 |       0     |
|   6 | noisy       | isotonic_dw   |     7   | 0    | indep κ=7          |       0.712 |                0 |         1696 |     6.183 |       0     |
|   6 | nominal     | isotonic      |     0.5 | 1.5  | joint κ=0.5 q=1.5  |       2.204 |                0 |         1718 |     2.946 |       0     |
|   6 | nominal     | isotonic      |     1   | 1.5  | joint κ=1 q=1.5    |       2.008 |                0 |         1718 |     2.968 |       0     |
|   6 | nominal     | isotonic      |     2   | 1.5  | joint κ=2 q=1.5    |       1.528 |                0 |         1718 |     3.015 |       0     |
|   6 | nominal     | isotonic      |     3   | 1.5  | joint κ=3 q=1.5    |       1.058 |                0 |         1718 |     3.089 |       0     |
|   6 | nominal     | isotonic      |     4   | 1.5  | joint κ=4 q=1.5    |       0.648 |                0 |         1718 |     3.224 |       0     |
|   6 | nominal     | isotonic      |     5   | 1.5  | joint κ=5 q=1.5    |       0.268 |                0 |         1718 |     3.337 |       0     |
|   6 | nominal     | isotonic      |     6   | 1.5  | joint κ=6 q=1.5    |       0.096 |                0 |         1718 |     3.44  |       0     |
|   6 | nominal     | isotonic      |     7   | 1.5  | joint κ=7 q=1.5    |       0.048 |                0 |         1718 |     3.469 |       0     |
|   6 | nominal     | isotonic      |     0.5 | 0    | joint κ=0.5 q=0    |       4.45  |                0 |         1718 |     2.91  |       0.324 |
|   6 | nominal     | isotonic      |     0.5 | 0.75 | joint κ=0.5 q=0.75 |       3.188 |                0 |         1718 |     2.903 |       0.08  |
|   6 | nominal     | isotonic      |     0.5 | 3    | joint κ=0.5 q=3    |       1.526 |                0 |         1718 |     3.016 |       0     |
|   6 | nominal     | isotonic      |     0.5 | 6    | joint κ=0.5 q=6    |       1.004 |                0 |         1718 |     3.128 |       0     |
|   6 | nominal     | isotonic      |     0.5 | 0    | indep κ=0.5        |       5.018 |                0 |         1718 |     2.694 |       0.38  |
|   6 | nominal     | isotonic      |     1   | 0    | indep κ=1          |       4.892 |                0 |         1718 |     2.714 |       0.336 |
|   6 | nominal     | isotonic      |     2   | 0    | indep κ=2          |       4.716 |                0 |         1718 |     2.764 |       0.322 |
|   6 | nominal     | isotonic      |     3   | 0    | indep κ=3          |       3.32  |                0 |         1718 |     3.01  |       0.052 |
|   6 | nominal     | isotonic      |     4   | 0    | indep κ=4          |       1.94  |                0 |         1718 |     3.64  |       0.008 |
|   6 | nominal     | isotonic      |     5   | 0    | indep κ=5          |       1.238 |                0 |         1718 |     4.095 |       0.002 |
|   6 | nominal     | isotonic      |     6   | 0    | indep κ=6          |       1.038 |                0 |         1718 |     4.22  |       0     |
|   6 | nominal     | isotonic      |     7   | 0    | indep κ=7          |       0.934 |                0 |         1718 |     4.33  |       0     |
|   6 | nominal     | isotonic_dw   |     0.5 | 1.5  | joint κ=0.5 q=1.5  |       1.884 |                0 |         1718 |     3.036 |       0     |
|   6 | nominal     | isotonic_dw   |     1   | 1.5  | joint κ=1 q=1.5    |       1.672 |                0 |         1718 |     3.062 |       0     |
|   6 | nominal     | isotonic_dw   |     2   | 1.5  | joint κ=2 q=1.5    |       1.082 |                0 |         1718 |     3.17  |       0     |
|   6 | nominal     | isotonic_dw   |     3   | 1.5  | joint κ=3 q=1.5    |       0.75  |                0 |         1718 |     3.258 |       0     |
|   6 | nominal     | isotonic_dw   |     4   | 1.5  | joint κ=4 q=1.5    |       0.32  |                0 |         1718 |     3.396 |       0     |
|   6 | nominal     | isotonic_dw   |     5   | 1.5  | joint κ=5 q=1.5    |       0.208 |                0 |         1718 |     3.453 |       0     |
|   6 | nominal     | isotonic_dw   |     6   | 1.5  | joint κ=6 q=1.5    |       0.15  |                0 |         1718 |     3.469 |       0     |
|   6 | nominal     | isotonic_dw   |     7   | 1.5  | joint κ=7 q=1.5    |       0.05  |                0 |         1718 |     3.529 |       0     |
|   6 | nominal     | isotonic_dw   |     0.5 | 0    | joint κ=0.5 q=0    |       4.67  |                0 |         1718 |     3.036 |       0.41  |
|   6 | nominal     | isotonic_dw   |     0.5 | 0.75 | joint κ=0.5 q=0.75 |       2.684 |                0 |         1718 |     3     |       0.026 |
|   6 | nominal     | isotonic_dw   |     0.5 | 3    | joint κ=0.5 q=3    |       1.1   |                0 |         1718 |     3.169 |       0     |
|   6 | nominal     | isotonic_dw   |     0.5 | 6    | joint κ=0.5 q=6    |       1.002 |                0 |         1718 |     3.202 |       0     |
|   6 | nominal     | isotonic_dw   |     0.5 | 0    | indep κ=0.5        |       5.254 |                0 |         1718 |     2.79  |       0.512 |
|   6 | nominal     | isotonic_dw   |     1   | 0    | indep κ=1          |       5.176 |                0 |         1718 |     2.794 |       0.456 |
|   6 | nominal     | isotonic_dw   |     2   | 0    | indep κ=2          |       4.238 |                0 |         1718 |     3.019 |       0.178 |
|   6 | nominal     | isotonic_dw   |     3   | 0    | indep κ=3          |       2.522 |                0 |         1718 |     3.607 |       0.01  |
|   6 | nominal     | isotonic_dw   |     4   | 0    | indep κ=4          |       1.602 |                0 |         1718 |     4.176 |       0.002 |
|   6 | nominal     | isotonic_dw   |     5   | 0    | indep κ=5          |       1.416 |                0 |         1718 |     4.267 |       0     |
|   6 | nominal     | isotonic_dw   |     6   | 0    | indep κ=6          |       1.296 |                0 |         1718 |     4.316 |       0     |
|   6 | nominal     | isotonic_dw   |     7   | 0    | indep κ=7          |       0.92  |                0 |         1718 |     4.691 |       0     |
|   8 | noisy       | isotonic      |     0.5 | 1.5  | joint κ=0.5 q=1.5  |       3.144 |                0 |         2274 |     3.859 |       0.07  |
|   8 | noisy       | isotonic      |     1   | 1.5  | joint κ=1 q=1.5    |       2.91  |                0 |         2274 |     3.878 |       0.014 |
|   8 | noisy       | isotonic      |     2   | 1.5  | joint κ=2 q=1.5    |       2.426 |                0 |         2274 |     3.935 |       0     |
|   8 | noisy       | isotonic      |     3   | 1.5  | joint κ=3 q=1.5    |       1.914 |                0 |         2274 |     4.031 |       0     |
|   8 | noisy       | isotonic      |     4   | 1.5  | joint κ=4 q=1.5    |       1.436 |                0 |         2274 |     4.138 |       0     |
|   8 | noisy       | isotonic      |     5   | 1.5  | joint κ=5 q=1.5    |       0.952 |                0 |         2274 |     4.254 |       0     |
|   8 | noisy       | isotonic      |     6   | 1.5  | joint κ=6 q=1.5    |       0.548 |                0 |         2274 |     4.394 |       0     |
|   8 | noisy       | isotonic      |     7   | 1.5  | joint κ=7 q=1.5    |       0.01  |                0 |         2274 |     4.686 |       0     |
|   8 | noisy       | isotonic      |     0.5 | 0    | joint κ=0.5 q=0    |       7.502 |                0 |         2274 |     3.566 |       1.38  |
|   8 | noisy       | isotonic      |     0.5 | 0.75 | joint κ=0.5 q=0.75 |       4.742 |                0 |         2274 |     3.782 |       0.65  |
|   8 | noisy       | isotonic      |     0.5 | 3    | joint κ=0.5 q=3    |       1.996 |                0 |         2274 |     4.015 |       0     |
|   8 | noisy       | isotonic      |     0.5 | 6    | joint κ=0.5 q=6    |       1.042 |                0 |         2274 |     4.225 |       0     |
|   8 | noisy       | isotonic      |     0.5 | 0    | indep κ=0.5        |       7.992 |                0 |         2274 |     3.528 |       1.432 |
|   8 | noisy       | isotonic      |     1   | 0    | indep κ=1          |       7.928 |                0 |         2274 |     3.531 |       1.432 |
|   8 | noisy       | isotonic      |     2   | 0    | indep κ=2          |       7.512 |                0 |         2274 |     3.565 |       1.434 |
|   8 | noisy       | isotonic      |     3   | 0    | indep κ=3          |       6.952 |                0 |         2274 |     3.707 |       1.462 |
|   8 | noisy       | isotonic      |     4   | 0    | indep κ=4          |       5.23  |                0 |         2274 |     3.953 |       0.736 |
|   8 | noisy       | isotonic      |     5   | 0    | indep κ=5          |       3.818 |                0 |         2274 |     4.294 |       0.176 |
|   8 | noisy       | isotonic      |     6   | 0    | indep κ=6          |       3.286 |                0 |         2274 |     5.183 |       0.096 |
|   8 | noisy       | isotonic      |     7   | 0    | indep κ=7          |       1.074 |                0 |         2274 |     6.397 |       0     |
|   8 | noisy       | isotonic_dw   |     0.5 | 1.5  | joint κ=0.5 q=1.5  |       2.734 |                0 |         2274 |     3.894 |       0.002 |
|   8 | noisy       | isotonic_dw   |     1   | 1.5  | joint κ=1 q=1.5    |       2.52  |                0 |         2274 |     3.934 |       0     |
|   8 | noisy       | isotonic_dw   |     2   | 1.5  | joint κ=2 q=1.5    |       2.006 |                0 |         2274 |     4.024 |       0     |
|   8 | noisy       | isotonic_dw   |     3   | 1.5  | joint κ=3 q=1.5    |       1.542 |                0 |         2274 |     4.122 |       0     |
|   8 | noisy       | isotonic_dw   |     4   | 1.5  | joint κ=4 q=1.5    |       1.056 |                0 |         2274 |     4.218 |       0     |
|   8 | noisy       | isotonic_dw   |     5   | 1.5  | joint κ=5 q=1.5    |       0.676 |                0 |         2274 |     4.343 |       0     |
|   8 | noisy       | isotonic_dw   |     6   | 1.5  | joint κ=6 q=1.5    |       0.108 |                0 |         2274 |     4.621 |       0     |
|   8 | noisy       | isotonic_dw   |     7   | 1.5  | joint κ=7 q=1.5    |       0.01  |                0 |         2274 |     4.686 |       0     |
|   8 | noisy       | isotonic_dw   |     0.5 | 0    | joint κ=0.5 q=0    |       7.43  |                0 |         2274 |     3.568 |       1.37  |
|   8 | noisy       | isotonic_dw   |     0.5 | 0.75 | joint κ=0.5 q=0.75 |       4.042 |                0 |         2274 |     3.784 |       0.444 |
|   8 | noisy       | isotonic_dw   |     0.5 | 3    | joint κ=0.5 q=3    |       1.906 |                0 |         2274 |     4.039 |       0     |
|   8 | noisy       | isotonic_dw   |     0.5 | 6    | joint κ=0.5 q=6    |       1     |                0 |         2274 |     4.239 |       0     |
|   8 | noisy       | isotonic_dw   |     0.5 | 0    | indep κ=0.5        |       7.936 |                0 |         2274 |     3.512 |       1.426 |
|   8 | noisy       | isotonic_dw   |     1   | 0    | indep κ=1          |       7.768 |                0 |         2274 |     3.531 |       1.444 |
|   8 | noisy       | isotonic_dw   |     2   | 0    | indep κ=2          |       7.25  |                0 |         2274 |     3.627 |       1.468 |
|   8 | noisy       | isotonic_dw   |     3   | 0    | indep κ=3          |       5.556 |                0 |         2274 |     3.87  |       0.844 |
|   8 | noisy       | isotonic_dw   |     4   | 0    | indep κ=4          |       4.122 |                0 |         2274 |     4.195 |       0.262 |
|   8 | noisy       | isotonic_dw   |     5   | 0    | indep κ=5          |       3.248 |                0 |         2274 |     4.939 |       0.118 |
|   8 | noisy       | isotonic_dw   |     6   | 0    | indep κ=6          |       2.664 |                0 |         2274 |     7.008 |       0     |
|   8 | noisy       | isotonic_dw   |     7   | 0    | indep κ=7          |       0.884 |                0 |         2274 |     6.258 |       0     |
|   8 | nominal     | isotonic      |     0.5 | 1.5  | joint κ=0.5 q=1.5  |       2.412 |                0 |         2299 |     3.083 |       0     |
|   8 | nominal     | isotonic      |     1   | 1.5  | joint κ=1 q=1.5    |       2.118 |                0 |         2299 |     3.111 |       0     |
|   8 | nominal     | isotonic      |     2   | 1.5  | joint κ=2 q=1.5    |       1.708 |                0 |         2299 |     3.158 |       0     |
|   8 | nominal     | isotonic      |     3   | 1.5  | joint κ=3 q=1.5    |       1.176 |                0 |         2299 |     3.221 |       0     |
|   8 | nominal     | isotonic      |     4   | 1.5  | joint κ=4 q=1.5    |       0.81  |                0 |         2299 |     3.323 |       0     |
|   8 | nominal     | isotonic      |     5   | 1.5  | joint κ=5 q=1.5    |       0.392 |                0 |         2299 |     3.414 |       0     |
|   8 | nominal     | isotonic      |     6   | 1.5  | joint κ=6 q=1.5    |       0.152 |                0 |         2299 |     3.532 |       0     |
|   8 | nominal     | isotonic      |     7   | 1.5  | joint κ=7 q=1.5    |       0.074 |                0 |         2299 |     3.556 |       0     |
|   8 | nominal     | isotonic      |     0.5 | 0    | joint κ=0.5 q=0    |       5.98  |                0 |         2299 |     3.011 |       0.648 |
|   8 | nominal     | isotonic      |     0.5 | 0.75 | joint κ=0.5 q=0.75 |       3.58  |                0 |         2299 |     3.034 |       0.184 |
|   8 | nominal     | isotonic      |     0.5 | 3    | joint κ=0.5 q=3    |       1.704 |                0 |         2299 |     3.158 |       0     |
|   8 | nominal     | isotonic      |     0.5 | 6    | joint κ=0.5 q=6    |       1.004 |                0 |         2299 |     3.269 |       0     |
|   8 | nominal     | isotonic      |     0.5 | 0    | indep κ=0.5        |       6.736 |                0 |         2299 |     2.793 |       0.864 |
|   8 | nominal     | isotonic      |     1   | 0    | indep κ=1          |       6.604 |                0 |         2299 |     2.812 |       0.8   |
|   8 | nominal     | isotonic      |     2   | 0    | indep κ=2          |       6.406 |                0 |         2299 |     2.868 |       0.856 |
|   8 | nominal     | isotonic      |     3   | 0    | indep κ=3          |       4.554 |                0 |         2299 |     3.137 |       0.236 |
|   8 | nominal     | isotonic      |     4   | 0    | indep κ=4          |       2.658 |                0 |         2299 |     3.772 |       0.052 |
|   8 | nominal     | isotonic      |     5   | 0    | indep κ=5          |       1.694 |                0 |         2299 |     4.188 |       0.008 |
|   8 | nominal     | isotonic      |     6   | 0    | indep κ=6          |       1.434 |                0 |         2299 |     4.309 |       0     |
|   8 | nominal     | isotonic      |     7   | 0    | indep κ=7          |       1.31  |                0 |         2299 |     4.403 |       0     |
|   8 | nominal     | isotonic_dw   |     0.5 | 1.5  | joint κ=0.5 q=1.5  |       2.006 |                0 |         2299 |     3.189 |       0     |
|   8 | nominal     | isotonic_dw   |     1   | 1.5  | joint κ=1 q=1.5    |       1.86  |                0 |         2299 |     3.2   |       0     |
|   8 | nominal     | isotonic_dw   |     2   | 1.5  | joint κ=2 q=1.5    |       1.19  |                0 |         2299 |     3.279 |       0     |
|   8 | nominal     | isotonic_dw   |     3   | 1.5  | joint κ=3 q=1.5    |       0.912 |                0 |         2299 |     3.353 |       0     |
|   8 | nominal     | isotonic_dw   |     4   | 1.5  | joint κ=4 q=1.5    |       0.426 |                0 |         2299 |     3.483 |       0     |
|   8 | nominal     | isotonic_dw   |     5   | 1.5  | joint κ=5 q=1.5    |       0.248 |                0 |         2299 |     3.547 |       0     |
|   8 | nominal     | isotonic_dw   |     6   | 1.5  | joint κ=6 q=1.5    |       0.16  |                0 |         2299 |     3.568 |       0     |
|   8 | nominal     | isotonic_dw   |     7   | 1.5  | joint κ=7 q=1.5    |       0.052 |                0 |         2299 |     3.614 |       0     |
|   8 | nominal     | isotonic_dw   |     0.5 | 0    | joint κ=0.5 q=0    |       6.276 |                0 |         2299 |     3.144 |       0.812 |
|   8 | nominal     | isotonic_dw   |     0.5 | 0.75 | joint κ=0.5 q=0.75 |       3.046 |                0 |         2299 |     3.129 |       0.08  |
|   8 | nominal     | isotonic_dw   |     0.5 | 3    | joint κ=0.5 q=3    |       1.192 |                0 |         2299 |     3.279 |       0     |
|   8 | nominal     | isotonic_dw   |     0.5 | 6    | joint κ=0.5 q=6    |       1.012 |                0 |         2299 |     3.329 |       0     |
|   8 | nominal     | isotonic_dw   |     0.5 | 0    | indep κ=0.5        |       7.012 |                0 |         2299 |     2.899 |       1.03  |
|   8 | nominal     | isotonic_dw   |     1   | 0    | indep κ=1          |       6.9   |                0 |         2299 |     2.896 |       0.948 |
|   8 | nominal     | isotonic_dw   |     2   | 0    | indep κ=2          |       5.69  |                0 |         2299 |     3.143 |       0.594 |
|   8 | nominal     | isotonic_dw   |     3   | 0    | indep κ=3          |       3.378 |                0 |         2299 |     3.751 |       0.068 |
|   8 | nominal     | isotonic_dw   |     4   | 0    | indep κ=4          |       2.168 |                0 |         2299 |     4.276 |       0.004 |
|   8 | nominal     | isotonic_dw   |     5   | 0    | indep κ=5          |       1.966 |                0 |         2299 |     4.363 |       0     |
|   8 | nominal     | isotonic_dw   |     6   | 0    | indep κ=6          |       1.808 |                0 |         2299 |     4.407 |       0     |
|   8 | nominal     | isotonic_dw   |     7   | 0    | indep κ=7          |       1.276 |                0 |         2299 |     4.78  |       0     |

## Matched question rate

Each joint point against the per-robot rule with the nearest question rate (McNemar exact on crossing robots, development seeds, exploratory).

|   N | condition   | calibration   | joint              |   joint_questions | matched_rule   |   rule_questions |   joint_collisions_pct |   rule_collisions_pct |   only_joint_collided |   only_rule_collided |   p |   joint_delay |   rule_delay |
|----:|:------------|:--------------|:-------------------|------------------:|:---------------|-----------------:|-----------------------:|----------------------:|----------------------:|---------------------:|----:|--------------:|-------------:|
|   6 | noisy       | isotonic      | joint κ=0.5 q=1.5  |             2.908 | indep κ=5      |            2.876 |                      0 |                     0 |                     0 |                    0 |   1 |         3.691 |        4.157 |
|   6 | noisy       | isotonic      | joint κ=1 q=1.5    |             2.618 | indep κ=6      |            2.472 |                      0 |                     0 |                     0 |                    0 |   1 |         3.692 |        5.105 |
|   6 | noisy       | isotonic      | joint κ=2 q=1.5    |             2.186 | indep κ=6      |            2.472 |                      0 |                     0 |                     0 |                    0 |   1 |         3.763 |        5.105 |
|   6 | noisy       | isotonic      | joint κ=3 q=1.5    |             1.75  | indep κ=6      |            2.472 |                      0 |                     0 |                     0 |                    0 |   1 |         3.846 |        5.105 |
|   6 | noisy       | isotonic      | joint κ=4 q=1.5    |             1.29  | indep κ=7      |            0.842 |                      0 |                     0 |                     0 |                    0 |   1 |         3.995 |        6.332 |
|   6 | noisy       | isotonic      | joint κ=5 q=1.5    |             0.89  | indep κ=7      |            0.842 |                      0 |                     0 |                     0 |                    0 |   1 |         4.156 |        6.332 |
|   6 | noisy       | isotonic      | joint κ=6 q=1.5    |             0.442 | indep κ=7      |            0.842 |                      0 |                     0 |                     0 |                    0 |   1 |         4.394 |        6.332 |
|   6 | noisy       | isotonic      | joint κ=7 q=1.5    |             0.008 | indep κ=7      |            0.842 |                      0 |                     0 |                     0 |                    0 |   1 |         4.684 |        6.332 |
|   6 | noisy       | isotonic      | joint κ=0.5 q=0    |             5.578 | indep κ=2      |            5.654 |                      0 |                     0 |                     0 |                    0 |   1 |         3.458 |        3.42  |
|   6 | noisy       | isotonic      | joint κ=0.5 q=0.75 |             4.19  | indep κ=4      |            3.916 |                      0 |                     0 |                     0 |                    0 |   1 |         3.618 |        3.722 |
|   6 | noisy       | isotonic      | joint κ=0.5 q=3    |             1.99  | indep κ=6      |            2.472 |                      0 |                     0 |                     0 |                    0 |   1 |         3.821 |        5.105 |
|   6 | noisy       | isotonic      | joint κ=0.5 q=6    |             1.012 | indep κ=7      |            0.842 |                      0 |                     0 |                     0 |                    0 |   1 |         4.115 |        6.332 |
|   6 | noisy       | isotonic_dw   | joint κ=0.5 q=1.5  |             2.46  | indep κ=5      |            2.462 |                      0 |                     0 |                     0 |                    0 |   1 |         3.697 |        4.823 |
|   6 | noisy       | isotonic_dw   | joint κ=1 q=1.5    |             2.268 | indep κ=5      |            2.462 |                      0 |                     0 |                     0 |                    0 |   1 |         3.749 |        4.823 |
|   6 | noisy       | isotonic_dw   | joint κ=2 q=1.5    |             1.8   | indep κ=6      |            1.938 |                      0 |                     0 |                     0 |                    0 |   1 |         3.849 |        6.949 |
|   6 | noisy       | isotonic_dw   | joint κ=3 q=1.5    |             1.376 | indep κ=6      |            1.938 |                      0 |                     0 |                     0 |                    0 |   1 |         3.972 |        6.949 |
|   6 | noisy       | isotonic_dw   | joint κ=4 q=1.5    |             0.96  | indep κ=7      |            0.712 |                      0 |                     0 |                     0 |                    0 |   1 |         4.127 |        6.183 |
|   6 | noisy       | isotonic_dw   | joint κ=5 q=1.5    |             0.552 | indep κ=7      |            0.712 |                      0 |                     0 |                     0 |                    0 |   1 |         4.327 |        6.183 |
|   6 | noisy       | isotonic_dw   | joint κ=6 q=1.5    |             0.08  | indep κ=7      |            0.712 |                      0 |                     0 |                     0 |                    0 |   1 |         4.624 |        6.183 |
|   6 | noisy       | isotonic_dw   | joint κ=7 q=1.5    |             0.008 | indep κ=7      |            0.712 |                      0 |                     0 |                     0 |                    0 |   1 |         4.684 |        6.183 |
|   6 | noisy       | isotonic_dw   | joint κ=0.5 q=0    |             5.488 | indep κ=2      |            5.458 |                      0 |                     0 |                     0 |                    0 |   1 |         3.461 |        3.481 |
|   6 | noisy       | isotonic_dw   | joint κ=0.5 q=0.75 |             3.562 | indep κ=4      |            3.072 |                      0 |                     0 |                     0 |                    0 |   1 |         3.633 |        4.028 |
|   6 | noisy       | isotonic_dw   | joint κ=0.5 q=3    |             1.778 | indep κ=6      |            1.938 |                      0 |                     0 |                     0 |                    0 |   1 |         3.856 |        6.949 |
|   6 | noisy       | isotonic_dw   | joint κ=0.5 q=6    |             1     | indep κ=7      |            0.712 |                      0 |                     0 |                     0 |                    0 |   1 |         4.117 |        6.183 |
|   6 | nominal     | isotonic      | joint κ=0.5 q=1.5  |             2.204 | indep κ=4      |            1.94  |                      0 |                     0 |                     0 |                    0 |   1 |         2.946 |        3.64  |
|   6 | nominal     | isotonic      | joint κ=1 q=1.5    |             2.008 | indep κ=4      |            1.94  |                      0 |                     0 |                     0 |                    0 |   1 |         2.968 |        3.64  |
|   6 | nominal     | isotonic      | joint κ=2 q=1.5    |             1.528 | indep κ=5      |            1.238 |                      0 |                     0 |                     0 |                    0 |   1 |         3.015 |        4.095 |
|   6 | nominal     | isotonic      | joint κ=3 q=1.5    |             1.058 | indep κ=6      |            1.038 |                      0 |                     0 |                     0 |                    0 |   1 |         3.089 |        4.22  |
|   6 | nominal     | isotonic      | joint κ=4 q=1.5    |             0.648 | indep κ=7      |            0.934 |                      0 |                     0 |                     0 |                    0 |   1 |         3.224 |        4.33  |
|   6 | nominal     | isotonic      | joint κ=5 q=1.5    |             0.268 | indep κ=7      |            0.934 |                      0 |                     0 |                     0 |                    0 |   1 |         3.337 |        4.33  |
|   6 | nominal     | isotonic      | joint κ=6 q=1.5    |             0.096 | indep κ=7      |            0.934 |                      0 |                     0 |                     0 |                    0 |   1 |         3.44  |        4.33  |
|   6 | nominal     | isotonic      | joint κ=7 q=1.5    |             0.048 | indep κ=7      |            0.934 |                      0 |                     0 |                     0 |                    0 |   1 |         3.469 |        4.33  |
|   6 | nominal     | isotonic      | joint κ=0.5 q=0    |             4.45  | indep κ=2      |            4.716 |                      0 |                     0 |                     0 |                    0 |   1 |         2.91  |        2.764 |
|   6 | nominal     | isotonic      | joint κ=0.5 q=0.75 |             3.188 | indep κ=3      |            3.32  |                      0 |                     0 |                     0 |                    0 |   1 |         2.903 |        3.01  |
|   6 | nominal     | isotonic      | joint κ=0.5 q=3    |             1.526 | indep κ=5      |            1.238 |                      0 |                     0 |                     0 |                    0 |   1 |         3.016 |        4.095 |
|   6 | nominal     | isotonic      | joint κ=0.5 q=6    |             1.004 | indep κ=6      |            1.038 |                      0 |                     0 |                     0 |                    0 |   1 |         3.128 |        4.22  |
|   6 | nominal     | isotonic_dw   | joint κ=0.5 q=1.5  |             1.884 | indep κ=4      |            1.602 |                      0 |                     0 |                     0 |                    0 |   1 |         3.036 |        4.176 |
|   6 | nominal     | isotonic_dw   | joint κ=1 q=1.5    |             1.672 | indep κ=4      |            1.602 |                      0 |                     0 |                     0 |                    0 |   1 |         3.062 |        4.176 |
|   6 | nominal     | isotonic_dw   | joint κ=2 q=1.5    |             1.082 | indep κ=7      |            0.92  |                      0 |                     0 |                     0 |                    0 |   1 |         3.17  |        4.691 |
|   6 | nominal     | isotonic_dw   | joint κ=3 q=1.5    |             0.75  | indep κ=7      |            0.92  |                      0 |                     0 |                     0 |                    0 |   1 |         3.258 |        4.691 |
|   6 | nominal     | isotonic_dw   | joint κ=4 q=1.5    |             0.32  | indep κ=7      |            0.92  |                      0 |                     0 |                     0 |                    0 |   1 |         3.396 |        4.691 |
|   6 | nominal     | isotonic_dw   | joint κ=5 q=1.5    |             0.208 | indep κ=7      |            0.92  |                      0 |                     0 |                     0 |                    0 |   1 |         3.453 |        4.691 |
|   6 | nominal     | isotonic_dw   | joint κ=6 q=1.5    |             0.15  | indep κ=7      |            0.92  |                      0 |                     0 |                     0 |                    0 |   1 |         3.469 |        4.691 |
|   6 | nominal     | isotonic_dw   | joint κ=7 q=1.5    |             0.05  | indep κ=7      |            0.92  |                      0 |                     0 |                     0 |                    0 |   1 |         3.529 |        4.691 |
|   6 | nominal     | isotonic_dw   | joint κ=0.5 q=0    |             4.67  | indep κ=2      |            4.238 |                      0 |                     0 |                     0 |                    0 |   1 |         3.036 |        3.019 |
|   6 | nominal     | isotonic_dw   | joint κ=0.5 q=0.75 |             2.684 | indep κ=3      |            2.522 |                      0 |                     0 |                     0 |                    0 |   1 |         3     |        3.607 |
|   6 | nominal     | isotonic_dw   | joint κ=0.5 q=3    |             1.1   | indep κ=7      |            0.92  |                      0 |                     0 |                     0 |                    0 |   1 |         3.169 |        4.691 |
|   6 | nominal     | isotonic_dw   | joint κ=0.5 q=6    |             1.002 | indep κ=7      |            0.92  |                      0 |                     0 |                     0 |                    0 |   1 |         3.202 |        4.691 |
|   8 | noisy       | isotonic      | joint κ=0.5 q=1.5  |             3.144 | indep κ=6      |            3.286 |                      0 |                     0 |                     0 |                    0 |   1 |         3.859 |        5.183 |
|   8 | noisy       | isotonic      | joint κ=1 q=1.5    |             2.91  | indep κ=6      |            3.286 |                      0 |                     0 |                     0 |                    0 |   1 |         3.878 |        5.183 |
|   8 | noisy       | isotonic      | joint κ=2 q=1.5    |             2.426 | indep κ=6      |            3.286 |                      0 |                     0 |                     0 |                    0 |   1 |         3.935 |        5.183 |
|   8 | noisy       | isotonic      | joint κ=3 q=1.5    |             1.914 | indep κ=7      |            1.074 |                      0 |                     0 |                     0 |                    0 |   1 |         4.031 |        6.397 |
|   8 | noisy       | isotonic      | joint κ=4 q=1.5    |             1.436 | indep κ=7      |            1.074 |                      0 |                     0 |                     0 |                    0 |   1 |         4.138 |        6.397 |
|   8 | noisy       | isotonic      | joint κ=5 q=1.5    |             0.952 | indep κ=7      |            1.074 |                      0 |                     0 |                     0 |                    0 |   1 |         4.254 |        6.397 |
|   8 | noisy       | isotonic      | joint κ=6 q=1.5    |             0.548 | indep κ=7      |            1.074 |                      0 |                     0 |                     0 |                    0 |   1 |         4.394 |        6.397 |
|   8 | noisy       | isotonic      | joint κ=7 q=1.5    |             0.01  | indep κ=7      |            1.074 |                      0 |                     0 |                     0 |                    0 |   1 |         4.686 |        6.397 |
|   8 | noisy       | isotonic      | joint κ=0.5 q=0    |             7.502 | indep κ=2      |            7.512 |                      0 |                     0 |                     0 |                    0 |   1 |         3.566 |        3.565 |
|   8 | noisy       | isotonic      | joint κ=0.5 q=0.75 |             4.742 | indep κ=4      |            5.23  |                      0 |                     0 |                     0 |                    0 |   1 |         3.782 |        3.953 |
|   8 | noisy       | isotonic      | joint κ=0.5 q=3    |             1.996 | indep κ=7      |            1.074 |                      0 |                     0 |                     0 |                    0 |   1 |         4.015 |        6.397 |
|   8 | noisy       | isotonic      | joint κ=0.5 q=6    |             1.042 | indep κ=7      |            1.074 |                      0 |                     0 |                     0 |                    0 |   1 |         4.225 |        6.397 |
|   8 | noisy       | isotonic_dw   | joint κ=0.5 q=1.5  |             2.734 | indep κ=6      |            2.664 |                      0 |                     0 |                     0 |                    0 |   1 |         3.894 |        7.008 |
|   8 | noisy       | isotonic_dw   | joint κ=1 q=1.5    |             2.52  | indep κ=6      |            2.664 |                      0 |                     0 |                     0 |                    0 |   1 |         3.934 |        7.008 |
|   8 | noisy       | isotonic_dw   | joint κ=2 q=1.5    |             2.006 | indep κ=6      |            2.664 |                      0 |                     0 |                     0 |                    0 |   1 |         4.024 |        7.008 |
|   8 | noisy       | isotonic_dw   | joint κ=3 q=1.5    |             1.542 | indep κ=7      |            0.884 |                      0 |                     0 |                     0 |                    0 |   1 |         4.122 |        6.258 |
|   8 | noisy       | isotonic_dw   | joint κ=4 q=1.5    |             1.056 | indep κ=7      |            0.884 |                      0 |                     0 |                     0 |                    0 |   1 |         4.218 |        6.258 |
|   8 | noisy       | isotonic_dw   | joint κ=5 q=1.5    |             0.676 | indep κ=7      |            0.884 |                      0 |                     0 |                     0 |                    0 |   1 |         4.343 |        6.258 |
|   8 | noisy       | isotonic_dw   | joint κ=6 q=1.5    |             0.108 | indep κ=7      |            0.884 |                      0 |                     0 |                     0 |                    0 |   1 |         4.621 |        6.258 |
|   8 | noisy       | isotonic_dw   | joint κ=7 q=1.5    |             0.01  | indep κ=7      |            0.884 |                      0 |                     0 |                     0 |                    0 |   1 |         4.686 |        6.258 |
|   8 | noisy       | isotonic_dw   | joint κ=0.5 q=0    |             7.43  | indep κ=2      |            7.25  |                      0 |                     0 |                     0 |                    0 |   1 |         3.568 |        3.627 |
|   8 | noisy       | isotonic_dw   | joint κ=0.5 q=0.75 |             4.042 | indep κ=4      |            4.122 |                      0 |                     0 |                     0 |                    0 |   1 |         3.784 |        4.195 |
|   8 | noisy       | isotonic_dw   | joint κ=0.5 q=3    |             1.906 | indep κ=6      |            2.664 |                      0 |                     0 |                     0 |                    0 |   1 |         4.039 |        7.008 |
|   8 | noisy       | isotonic_dw   | joint κ=0.5 q=6    |             1     | indep κ=7      |            0.884 |                      0 |                     0 |                     0 |                    0 |   1 |         4.239 |        6.258 |
|   8 | nominal     | isotonic      | joint κ=0.5 q=1.5  |             2.412 | indep κ=4      |            2.658 |                      0 |                     0 |                     0 |                    0 |   1 |         3.083 |        3.772 |
|   8 | nominal     | isotonic      | joint κ=1 q=1.5    |             2.118 | indep κ=5      |            1.694 |                      0 |                     0 |                     0 |                    0 |   1 |         3.111 |        4.188 |
|   8 | nominal     | isotonic      | joint κ=2 q=1.5    |             1.708 | indep κ=5      |            1.694 |                      0 |                     0 |                     0 |                    0 |   1 |         3.158 |        4.188 |
|   8 | nominal     | isotonic      | joint κ=3 q=1.5    |             1.176 | indep κ=7      |            1.31  |                      0 |                     0 |                     0 |                    0 |   1 |         3.221 |        4.403 |
|   8 | nominal     | isotonic      | joint κ=4 q=1.5    |             0.81  | indep κ=7      |            1.31  |                      0 |                     0 |                     0 |                    0 |   1 |         3.323 |        4.403 |
|   8 | nominal     | isotonic      | joint κ=5 q=1.5    |             0.392 | indep κ=7      |            1.31  |                      0 |                     0 |                     0 |                    0 |   1 |         3.414 |        4.403 |
|   8 | nominal     | isotonic      | joint κ=6 q=1.5    |             0.152 | indep κ=7      |            1.31  |                      0 |                     0 |                     0 |                    0 |   1 |         3.532 |        4.403 |
|   8 | nominal     | isotonic      | joint κ=7 q=1.5    |             0.074 | indep κ=7      |            1.31  |                      0 |                     0 |                     0 |                    0 |   1 |         3.556 |        4.403 |
|   8 | nominal     | isotonic      | joint κ=0.5 q=0    |             5.98  | indep κ=2      |            6.406 |                      0 |                     0 |                     0 |                    0 |   1 |         3.011 |        2.868 |
|   8 | nominal     | isotonic      | joint κ=0.5 q=0.75 |             3.58  | indep κ=4      |            2.658 |                      0 |                     0 |                     0 |                    0 |   1 |         3.034 |        3.772 |
|   8 | nominal     | isotonic      | joint κ=0.5 q=3    |             1.704 | indep κ=5      |            1.694 |                      0 |                     0 |                     0 |                    0 |   1 |         3.158 |        4.188 |
|   8 | nominal     | isotonic      | joint κ=0.5 q=6    |             1.004 | indep κ=7      |            1.31  |                      0 |                     0 |                     0 |                    0 |   1 |         3.269 |        4.403 |
|   8 | nominal     | isotonic_dw   | joint κ=0.5 q=1.5  |             2.006 | indep κ=5      |            1.966 |                      0 |                     0 |                     0 |                    0 |   1 |         3.189 |        4.363 |
|   8 | nominal     | isotonic_dw   | joint κ=1 q=1.5    |             1.86  | indep κ=6      |            1.808 |                      0 |                     0 |                     0 |                    0 |   1 |         3.2   |        4.407 |
|   8 | nominal     | isotonic_dw   | joint κ=2 q=1.5    |             1.19  | indep κ=7      |            1.276 |                      0 |                     0 |                     0 |                    0 |   1 |         3.279 |        4.78  |
|   8 | nominal     | isotonic_dw   | joint κ=3 q=1.5    |             0.912 | indep κ=7      |            1.276 |                      0 |                     0 |                     0 |                    0 |   1 |         3.353 |        4.78  |
|   8 | nominal     | isotonic_dw   | joint κ=4 q=1.5    |             0.426 | indep κ=7      |            1.276 |                      0 |                     0 |                     0 |                    0 |   1 |         3.483 |        4.78  |
|   8 | nominal     | isotonic_dw   | joint κ=5 q=1.5    |             0.248 | indep κ=7      |            1.276 |                      0 |                     0 |                     0 |                    0 |   1 |         3.547 |        4.78  |
|   8 | nominal     | isotonic_dw   | joint κ=6 q=1.5    |             0.16  | indep κ=7      |            1.276 |                      0 |                     0 |                     0 |                    0 |   1 |         3.568 |        4.78  |
|   8 | nominal     | isotonic_dw   | joint κ=7 q=1.5    |             0.052 | indep κ=7      |            1.276 |                      0 |                     0 |                     0 |                    0 |   1 |         3.614 |        4.78  |
|   8 | nominal     | isotonic_dw   | joint κ=0.5 q=0    |             6.276 | indep κ=2      |            5.69  |                      0 |                     0 |                     0 |                    0 |   1 |         3.144 |        3.143 |
|   8 | nominal     | isotonic_dw   | joint κ=0.5 q=0.75 |             3.046 | indep κ=3      |            3.378 |                      0 |                     0 |                     0 |                    0 |   1 |         3.129 |        3.751 |
|   8 | nominal     | isotonic_dw   | joint κ=0.5 q=3    |             1.192 | indep κ=7      |            1.276 |                      0 |                     0 |                     0 |                    0 |   1 |         3.279 |        4.78  |
|   8 | nominal     | isotonic_dw   | joint κ=0.5 q=6    |             1.012 | indep κ=7      |            1.276 |                      0 |                     0 |                     0 |                    0 |   1 |         3.329 |        4.78  |

## Joint against the per-robot frontier, interpolated at the same question rate

Delay saved = per-robot delay minus joint delay (s per robot); collision difference = joint minus per-robot (percentage points).

|                               |   points |   delay_saved_mean |   delay_saved_min |   delay_saved_max |   col_diff_mean_pp |   col_diff_max_pp |
|:------------------------------|---------:|-------------------:|------------------:|------------------:|-------------------:|------------------:|
| (6, 'noisy', 'isotonic')      |       10 |              1.281 |            -0.014 |             2.14  |                  0 |                 0 |
| (6, 'noisy', 'isotonic_dw')   |        9 |              1.813 |             0.012 |             3.014 |                  0 |                 0 |
| (6, 'nominal', 'isotonic')    |        8 |              0.664 |            -0.099 |             1.129 |                  0 |                 0 |
| (6, 'nominal', 'isotonic_dw') |        7 |              0.94  |            -0.121 |             1.407 |                  0 |                 0 |
| (8, 'noisy', 'isotonic')      |        8 |              1.345 |             0.002 |             2.06  |                  0 |                 0 |
| (8, 'noisy', 'isotonic_dw')   |        9 |              2.037 |             0.026 |             3.013 |                  0 |                 0 |
| (8, 'nominal', 'isotonic')    |        6 |              0.681 |            -0.082 |             1.026 |                  0 |                 0 |
| (8, 'nominal', 'isotonic_dw') |        4 |              0.749 |            -0.121 |             1.193 |                  0 |                 0 |
