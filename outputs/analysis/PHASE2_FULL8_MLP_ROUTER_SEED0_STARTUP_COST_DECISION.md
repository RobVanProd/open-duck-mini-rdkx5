# Full-8 MLP Router Seed0 Startup-Cost Decision

status: `HOLD_FULL8_MLP_ROUTER_SEED0_FIX_REGRESSES_SEED5`

Offline analysis only. No robot tests, SSH, deploy, grounded replay, training
against hardware, or runtime behavior change was performed.

## Inputs

- gate training report: `outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_STARTUP_COST_SEPARABILITY.md`
- gate npz sha256: `e663f806af55dde33295b169a445551515d8435da82b623738523fb2904f4861`
- composed candidate: `outputs/analysis/phase2_full8_mlp_router_seed0_startup_cost_candidate/candidate.onnx`
- composed candidate sha256: `b4a7e338eae789803ad132459df9e1b1b98c36172bed5845f8bbeff10fcaab36`
- ONNX verification sha256: `36c30e1c85b261da294d2ae1329f9bd37e271c2bb61540fae0049b4cfa96c574`
- hard screen: `outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_STARTUP_COST_X008_SEED0_5_7_GATE.md`

## Gate Training

The nonlinear observation gate was retrained with the failed seed-0 MLP-router
trace added as a branch-A corrective set:

```text
extra_negative_trace: outputs/analysis/phase2_full8_mlp_router_candidate_seed0_trace/full8_mlp_router/seed_000/trace.jsonl
extra_negative_first_ticks: 80
extra_negative_weight: 50.0
```

The held-out trace-label classifier still passed the separability thresholds:

```text
status: PASS_MLP_ROUTER_SEPARABLE
test balanced accuracy: 87.14%
test positive selected: 76.67%
test negative false selected: 2.38%
```

The composed stateless ONNX router preserved the fixed policy contract and
verified exactly:

```text
status: PASS_ONNX_OBS_MLP_GATE_VERIFY
max_abs_error: 0.0
```

## Closed-Loop Screen

The hard corrected-bridge rough-terrain screen was run at `x=0.08`, fitted
bridge, `z=0.0075`, home-support reset, and gentle pushes over seeds `0,5,7`.

| seed | status | samples | vx | track_ratio | body_pitch_p95 | base_min | p95_vel_excess | max_vel_excess |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0298 | 0.3721 | 0.1887 | 0.1581 | 0.0000 | 0.0000 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 158 | 0.1298 | 1.6227 | 0.8237 | 0.0149 | 0.0000 | 0.0000 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0275 | 0.3438 | 0.1895 | 0.1581 | 0.0000 | 0.0000 |

Distribution:

```text
passes: 2/3
falls: 1/3
mean track ratio: 0.7795
mean vx: 0.0624 m/s
velocity excess: 0.0000 p95, 0.0000 instantaneous
```

## Decision

Do not promote this candidate and do not start Phase 2 domain-randomization
training from it.

The seed-0 startup correction fixed the previous seed-0 regression but shifted
the closed-loop failure to seed 5. This proves the MLP router boundary is
movable, but scalar one-sided correction is not enough. The next router
attempt must jointly constrain seed-0 startup behavior and seed-5 behavior
instead of optimizing a single corrective trace in isolation.

Recommended next step:

```text
Build a multi-constraint, closed-loop-aware router objective:
  - seed 0 startup should remain branch A / command-gated
  - seed 5 startup and trajectory should remain branch B / iter25
  - seed 7 should preserve the currently passing behavior
  - hard-screen the composed ONNX before any full-8 or DR promotion
```

Phase 2 DR remains blocked until a deployable corrected-bridge candidate passes
the canonical multi-seed gate.
