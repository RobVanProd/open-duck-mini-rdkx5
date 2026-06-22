# Policy / Sim Contract Reconciliation

## Executive Summary

- `BEST_WALK_ONNX_2` requires `obs[1,101] -> continuous_actions[1,14]`.
- The local `../Open_Duck_Playground` `Joystick(flat_terrain)` env matches the 101-observation / 14-action contract when instantiated with the `envs/open-duck-playground` Python environment.
- Telemetry replay bridge reproduction is useful, but it is not a replacement for the full policy/sim loop.

assessment_status: `PASS_POLICY_SIM_CONTRACT`
recommended_next: `run full actuator bridge policy-loop eval`

## Known Deployed Policy / Runtime Contract

- policy_path: `/home/lsd/robots/open-duck-mini-rdkx5/policy/BEST_WALK_ONNX_2.onnx`
- policy_sha256: `3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067`
- observation: `[1, 101]`
- action: `[1, 14]`

| obs slice | meaning |
|---|---|
| `0:3` | gyro |
| `3:6` | accel |
| `6:13` | command |
| `13:27` | joint_position_error |
| `27:41` | joint_velocity_scaled |
| `41:83` | action_history |
| `83:97` | previous_motor_targets |
| `97:99` | foot_contacts |
| `99:101` | phase |

| action index | joint |
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

- playground_path: `/home/lsd/robots/Open_Duck_Playground`
- env_python: `/home/lsd/robots/envs/open-duck-playground/bin/python`
- env_status: `PASS_ENV_INSTANTIATED`
- jax_backend: `gpu`
- jax_devices: `['rocm:0']`
- action_size: `14`
- observation_size: `{'privileged_state': [212], 'state': [101]}`
- MJCF nu/nq/nv: `14/21/20`
- keyframe home ctrl len: `14`
- control dt / sim dt: `0.02` / `0.002`
- action_scale: `0.25`
- max_motor_velocity: `5.24`
- action delay config: `0-3`
- imu delay config: `0-3`

### Actuator Names

- `0` `left_hip_yaw`
- `1` `left_hip_roll`
- `2` `left_hip_pitch`
- `3` `left_knee`
- `4` `left_ankle`
- `5` `neck_pitch`
- `6` `head_pitch`
- `7` `head_yaw`
- `8` `head_roll`
- `9` `right_hip_yaw`
- `10` `right_hip_roll`
- `11` `right_hip_pitch`
- `12` `right_knee`
- `13` `right_ankle`

### Static XML Candidates

| xml | nu_static | keyframe ctrl lens |
|---|---:|---|
| `/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/joints_properties.xml` | 0 | `[]` |
| `/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/open_duck_mini_v2.xml` | 14 | `[]` |
| `/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/open_duck_mini_v2_backlash.xml` | 14 | `[]` |
| `/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_flat_terrain.xml` | 14 | `[14]` |
| `/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml` | 14 | `[14]` |
| `/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_rough_terrain_backlash.xml` | 14 | `[14]` |
| `/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/sensors.xml` | 0 | `[]` |

## Mismatch Table

| field | runtime / policy | local sim | status |
|---|---|---|---|
| obs length | 101 | 101 | `PASS` |
| action length | 14 | 14 | `PASS` |
| action order | left_hip_yaw, left_hip_roll, left_hip_pitch, left_knee, left_ankle, neck_pitch, head_pitch, head_yaw, head_roll, right_hip_yaw, right_hip_roll, right_hip_pitch, right_knee, right_ankle | left_hip_yaw, left_hip_roll, left_hip_pitch, left_knee, left_ankle, neck_pitch, head_pitch, head_yaw, head_roll, right_hip_yaw, right_hip_roll, right_hip_pitch, right_knee, right_ankle | `PASS` |
| head/neck presence | neck_pitch, head_pitch, head_yaw, head_roll present | True | `PASS` |
| command vector | 7 values obs[6:13] | 7 values from joystick.py command | `PASS` |
| IMU representation | raw gyro + accelerometer | raw gyro + accelerometer in _get_obs | `PASS` |
| contact representation | 2 foot contacts obs[97:99] | 2 contacts in _get_obs | `PASS` |
| phase | 2 values obs[99:101] | imitation_phase 2 values | `PASS` |
| action delay | runtime telemetry measured 3-4 tick lag; training prior 0-3 | 0-3 | `WARN` |
| actuator model | real bridge delay/lag/velocity limit needed | max_motor_velocity=5.24 | `WARN` |

## Candidate Resolution Paths

1. **Use the instantiated local 14-action Playground env.**
   This is currently the recommended path because the env instantiated with 101 state observations, 14 actions, matching actuator order, and ROCm JAX visibility.
2. Restore an archived 14-actuator env only if later eval reveals hidden drift.
3. Build a compatibility eval env only if the local 14-action env cannot run the full policy-loop bridge.
4. Train a 10-actuator no-head policy only as an explicit new robot target, not as a BEST_WALK_ONNX_2-compatible fix.

## Recommendation

Proceed to the full policy-loop actuator bridge eval using `../Open_Duck_Playground` under `../envs/open-duck-playground/bin/python`. Do not train yet.
