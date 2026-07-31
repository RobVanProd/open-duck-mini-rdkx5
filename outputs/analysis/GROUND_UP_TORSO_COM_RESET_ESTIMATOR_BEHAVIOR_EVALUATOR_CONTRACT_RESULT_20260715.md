# Ground-Up Torso-COM Reset-Estimator Behavior Evaluator Contract Result — 2026-07-15

Status: `FAIL_RESET_ESTIMATOR_BEHAVIOR_EVALUATOR_CONTRACT`

The preregistered reset-only CPU contract failed before any policy step or
formal behavior cell. With only
`ground_up_reset_com_estimator_input=True`, the evaluator retained the
playground's stochastic initial reset. At frozen seed 167931544 the measured
reset accelerometers were outside the nominal calibration anchors and all
three torso-COM cells latched `+1.0`; strict class ordering therefore failed.
The later deterministic home-support replacement does not recompute the latch.

All other contract checks passed, including default-off 115-D identity,
enabled 116-D propagation at index 101, independent estimator agreement,
body-2 `trunk_assembly` X-only mutation, exact graph identity, and CPU-only
execution. This is evaluator plumbing evidence, not policy behavior evidence.

Decision: `STOP_BEFORE_BEHAVIOR_RESET_CALIBRATION_MISMATCH`.

The raw result is
`outputs/analysis/ground_up_reset_com_estimator_behavior_evaluator_contract.json`.
No training, Colab, GPU/iGPU, RDK-X5, robot, policy step, or formal behavior
cell ran.
