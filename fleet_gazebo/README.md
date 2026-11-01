# Fleet validation in Gazebo

Checks the offline closed-loop simulator (`fleet_qubo/fleet_sim.py`) against Gazebo with several
TurtleBot3s, as Ask or Act did for one robot (97.5% collision-outcome agreement over 320 runs).

## Design

- **World.** One `gzserver`, an empty world with the entity-state plugin. Robot *i* drives
  the Ask or Act line in its own lane, shifted 10 m in y; its scripted pedestrian is shifted
  the same way. Lanes never interact, as in the offline model. Every node works in the Ask or
  Act frame (`odom_offset_y` and `lane_offset_y` undo the shift).
- **Nodes.** Each robot has its own namespace (`/robot_<i>`) with a controller
  (`fleet_controller.py`) and a pedestrian (`fleet_pedestrians.py`). One
  `fleet_coordinator.py` acts as the shared operator (first come, first served, 1.5 s per
  question) and, in joint mode, closes decision epochs and runs the exact queue-aware solver.
- **Shared rules.** The operator and epoch rules live in `coordinator_core.py`, which the test
  suite checks against the offline simulator (`tests/test_fleet_gazebo_core.py`): the ROS-free
  pipeline reproduces offline collisions and question counts robot for robot.
- **Timing.** Robots wait for a common `/fleet/go`, then start on the same relative offsets as
  offline. Each observes from 2 s before its own start, as offline.

The Ask or Act nodes are not modified; these are adapted copies.

## Setup (on the Ask or Act machine: Ubuntu 22.04, ROS 2 Humble, Gazebo 11)

1. The Ask or Act repository at `~/ask_or_act`, with `predictor/intent_model.pkl`, and
   `~/burger_novis.sdf`, as for Ask or Act.
2. This repository at `~/fleet_qubo`, with `results/deadline_probs.csv`. Its pure-Python
   dependencies: `pip install numpy pandas scipy` (Qiskit is not needed here).
3. The model must be the one the deadline pool was built from. If you retrain, rebuild the pool
   with `scripts/extract_deadline_probs.py`.

## Run

```bash
cd ~/fleet_qubo/fleet_gazebo
source /opt/ros/humble/setup.bash          # and the HuNavSim workspace, as for Ask or Act

# 0. Check the machine first (every line should say PASS)
python3 check_setup.py

# 1. Smoke test: one epoch, 2 robots, watch it
python3 run_fleet_gazebo.py --N 2 --epochs 0 --conditions nominal --methods joint --gui --out runs_smoke

# 2. Development validation: N = 4, 20 epochs, nominal + noisy, both methods (80 epochs, 320 robot-runs)
python3 run_fleet_gazebo.py --N 4 --epochs 0-19
python3 compare_fleet_validation.py

# 3. Final validation, only after the freeze
python3 run_fleet_gazebo.py --final --N 4 --epochs 0-19 --out runs_final
python3 compare_fleet_validation.py --runs runs_final
```

Each epoch takes about 1-2 minutes, so the full validation is roughly 2-3 hours. The runs are
resumable.

## Agreement criteria (to be frozen with the analysis plan)

- Collision outcome agrees for at least 95% of robot-runs.
- Question count agrees for at least 90% of robot-runs.
- In joint mode, the assigned action agrees for at least 90% of robots.

## If the smoke test fails

- *"Robot i is x m from its start point"*: the robot model's odometry is not in world
  coordinates. Check the `odometry_source` of the diff-drive plugin in `burger_novis.sdf`;
  Ask or Act relied on world coordinates.
- *Robots never start*: the coordinator sends `/fleet/go` only when every controller reports
  ready. Check `runs*/e*/*/nodes.log` for a controller that crashed.
- *Robots do not move but no error*: check that `spawn_entity.py -robot_namespace` put the
  diff-drive topics under `/robot_<i>` (`ros2 topic list`).

This code was written and unit-tested without a ROS machine, so the smoke test is its first
real run. Send me the logs from any failure and I will fix it.
