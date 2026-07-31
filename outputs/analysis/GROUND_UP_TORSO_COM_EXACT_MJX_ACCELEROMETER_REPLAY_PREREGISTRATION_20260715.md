# Ground-Up Torso-COM Exact MJX Accelerometer-Replay Preregistration

status: `PREREGISTERED_READ_ONLY_CPU_EXACT_MJX_ACCELEROMETER_REPLAY`

## Evidence and correction

The native matched-state accelerometer map is invalid. Reconstructing from the
reporting-only saved `qpos/qvel/ctrl` subset misses the saved MJX actor
accelerometer by up to 7.427465 m/s^2 and misses the frozen tick-zero COM
direction by .173359 m/s^2, both beyond the frozen 1e-3 tolerance. Its apparent
cell classes have no authority.

The failure identifies a method requirement, not a physical outcome. A valid
matched map must branch the exact live MJX environment state used to construct
the actor observation, retaining solver, contact, observation-history, and
environment-info state. This study performs that correction without changing
the policy or baseline trajectory.

## Frozen sources

- invalid native-map result SHA-256:
  `68e88dc9d2cb32cadb85c7ae6a69cea499653b507c78474555183b835b7801df`;
- exact full-observation replay manifest SHA-256:
  `ac42abc8a940d97f0c0373ce624eaf2d2f803ac574e0de52c82303c7a759da07`;
- exact replay trace-manifest SHA-256:
  `7d7ccbe3b06e3a58546be5da02bdb138a218c08c11a0f10dea74a29d891c9f01`;
- pre-instrumentation `closed_loop_sim_eval.py` SHA-256:
  `e6182ad45c0409820ad8086694a5d12b9c7154ed70a47a836895dc61ab55fd90`;
- pre-instrumentation `evaluate_ground_up_policy.py` SHA-256:
  `b05f49e0692237aa6aff924d9fa41fe9ce06b46d806187597022ac52eb2a4d3a`;
- the same 12 nominal policy/checkpoint/fit matrices and moving commands
  x=.074/.077/.080, yielding the same 36 exact baseline runs;
- the same policies, fits, playground commit, scene, reference table,
  deterministic home-support reset, seed 167931544, and 600-tick horizon.

The frozen reset half-direction remains
`d=[1.1654748916625977,0.11948448419570923,1.0919904708862305] m/s^2`.
No reward is used for selection.

## Frozen append-only instrumentation

Add one default-off tuple to `ClosedLoopConfig` and a corresponding evaluator
CLI option naming accelerometer-map ticks. When empty, execution and trace
schema remain unchanged. When set to `[0,24,32,40]`, additional reporting
fields are recorded before the policy call at those ticks only.

At initialization derive two immutable MJX models from exact nominal
`env.mjx_model`: change only name-resolved `trunk_assembly`
`body_ipos[2,0]` by -.05 m for `COM_NEG` and +.05 m for `COM_POS`.

At each selected pre-policy state:

1. record exact current actor `obs_state[3:6]` as `a_nom`;
2. call `mujoco.mjx.forward(COM_NEG_model,state.data)` and read the
   name-resolved accelerometer as `a_neg`;
3. call `mujoco.mjx.forward(COM_POS_model,state.data)` and read it as `a_pos`;
4. discard both branch data objects without advancing time, changing `state`,
   or feeding either branch to the policy.

The normal policy call and baseline step then proceed once. New fields are
append-only and cannot affect action, recurrence, bridge, RNG, observation
history, reward, termination, or next baseline state.

## Frozen replay and validity

Run exactly 12 nominal matrices with three moving commands. Every new 600-row
baseline trace, after removing only new map fields, must reproduce its prior
exact full-observation trace field-for-field. Additionally:

- each selected `a_nom` equals row `obs_state[3:6]` exactly;
- each run has exactly four map rows at ticks 0/24/32/40;
- all 36 tick-zero `(a_pos-a_neg)/2` vectors match frozen `d` within 1e-3
  m/s^2 maximum absolute error;
- MJX models differ from nominal only at `body_ipos[2,0]` by exact offsets;
- all values are finite and CPU-only.

Failure yields `INVALID_EXACT_MJX_ACCELEROMETER_REPLAY`. No tolerance, tick,
state, engine, model, or trace substitution is allowed after outcomes.

## Frozen physical map and classes

For 36 runs x four ticks define `h=(a_pos-a_neg)/2`,
`r=(a_pos+a_neg)/2-a_nom`, `c=dot(h,d)/(norm(h)*norm(d))`,
`m=norm(h)/norm(d)`, and `q=norm(r)/norm(h)`.

Classify in fixed order:

1. `WEAK_SIGNAL` if `norm(h)<.25*norm(d)`;
2. otherwise `NONLINEAR_CENTER` if `q>.25`;
3. otherwise `DIRECTION_ROTATED` if `c<.80`;
4. otherwise `FIXED_DIRECTION_COMPATIBLE`.

No p-value or confidence claim is made.

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
   `EXACT_MJX_ACCELEROMETER_MAP_UNRESOLVED_NO_FAMILY_SELECTED`.

These are the same substantive thresholds as the invalid attempt; only the
state/engine method changes. No closest outcome is promoted.

## Contract and authority boundary

Before outcomes, a committed CPU-only contract must verify pre-instrumentation
hashes, inspect the patch as default-off and append-only, lock new evaluator
hashes, verify sources/cardinality/name-resolved body/sensor fields, and execute
a default-off regression proving trace schema and normalized behavior remain
unchanged. It may not read a formal COM branch cell.

This authorizes one contract and one exact 36-run/144-cell CPU MJX reporting
replay. Baseline replay steps are authorized; COM branches may call
`mjx.forward` but not advance time. No actor fork, training, retry, tolerance
change, Colab, GPU/iGPU, R2/R3, policy/reward/model-family change, explicit COM
input, memory/estimator implementation, runtime design, RDK-X5, robot access,
deployment, torque, or motors is authorized.
