# Policy / Sim Contract Reconciliation

Last updated: 2026-06-21

## Executive Summary

`BEST_WALK_ONNX_2` requires:

```text
observation: [1, 101]
action:      [1, 14]
```

The local `../Open_Duck_Playground` initially looked like a `10` actuator
no-head environment because `constants.py` contains `JOINTS_ORDER_NO_HEAD`.
That was an incomplete static check.

When the environment is instantiated with the project Python environment:

```text
../envs/open-duck-playground/bin/python
```

the local `Joystick(flat_terrain)` environment matches the deployed policy
contract:

```text
state observation: 101
action size:       14
MJCF nu:           14
home ctrl length:  14
actuator order:    matches runtime / policy order
JAX backend:       gpu
JAX device:        rocm:0
```

So the previous `HOLD_POLICY_SIM_CONTRACT_MISMATCH` is resolved. The current
hold is:

```text
HOLD_SIM_INTEGRATION_PENDING
```

Meaning: the correct sim contract exists, but the closed-loop JAX/MJX policy
eval path with the fitted actuator bridge still needs to be wired.

Telemetry replay bridge reproduction remains useful, but it is not a substitute
for the full policy-in-sim loop.

## Known Deployed Policy / Runtime Contract

Observation:

| obs slice | meaning |
|---|---|
| `0:3` | raw gyro |
| `3:6` | raw accelerometer |
| `6:13` | command vector |
| `13:27` | joint position error |
| `27:41` | joint velocity scaled |
| `41:83` | action history |
| `83:97` | previous motor targets |
| `97:99` | foot contacts |
| `99:101` | gait phase |

Action order:

| index | joint |
|---:|---|
| 0 | `left_hip_yaw` |
| 1 | `left_hip_roll` |
| 2 | `left_hip_pitch` |
| 3 | `left_knee` |
| 4 | `left_ankle` |
| 5 | `neck_pitch` |
| 6 | `head_pitch` |
| 7 | `head_yaw` |
| 8 | `head_roll` |
| 9 | `right_hip_yaw` |
| 10 | `right_hip_roll` |
| 11 | `right_hip_pitch` |
| 12 | `right_knee` |
| 13 | `right_ankle` |

## Local Playground Contract

Audited with:

```bash
python3 tools/audit_policy_sim_contract.py \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --output-md outputs/analysis/POLICY_SIM_CONTRACT_AUDIT.md \
  --output-json outputs/analysis/policy_sim_contract_audit.json
```

Result:

```text
assessment_status: PASS_POLICY_SIM_CONTRACT
```

Instantiated environment:

```text
env:                playground.open_duck_mini_v2.joystick.Joystick(flat_terrain)
action_size:        14
observation state:  101
privileged state:   212
MJCF nu/nq/nv:      14 / 21 / 20
home ctrl len:      14
ctrl_dt:            0.02
sim_dt:             0.002
action_scale:       0.25
max_motor_velocity: 5.24
action delay:       0-3 env steps
IMU delay:          0-3 env steps
```

Actuator names:

```text
left_hip_yaw
left_hip_roll
left_hip_pitch
left_knee
left_ankle
neck_pitch
head_pitch
head_yaw
head_roll
right_hip_yaw
right_hip_roll
right_hip_pitch
right_knee
right_ankle
```

Static MJCF scan:

```text
open_duck_mini_v2.xml:           14 actuators
open_duck_mini_v2_backlash.xml:  14 actuators
scene_flat_terrain.xml:          14 actuators, home ctrl len 14
scene_flat_terrain_backlash.xml: 14 actuators, home ctrl len 14
scene_rough_terrain_backlash.xml:14 actuators, home ctrl len 14
```

## Mismatch Table

| field | runtime / policy | local sim | status |
|---|---|---|---|
| observation length | `101` | `101` | `PASS` |
| action length | `14` | `14` | `PASS` |
| action order | runtime order | same instantiated actuator order | `PASS` |
| head/neck presence | present | present | `PASS` |
| command vector | `7` values | `7` values | `PASS` |
| IMU representation | raw gyro + accel | raw gyro + accel | `PASS` |
| foot contacts | `2` values | `2` values | `PASS` |
| phase | `2` values | `2` values | `PASS` |
| action delay | measured lag needs bridge | training config `0-3` | `WARN` |
| actuator model | measured delay/velocity limit needed | optimistic position target model | `WARN` |

## Candidate Resolution Paths

1. **Use the instantiated local 14-action Playground env.**
   This is the recommended path. The original concern came from the
   `JOINTS_ORDER_NO_HEAD` constant, but the actual env/MJCF contract is 14
   actions and 101 observations.

2. Restore an archived 14-actuator env only if closed-loop eval reveals hidden
   drift from the deployed policy contract.

3. Build a compatibility eval env only if the existing `Joystick` env cannot
   support the fitted actuator bridge without invasive changes.

4. Train a 10-actuator no-head policy only if the project intentionally changes
   robot/policy target. That would not be a `BEST_WALK_ONNX_2` compatibility
   path.

## Recommendation

Proceed to a full closed-loop sim actuator bridge eval using:

```text
../Open_Duck_Playground
../envs/open-duck-playground/bin/python
```

Do not train yet. The next PR should wire the fitted actuator bridge into the
JAX/MJX eval path and test current `BEST_WALK_ONNX_2` with and without the
bridge.
