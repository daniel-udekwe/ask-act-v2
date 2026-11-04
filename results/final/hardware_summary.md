# Hardware run (ibm_kingston, 4 Nov 2026; descriptive, prereg/HARDWARE.md)

40 circuits, 4,000 shots each; parameters trained noiselessly. Medians over 10 final instances.

|   N |   depth |   instances |   cz |   lift_sim |   lift_hw |   lift_hw_min |   feas_sim |   feas_hw |   hw_lift_ge10 |   opt_found |   feas_gap_hw |   random_feas |
|----:|--------:|------------:|-----:|-----------:|----------:|--------------:|-----------:|----------:|---------------:|------------:|--------------:|--------------:|
|   4 |       1 |          10 |   27 |       8.64 |      7.33 |          5.89 |      0.953 |     0.9   |              1 |          10 |         1.68  |         0.316 |
|   4 |       2 |          10 |   58 |      15.3  |     11.6  |          4.86 |      0.987 |     0.878 |              8 |          10 |         0.748 |         0.316 |
|   6 |       1 |          10 |   63 |      26.4  |     20    |         12.3  |      0.948 |     0.787 |             10 |          10 |         1.84  |         0.178 |
|   6 |       2 |          10 |  149 |      55.4  |     22.5  |          9.22 |      0.983 |     0.687 |              9 |          10 |         1.15  |         0.178 |
