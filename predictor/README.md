# Predictor used by every fleet result

`intent_model.pkl` is the Ask or Act MLP (32, 32) with its calibrators (raw, temperature,
isotonic, decision-aware isotonic), rebuilt with the Ask or Act repository's own scripts
(commit c0f46e3, `build_dataset.py` then `train_predictor.py`, default settings) under
scikit-learn 1.9.1. `metrics.csv` is the training script's output. The paper's original model
needs scikit-learn 0.23.2 and is not used here.

SHA-256 prefix of intent_model.pkl: 788ea654e61b31db.

Note: the Ask or Act policy caches predictions incorrectly (see fleet_qubo/fleet_sim.py,
FleetPolicy.predict); all fleet code uses the corrected policy.
