# Grounded Rate165 Gate-0/1 Runner Audit

Date: 2026-07-11

Status: `PASS_OFFLINE_RUNNER_READY; HARDWARE_ACTION_NOT_AUTHORIZED`

## Purpose

The generic first-evidence helper can collect several diagnostics in one
session. Candidate validation requires narrower authority: read-only snapshot
and supported home pose are separate approvals.

`scripts/collect_grounded_rate165_gate01.sh` now provides mutually exclusive
modes:

```text
plan (default): no SSH and no local evidence directory
--run-gate0: read-only snapshot only
--run-gate1: supported home command, log retrieval, and stationary analysis
```

Gate 1 fails closed unless all of these are true:

- `--i-am-physically-present` is supplied;
- a reviewed `--gate0-snapshot` is supplied;
- the snapshot uses schema `open_duck_mini_config_snapshot_v2`;
- the snapshot is no more than 24 hours old;
- the operator types `RUN_SUPPORTED_HOME_GATE1` exactly.

It captures telemetry and the terminal stream separately, runs
`evaluate_supported_home_telemetry.py`, and explicitly leaves physical pose
approval open for the operator's visual comparison.

All SSH/SCP commands pin the supplied known-hosts file and use
`StrictHostKeyChecking=yes`.

## Offline Tests

```text
PASS: bash syntax
PASS: plan mode produced no SSH and created no evidence directory
PASS: plan includes separate Gate 0 and Gate 1 commands
PASS: missing physical-presence flag refused Gate 1 with exit 2
PASS: simultaneous Gate 0/Gate 1 modes refused with exit 2
PASS: ShellCheck (intentional reviewed client-side remote command expansion noted)
PASS: git diff --check
```

No SSH connection, robot command, deployment, or GPU workload was performed.
