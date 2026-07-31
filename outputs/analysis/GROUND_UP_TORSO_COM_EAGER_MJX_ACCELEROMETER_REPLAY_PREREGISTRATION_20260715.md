# Ground-Up Torso-COM Eager-MJX Accelerometer Replay Preregistration

status: `PREREGISTERED_READ_ONLY_CPU_EAGER_MJX_ACCELEROMETER_REPLAY`

## Evidence and single correction

The exact-MJX map is invalid because its diagnostic branch was JIT-compiled.
The frozen JIT-boundary audit reproduces the invalid half-direction bit-for-bit
with the exact evaluator JIT closure, while the same closure executed eagerly
matches both endpoint oracle vectors with zero error. External model arguments
and paired endpoint JIT do not repair the discrepancy.

This study changes only the default-off diagnostic branch runner from
`jax.jit(read_com_accelerometer)` to the eager
`read_com_accelerometer` closure. Baseline environment stepping, actor calls,
models, observations, traces, and decisions remain frozen. No training reward
is used.

## Frozen sources

- valid JIT-boundary result SHA-256:
  `11a50e76e84e0e0ae67d33dd12d587864ba9a557db27355d97743eab0f717575`;
- invalid exact-MJX map result SHA-256:
  `23b4ad8444fc4eaa9dd83dcffb64b3b070431f3b424a83d71bf9a5b2a5ffcf3b`;
- exact replay manifest SHA-256:
  `ac42abc8a940d97f0c0373ce624eaf2d2f803ac574e0de52c82303c7a759da07`;
- pre-correction `closed_loop_sim_eval.py` SHA-256:
  `d2c452b19826e4ff9e399bf61fe09e654514c4fc194966871e35fba0850f20d7`;
- unchanged evaluator CLI SHA-256:
  `347d3e4151d3f634710660b8c11bcce13724c66d33caafb5edbf86ebe2638030`;
- the same 12 nominal policy/checkpoint/fit matrices, moving commands
  x=.074/.077/.080, policies, fits, playground/model/scene/reference hashes,
  home-support reset, seed 167931544, and 600-tick horizon are frozen.

The frozen reset half-direction remains
`d=[1.1654748916625977,.11948448419570923,1.0919904708862305] m/s^2`.

## Frozen correction and branch operation

Change exactly one executable assignment inside the already-default-off map
guard:

```python
com_accelerometer_map_runner = read_com_accelerometer
```

The closure remains otherwise exact: accept current `state.data` and one
branch `body_ipos`, immutably replace only the nominal MJX model's
name-resolved `trunk_assembly` `body_ipos[2,0]`, call `mjx.forward`, and read
the name-resolved accelerometer. At each frozen tick 0/24/32/40 call NEG then
POS, discard both branch data objects, then perform the normal single policy
call and baseline step. The diagnostic branch never calls `mjx.step` or
advances time.

No `jax.disable_jit`, precision flag, device option, field reset, model copy,
endpoint order, tick, tolerance, or other evaluator change is allowed.

## Frozen default-off contract

Before formal cells, a committed CPU-only contract must:

- hash-lock the sources and one-line correction;
- prove all map work remains guarded by the nonempty default-off tick tuple;
- prove branch code contains `mjx.forward` and no branch time step;
- execute one complete 600-tick default-off A05_DIRECT_1003520/P30/x=.074 run;
- reproduce its prior trace field-for-field and byte-for-byte at SHA-256
  `e4a2452df4beaa703553bcb6b3f4e206d9e104258a48212ffe2d4f4541f1dd7c`;
- observe zero map fields and execute zero formal COM cells.

## Frozen replay, validity, and cells

Run exactly 12 matrices x three moving commands = 36 baseline runs. Each trace
has 600 ticks and four map rows, producing 144 cells. After removing only the
append-only map field, every baseline row must match its prior exact trace
field-for-field. Additionally:

- every selected nominal sensor equals row `obs_state[3:6]` exactly;
- all 36 tick-zero half-directions match frozen `d` within 1e-3 m/s^2 maximum
  absolute error;
- models differ only at `body_ipos[2,0]` by exact -.05/+ .05 m;
- all values are finite and execution is CPU-only.

Failure yields `INVALID_EAGER_MJX_ACCELEROMETER_REPLAY`; no cell class or
decision may be interpreted.

For each valid cell define `h=(a_pos-a_neg)/2`,
`r=(a_pos+a_neg)/2-a_nom`, `c=dot(h,d)/(norm(h)*norm(d))`,
`m=norm(h)/norm(d)`, and `q=norm(r)/norm(h)`. Classify in frozen order:

1. `WEAK_SIGNAL` if `norm(h)<.25*norm(d)`;
2. otherwise `NONLINEAR_CENTER` if `q>.25`;
3. otherwise `DIRECTION_ROTATED` if `c<.80`;
4. otherwise `FIXED_DIRECTION_COMPATIBLE`.

No p-value or confidence claim is authorized.

## Frozen persistence and decision

A tick is `FIXED_COMPATIBLE_TICK` only if at least 27/36 cells are compatible
and no other individual class exceeds 3/36.

1. All four ticks fixed-compatible:
   `SUPPORT_PREREGISTERED_FINE_GRAINED_COUPLING_MAP`.
2. Tick zero fixed-compatible and each mid-gait tick has at least 27 weak cells:
   `SUPPORT_PREREGISTERED_TEMPORAL_SENSOR_INFORMATION_STUDY`.
3. Tick zero fixed-compatible and any mid-gait tick has at least 18 combined
   rotated plus nonlinear-center cells:
   `SUPPORT_PREREGISTERED_MATCHED_SENSOR_ACTOR_RESPONSE_STUDY`.
4. Otherwise:
   `EAGER_MJX_ACCELEROMETER_MAP_UNRESOLVED_NO_FAMILY_SELECTED`.

These are the original exact-map thresholds with only the validated eager
diagnostic method substituted. No closest outcome is promoted.

## Authority boundary

This preregistration authorizes one contract and one corrected exact
36-run/144-cell CPU reporting replay. Baseline simulation steps and normal
policy calls are authorized solely to reproduce the frozen traces; COM
branches may call eager `mjx.forward` but never advance time. It authorizes no
actor counterfactual, training, retry, tolerance/tick/model change, Colab,
GPU/iGPU, R2/R3, policy/reward/model-family change, explicit COM input,
memory/estimator implementation, runtime design, RDK-X5, robot access,
deployment, torque, or motors.
