# Full-8 MLP Router Live-Corrected Iter2 Decision

status: `HOLD_FULL8_MLP_ROUTER_LIVE_CORRECTION_REGRESSES_SEED7`

Offline analysis only. No robot tests, SSH, deploy, grounded replay, hardware
training, or runtime behavior change was performed.

## Inputs

- seed-0 threshold-failure trace: `outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_TNEG2_SEED0_TRACE_GATE.md`
- seed-0 threshold-failure branch trace: `outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_TNEG2_SEED0_BRANCH_TRACE.md`
- iter2 separability: `outputs/analysis/PHASE2_FULL8_MLP_ROUTER_LIVE_CORRECTED_ITER2_SEPARABILITY.md`
- iter2 hard screen: `outputs/analysis/PHASE2_FULL8_MLP_ROUTER_LIVE_CORRECTED_ITER2_X008_SEED0_5_7_GATE.md`

The iter2 gate used the existing full-8 selected source manifest plus
closed-loop corrective traces:

```text
branch-A correction: prior seed-0 MLP-router failure, first 80 ticks, weight 50
branch-A correction: threshold=-2 seed-0 failure, first 80 ticks, weight 50
branch-B correction: seed-5 failure trace from seed0-startup-cost router, first 80 ticks, weight 50
```

## Separability

The wider stateless MLP still separated the held-out source labels:

```text
status: PASS_MLP_ROUTER_SEPARABLE
test balanced accuracy: 88.43%
test positive selected: 80.00%
test negative false selected: 3.14%
gate_npz_sha256: 3e7d6797065d690acfa0217ffd8cce7dc2847aa8a5ba6aba2dc6fa9b6ea88615
candidate_sha256: 7192c7b193100ac60ad6a44d9167aa1337d24cde17a0e50a8a0662f78eaba6d9
onnx_verify_sha256: 95ad864bf5e2c747a8dc4cc392616e42c9518d896be4986d5195380d689343ec
```

The composed ONNX verified exactly:

```text
status: PASS_ONNX_OBS_MLP_GATE_VERIFY
max_abs_error: 0.0
```

## Closed-Loop Screen

The composed router was screened at `x=0.08`, fitted corrected bridge,
`rough_terrain_backlash`, `z=0.0075`, home-support reset, and gentle pushes.

| seed | status | samples | vx | track_ratio | body_pitch_p95 | base_min | p95_vel_excess | max_vel_excess |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0252 | 0.3149 | 0.1941 | 0.1588 | 0.0000 | 0.0000 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 169 | 0.1257 | 1.5711 | 0.7670 | 0.0100 | 0.0000 | 0.0000 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 605 | 0.0549 | 0.6863 | 0.2476 | 0.0106 | 0.0000 | 0.0000 |

## Decision

Do not promote this candidate and do not start Phase 2 domain-randomization
training from it.

Live-correcting the stateless MLP gate with the new seed-0 failed rollout
recovers seed 0 but still fails seed 5 and now regresses seed 7. The result
confirms the threshold-tradeoff finding: source-label and closed-loop failure
trace classification are not sufficient objectives for this stateless router.

Recommended next step:

```text
Close the stateless MLP-router sub-branch.
Move to a stateful/prefix-conditioned router or trainable closed-loop mixture
whose objective is rollout outcome, not trace-label separability.
```

Phase 2 DR remains blocked until a deployable corrected-bridge candidate clears
the canonical multi-seed gate.
