# Ground-Up Measured Bridge Integration Audit

status: `PASS_SELECT_CAUSAL_BRIDGE_ONLY_ARM`

## Question

Can the already fitted actuator transition be inserted after the ground-up
hard target limit without changing the observation/action meaning or reviving
the penalty route that previously collapsed to standing?

## Result

Yes. The technically consistent transition is:

`policy action -> hard-bounded sent target -> delay/tau/velocity bridge -> physics`

The sent target remains in `motor_targets` and action history; the returned
observation also contains the actual joint state produced by the bridged plant.
This matches the existing closed-loop evaluator.

The CPU-only audit compared the exact JAX bridge equations with the independent
NumPy `ActuatorBridgeModel` across five deterministic 256-tick sequences:
home hold, step, alternating, chirp, and seeded bounded random. All values were
finite. The global maximum disagreement was `1.4305115e-7 rad`, below the
frozen `1e-6 rad` threshold.

All nine source-order checks and all four vector-provenance checks passed.
Machine-readable evidence:
`outputs/analysis/ground_up_measured_bridge_integration_audit.json`.

## Parameter provenance

- Delay ticks and tau values match the 14-joint combined P30 fit exactly.
- The six pitch-chain velocity limits match the primary pitch fit exactly:
  indices `2,3,4,11,12,13` use `1.50,1.50,1.75,1.25,1.00,1.25 rad/s`.
- The other eight velocity entries are neutral `5.24 rad/s` values. They are
  not represented as measured limits because the earlier preregistration
  deliberately neutralized non-pitch fits that hit bounds or did not decide
  the failed gate.

## Decision

The audit selects one structural causal arm: continue the strongest nominal
hard-vector command-support checkpoint with the fitted plant transition active.
It must not restore the prior target-rate, actuator-tracking, behavior-prior,
restore-KL, or other penalty stack. That exact penalty route already produced
double-support standing and is closed.

This audit alone authorizes no training or accelerator session. The next gate
is a separate frozen preregistration and CPU transition/restore/export contract.
No robot, RDK-X5, iGPU, onboard GPU, deployment, torque, or motor access is
authorized.

