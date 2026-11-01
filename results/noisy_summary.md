# QAOA under the ibm_kingston noise model

Real-probability instances (noisy tracking, decision-aware calibration, dev seeds), N = 4: 8 instances at 4000 shots; N = 6 none: 3 instances (1 at 4000, 2 at 2000 shots); N = 6 single corridor: 3 instances at 2000 shots, depths 1-2. Parameters trained noiselessly. Retained = noisy p_opt / noiseless p_opt; lift = noisy p_opt / uniform random.

|   N | layout   | encoding   |   depth |   qubits |   cz_gates |   random_p_opt |   p_feasible_kingston_noise |   p_feasible_noiseless |   p_opt_kingston_noise |   p_opt_noiseless |   p_opt_retained |   lift_noisy |
|----:|:---------|:-----------|--------:|---------:|-----------:|---------------:|----------------------------:|-----------------------:|-----------------------:|------------------:|-----------------:|-------------:|
|   4 | none     | slack      |       1 |       10 |         64 |         0.0049 |                      0.6799 |                 0.7089 |                 0.0132 |            0.013  |           1.0122 |       2.6944 |
|   4 | none     | slack      |       2 |       10 |        142 |         0.0049 |                      0.8214 |                 0.9017 |                 0.0168 |            0.0192 |           0.8795 |       3.4496 |
|   4 | none     | slack      |       3 |       10 |        224 |         0.0049 |                      0.8557 |                 0.9399 |                 0.0286 |            0.0331 |           0.8621 |       5.8496 |
|   4 | none     | unbalanced |       1 |        8 |         27 |         0.0049 |                      0.8457 |                 0.8936 |                 0.0306 |            0.0335 |           0.9151 |       6.272  |
|   4 | none     | unbalanced |       2 |        8 |         60 |         0.0049 |                      0.8861 |                 0.9462 |                 0.0515 |            0.0573 |           0.8977 |      10.5408 |
|   4 | none     | unbalanced |       3 |        8 |         99 |         0.0049 |                      0.8292 |                 0.8983 |                 0.0831 |            0.1002 |           0.8289 |      17.0112 |
|   6 | none     | slack      |       1 |       14 |        113 |         0.0005 |                      0.5147 |                 0.5838 |                 0.0017 |            0.002  |           0.8819 |       3.584  |
|   6 | none     | slack      |       2 |       14 |        278 |         0.0005 |                      0.6358 |                 0.7786 |                 0.0011 |            0.0026 |           0.415  |       2.2187 |
|   6 | none     | slack      |       3 |       14 |        486 |         0.0005 |                      0.6468 |                 0.8854 |                 0.0024 |            0.0035 |           0.6832 |       4.9493 |
|   6 | none     | unbalanced |       1 |       12 |         77 |         0.0005 |                      0.7008 |                 0.7981 |                 0.0035 |            0.0051 |           0.6876 |       7.168  |
|   6 | none     | unbalanced |       2 |       12 |        157 |         0.0005 |                      0.7006 |                 0.8198 |                 0.0048 |            0.0067 |           0.7225 |       9.8987 |
|   6 | none     | unbalanced |       3 |       12 |        263 |         0.0005 |                      0.5962 |                 0.7363 |                 0.0087 |            0.01   |           0.869  |      17.7493 |
|   6 | single   | slack      |       1 |       14 |        193 |         0.0002 |                      0.5627 |                 0.6414 |                 0.0005 |            0.001  |           0.4895 |       2.048  |
|   6 | single   | slack      |       2 |       14 |        509 |         0.0002 |                      0.618  |                 0.8195 |                 0.0015 |            0.0012 |           1.2529 |       6.144  |
|   6 | single   | unbalanced |       1 |       12 |        150 |         0.0002 |                      0.6875 |                 0.8307 |                 0.0027 |            0.0031 |           0.8631 |      10.9227 |
|   6 | single   | unbalanced |       2 |       12 |        359 |         0.0002 |                      0.724  |                 0.9043 |                 0.003  |            0.0034 |           0.8721 |      12.288  |
