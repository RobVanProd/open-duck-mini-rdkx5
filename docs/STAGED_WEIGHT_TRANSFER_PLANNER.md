# Staged Weight-Transfer Planner

Purpose: test whether a balance-first target generator can create low-command
forward motion without the lateral impulse seen in the closed-loop teacher
probes.

This is offline only. It does not train, deploy, SSH, or touch the robot.

## Planner Shape

`tools/probe_staged_weight_transfer_planner.py` uses a two-stage half-step:

1. Balance phase:
   - apply roll/lateral feedback
   - suppress forward reach and stance push
   - wait for lateral velocity, base-y, height, and pitch gates

2. Step phase:
   - enable swing knee/ankle lift
   - enable swing hip reach
   - enable stance retract and stance push
   - keep the same lateral and pitch feedback active

Each trace records:

```text
planner_step_enabled
planner_balance_phase
planner_lateral_ok
planner_base_y_ok
planner_height_ok
planner_pitch_ok
```

The traces are scored by `tools/score_target_candidates_objective.py` with the
same 100/150 tick target gates used for prior target-source probes.

## Current Result

Artifacts:

```text
outputs/analysis/STAGED_WEIGHT_TRANSFER_PLANNER_PROBE.md
outputs/analysis/STAGED_WEIGHT_TRANSFER_PLANNER_SCORE_100.md
outputs/analysis/STAGED_WEIGHT_TRANSFER_PLANNER_SCORE_150.md
```

Result:

```text
probe status: PASS_PLANNER_PROBE_RAN
100/150 status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0
```

Best 100-tick candidate:

```text
seed0 vx: 0.0015 m/s
seed2 vx: 0.0034 m/s
seed0 vy95: 0.1149 m/s
seed2 vy95: 0.1197 m/s
seed0 / seed2 double support: 89% / 85%
seed0 / seed2 single support: 11% / 15%
```

Interpretation: the staged planner can preserve lateral gates and generate
support transitions, but it does so by suppressing forward displacement. This
is the opposite failure from the more aggressive teacher probes. The useful
lesson is that balance gating alone is insufficient; the next generator needs
optimization over a short horizon or a richer body-state controller that can
trade lateral error, support state, and forward impulse jointly.

## Stop Rule

Do not keep expanding random grids over these same planner terms. A wider grid
would mostly retest the same tradeoff:

```text
aggressive targets: more vx, too much lateral impulse
staged gate targets: acceptable lateral, near-zero vx
```

The next offline target-source branch should be one of:

- short-horizon trajectory optimization over target sequences
- model-predictive balance/step planner with a terminal forward-progress term
- closed-loop teacher with explicit CoM/foot-placement state, not only actuator
  offsets

No supervised target dataset should be built until a source passes the
seed-robust 100/150 tick gates.
