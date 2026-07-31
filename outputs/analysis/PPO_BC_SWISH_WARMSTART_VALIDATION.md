# PPO BC Swish Warm-Start Validation

status: `HOLD_STEP0_CLOSED_LOOP_STABILITY`

This is an offline warm-start validation artifact. It did not run PPO updates,
SSH, deploy, run robot tests, or change robot runtime behavior.

## Why This Exists

The first PPO-loc student used the right PPO output contract but the wrong
hidden activation for the Playground PPO actor. The Playground PPO/export path
uses `swish`; the first PPO-loc BC trainer used `tanh`.

This pass retrained the supervised student with:

```text
hidden sizes: 512,256,128
activation: swish
output: tanh(loc)
```

## Swish PPO-Loc BC Fit

```text
artifact: outputs/analysis/PPO_LOC_SWISH_BC_STUDENT.md
status: PASS_PPO_LOC_BC_FIT_SMOKE
ONNX: outputs/analysis/ppo_loc_swish_bc_student_candidate/candidate.onnx
NPZ:  outputs/analysis/ppo_loc_swish_bc_student_candidate/candidate_mlp.npz
```

Fit metrics:

```text
MAE: 0.012030
p95 action error: 0.035899
max action error: 0.317852
target-rate p95: 2.228610 rad/s
target-rate max: 4.498640 rad/s
```

## PPO Param Export Fidelity

Actual PPO params were built from the swish BC NPZ:

```text
artifact: outputs/analysis/PPO_BC_SWISH_WARMSTART_STEP0_EXPORT_FIDELITY.md
status: PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY
checkpoint: outputs/analysis/ppo_bc_swish_warmstart_step0_checkpoint
exported ONNX: outputs/analysis/ppo_bc_swish_warmstart_step0.onnx
```

Action-level fidelity against the swish BC ONNX:

```text
samples checked: 2048
MAE: 0.00000004
p95 abs error: 0.00000012
max abs error: 0.00000036
```

This closes the actor-shape/activation/export problem. The exported PPO step-0
policy is a faithful view of the checkpointed policy.

## Closed-Loop Step-0 Gate

Strict task-matched fitted bridge gate:

```text
outputs/analysis/PPO_BC_SWISH_WARMSTART_STEP0_VALIDATION_FITTED_BACKLASH.md
outputs/analysis/ppo_bc_swish_warmstart_step0_validation_fitted_backlash.json
task: flat_terrain_backlash
command: straight x=0.08
bridge: fitted
duration: 10s
seeds: 0-7
```

Result:

| policy | runs | falls | duration complete | mean vx | mean track ratio | sent vel p95 range | tracking p95 range | result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `ppo_swish_step0` | 8 | 1 | 7 | 0.0115 | 0.1441 | 3.4393-3.8002 | 0.2584-0.2874 | `HOLD_STEP0_CLOSED_LOOP_STABILITY` |

Seed 5 is the blocker:

```text
seed: 5
samples: 74
termination: fall_or_nan
mean vx: -0.1976 m/s
track ratio: -2.4697
base height min: 0.0717 m
```

The other seven seeds complete duration but still hold on fitted tracking.

## Decision

Do not start PPO updates from this checkpoint yet.

What is solved:

```text
PPO actor shape
PPO swish activation
PPO tanh(loc) output contract
Orbax checkpoint creation
Playground ONNX export fidelity
```

What is not solved:

```text
step-0 closed-loop stability across seeds
fitted actuator tracking
seed-5 reverse/fall mode
```

Next branch should improve the warm-start policy before PPO, not debug export
plumbing:

```text
PLAN_IMPROVE_SWISH_WARMSTART_SEED5
```

Recommended next probes:

```text
1. collect a full trace for ppo_swish_step0 seed 5
2. compare seed 5 against successful seeds 0/2
3. add or relabel seed-5-adjacent states in the swish dataset
4. retrain swish PPO-loc BC
5. rerun the step-0 closed-loop fitted gate
```

PPO fine-tuning should wait until the step-0 warm start has no immediate
reverse/fall seed.
