# Open Duck Mini RDK-X5 Sim-To-Real Bridge

## Mission

Turn this repository into a safe, repeatable sim-to-real diagnostic and bridging pipeline for the Open Duck Mini running `BEST_WALK_ONNX_2` on the RDK-X5.

The project is not trying to train a new policy yet. The current mission is to prove the deployed robot's sensor observations, policy actions, joint commands, and real joint movement match the policy and simulation contract closely enough to rerun the known baseline responsibly.

## Current Robot Status

- Robot is mostly assembled.
- Battery is in the intended location.
- Missing only a thin PLA top/back shell piece.
- IMU is configured.
- Robot can hold home pose.
- Robot can hold static balance.
- The board policy hash matches the audited `BEST_WALK_ONNX_2.onnx`.
- The live RDK-X5 config snapshot is in `evidence/20260621T180046Z_rdkx5_config_snapshot.json`.
- The board runtime is an RDK-X5 fork captured under `runtime/`.

## Current Failure

`BEST_WALK_ONNX_2` leans the robot forward and the robot falls during walking.

The key unresolved question is whether this is policy behavior or whether the deployed robot is feeding/receiving data that differs from the sim and policy contract.

## Known Policy Contract

Policy file:

```text
policy/BEST_WALK_ONNX_2.onnx
```

Policy hash:

```text
3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067
```

ONNX I/O:

```text
input:  obs, shape [1, 101], float32
output: continuous_actions, shape [1, 14], float32
```

Observation vector:

| Range | Meaning |
| ---: | --- |
| `0:3` | raw gyro |
| `3:6` | raw accelerometer |
| `6:13` | commands |
| `13:27` | joint position error |
| `27:41` | joint velocity scaled by `0.05` |
| `41:83` | action history |
| `83:97` | previous motor targets |
| `97:99` | foot contacts |
| `99:101` | gait phase |

Action vector:

```text
target_rad[i] = home_rad[i] + action[i] * 0.25
```

Runtime then applies rate limiting before sending servo targets.

## Current Root-Cause Ranking

1. IMU accelerometer frame or offset mismatch.
2. Live joint offset or home pose mismatch.
3. Joint physical direction mismatch.
4. Servo bus feedback/read reliability.
5. Gait phase timing mismatch.
6. Actuator tracking under load.
7. Contact/friction and TPU effects, only after the above are ruled out.

## Definition Of Done

The sim-to-real bridge is done when:

- The live board config, policy hash, runtime path, and package versions are captured and reproducible.
- Home pose telemetry shows stable gyro, upright accelerometer, small joint tracking errors, plausible foot contacts, and low bus errors.
- IMU tilt telemetry maps physical nose-forward/back and left/right tilt to the expected accelerometer axes and signs.
- Foot contact telemetry proves left/right polarity.
- Joint identity testing proves policy index, joint name, servo ID, physical joint, command sign, and measured response.
- Suspended policy replay shows bounded actions, reasonable tracking, no bus-error bursts, and no obvious forward-biased posture in the air.
- Grounded replay is attempted only after the above gates pass.
- Any fix is a minimal reviewed patch tied to a specific failed gate.
- `BEST_WALK_ONNX_2` is rerun after each minimal fix before training new policy variants.

## Non-Goals For Now

- No retraining.
- No gain tuning.
- No joint offset edits.
- No IMU remap edits.
- No action-scale edits.
- No phase-timing edits.
- No friction/contact tuning before observation/action/joint truth tables pass.
