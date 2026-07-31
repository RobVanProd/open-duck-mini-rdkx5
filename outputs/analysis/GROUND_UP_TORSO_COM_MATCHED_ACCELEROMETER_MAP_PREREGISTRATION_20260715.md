# Ground-Up Torso-COM Matched Accelerometer-Map Preregistration

status: `PREREGISTERED_READ_ONLY_CPU_MATCHED_ACCELEROMETER_MAP`

## Evidence question

The crossed signed-response study is valid but unresolved. Every checkpoint has
a distributed target-state/donor-response decomposition. Interaction is the
largest descriptive fraction for all six, but misses the frozen dominance
rule. That result must not be converted into a joint-phase selection.

One premise remains untested: the signed and crossed studies applied the one
accelerometer COM direction measured at deterministic reset to every mid-gait
state. Earlier full-observation evidence showed that this direction is cleanly
observable only at the reset transient under the frozen probes. Therefore the
fixed mid-gait input perturbation may not equal the instantaneous physical
accelerometer difference caused by torso COM at that state.

This study asks only whether the physical `COM_NEG` to `COM_POS` accelerometer
map at identical states remains strong, centered on nominal, and aligned with
the frozen reset direction through ticks 0/24/32/40. It changes no policy and
runs no action-response branch.

## Frozen sources

- crossed result JSON SHA-256:
  `9c0823c7fce7bd409acbc53176c412dc45863f9c9ebaa27fa00a4f4597984ef0`;
- signed result JSON SHA-256:
  `8c09ada8ce392c09fcee3cd9e7f449be5b1c50ca28b1640a4a3103755cc3b814`;
- exact replay manifest SHA-256:
  `ac42abc8a940d97f0c0373ce624eaf2d2f803ac574e0de52c82303c7a759da07`;
- signed evaluator SHA-256:
  `6e25285e9b12b8763aac0723e16c6d5ca63cac9e1956205fd44bdff714179b4d`;
- the same 36 nominal moving traces, model, scene, reference table, and
  measured fits frozen by the signed and crossed studies.

The reset half-direction remains exactly:

`d = [1.1654748916625977, 0.11948448419570923, 1.0919904708862305] m/s^2`.

No training reward is a source or selector.

## Frozen states and physical readback

Use the same 36 nominal moving traces and target ticks `[0,24,32,40]`, yielding
exactly 144 cells. At tick zero use the deterministic home-support reset state.
At later ticks use the same preceding-row `qpos`, `qvel`, and applied control
indexing already contracted by the signed study.

For each cell construct three native CPU MuJoCo models and data objects from the
identical state:

- `NOMINAL`: unchanged model;
- `COM_NEG`: change only name-resolved `trunk_assembly`
  `body_ipos[2,0]` by -.05 m;
- `COM_POS`: change only the same field by +.05 m.

Assign identical `qpos`, `qvel`, and control, then call `mj_forward` once in
each branch. Do not advance simulation time and do not apply a new policy
action. Read exactly the name-resolved three-dimensional MuJoCo
`accelerometer` sensor. The compiled sensor contract is address 6, dimension
3, attached to the unchanged `imu` site; name resolution remains authoritative.

Record `a_nom`, `a_neg`, and `a_pos`, then define:

- physical half-direction `h = (a_pos - a_neg) / 2`;
- center residual `r = (a_pos + a_neg) / 2 - a_nom`;
- direction cosine `c = dot(h,d)/(norm(h)*norm(d))`;
- magnitude ratio `m = norm(h)/norm(d)`;
- center ratio `q = norm(r)/norm(h)` when `norm(h)>0`.

All values are deterministic measurements. No p-value or independent-sample
claim is allowed.

## Frozen validity contract

Before formal cells, a committed zero-outcome CPU contract must verify all
source hashes, exact 36-trace/144-state indexing, sensor name/address/dimension,
body-2 X-only COM mutations, source-state schema, finite state arrays, and the
absence of GPU/iGPU providers.

The formal result is valid only if both hold for all applicable cells:

1. native nominal accelerometer readback matches saved `obs_state[3:6]` within
   1e-3 m/s^2 maximum absolute error across all 144 cells;
2. each of the 36 tick-zero physical half-directions matches frozen `d` within
   1e-3 m/s^2 maximum absolute error.

These tolerances are frozen before any COM sensor outcome. Failure yields
`INVALID_MATCHED_ACCELEROMETER_READBACK`; no tolerance change or partial result
is allowed.

## Frozen cell classes

Let `d_norm = norm(d)`.

1. `WEAK_SIGNAL` if `norm(h) < .25*d_norm`.
2. Otherwise `NONLINEAR_CENTER` if `q > .25`.
3. Otherwise `DIRECTION_ROTATED` if `c < .80`.
4. Otherwise `FIXED_DIRECTION_COMPATIBLE`.

The .25 magnitude floor, .25 center-ratio ceiling, and .80 cosine boundary are
frozen before outcomes. The ordering above is authoritative and makes the
classes mutually exclusive.

## Frozen persistence and decision

Summarize the 36 cells at each tick. A tick is `FIXED_COMPATIBLE_TICK` only if
at least 27/36 cells are `FIXED_DIRECTION_COMPATIBLE` and no other individual
class exceeds 3/36.

1. If all four ticks are `FIXED_COMPATIBLE_TICK`, decision
   `SUPPORT_PREREGISTERED_FINE_GRAINED_COUPLING_MAP`. The fixed direction is
   physically valid across these phases; only a further read-only coupling map
   may be preregistered.
2. If tick zero is fixed-compatible and each of ticks 24/32/40 has at least
   27/36 `WEAK_SIGNAL` cells, decision
   `SUPPORT_PREREGISTERED_TEMPORAL_SENSOR_INFORMATION_STUDY`. This supports
   only a read-only temporal-information study, not memory implementation.
3. If tick zero is fixed-compatible and at least one mid-gait tick has at least
   18/36 combined `DIRECTION_ROTATED` plus `NONLINEAR_CENTER` cells, decision
   `SUPPORT_PREREGISTERED_MATCHED_SENSOR_ACTOR_RESPONSE_STUDY`. This supports
   only a read-only actor fork using the actual per-state `a_neg/a_pos` values.
4. Otherwise decision `MATCHED_ACCELEROMETER_MAP_UNRESOLVED_NO_FAMILY_SELECTED`.

No closest tick, state, policy, fit, command, class, or threshold is promoted.
The result selects at most the named next preregistration and never a policy,
architecture, objective, estimator, memory mechanism, or training run.

## Authority boundary

This preregistration authorizes one zero-outcome contract and one exact
144-cell native CPU `mj_forward` sensor map. It authorizes no dynamic simulator
step, actor fork, outcome retry, tolerance change, new tick/state/trace, policy
or reward change, training, Colab, GPU/iGPU, R2/R3, explicit COM input, memory
or estimator implementation, runtime design, RDK-X5, robot access, deployment,
torque, or motors.
