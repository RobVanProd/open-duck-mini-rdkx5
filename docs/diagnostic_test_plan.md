# Open Duck Mini Diagnostic Test Plan

Purpose: collect synchronized sim-to-real evidence before changing policy, gains, offsets, or training.

## General Rules

- Robot must be supported for any test that can move joints unless the test explicitly says grounded.
- Default movement amplitudes must be small.
- Logging must be off by default and enabled with an explicit flag such as `--log-telemetry`.
- Dry-run mode should build observations and run ONNX without sending servo writes where possible.
- Every log file should include the ONNX path, ONNX SHA256, runtime git commit if available, `duck_config.json` contents or hash, control frequency, action scale, and joint map.
- Prefer JSONL for full-vector telemetry. CSV is acceptable for reduced scalar summaries.

## Test Order

1. `home_pose_log_test`
2. `imu_tilt_test`
3. `joint_identity_test`
4. `suspended_policy_replay`
5. push test
6. `grounded_policy_replay`
7. `actuator_sine_sweep`

## home_pose_log_test

Goal: verify home pose, steady IMU channels, servo offsets, contact sensors, and tracking error.

Setup:

- Robot on stand or held safely.
- No policy walking commands.
- Torque enabled and moved to home pose.

Duration: 10 seconds.

Log:

- timestamp, dt, tick
- raw IMU gyro/accel
- policy observation vector
- commanded joint positions
- actual joint positions
- tracking error
- feet contacts
- battery/servo voltage if available
- servo bus read/write errors

Pass indicators:

- Actual joint positions settle near home.
- Tracking error is small and stable.
- Upright accel vector is stable and matches expected axis/sign.
- No repeated servo bus read failures that correlate with control damage.

## imu_tilt_test

Goal: map physical tilt to raw IMU and policy-space IMU indices.

Setup:

- Torque disabled or robot safely supported.
- No policy inference required.

Procedure:

- Hold upright for 3 seconds.
- Tilt nose forward, return upright.
- Tilt nose backward, return upright.
- Tilt left, return upright.
- Tilt right, return upright.

Log:

- raw accel/gyro
- any derived pitch/roll used only for diagnostics
- policy observation indices 0-5
- `imu_upside_down` config

Pass indicators:

- Direction changes are repeatable and documented.
- Upright values match the ONNX normalization mean scale closely enough to be plausible.

## joint_identity_test

Goal: prove policy action index, joint name, servo ID, sign, and physical movement direction.

Setup:

- Robot supported.
- Policy disabled.
- Start at home pose.

Procedure:

- For each joint index 0-13:
  - command `home + small_delta`, default `+0.03 rad`
  - hold 0.5 s
  - log actual movement
  - command `home - small_delta`
  - hold 0.5 s
  - return home

Log:

- joint index
- joint name
- servo ID
- commanded delta
- actual delta
- observed physical direction
- tracking error
- bus errors

Pass indicators:

- Correct servo moves for each index.
- Positive command direction is documented.
- No unexpected coupled or opposite-side motion.

## suspended_policy_replay

Goal: run `BEST_WALK_ONNX_2` with feet off ground to inspect policy actions and joint tracking without ground-contact instability.

Setup:

- Robot suspended or on a stand with feet free.
- Use normal runtime policy path.
- Start paused, then unpause only after logging has started.

Procedure:

- Use command x `0.0` first.
- Repeat with small command x, e.g. `0.08`, only if zero-command replay is safe.
- Stop after 10-20 seconds.

Log:

- full telemetry schema every tick
- ONNX action
- scaled action delta
- motor targets before and after rate limit
- actual joint positions
- tracking error
- phase
- commands

Pass indicators:

- Actions are bounded and periodic.
- Actual joints track targets without large lag or asymmetry.
- No bus error bursts. Isolated CRC/read retries are warnings unless they
  align with dt spikes, action jumps, post-startup tracking spikes, write
  failures, or visible twitching.

## grounded_policy_replay

Goal: capture the forward fall with enough data to separate policy behavior from hardware/sensor mismatch.

Setup:

- Clear floor area.
- Side-view camera, level with the robot.
- Manual stop ready.
- Start paused and logging before unpause.

Procedure:

- Run `BEST_WALK_ONNX_2` with a conservative command.
- Stop on fall, large lean, or manual stop.

Log:

- full telemetry schema every tick
- stop reason
- final 3-5 seconds before fall

Video:

- Side view.
- Include full body and feet.
- Useful visual checks: body pitches before stepping, feet slip backward, toes catch, ankles collapse, knees lag, side asymmetry.

## actuator_sine_sweep

Goal: measure actuator dynamics and tracking under small safe commands.

Setup:

- Robot supported.
- Policy disabled.

Procedure:

- Sweep one joint or mirrored pair at a time.
- Default amplitude `0.03-0.06 rad`.
- Frequencies: start `0.25 Hz`, then `0.5 Hz`, then `1.0 Hz` only if safe.
- Priority joints: hip pitch, knee, ankle pitch.

Log:

- target position
- actual position
- tracking error
- phase lag estimate
- voltage/current/load if available

Pass indicators:

- Similar response left vs right.
- No saturation, large lag, or bus error bursts.

## Required Artifacts From Robot

- `home_pose_log_test.jsonl`
- `imu_tilt_test.jsonl`
- `joint_identity_test_summary.md` or `.json`
- `suspended_policy_replay.jsonl`
- `grounded_policy_replay.jsonl`
- short side-view video of grounded failure
- live RDK-X5 `duck_config.json` snapshot
