# Ground-Up Torso-COM Reset-Estimator Epsilon-Aware Hosted Expansion Contract — 2026-07-15

## Result

`PASS_EPSILON_AWARE_HOSTED_EXPANSION_CONTRACT`

All frozen CPU-only checks pass with zero Colab sessions, remote bytes, PPO
steps, or behavior cells.

The wrapper preserves the original hosted source and raw failed report. It
accepts only the exact sole `step_zero_outputs_exact` failure with source hash
`05c0...920e`, z=-1/0/+1, zero critic error, actor error no greater than
float32 epsilon, exact `cuda:0` report plus live GPU proof, and the hash-locked
passing ULP audit. Over-epsilon, nonzero-critic, wrong-source, extra-failure,
original-pass, and missing-GPU controls all fail.

The original arm, 2M steps, seed 100, optimizer/reward/architecture, uniform
COM schedule, command support, actuator bridge, conservative envelope, and
0/1,003,520/2,007,040 exports remain exact. The raw `1e-7` failure is retained
inside the corrected report rather than rewritten.

## Authority

This authorizes only construction and zero-session validation of the frozen
wall-only launcher. No Colab allocation or training occurs from this contract.
No local GPU/iGPU, behavior evaluation, RDK-X5, runtime, or robot action is
authorized.

