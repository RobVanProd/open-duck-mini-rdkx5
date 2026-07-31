# Full-8 MLP Router Wide Threshold -2 Decision

status: `HOLD_FULL8_MLP_ROUTER_THRESHOLD_TRADEOFF`

Offline analysis only. No robot tests, SSH, deploy, grounded replay, hardware
training, or runtime behavior change was performed.

## Inputs

- base gate: `outputs/analysis/phase2_full8_mlp_router_gate_seed0_seed5_startup_cost_wide/gate_mlp.npz`
- threshold: `-2.0`
- composed candidate: `outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_tneg2_candidate/candidate.onnx`
- seed-5 gate: `outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_TNEG2_X008_SEED5_GATE.md`
- seed-0/7 gate: `outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_TNEG2_X008_SEED0_7_GATE.md`

## Result

Lowering the wide symmetric MLP-router threshold from `0.0` to `-2.0`
increases branch-B selection and fixes the previous seed-5 fall:

| seed | status | samples | vx | track_ratio | body_pitch_p95 | base_min | p95_vel_excess | max_vel_excess |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0316 | 0.3947 | 0.1724 | 0.1580 | 0.0000 | 0.0000 |
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 166 | 0.1265 | 1.5808 | 0.8282 | 0.0083 | 0.0000 | 0.0000 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0352 | 0.4396 | 0.1833 | 0.1562 | 0.0000 | 0.0000 |

## Decision

Do not promote this candidate.

The threshold shift proves seed 5 can be recovered by selecting more branch B,
but that same change regresses seed 0 into the same lunge/fall signature. The
problem is therefore not a global branch-B amount. It is a seed/state-specific
routing conflict that a scalar threshold cannot solve.

Recommended next step:

```text
Use a closed-loop-aware router objective or stateful/prefix router that can
choose branch B for seed-5 startup without choosing it for seed-0 startup.
Do not keep sweeping scalar thresholds as if a single global cutoff is likely
to satisfy both constraints.
```

Phase 2 DR remains blocked until a deployable corrected-bridge candidate clears
the canonical multi-seed gate.
