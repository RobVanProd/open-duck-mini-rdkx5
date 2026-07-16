# Winner v2 Bridge-Observer Contract Preregistration

Status: `PREREGISTERED_BEFORE_FORMAL_REPLAY`

## Question

Does the already-versioned pure CPU `ActuatorBridgeModel` reproduce the exact
bridge-realized target semantics required at winner observation indices 83:97?

## Frozen inputs

- Composite policies: SHA-256 `99d3afce...04de` and `0dfc24bd...f4ece`.
- All 16 composite R1 traces: two checkpoints x two fits x four commands,
  600 rows each.
- Fits: P30 SHA-256 `908ddb01...db0b`; the committed P31/34 fit file and hash
  recorded by the checker.
- Joint order: the existing 14-entry `actuator_bridge_model.JOINT_NAMES`.
- Initial observer state: the configured home target, independently recovered
  from each trace's first sent target and delayed action using the frozen
  0.25-rad action scale; all recovered home vectors must agree.
- Transition: per-joint fitted integer delay, exact first-order
  `1-exp(-dt/tau)`, then fitted velocity clip, at recorded dt=0.02 s.
- Tolerance: maximum absolute reconstruction error <=1e-12 rad.

The checker and this preregistration must be committed before the formal replay.
No trace, fit, policy, tolerance, indexing or formula may change after reading
the formal result.

## Pass rule

Pass only if all 16 expected traces and exactly 9,600 rows are present; every
row is finite and 14-D; both fits and both checkpoints are covered; all home
vectors agree within 1e-12 rad; and every reconstructed applied target matches
the recorded `applied_target_rad` within 1e-12 rad.

Pass authorizes only the v2 offline contract resolution: obs[83:97] must be
filled by this forward observer initialized at home and advanced once per sent
target. It does not authorize integrating the runtime, selecting a hardware fit,
Gate 5, RDK-X5, robot access or deployment.

