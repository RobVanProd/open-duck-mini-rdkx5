# Grounded Rate165 Gate-1 Analyzer Audit

Date: 2026-07-11

Status: `PASS_OFFLINE_ANALYZER_READY; CURRENT_GATE1_NOT_RUN`

## Finding

`tools/analyze_suspended_replay.py` is a dynamic 50 Hz policy-loop analyzer.
Applying it to a home-pose diagnostic trace produced a false hold because the
stationary diagnostic intentionally ran near 20 Hz. Weakening the dynamic
cadence gate would erase useful policy-replay protection.

`tools/evaluate_supported_home_telemetry.py` now implements a separate,
stationary contract:

- discard 25 startup samples;
- require at least 50 post-startup samples;
- pitch-chain tracking p95 strictly below `0.08 rad`;
- hold on 3 consecutive pitch-chain samples above `0.10 rad`;
- gyro absolute p95 strictly below `0.20 rad/s`;
- require positive-Z-dominant upright acceleration;
- require zero final bus read/write counters;
- require a terminal log and hold on write errors, control-budget overruns, or
  exceptions.

It deliberately reports `REQUIRES_OPERATOR_VISUAL_CONFIRMATION` even when the
telemetry component passes. Compensated readback cannot prove mechanical pose.

## Historical Regression

Input:

```text
outputs/first_evidence/20260627T003945Z_physical_start_pose_gate/
  home_pose_physical_pose_gate.jsonl
  home_pose_physical_pose_gate_terminal.log
```

Result:

```text
PASS_TELEMETRY_COMPONENT
physical_pose_status: REQUIRES_OPERATOR_VISUAL_CONFIRMATION
pitch-chain p95 range: 0.0000-0.0050 rad
max consecutive pitch samples >0.10 rad: 0
gyro absolute p95 max: 0.0142 rad/s
accel mean: [1.6935, 0.0631, 9.7242] m/s^2
bus holds: none
terminal holds: none
```

This historical pass verifies analyzer behavior only. It predates the later
left-knee correction and is not current Gate-1 evidence.

## Collection Dry Run

The evidence helper was dry-run without SSH. Its snapshot, SSH, and SCP plans
now use the supplied pinned `known_hosts` file with
`StrictHostKeyChecking=yes`; the previous `no` setting was removed.

No SSH, robot command, deployment, or GPU workload was performed.
