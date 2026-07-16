# Viability Prevention Replay Preregistration

Status: `PREREGISTERED_BEFORE_B2_OUTCOMES`

B2 evaluates exactly three frozen comparators: applied-target 1M, the closest
persistent tail arm T2_EQUAL at its 1M endpoint, and BEST_WALK_ONNX_2 as a
comparator only. Each runs x = .074/.077/.080, seeds 100/101, P30,
home-support reset and 600 ticks: 18 cells total. Full qpos/qvel/contact traces
are required.

Every tick is scored against the frozen B1 X_NEG and X_POS neighborhoods.
X_NEG proximity has weight 3 and X_POS weight 1. The radius is fixed at
0.6954732013592478 and cannot be widened.

An actual fall is a non-duration termination or a trace shorter than 600
ticks. A fall routes only if it enters either neighborhood with at least four
ticks of lead. B3 is positive only if every policy contributes at least one
actual fall and every actual fall routes. Tracking holds and low-progress
holds are not relabeled as falls. A negative result closes the hosted
viability-prevention branch; there is no vacuous pass and no closest-policy
promotion.

No training reward is used. CPU simulation only; no hosted session, GPU/iGPU,
RDK-X5 or robot access. Robot clearance remains `NO`.
