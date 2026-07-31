# Ground-Up Torso-COM Reset Estimator Feasibility Result

status: `PASS_RESET_COM_ESTIMATOR_FEASIBILITY_COMPLETE`

decision: `SUPPORT_RESET_LATCHED_PIECEWISE_LINEAR_COM_ESTIMATOR_ARM`

This is one deterministic reset curve (effective n=1), not a statistical or hardware-robustness result.

| actual offset (m) | role | estimate (m) | absolute error (m) | anchor sensor error (m/s^2) |
|---:|---|---:|---:|---:|
| -0.05 | anchor | — | — | 0 |
| -0.04 | held-out | -0.040857287 | 0.000857287271 | — |
| -0.03 | held-out | -0.031213976 | 0.00121397629 | — |
| -0.02 | held-out | -0.021140734 | 0.00114073389 | — |
| -0.01 | held-out | -0.010707251 | 0.000707250513 | — |
| +0.00 | anchor | — | — | 0 |
| +0.01 | held-out | +0.009941236 | 5.87639244e-05 | — |
| +0.02 | held-out | +0.019961405 | 3.85951708e-05 | — |
| +0.03 | held-out | +0.030060822 | 6.08216971e-05 | — |
| +0.04 | held-out | +0.040094625 | 9.46247368e-05 | — |
| +0.05 | anchor | — | — | 0 |

All held-out signs correct: `true`. Strictly ordered: `true`. Maximum error: `0.00121397629` m. Minimum adjacent sensor separation: `0.279735532` m/s^2.

A passing decision authorizes only a separate preregistration for the named estimator arm. It is not policy, training, deployment, or robot clearance.

## Evidence interpretation

All three anchors reproduce exactly. All eight held-out points select the
correct sign segment and remain strictly ordered. Negative-side errors range
from .707 mm to 1.214 mm; positive-side errors range from .039 mm to .095 mm.
The weakest adjacent 1 cm sensor separation is still 279.7 times the frozen
1e-3 m/s^2 floor.

Under this one deterministic simulator reset, the reset accelerometer is
therefore sufficient for the frozen latched piecewise-linear X-COM estimate.
The result does not establish sensor-noise, reset-pose, floor, hardware, or
deployment robustness. It selects only a separately preregistered estimator-
input policy arm; it does not authorize training that arm.
