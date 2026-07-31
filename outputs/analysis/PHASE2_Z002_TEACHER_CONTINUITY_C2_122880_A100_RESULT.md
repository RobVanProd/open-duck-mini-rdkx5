# Phase 2 z=0.002 Teacher Continuity From C2-122880 A100 Result

status: `HOLD_NO_CLEAR_IMPROVEMENT`
generated_at: `2026-06-30T12:00:00Z`

## Run

- workflow: `phase2-z002-teacher-continuity`
- session: `open-duck-a100-phase2d`
- hardware: Colab A100
- JAX/JAXLIB: `0.7.2`
- restore checkpoint: `outputs/phase2_domain_randomization/stage_z002_tracking_margin_c2_a100/smoke_20260630T102226Z_gpu/2026_06_30_103539_122880`
- target-rate scale: `-0.01`
- actuator-tracking scale: `-0.005`
- behavior prior: enabled, scale `-0.18`
- robot touched: `false`

Training completed successfully in `876.3 s` and exported checkpoints at
`40960`, `81920`, and `122880` steps.

## ONNX Hashes

| step | sha256 |
|---:|---|
| 40960 | `80c82afb554a7d88f813a87ad39e0d79b52d425b76d14d5d86ff14498ce46f70` |
| 81920 | `d22a6982cd71a1a9d92b2805ced37daa7f413fc204137bfd7fbc831b20ddae20` |
| 122880 | `d137bdc7a00d47448972e2b47052c671639683a3cbe158750dbb2617ec2c2b2d` |

## Compact Sweep

Local CPU sweep, fitted corrected bridge, commands `0.0,0.08`, duration `1.0 s`.

| step | command_x | status | vel p95 | tracking p95 | track ratio | mean local vx |
|---:|---:|---|---:|---:|---:|---:|
| 40960 | 0.00 | `PASS_CANDIDATE_SIM_GATE` | 1.0536 | 0.1943 | NA | 0.0064 |
| 40960 | 0.08 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 1.5504 | 0.2163 | 0.2232 | 0.0179 |
| 81920 | 0.00 | `PASS_CANDIDATE_SIM_GATE` | 1.0550 | 0.1944 | NA | 0.0065 |
| 81920 | 0.08 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 1.5591 | 0.2168 | 0.2091 | 0.0167 |
| 122880 | 0.00 | `PASS_CANDIDATE_SIM_GATE` | 1.1407 | 0.1945 | NA | 0.0051 |
| 122880 | 0.08 | `HOLD_CANDIDATE_TRACKING` | 1.4952 | 0.2156 | 0.2965 | 0.0237 |

## Interpretation

The teacher-continuity run did not produce a clear promotion over the previous
C2-122880 parent:

- prior C2-122880 result: ratio `0.3018`, tracking p95 `0.2163`
- best teacher-continuity result: ratio `0.2965`, tracking p95 `0.2156`

The teacher-continuity result slightly reduced tracking error but also slightly
reduced forward progress. Treat it as a hold, not a new anchor. Keep the current
best restore anchor at
`outputs/phase2_domain_randomization/stage_z002_tracking_margin_c2_a100/smoke_20260630T102226Z_gpu/2026_06_30_103539_122880`.

The next useful change should not be another small scalar reward tweak. The
current plateau points toward a structural mechanism, such as live-oracle
DAgger or phase/memory-aware student training, if the campaign continues from
this branch.

No robot test, SSH, deployment, grounded replay, or runtime behavior change was
performed.
