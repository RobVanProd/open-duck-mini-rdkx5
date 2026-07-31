# Phase 2 z=0.0025 Boundary Rate1p9 Full Gate Decision

status: `HOLD_ZERO_COMMAND_SEED5_COLLAPSE`
generated_at: `2026-07-02T06:55:00Z`

This is an offline sim gate decision. It did not train, SSH, deploy, run robot
tests, touch hardware, or change runtime behavior.

## Candidate

- policy: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0_contactphase_rate1p9_bc_candidate/candidate.onnx`
- source decision: `outputs/analysis/PHASE2_Z0025_LIVE_ORACLE_BOUNDARY_ITER0_CONTACTPHASE_RATE1P9_BC_DECISION_20260701.md`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.0025`
- bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- evaluator: canonical corrected closed-loop seed sweep

## x=0.08 Full Gate

Artifact:

```text
outputs/analysis/PHASE2_Z0025_BOUNDARY_RATE1P9_FULL_X008_GATE_CPU.md
outputs/analysis/phase2_z0025_boundary_rate1p9_full_x008_gate_cpu.json
```

Result:

```text
PASS_X008_FULL_GATE
```

Summary:

| metric | value |
|---|---:|
| seeds passed | `8/8` |
| falls | `0/8` |
| samples | `750/750` each seed |
| mean track ratio | `0.3742` |
| mean local vx | `0.0299 m/s` |
| max pitch sent velocity p95 range | `1.9065-1.9234 rad/s` |
| max tracking p95 range | `0.1917-0.1953 rad` |
| p95 velocity excess | `0.0000` |
| max velocity excess | `0.0000` |

This is the strongest z=0.0025 positive-command evidence so far. Seed 5, the
previous terrain/support weak seed, completed the full 15-second x=0.08 gate
with no corrected-envelope velocity excess.

## x=0.0 Preservation Gate

Artifact:

```text
outputs/analysis/PHASE2_Z0025_BOUNDARY_RATE1P9_FULL_X000_GATE_CPU.md
outputs/analysis/phase2_z0025_boundary_rate1p9_full_x000_gate_cpu.json
```

Result:

```text
HOLD_X0_SEED5_COLLAPSE
```

Summary:

| metric | value |
|---|---:|
| seeds passed | `7/8` |
| failing seed | `5` |
| failing samples | `43` |
| failing termination | `fall_or_nan` |
| failing mean local vx | `-0.3468 m/s` |
| failing base height min | `0.0575 m` |
| failing max tracking p95 | `0.2106 rad` |
| p95 velocity excess | `0.0000` |
| max velocity excess | `0.0000` |

The failure is not a corrected-envelope velocity excess. It is a zero-command
support/command-conditioning failure on seed 5.

## Decision

```text
HOLD_ZERO_COMMAND_SEED5_COLLAPSE
```

The rate1p9 contact+phase candidate is useful as a z=0.0025 motion/support
source, but it is not a deployable or robot-test candidate because it does not
preserve x=0.0 command semantics across seeds.

Next aligned offline work:

1. Use this candidate's x=0.08 z=0.0025 passing traces as positive terrain
   motion/support source evidence.
2. Do not promote the candidate until zero-command seed 5 is repaired and the
   full x=0.0 gate passes.
3. Treat the next source/oracle strengthening target as seed-5 zero-command
   support at z=0.0025, not another scalar x=0.08 progress tweak.
4. After zero-command preservation is fixed, repeat both full x=0.08 and x=0.0
   gates before any A100 scaling or higher terrain rung.

No robot, SSH, deploy, grounded replay, or runtime behavior change is
authorized by this decision.
