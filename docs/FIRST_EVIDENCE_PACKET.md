# First Evidence Packet

Purpose: collect the first non-walking evidence needed to decide whether the Open Duck Mini's deployed observation contract matches the `BEST_WALK_ONNX_2` policy contract.

This packet is intentionally limited. It should answer:

- Does upright `obs[3:6]` match the ONNX policy's expected accelerometer orientation?
- Is gyro stable at home?
- Are joint tracking errors small at home?
- Are foot contacts plausible?
- Are bus errors present while stationary?
- Does physical tilt map to the expected accelerometer axes and signs?

## Safety Checklist

- No walking yet.
- No tuning yet.
- No grounded replay yet.
- Stop if home pose or IMU tilt fails.
- Do not change gains, offsets, IMU remaps, action scale, phase timing, or policy files.
- Robot must be physically supported for `home_pose_log_test`.
- Rob must be physically present before any moving diagnostic command is run.
- Keep fingers clear and be ready to cut power.

## Prerequisites

Workstation:

- This repository checked out.
- SSH key material available outside git:
  - `/home/lsd/robots/.duck_access/rdk_key`
  - `/home/lsd/robots/.duck_access/known_hosts`
- Python 3 available for local analysis.
- `tools/analyze_telemetry_obs.py` and `tools/snapshot_robot_config.py` available.

Robot:

- RDK-X5 reachable at `sunrise@192.168.1.50`.
- Runtime path: `/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5`.
- Python env: `/home/sunrise/duck_env/bin/python`.
- Policy path: `/home/sunrise/BEST_WALK_ONNX_2.onnx`.
- Diagnostics deployed to the board runtime before running hardware tests.
- Robot powered and physically safe for the selected test.

## Expected Robot Setup

- Battery/power stable.
- Robot supported for home pose logging.
- Feet can be manually lifted/touched for foot contact test.
- IMU tilt test can be performed by hand without stressing joints or cables.
- No walking policy unpause during this packet.

## Expected Workstation Setup

Create a packet directory:

```bash
mkdir -p outputs/first_evidence/$(date -u +%Y%m%dT%H%M%SZ)
```

Or use the helper:

```bash
bash scripts/collect_first_evidence.sh --dry-run
```

## Command Sequence

The recommended path is to use the helper:

```bash
bash scripts/collect_first_evidence.sh \
  --ssh sunrise@192.168.1.50 \
  --identity-file /home/lsd/robots/.duck_access/rdk_key \
  --known-hosts /home/lsd/robots/.duck_access/known_hosts
```

By default it prints the command plan and does not run moving tests.

When Rob is physically present and the robot is supported:

```bash
bash scripts/collect_first_evidence.sh \
  --ssh sunrise@192.168.1.50 \
  --identity-file /home/lsd/robots/.duck_access/rdk_key \
  --known-hosts /home/lsd/robots/.duck_access/known_hosts \
  --i-am-physically-present \
  --run-moving
```

The sequence is:

1. Read-only config snapshot.
2. Home pose log.
3. Copy home pose log back.
4. Analyze home pose log locally.
5. IMU tilt test.
6. Copy IMU tilt log back.
7. Analyze IMU tilt log locally.
8. Foot contact test.
9. Copy foot contact log back.
10. Generate `FIRST_EVIDENCE_SUMMARY.md`.

## Expected Output Files

Inside the first evidence output directory:

```text
*_rdkx5_config_snapshot.json
home_pose_log_test.jsonl
home_pose_analysis.md
imu_tilt_test.jsonl
imu_tilt_analysis.md
foot_contact_test.jsonl
foot_contact_summary.md
```

Generated summary:

```text
outputs/analysis/FIRST_EVIDENCE_SUMMARY.md
```

Raw JSONL files should usually stay outside git. Commit summaries only when they support a decision.

## What To Paste Back Into ChatGPT

Paste:

- `FIRST_EVIDENCE_SUMMARY.md`
- home pose analyzer warnings
- IMU tilt analyzer warnings
- foot contact summary
- any stop condition hit

Do not paste huge raw JSONL unless a specific excerpt is needed.

## Pass/Fail Gates

### Home Pose Pass

- `obs[0:3]` gyro near zero.
- `obs[3:6]` roughly `[small, small, +9.5]`.
- Joint tracking errors small and stable.
- Bus errors zero or very rare.
- Foot contacts plausible.

### Home Pose Fail

- Gravity appears on the wrong axis.
- `accel_z` is negative while upright.
- Large unexplained x/y accel bias while upright.
- Gyro is nonzero while stationary.
- Large home tracking error.
- Repeated bus errors while stationary.

### IMU Tilt Pass

- Nose forward/back changes one accelerometer axis with opposite signs.
- Left/right tilt changes a different axis with opposite signs.
- Returning upright returns accel near the original upright value.

### IMU Tilt Fail

- Forward/back tilt appears swapped.
- Roll and pitch axes are swapped.
- An axis is inverted relative to physical motion.
- Upright accel is not close to the ONNX expected orientation.

### Foot Contact Pass

- Left foot down/up maps to left contact true/false.
- Right foot down/up maps to right contact true/false.
- Contacts are not swapped or inverted.

## Stop Conditions

Stop and do not run later gates if:

- Home pose fails.
- IMU tilt fails.
- Foot contact polarity is wrong.
- The robot moves unexpectedly.
- Bus errors repeat while stationary.
- The robot is not physically supported for a moving test.
