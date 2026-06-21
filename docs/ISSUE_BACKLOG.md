# Issue Backlog

This backlog is ordered around evidence gates. Do not skip ahead to tuning.

## P0: First Evidence Gates

### Keep Docs And Repo State Current

- Update README current next step when the active gate changes.
- Update evidence manifests when snapshots or summaries are added.
- Update root-cause ranking after analysis.
- Keep `docs/ROBOTICIST_PLAYBOOK.md` and `AGENTS.md` aligned with the actual workflow.

### Run Config Snapshot

- Capture live `duck_config.json`.
- Confirm `imu_upside_down`.
- Confirm policy hash.
- Confirm runtime path and package versions.
- Confirm IMU calibration file presence or absence.

### Run Home Pose Log

- Hold home pose for 10 seconds.
- Log raw observation, IMU, joint state, motor targets, foot contacts, and bus counters.
- Do not walk.

### Analyze Home Pose `obs[0:6]`

- Compute mean/std/min/max for gyro and accel.
- Compare accel z-scores against ONNX normalization.
- Check stationary gyro bias.
- Check joint tracking p50/p95/p99.
- Check bus errors and contact state.

### Run IMU Tilt Test

- Log upright, nose forward, upright, nose backward, upright, left tilt, upright, right tilt.
- Do not move joints.

### Analyze IMU Axis/Sign Mapping

- Map physical tilt to accelerometer axis and sign.
- Decide whether `imu_upside_down=true` is supported by evidence.
- Stop if axes are swapped or inverted.

### Run Foot Contact Test

- Verify left/right mapping.
- Verify polarity.
- Confirm contact values enter policy indices `97:99`.

### Run Joint Identity Test

- Supported robot only.
- Move each joint by small positive/negative delta.
- Record servo ID, actual delta, tracking error, and visual direction.

### Run Suspended Replay `x=0.0`

- Suspended robot only.
- Start paused.
- Log full telemetry.
- Stop on saturation, asymmetry, bus burst, or forward-biased posture.

## P1: Decision Report

### Analyze Suspended Replay

- Action mean/std/min/max.
- Action saturation percentage.
- Target-vs-actual tracking p50/p95/p99.
- dt jitter.
- Bus errors.
- Phase values.
- Forward-bias assessment.

### Capture Servo Bus Warning Evidence

- Capture terminal logs beside suspended replay JSONL.
- Count CRC/read/write/control-budget warnings.
- Correlate timing spikes with tracking spikes.
- Hold `x=0.08` replay until `x=0.0` has a clean gate summary.

### Create `SIM2REAL_RESULTS_SUMMARY.md`

- Summarize completed gates.
- Rank root causes.
- Choose one next action with evidence.

### Decide First Minimal Patch

Choose exactly one:

- IMU remap/offset fix.
- Joint offset/calibration fix.
- Joint mapping/sign fix.
- Servo bus reliability fix.
- More evidence collection.

## P2: Later Bridge Work

### Grounded Replay With Video

- Only after P0 gates pass.
- Capture synchronized JSONL and side-view video.
- Stop on fall or large lean.

### Actuator Sine Sweep

- Supported robot only.
- Measure tracking and phase lag for hip pitch, knee, and ankle pitch.

### Contact/Friction Prior

- Only after sensor/action/joint gates pass.
- Use grounded evidence to reason about TPU/contact/friction.

### Training Config Bridge

- Only after measured sim-to-real gaps are known.
- Update sim/training assumptions from evidence, not guesses.
