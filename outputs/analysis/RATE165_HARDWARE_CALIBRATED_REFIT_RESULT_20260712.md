# Rate165 Hardware-Calibrated Refit Result

status: `REJECT_BC_REFIT_PPO_ROUTE_SUPPORTED`

The exact preregistered 7000-step CPU refit reduced aggregate target-rate p95
from `1.4235` to `1.2649 rad/s`, but increased cloning p95 error from `0.0176`
to `0.0266`. ONNX export fidelity passed.

On the unchanged P30 fixed-target bridge at x=.08 seed 0 it completed 15 s but
failed the frozen rules:

- mean vx `0.0217 m/s` vs required `0.0257`
- tracking ratio `0.2707` vs required `0.3213`
- single support `15.8667%` vs required `20%`
- p95 velocity excess `0.2434 rad/s` vs required `0`
- max velocity excess `0.4903 rad/s` vs required `0`

Close this exact BC refit without scale/limit/seed/length tuning. The result
shows that supervised temporal regularization trades away motion before meeting
the independently measured envelope. A separately preregistered constrained
policy-optimization route against the fixed-target bridge is supported; it is
not authorized by this document. Preserve the promoted rate165 policy.

