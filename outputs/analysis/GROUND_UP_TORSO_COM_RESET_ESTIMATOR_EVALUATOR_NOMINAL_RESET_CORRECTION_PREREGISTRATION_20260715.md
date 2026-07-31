# Ground-Up Torso-COM Reset-Estimator Evaluator Nominal-Reset Correction Preregistration — 2026-07-15

## Evidence and scope

The first reset-only evaluator contract failed because its sole new estimator
switch left `nominal_reference_bootstrap=False`. That stochastic pre-reset is
later replaced by home-support state, but its saturated latch survives. Hosted
training explicitly used both `--nominal_reference_bootstrap` and
`--ground_up_reset_com_estimator_input`; the earlier CPU estimator package also
used both and measured the frozen three-anchor ordering.

This preregisters one correction before implementation: when and only when
`policy_reset_com_estimator_input=True`, the evaluator sets both existing
environment config fields
`ground_up_reset_com_estimator_input=True` and
`nominal_reference_bootstrap=True` before environment construction. The CLI,
model override, environment reset, home-support propagation, policy graphs,
commands, seed, thresholds, and frozen 12-matrix/48-cell behavior plan remain
unchanged. Default-off evaluation remains unchanged.

The same reset-only CPU contract must then pass, including independent latch
agreement and strict ordering at -.05/0/+.05 m, before any policy step. The
original failed JSON and decision remain preserved; they may not be replaced.
No behavior outcome may authorize retry or parameter changes.

No training, Colab, local GPU/iGPU, RDK-X5, runtime, robot, deployment, torque,
or motor action is authorized.
