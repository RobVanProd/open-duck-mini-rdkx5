# Ground-Up Closed-Loop Corrective Source Audit

status: `NO_ELIGIBLE_VALIDATED_CORRECTIVE_SOURCE`

The repository contains `32` scored algorithmic controller/optimizer result
sets across closed-loop weight transfer, COM transfer, foot-placement MPC,
staged/support transfer, and contact-sequence optimization. All `32` are
eligible under the ground-up constraint; none passes its seed-robust target
gate. Their recorded statuses are `HOLD_NO_SEED_ROBUST_TARGETS` or
`HOLD_HORIZON_SEQUENCE_NO_ROBUST_TARGET`.

The remaining sources are ineligible or invalid:

- the projected polynomial reference fails the direct CPU behavior gate even
  after exact-command interpolation;
- `BEST_WALK_ONNX_2` has the strongest persistent closed-loop propulsion
  evidence, but is a frozen comparator and may not be a teacher or warm start;
- the rate-bounded DAgger-derived controller has long-duration gait evidence,
  but depends on an existing learned-policy lineage and is prohibited by the
  same contract.

## Selected untried source class

The next CPU-only probe is an oracle-dynamics receding-horizon shooting
controller. It is materially different from the failed hand-authored families:
it replans from current simulated state and directly optimizes forward
displacement while penalizing falls, lateral motion, tilt, reference residual,
action variation, and measured actuator-rate use.

This selection does not claim the controller will work. It is selected because
it directly addresses the documented missing propulsion mechanism without
using an existing learned policy. It must prove persistent gait in the fitted
simulator before it can supply any learning data.

Authorization is limited to local CPU contract and source probes. No Colab,
local GPU, iGPU, onboard GPU, RDK-X5, or robot access is authorized.
