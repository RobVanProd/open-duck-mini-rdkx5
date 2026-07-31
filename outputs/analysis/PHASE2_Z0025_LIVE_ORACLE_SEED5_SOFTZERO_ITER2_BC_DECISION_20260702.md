# Phase 2 z=0.0025 Live-Oracle Seed5 Soft-Zero Iter2 BC Decision

status: `HOLD_SOFTZERO_ITER2_X0_SEED5_COLLAPSE`

This was an offline supervised behavior-cloning fit and short seed gate. It did
not train PPO, SSH, deploy, run robot tests, touch hardware, or change runtime
behavior.

## Input

- aggregate manifest: `outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2_run/live_oracle_dagger_aggregate_manifest.json`
- aggregate dataset_id: `8229af2c3e92a70d`
- aggregate samples: `12043`
- x=0.0 relabel: `zero_action`, alpha `0.50`
- model: contact/phase-modulated feed-forward BC student
- context indices: `[6, 97, 98, 99, 100]`
- target-rate regularizer: scale `1.5`, scalar limit `1.9 rad/s`

## Fit Result

- fit artifact: `outputs/analysis/PHASE2_Z0025_LIVE_ORACLE_SEED5_SOFTZERO_ITER2_CONTACTPHASE_RATE1P9_BC_STUDENT.md`
- candidate ONNX: `outputs/analysis/phase2_z0025_live_oracle_seed5_softzero_iter2_contactphase_rate1p9_bc_candidate/candidate.onnx`
- candidate ONNX sha256: `444a460222d719970db182ea27e3fa94d9cbfa7c58122e621b81fef4258a60ab`
- candidate NPZ sha256: `2402382f2f6e4298ad3fad11500bfd09580777203642c52ad7eddb27062cdd3a`
- MAE: `0.008747`
- p95 abs error: `0.028583`
- target-rate p95: `1.746516 rad/s`
- target-rate max: `2.001389 rad/s`
- ONNX fidelity p95 abs error: `0.00000013`
- ONNX fidelity max abs error: `0.00000030`

The supervised fit itself is clean and in the same range as prior BC students.

## Immediate x=0.0 Seed-5 Gate

Artifact:

```text
outputs/analysis/PHASE2_Z0025_LIVE_ORACLE_SEED5_SOFTZERO_ITER2_SHORT_X0_SEED5_GATE.md
outputs/analysis/phase2_z0025_live_oracle_seed5_softzero_iter2_short_x0_seed5_gate.json
```

Result:

```text
status:                    HOLD_CANDIDATE_FALL_OR_TERMINATION
duration:                  2.0 s
samples:                   43
termination:               fall_or_nan
mean local vx:             -0.3652 m/s
base height min:           0.0460 m
max pitch velocity p95:    0.4322 rad/s
velocity excess:           0.0000
max tracking p95:          0.2168 rad
```

The candidate failed at the same sample count as the parent zero-command seed-5
collapse. It did not fail by exceeding the corrected velocity envelope; it
failed by reverse drift and support collapse at zero command.

## Decision

`HOLD_SOFTZERO_ITER2_X0_SEED5_COLLAPSE`

Do not promote this candidate. Do not run the full `x=0.0` / `x=0.08` gates,
A100 scaling, robot validation, push curriculum, or higher-terrain curriculum
from this candidate.

The result shows that adding 43 soft-zero labels from the same failure pocket is
not enough to repair seed 5. The next branch needs a stabilizing zero-command
support source/teacher for seed 5 before another supervised fit, or a different
command-conditioning mechanism that prevents the reverse-support pocket.
