# Ground-Up Guard Winner x=0 Preregistration

status: `PREREGISTERED_CPU_ONLY`

The selected `G1_EXACT_BOUNDARY/T2_EQUAL` formulation must preserve safe
zero-command behavior at both its 512,000 and 1,024,000 checkpoints. The frozen
matrix is command `x=0`, seeds 100/101, 600 ticks, flat backlash, home-support
reset: exactly four CPU cells.

Every cell must be finite, complete 600 ticks without termination, pass the
existing candidate simulation gate, retain zero action saturation and zero
pitch-chain rate excess, stay below `0.20 rad` tracking and `0.25 rad` body
pitch p95, stay above `0.12 m` base height, and keep absolute mean local forward
velocity at or below the existing `0.02 m/s` deadband.

Both checkpoints and all four cells must pass. Passing advances only to a
separately preregistered robustness ladder for randomization, delays, and
pushes. It does not authorize that ladder yet, training, Colab, local GPU,
RDK-X5, robot, deployment, torque, or motor access.
