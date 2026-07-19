# Winner-v2 Policy-to-RDK-X5 Runtime Handoff

Status: `BLOCKED`

Disposition: `REQUIRES_REVIEWED_115_RUNTIME_V2`

Robot clearance: `false`

This package answers `Comms.md` from the native-runtime branch
`agent/measurement-contract-evidence` at reviewed commit
`a6f62b25b5960987e3955bd327ac95ddbf25a336`. It is an offline, CPU-only
interface handoff. It does not authorize Gate 5, deployment, the robot, the
RDK-X5, any GPU/iGPU, hosted compute, or training.

## Disposition and candidate identity

The protected winner is not compatible with the frozen
`open-duck-mini.best-walk.101x14.v1` runtime contract. Both persistent policy
graphs have these mandatory static float32 inputs and outputs:

```text
inputs:
  obs                 [1,115]
  previous_action     [1,14]
outputs:
  continuous_actions  [1,14]
  previous_action_out [1,14]
```

The repository evidence requires both checkpoints to persist through the
matrix. It does not select one checkpoint as the deployment binary. Choosing
half or final after seeing the outcomes would be a new selection decision, so
`SELECTED_ONNX_SHA256` remains `NOT_READY`. The two protected candidates are:

| checkpoint | file | bytes | SHA-256 |
|---:|---|---:|---|
| 512000 | `policies/T2_EQUAL_512000.onnx` | 906951 | `99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de` |
| 1024000 | `policies/T2_EQUAL_1024000.onnx` | 906951 | `0dfc24bde5d839e4d346dd8c08d9a7d0222a3847764ec6738bfc7f8d947f4ece` |

Both are ONNX IR 10, default-domain opset 12, producer
`open-duck-playground-ground-up`, with 40 nodes and 24 initializers. The
machine-readable readback is in `policy_contract.json`.

The package supersedes no prior policy evidence. It confirms the previously
pinned identities:

- winner-v2 runtime-contract MD SHA-256
  `2c0e3f963fb6cb55457d5928a699b8741ebb6b36bf1aa628944d211c99bff18c`;
- observer cross-fit MD SHA-256
  `42282815986035105a5ab4f29b1d76ac082142ff096e46a8ffcf260f99362102`;
- P30 observer pin MD SHA-256
  `1c320276f8ea6343a1059f9ec7eda670b596f13141c49a0f7ae69af84ba15c85`.

The exact package commit is intentionally reported in the relay response. A
commit cannot embed its own final identity without changing that identity.
`manifest.json` instead pins the evidence base plus every package and external
artifact by SHA-256.

## Clearance and robustness scope

The composite G1/T2 policy family is the first persistent nominal winner. With
the actual-centered guard, x=0 deadband, hard-vector projection, conservative
left-ankle repair, and pinned P30 observer, it passes the frozen nominal/R1
matrix at both persistent checkpoints and both measured actuator fits. The P30
observer cross-fit is 32/32 cells, worst tracking p95
`0.1831700384616852 rad`, minimum moving mean vx
`0.08408497237367556 m/s`, zero measured rate excess, and zero envelope excess.

The sequential R2 matrix did not finish or pass every required condition. It
passed conditions 1–6 (floor friction low/high, joint friction loss low/high,
armature low/high), then stopped at the first failure, corrected
`TORSO_COM_X_NEG`, condition 7. Later signed COM studies also failed at the
positive endpoint. Those failures are not erased by nominal success.

The current robot-readiness decision is
`HOLD_REAL_BUILD_COM_INPUTS_INCOMPLETE`: the build-specific torso COM/inertia
calculator has 46 missing required fields and therefore makes no numerical COM
estimate. The allowed measured build-to-sim torso X-COM interval after frozen
margin is `[-0.021875, +0.0046875] m`; membership is unknown. Consequently
`robot_clearance` is `false`.

Exact blockers:

1. No single deployment checkpoint is selected; both graphs are persistence
   evidence.
2. The reviewed native runtime implements the frozen 101-D v1 contract, not
   this stateful 115-D v2 interface.
3. The real-build torso COM/inertia audit is incomplete, so the policy
   repository does not clear the robot.

## Observation contract

`observation_map.json` is authoritative for every scalar, including exact
per-checkpoint `obs_mean` and `obs_std` initializers. Normalization occurs
inside each ONNX graph:

```text
obs_normalized = (obs - obs_mean) / obs_std
```

The host must provide raw float32 values. It must not normalize them again.

| slice | field | units and tick semantics |
|---|---|---|
| `0:3` | torso-site local gyro xyz | rad/s, current tick |
| `3:6` | torso-site local accelerometer xyz | m/s² specific force, current tick |
| `6:13` | vx, vy, yaw rate, neck pitch, head pitch/yaw/roll | m/s, m/s, rad/s, rad; current command |
| `13:27` | logical joint position minus home | rad, current sample, 14-joint order |
| `27:41` | logical joint velocity × 0.05 | rad/s × 0.05 s, current sample |
| `41:55` | final action t−1 | normalized action |
| `55:69` | final action t−2 | normalized action |
| `69:83` | final action t−3 | normalized action |
| `83:97` | bridge-realized target from preceding transition | absolute logical rad |
| `97:99` | left/right contact | float32 1=contact, 0=no contact |
| `99:101` | current gait phase | `[cos,sin]` |
| `101:115` | projected reference action | normalized action for current command/current phase |

Training `obs[83:97]` is exactly
`info['ground_up_actuator_bridge_applied_targets']`, updated by
`Joystick._apply_ground_up_measured_actuator_bridge` before simulated physics
and read by `_get_obs` after that transition. Therefore observation tick `t`
contains the target realized by transition `t-1`. It is not the post-slew
commanded target and not the measured current joint position. On hardware it
must be reproduced by the pinned P30 forward observer.

The extra 14 elements are `obs[101:115]`, a projected reference action looked
up from the frozen `240 × 27 × 14` table using current forward/lateral/yaw
command and current phase. It is zero when `norm(command[0:3]) <= 0.01`.

No actor input is privileged. IMU, joint state, and foot contacts are direct
runtime inputs. Command, action histories, phase, reference action, and P30
state are host-maintained. The P30 realized target is not directly measured by
an X5 sensor. All required direct samples must be fresh and from one tick; no
mixed-age or silently reused observation is allowed.

The formal simulator input has noise disabled. Training noise at configured
level 1 was gyro ±0.1 rad/s, accelerometer ±0.05 m/s², position noise by joint
class (hips ±0.03, knees ±0.05, ankles ±0.08 rad), and joint velocity
±2.5 rad/s before the 0.05 scale. The actor gyro/accelerometer path has no
explicit delay. The IMU history in the training source delays gravity for the
privileged path, not the actor's six IMU values.

The simulator accelerometer is a MuJoCo site sensor in its local frame and
reports specific force, so a stationary sensor contains gravitational
response. Tick 0 also contains the deterministic reset/forward settling
transient shown in the golden pack. Hardware must use the reviewed BNO055 frame
and sign mapping; numerical similarity at reset is not a calibration proof.

## Stateful inference, phase, and reset

`previous_action` is float32 `[1,14]` in normalized action units and the same
joint order as the output. Initialize it to exact zeros. At tick `t`:

1. assemble `obs[t]` using current phase and the observer value from the
   preceding transition;
2. infer with `previous_action[t]`;
3. accept `continuous_actions[t]` as the final normalized action;
4. store `previous_action_out[t]` as `previous_action[t+1]`;
5. convert/send the logical target;
6. advance the P30 observer once after a confirmed send;
7. advance phase once for the next observation.

The graph proves `previous_action_out == continuous_actions` for every packaged
row. Do not substitute a pre-guard or pre-deadband action into recurrent state.

Phase period is 27 ticks:

```text
phase(index) = [cos(2*pi*index/27), sin(2*pi*index/27)]
```

Deterministic home reset starts at index 0, so ONNX sees `[1,0]` at tick 0 and
phase index 1 at tick 1. The correct ordering is observe-then-advance. This
matches the current native runtime order. An advanced-first substitution
diverges at tick 0 for moving traces; the exact errors are recorded in
`golden_evidence.json`.

Supported commands are stand at exactly x=0 and forward x in
`[0.074,0.080] m/s`, with all remaining command values exactly zero. The frozen
matrix explicitly includes x=.074, .077, and .080. Unsupported commands must be
rejected, not clipped. The graph deadband reads raw `obs[6]`; when
`abs(x) <= 0.009999999776482582`, it produces bit-exact zero action and
bit-exact zero recurrent state. Both x=0 traces contain 600 exact-zero output
ticks.

The passing reset is `home-support`: MuJoCo qpos is the exact 31-vector in
`policy_contract.json`, qvel is 30 zeros, control/observer target is `HOME_RAD`,
contacts are `[1,1]`, action histories and recurrent state are zeros, and phase
index is zero. Control dt is 0.02 s; physics dt is 0.002 s with 10 substeps.

## Action and actuator-transition contract

The ONNX output is already the final normalized absolute home-offset action,
not a residual that the host should add. Reference/residual composition is
inside the graph:

```text
logical_target_rad[i] = HOME_RAD[i] + continuous_actions[i] * 0.25
```

The graph also contains, in this order:

1. per-joint stateful hard-vector clamp relative to `previous_action`;
2. actual-centered ±0.20 rad guard on pitch-chain joints using raw
   `obs[13:27] + HOME_RAD`;
3. x=0 deadband selecting zero for both output tensors.

The final conservative per-joint measured rate vector is:

```text
[5.24, 5.24, 1.50, 1.50, 1.50, 5.24, 5.24,
 5.24, 5.24, 5.24, 5.24, 1.25, 1.00, 1.25] rad/s
```

The left-ankle repair is graph initializer `max_action_delta[0,4] =
0.11999999731779099` normalized action/tick, which is 1.50 rad/s at scale 0.25
and dt 0.02. It replaced the prior 1.75 rad/s constant.

The final graph is authoritative. The inherited runtime 5.24 rad/s limiter is
redundant and measured as an exact no-op across all 2400 packaged ticks. It may
remain only behind a runtime assertion that it changes no target; a nonzero
change is a contract failure. Do not add a filter, second measured-vector
projection, gain, or clip. Head overlay is forbidden; all head commands are
zero and the graph produces its own head-chain outputs.

The P30 bridge is not in ONNX. `observer/winner_v2_contract.py` is the exact
CPU implementation. For each joint:

```text
queue.append(sent_target)
retain delay_ticks + 1 values
delayed = queue[0]
alpha = 1 - exp(-0.02 / tau)                 # when tau > 0
desired = previous + alpha*(delayed-previous) # else desired=delayed
step = clip(desired-previous, ±velocity_limit*0.02)
value = previous + step
```

The output is a forward estimate of the simulated realized absolute logical
position target, not a new command and not current measured position. It
consumes the confirmed logical sent target only. Initialize value and every
delay queue from home. Advance exactly once after each confirmed 20 ms send so
the result becomes next tick's `obs[83:97]`.

If a required sensor is stale, a send fails, timing is not one 20 ms tick, or
observer update count is ambiguous, invalidate the policy loop. Do not reuse,
skip, double-step, or silently repair observer state. Resume requires a
separately defined safe reset; this handoff does not authorize a motor reset.

The P30 fit is from the P30 fixed-target telemetry after ten startup ticks,
selected by p95 absolute error. Its per-joint fit statistics are in
`observer_contract.json`. The frozen P30 observer was then tested on both the
P30 and independently measured P31/34 simulated plant fits: 32/32 cells pass,
with maximum observer/plant separation 0.004135804 rad. Across this package's
2400 P30 rows, host observer and simulated bridge outputs agree exactly.

## Golden and trace pack

For each checkpoint and command x=0/.080:

- `golden/T2_EQUAL_<step>_x<command>.npz` contains every tick and every
  semantic tensor required to build a field-by-field runtime verifier;
- `golden/full_traces/*.jsonl.gz` is a deterministic, lossless archive of the
  full 600-tick CPU simulator trace;
- `compact_golden_vectors.json` contains adjacent ticks 0–4 in text form.

The NPZ fields distinguish raw graph action, rate-bounded action, guarded
action, final action, incoming/outgoing recurrent state, pre-runtime target,
sent target, bridge-applied target, observer result, actual joint position,
phase before/after, raw/normalized command, saturation, tracking, and rate
excess. `golden_evidence.json` records source hashes and measured errors.

The fresh full-observation traces reproduce the pre-existing frozen P30 traces
at zero error for all 600 rows in action, sent target, applied target, actual
position, and `obs[0:6]`. Local ONNX output matches the frozen trace exactly.
The independent CPU JAX replay of the final graph from its ONNX initializers is
within `1e-6`; it is explicitly not represented as an Orbax checkpoint-restore
comparison. Runtime ONNX golden tolerance is `1e-6`; x=0 output and recurrent
state must remain bit-exact zero.

For x=.080, replacing `obs[83:97]` with the legacy commanded target first
changes policy output at tick 1. For moving traces, advancing phase/reference
before observation first changes output at tick 0. Exact checkpoint-specific
errors are in `golden_evidence.json`. Correct current-phase ordering does not
diverge from the policy contract.

Generate and inspect on CPU:

```bash
python tools/generate_winner_v2_runtime_handoff_traces.py \
  --recreate --output-root /tmp

CUDA_VISIBLE_DEVICES='' JAX_PLATFORMS=cpu \
  python tools/build_winner_v2_runtime_handoff.py --trace-root /tmp

CUDA_VISIBLE_DEVICES='' \
  python artifacts/runtime_handoff/rdkx5_native_20260719/inspect_and_smoke.py
```

The builder only packages already generated traces. The simulation generation
contract is pinned in `golden_evidence.json`: control commit
`b9be205ac64488c23504ca42e5ec790337adeec3`, frozen patch stack, CPU backend,
seed 167931544, P30 fit, 600 ticks, `home-support`, no noise, no action delay,
current-phase observation, and the exact reference table. No training reward is
used for selection.

## Runtime review boundary

The native-runtime agent can use this package to specify and review a versioned
115-D v2 interface. A passing CPU verifier will establish tensor/semantic
compatibility only. It will not select a deployment checkpoint, complete the
real-build COM audit, change Gate 5 from `NOT_RUN`, or clear the robot.
