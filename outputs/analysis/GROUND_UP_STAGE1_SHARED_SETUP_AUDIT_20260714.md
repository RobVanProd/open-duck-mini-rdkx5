# Ground-Up Stage-One Shared Setup Audit

status: `OBJECTIVE_AND_CURRICULUM_MISMATCH_FOUND`

## Finding

The reference motion was active from the first update, but the declared staged curriculum was not implemented as stages. Domain randomization, reset/sensor noise, action and IMU delay, and mild pushes were active from the first update.

Reference phase 0 requests contacts `[1, 0]` and has home-pose squared leg error `0.362490`. The deterministic closest home-compatible double-support phase is `20`, with squared error `0.112681`.

The actor's reset phase feature is `[0,0]` (norm 0), while every normal cyclic phase feature after the first step has norm 1. Thus the first action of every episode receives an out-of-contract phase sentinel rather than the reset reference phase.

The continuous positive-command sampler does not produce a continuous reference target:

| discrete reference dx | training-sample fraction |
|---:|---:|
| 0.074 | 88.750% |
| 0.148 | 11.250% |

The positive core objective (alive + angular tracking + linear tracking) weakly separates stationary behavior from exact speed tracking:

| command x | stationary linear term | stationary core | perfect core | retained |
|---:|---:|---:|---:|---:|
| 0.040 | 0.8521 | 28.1304 | 28.5000 | 98.70% |
| 0.074 | 0.5783 | 27.4458 | 28.5000 | 96.30% |
| 0.080 | 0.5273 | 27.3182 | 28.5000 | 95.85% |
| 0.120 | 0.2369 | 26.5923 | 28.5000 | 93.31% |

These are objective diagnostics, not policy-selection metrics. The completed behavior gates remain authoritative.

## Supported next step

Preregister a nominal reference-bootstrap screen before more architecture or scalar search. It must isolate a clean nominal stage and test deterministic home-compatible phase alignment before adding zero-command mixing, randomization, delay, pushes, or rough terrain. No training is authorized by this audit alone.

No robot, RDK-X5, local GPU, iGPU, or onboard GPU access occurred.
