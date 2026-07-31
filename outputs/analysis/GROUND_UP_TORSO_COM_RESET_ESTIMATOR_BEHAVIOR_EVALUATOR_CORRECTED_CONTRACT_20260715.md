# Ground-Up Torso-COM Reset-Estimator Behavior Evaluator Corrected Contract — 2026-07-15

Status: `PASS_RESET_ESTIMATOR_BEHAVIOR_EVALUATOR_CONTRACT`

The preregistered nominal-reset correction passes on CPU with zero policy
steps and zero formal behavior cells. Default-off remains 115-D with no latch.
Enabled resets are 116-D and preserve the final 14-D reference action; the
latch is at actor observation index 101.

Exact reset readbacks are:

| Torso-COM offset | Body | Latched normalized estimate |
|---:|---|---:|
| -0.05 m | body 2 `trunk_assembly` | -1.0 |
| 0.00 m | body 2 `trunk_assembly` | -0.0000445114 |
| +0.05 m | body 2 `trunk_assembly` | +0.999988556 |

All latches match the independent frozen estimator within 1e-6, are finite,
bounded, and strictly ordered. The endpoint models mutate body 2 X only. Both
contracted transformed graphs match their exact hashes, expose a 116-D actor
input, and load through CPU ONNX Runtime only.

Decision: `PROCEED_FROZEN_RESET_EST_LATCH_U05_BEHAVIOR_MATRIX`.

The original saturated-latch failure remains preserved separately. This pass
authorizes only the already-frozen 12 matrices / 48 cells; it does not authorize
training, Colab, GPU/iGPU, RDK-X5, runtime work, or robot use.
