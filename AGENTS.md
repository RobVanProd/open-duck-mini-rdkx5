# Agent Instructions

This repository controls work around a real biped robot. Preserve safety and evidence quality over speed.

## Core Rules

- Never tune before evidence.
- Do not train a new policy yet.
- Do not change gains, offsets, IMU remaps, action scale, or phase timing without a reviewed evidence-backed task.
- Do not deploy behavior changes to the robot unless explicitly requested.
- Do not run moving hardware tests unless Rob is physically present and explicitly approves that exact test.
- Default to docs, tools, analysis, and tests first.
- Keep PRs small and single-purpose.
- Treat documentation as part of the robot state. Update README, roadmap, audit, evidence manifest, and runbooks when project facts change.
- Do not leave important state only in chat, board-local files, or untracked scratch outputs.

## Hardware Safety

- Read-only SSH checks are acceptable.
- Moving scripts require explicit user confirmation and physical support unless grounded by design.
- Start paused wherever possible.
- Stop on unexpected motion, bus-error bursts, large lean, wrong joint, wrong side, or wrong sign.

## Repository Hygiene

- Do not commit `.duck_access/`.
- Do not commit private SSH keys, known_hosts, tokens, or secrets.
- Do not commit huge raw JSONL logs or videos by default.
- Commit summaries and selected evidence only when they support a decision.
- Keep evidence filenames, manifests, and docs synchronized.
- When adding a tool or workflow, document how to run it and what output is expected.

## RHO-Inspired Operating Model

- Keep agent reasoning and experimentation outside the live robot control loop.
- Ship frozen, readable code that can be inspected before it runs on hardware.
- Treat each PR as a candidate mutation with evidence gates.
- Accept changes only when they improve or clarify a measured gate.
- Preserve rejected or inconclusive findings as notes so the project does not repeat the same investigation.
- Prefer whole-repository understanding over isolated one-file edits when a change touches sensor, policy, and hardware contracts.

## Validation

Before finalizing changes, run applicable checks:

```bash
python3 -m py_compile tools/*.py instrumentation/mini_bdx_runtime/telemetry.py instrumentation/scripts/sim2real_diagnostics.py
python3 -m json.tool docs/telemetry_schema.json >/tmp/telemetry_schema.validated.json
```

For docs-only changes, still check repo status and confirm no runtime behavior files changed unintentionally.

## Current Next Gate

Collect first evidence:

1. Config snapshot.
2. Home pose log.
3. Home pose analysis.
4. IMU tilt log.
5. IMU tilt analysis.
6. Foot contact test.

Do not proceed to grounded walking until low-risk gates pass.
