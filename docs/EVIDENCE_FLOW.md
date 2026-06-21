# Evidence Flow

This project should produce decisions, not piles of unmanaged logs.

## How Evidence Enters The Repo

Evidence starts outside git:

```text
robot -> /home/sunrise/duck_logs
workstation -> local analysis/output directory
```

Small, durable artifacts can then be copied into git when they are useful for review.

## Recommended Directories

Inside this repository:

```text
evidence/                 small snapshots and selected config evidence
docs/                     summaries, decisions, runbooks
outputs/analysis/         generated markdown summaries if added later
```

Outside this repository:

```text
raw JSONL logs
videos
long console logs
large repeated telemetry captures
```

## File Naming

Use UTC timestamps:

```text
YYYYMMDDTHHMMSSZ_description.ext
```

Examples:

```text
20260621T180046Z_rdkx5_config_snapshot.json
20260622T011500Z_home_pose_analysis.md
20260622T012000Z_imu_tilt_analysis.md
```

## Safe To Commit

- Config snapshots with no secrets.
- Policy hashes and metadata.
- Small analyzer markdown summaries.
- Joint identity summary JSON or markdown.
- Foot contact summary.
- Evidence manifests.
- Small selected JSON snippets needed to support a decision.

## Never Commit

- Private SSH keys.
- `known_hosts`.
- API tokens.
- Password files.
- Raw huge JSONL telemetry logs by default.
- Videos by default.
- Personal network credentials.
- Anything from `.duck_access/`.

## First Evidence Packet

The first packet should include:

```text
config snapshot JSON
home pose analyzer summary
IMU tilt analyzer summary
foot contact summary
joint identity summary if completed
suspended replay x=0 analyzer summary if completed
```

Raw logs should stay outside git unless a small excerpt is required for review.

## Evidence Review Rule

Every root-cause claim should cite:

- file path
- metric or observation
- pass/fail threshold or reason

Example:

```text
IMU upright accel failed because home_pose_analysis.md shows obs[5] mean = -9.6 m/s^2.
```
