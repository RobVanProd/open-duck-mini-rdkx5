# Winner-v2 Observer Cross-Fit Contract Initial-State Correction

Status: `INITIAL_HOLD_PRESERVED_EXACT_READBACK_INITIALIZATION_FIXED`

The first completed contract result is preserved as
`HOLD_WINNER_V2_OBSERVER_CROSS_FIT_DEFAULT_OFF_CONTRACT`. Default-off trace and
canonical-result identity, enabled routing, previous-observer timing, CPU
execution and distinct plant/observer state all passed. Only the two offline
reconstruction checks failed, both by exactly
`5.1498413089490214e-8` rad.

The checker initialized its independent reconstruction models from an ideal
decimal home vector. The evaluator initializes both bridges from the actual
JAX reset target, whose float32 readback is recorded at tick zero. This violated
the preregistered requirement that the verification models and evaluator use
the exact same initial target.

The correction initializes both verification models from the enabled trace's
tick-zero obs[83:97] readback. The reconstruction threshold remains unchanged
at `1e-12` rad; no result value, evaluator behavior, policy, fit, matrix, gate
or authority changes. The initial HOLD remains in the artifact record, and this
correction is committed before rerun.
