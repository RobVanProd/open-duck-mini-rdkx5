# PPO-Loc BC Policy Validation

status: `HOLD_PPO_LOC_BC_TRACKING`

This is an offline validation artifact. It did not SSH, deploy, run robot
tests, start PPO training, or change robot runtime behavior.

## Purpose

The previous PPO-shape BC student matched PPO hidden-layer sizes but was trained
as an action-space MLP. That created a mismatch with the Brax PPO actor, whose
deterministic export is:

```text
tanh(loc)
```

This pass trained a PPO-compatible BC student directly through the same
`tanh(loc)` contract.

## Fit

```text
artifact: outputs/analysis/PPO_LOC_BC_STUDENT.md
status: PASS_PPO_LOC_BC_FIT_SMOKE
manifest: outputs/analysis/source_vx_selector_trace_dagger3_manifest.json
samples: 9268
hidden sizes: 512,256,128
```

Candidate:

```text
outputs/analysis/ppo_loc_bc_student_candidate/candidate.onnx
outputs/analysis/ppo_loc_bc_student_candidate/candidate_mlp.npz
```

Fit metrics:

```text
MAE: 0.014198
p95 action error: 0.040378
max action error: 0.284595
target-rate p95: 2.203947 rad/s
target-rate max: 5.154907 rad/s
ONNX verify max error: 0.00000059
```

## Standard Gate

Strict task-matched fitted bridge gate:

```text
outputs/analysis/DEPLOYABLE_SOURCE_VX_PPO_LOC_BC_VALIDATION_FITTED_BACKLASH.md
outputs/analysis/deployable_source_vx_ppo_loc_bc_validation_fitted_backlash.json
task: flat_terrain_backlash
command: straight x=0.08
bridge: fitted
duration: 10s
seeds: 0-7
```

Result:

| policy | runs | falls | duration complete | mean vx | mean track ratio | sent vel p95 range | tracking p95 range | result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `ppo_loc_bc` | 8 | 0 | 8 | 0.0381 | 0.4761 | 3.8384-3.9250 | 0.2641-0.2703 | `HOLD_CANDIDATE_TRACKING` |

## Comparison

```text
DAgger-3 128x128 rate-reg:
  mean vx: 0.0420
  mean track ratio: 0.5255
  sent vel p95: 3.7121-3.8488
  tracking p95: 0.2623-0.2767

PPO-shape action BC:
  mean vx: 0.0396
  mean track ratio: 0.4953
  sent vel p95: 3.7842-3.8409
  tracking p95: 0.2570-0.2684

PPO-loc BC:
  mean vx: 0.0381
  mean track ratio: 0.4761
  sent vel p95: 3.8384-3.9250
  tracking p95: 0.2641-0.2703
```

The PPO-loc student fixes the actor output-contract mismatch but does not
improve the closed-loop fitted gate. It moves forward and completes all eight
seeds, but it is lower-progress and slightly higher-rate than the PPO-shape
action-space BC. It is not a robot-ready policy.

## Decision

Do not run stress or robot validation.

The output contract problem is now understood:

```text
action-space BC -> poor direct PPO loc fidelity
PPO-loc BC      -> native PPO deterministic export, but same tracking hold
```

The remaining problem is not ONNX export or actor shape. It is that supervised
imitation of the selector is not enough to reduce fitted actuator tracking in
closed loop.

Next branch:

```text
PLAN_PPO_FINE_TUNE_FROM_PPO_LOC_BC
```

Before PPO updates:

```text
1. build actual PPO params from the PPO-loc NPZ
2. initialize loc branch from PPO-loc weights
3. initialize scale logits deliberately
4. leave value network fresh
5. run step-0 standard fitted closed-loop gate
6. only train if step-0 behavior matches this ONNX candidate
```

PPO fine-tuning should be judged by whether fitted tracking improves without
losing forward progress, not by reward alone.
