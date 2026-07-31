# Grounded Rate165 Gate-3 x=0 Runner Audit

Date: 2026-07-12

Status: `PASS_OFFLINE_RUNNER_READY; GATE3_NOT_AUTHORIZED`

## Exact Contract

`scripts/collect_grounded_rate165_gate3_x0.sh` exposes only one moving mode:

```text
suspended_policy_replay
candidate: /home/sunrise/phase2_grounded_rate165_20260712_e06643e5.onnx
command: [x=0.0, y=0.0, yaw=0.0]
duration: 15 seconds
action_scale: 0.25 (unchanged)
telemetry: every tick
```

There is no `x=0.08` or grounded option.

## Fail-Closed Prerequisites

Before motor initialization, run mode requires:

- `--i-am-physically-present`;
- a v2 Gate-2 snapshot no older than 24 hours;
- the staged candidate and its exact SHA256 in that snapshot;
- `start_paused=true`;
- exact live candidate and config hashes;
- exact deployed hashes for `sim2real_diagnostics.py`,
  `v2_rl_walk_mujoco.py`, and `turn_off.py`;
- no active walker, diagnostic, or mini-bdx runtime process;
- exact typed confirmation `RUN_SUSPENDED_X0_GATE3`.

The diagnostic initializes paused, receives one deliberate newline to unpause,
stops at 15 seconds, logs telemetry/terminal output, and invokes its own
`RLWalk.cleanup()`. The runner also has an exit trap that calls the canonical
`turn_off.py` as a fallback before returning.

## Analyzer

The returned evidence is passed to `tools/analyze_suspended_replay.py`. Review
must stop before any nonzero command. The prior June-28 corrected candidate x=0
trace demonstrated why the bus rule matters: tracking was clean, but an 18/747
read-retry rate (`2.41%`) exceeded the established 2% red threshold. The new
candidate receives no exemption from that gate.

## Offline Validation

```text
PASS: Bash syntax
PASS: ShellCheck
PASS: plan mode created no evidence directory and made no SSH connection
PASS: plan fixes x/y/yaw to zero and duration to 15 seconds
PASS: missing physical-presence flag refused run mode with exit 2
PASS: no x=0.08 or grounded run mode exists
PASS: git diff --check
```

No SSH, motor command, policy execution, or GPU workload occurred during this
audit.
