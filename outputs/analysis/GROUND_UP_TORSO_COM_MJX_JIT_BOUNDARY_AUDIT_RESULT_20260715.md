# Ground-Up Torso-COM MJX JIT-Boundary Audit Result

status: `PASS_VALID_MJX_JIT_BOUNDARY_AUDIT`

decision: `GENERAL_JIT_FORWARD_DISCREPANCY_OR_UNRESOLVED`

This is one deterministic tick-zero reset state (effective n=1); it is a methods audit, not a statistical result.

| variant | endpoint class | combined endpoint error | oracle direction error | prior-invalid direction error |
|---|---:|---:|---:|---:|
| `EAGER_REPLACE_INSIDE` | `MATCH_ENDPOINT_ORACLE` | 0 | 0 | 0.0133886337 |
| `JIT_REPLACE_INSIDE_SEQUENTIAL` | `MISS_ENDPOINT_ORACLE` | 0.0268936157 | 0.0133886337 | 0 |
| `JIT_MODEL_ARGUMENT_SEQUENTIAL` | `MISS_ENDPOINT_ORACLE` | 0.0269031525 | 0.0133867264 | 7.24196434e-06 |
| `JIT_PAIR_REPLACE_INSIDE` | `MISS_ENDPOINT_ORACLE` | 0.0268936157 | 0.0133886337 | 0 |

The decision selects only a candidate evaluation-method correction for separate preregistration. It does not authorize the 144-cell map, actor work, training, hardware, or deployment.

## Evidence interpretation

The exact eager closure matches both endpoint vectors with zero error. The
exact evaluator JIT closure misses the endpoint oracle by a combined maximum
of 0.0268936157 m/s^2 and reproduces the preceding invalid half-direction
bit-for-bit. Passing immutable models as compiled arguments changes the result
by at most 7.24196e-6 m/s^2 relative to that invalid direction and still
misses the oracle. Returning both endpoints from one compiled call reproduces
the invalid direction exactly.

Therefore neither model construction inside JIT nor sequential endpoint calls
is sufficient to explain or correct the discrepancy. The supported methods
localization is a general JIT-versus-eager `mjx.forward` discrepancy for this
tick-zero diagnostic sensor branch. A separately preregistered exact-map
validation may test an eager, default-off branch reader while preserving the
baseline evaluator byte-for-byte after stripping the diagnostic field.
