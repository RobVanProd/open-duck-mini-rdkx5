# Ground-Up Torso-COM Matched Accelerometer-Map Result

status: `INVALID_MATCHED_ACCELEROMETER_READBACK`
decision: `INVALID_MATCHED_ACCELEROMETER_READBACK`

**Validity failure:** the classification table below is retained only as an
audit trail of executed cells. It has no selection or physical-interpretation
authority.

| tick | fixed compatible | weak | nonlinear center | rotated | tick class |
|---:|---:|---:|---:|---:|---|
| 0 | 36 | 0 | 0 | 0 | `FIXED_COMPATIBLE_TICK` |
| 24 | 8 | 14 | 6 | 8 | `NON_FIXED_TICK` |
| 32 | 4 | 1 | 2 | 29 | `NON_FIXED_TICK` |
| 40 | 24 | 6 | 0 | 6 | `NON_FIXED_TICK` |

Validity:

- nominal-vs-saved maximum error: 7.4274649817213145 m/s^2;
- tick-zero direction maximum error: 0.17335918773665471 m/s^2;
- all values finite: true.

No p-value or training reward is used. The result authorizes at most the next read-only preregistration named by the frozen decision.

The native nominal sensor reconstructed from saved `qpos/qvel/ctrl` differs
from the saved MJX actor observation by as much as 7.4274649817 m/s^2, far above
the frozen 1e-3 tolerance. The native tick-zero COM half-direction also differs
from frozen `d` by .1733591877 m/s^2, above the same tolerance. Both validity
requirements fail; no tolerance change, partial result, or closest class is
permitted.

This is a method failure, not evidence that the physical direction is fixed,
weak, rotated, or nonlinear. In particular, the apparent 72/21/8/43 class
counts and per-tick table cannot select a subsequent mechanism.

The failure localizes the next methodological requirement: any matched sensor
study must branch from an exact replayed MJX environment state carrying the
observation-generation and solver state, rather than reconstructing a native
state from the reporting-only `qpos/qvel/ctrl` subset. That work requires a new
preregistration. No actor fork, dynamic step, training, Colab, GPU/iGPU,
RDK-X5, runtime, or robot work is authorized by this invalid result.
