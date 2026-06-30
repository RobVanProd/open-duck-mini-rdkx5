# Phase 2 z=0.002 Tracking Polish From C2-122880 A100 Result

status: `HOLD_NO_TRACKING_IMPROVEMENT`
generated_at: `2026-06-30T11:15:00Z`

## Run

- workflow: `phase2-z002-tracking-margin`
- session: `open-duck-a100-phase2c`
- hardware: Colab A100
- JAX/JAXLIB: `0.7.2`
- restore checkpoint: `outputs/phase2_domain_randomization/stage_z002_tracking_margin_c2_a100/smoke_20260630T102226Z_gpu/2026_06_30_103539_122880`
- override target-rate scale: `-0.025`
- override actuator-tracking scale: `-0.012`
- robot touched: `false`

Training completed successfully in `763.1 s` and exported checkpoints at
`40960`, `81920`, and `122880` steps.

## ONNX Hashes

| step | sha256 |
|---:|---|
| 40960 | `a0efa9b767afb3c3ec3ab79657dbcac8a227dced17a53f1efa549af87a372d2a` |
| 81920 | `9cc6f900640adaa7867acace3e11986e9fa713e43cc4cca916db53c6d6520916` |
| 122880 | `a56008dd0aaa68739721c0194f734eb75bf2cdf6b91e4eeccf7f93cab5220416` |

## Compact Sweep

Local CPU sweep, fitted corrected bridge, commands `0.0,0.08`, duration `1.0 s`.

| step | command_x | status | vel p95 | tracking p95 | track ratio | mean local vx |
|---:|---:|---|---:|---:|---:|---:|
| 40960 | 0.00 | `PASS_CANDIDATE_SIM_GATE` | 1.1534 | 0.1943 | NA | 0.0056 |
| 40960 | 0.08 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 1.5661 | 0.2155 | 0.2171 | 0.0174 |
| 81920 | 0.00 | `PASS_CANDIDATE_SIM_GATE` | 1.1532 | 0.1944 | NA | 0.0052 |
| 81920 | 0.08 | `HOLD_CANDIDATE_TRACKING` | 1.5042 | 0.2180 | 0.3067 | 0.0245 |
| 122880 | 0.00 | `PASS_CANDIDATE_SIM_GATE` | 1.0621 | 0.1946 | NA | 0.0065 |
| 122880 | 0.08 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 1.5605 | 0.2158 | 0.2132 | 0.0171 |

## Interpretation

The stronger scalar tracking/target-rate polish did not beat the previous parent:

- prior C2-122880 result: ratio `0.3018`, tracking p95 `0.2163`
- best polish result: ratio `0.3067`, tracking p95 `0.2180`

This keeps the current best restore anchor at
`outputs/phase2_domain_randomization/stage_z002_tracking_margin_c2_a100/smoke_20260630T102226Z_gpu/2026_06_30_103539_122880`.

The next useful training change should not be another small scalar
tracking-penalty tweak. The evidence points toward a continuity or teacher-action
mechanism that preserves the moving gait while reducing tracking error.

No robot test, SSH, deployment, grounded replay, or runtime behavior change was
performed.
