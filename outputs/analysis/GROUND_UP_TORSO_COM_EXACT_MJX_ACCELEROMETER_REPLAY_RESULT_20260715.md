# Ground-Up Torso-COM Exact MJX Accelerometer-Replay Result

status: `INVALID_EXACT_MJX_ACCELEROMETER_REPLAY`
decision: `INVALID_EXACT_MJX_ACCELEROMETER_REPLAY`

**Validity failure:** the class table is retained only as an audit trail. It
has no physical-interpretation or selection authority.

| tick | fixed compatible | weak | nonlinear center | rotated | tick class |
|---:|---:|---:|---:|---:|---|
| 0 | 36 | 0 | 0 | 0 | `FIXED_COMPATIBLE_TICK` |
| 24 | 3 | 23 | 10 | 0 | `NON_FIXED_TICK` |
| 32 | 2 | 13 | 18 | 3 | `NON_FIXED_TICK` |
| 40 | 7 | 19 | 10 | 0 | `NON_FIXED_TICK` |

Validity:

- baseline row mismatches after stripping map fields: 0;
- nominal actor observation maximum error: 0 m/s^2;
- tick-zero direction maximum error: 0.013388633728027344 m/s^2;
- all values finite: true.

No p-value or training reward is used. The frozen result authorizes at most its named next preregistration.

All baseline-side validity checks pass: 36/36 traces reproduce their prior
600 rows exactly after stripping the append-only map field, with zero total row
mismatches, and `a_nom` equals the actor observation with zero error. Thus the
instrumentation is behavior-neutral and the live-state indexing is exact.

The remaining frozen validity check fails uniformly. All 36 tick-zero
half-directions differ from frozen `d` by .013388633728027344 m/s^2 maximum
absolute error, exceeding the preregistered 1e-3 tolerance. No tolerance change
or partial interpretation is permitted. The apparent aggregate counts
(48 compatible, 55 weak, 38 nonlinear-center, 3 rotated) and per-tick table
therefore cannot select any next mechanism.

This further localizes the method discrepancy: it is not native-versus-MJX
engine choice, saved-state indexing, nominal observation reproduction, or
baseline perturbation. The live nominal `state.data` forwarded under a replaced
COM model is not identical to a state initialized under that COM model at the
frozen tick-zero anchor. The exact responsible model/data initialization field
is not yet established and requires a separately preregistered read-only
initialization-order audit.

No actor fork, training, Colab, GPU/iGPU, RDK-X5, runtime, or robot work is
authorized by this invalid result.
