# Grounded Rate165 Robot-Validation Approval Packet

Date: 2026-07-11

Status: **READY FOR OPERATOR REVIEW; HARDWARE ACTION NOT AUTHORIZED**

## Candidate

- path: `policy/candidates/phase2_corrected_live_oracle_iter1_rate165_20260703/candidate.onnx`;
- SHA256: `e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33`;
- ONNX contract: `obs[1,101] -> continuous_actions[1,14]` pass;
- grounded home-support gates: `8/8` pass at `x=0` and `x=0.08`;
- current-tool regressions: both pass and reproduce recorded metrics;
- package status: `INFO_NON_DEPLOYABLE_ARTIFACT` by design.

## Why Hardware Is Still Held

The June 21 first-evidence packet passed the available software/electrical
checks, but it did not freshly prove current physical joint geometry. The
historical `left_knee` soft offset was `-1.4880 rad`; it was corrected to
`0.0371 rad` on June 27. A post-correction snapshot and supported low-speed
tracking evidence confirm that correction. The old value is not current.

The remaining gate is freshness and full-pose evidence: first capture the
current configuration, then command supported home pose and compare the real
hip/knee/ankle/foot geometry with the documented home reference. Leave offsets
unchanged if geometry and tracking are correct.

## Required Operator Conditions

- Rob explicitly approves the exact test stage;
- Rob is physically present;
- robot is securely suspended/supported;
- stable power and accessible emergency stop/power cut;
- fingers, cables, and fixtures clear;
- runtime remains start-paused;
- candidate is staged under a new filename; do not overwrite
  `BEST_WALK_ONNX_2.onnx`;
- telemetry JSONL and terminal log paths are selected before motion.

## Ordered Gates

### Gate 0 — Read-Only Snapshot

Capture current runtime revision, `duck_config.json`, policy hashes,
`start_paused`, IMU configuration, joint offsets, and instrumentation status.
No writes and no motion.

The stage-specific helper defaults to plan-only mode:

```bash
bash scripts/collect_grounded_rate165_gate01.sh
```

Run `--run-gate0` only after explicit Gate-0 approval. Gate 1 is a distinct
mode and requires the reviewed v2 snapshot path; snapshots older than 24 hours
are rejected.

### Gate 1 — Supported Physical Home Pose

Command and hold runtime home pose only, with the robot supported. Compare the
physical pose to `home_contact_sheet.png` and capture home-pose telemetry.

Pass requires:

- visually correct bilateral hip, knee, ankle, and foot geometry;
- small stable joint tracking error;
- upright IMU/gyro consistent with the existing contract;
- no repeated bus-write failures or correlated control damage.

Stop on wrong joint/side/sign, unexpected motion, large lean, visibly wrong
left knee geometry, or repeated bus errors. If geometry is wrong, stop and
review soft offsets separately; do not continue to policy replay.

Analyze the telemetry component separately from the visual pose decision:

```bash
python3 tools/evaluate_supported_home_telemetry.py \
  <home_pose.jsonl> \
  --terminal-log <home_pose_terminal.log> \
  --output-md <supported_home_telemetry_gate.md> \
  --output-json <supported_home_telemetry_gate.json>
```

`PASS_TELEMETRY_COMPONENT` is necessary but cannot approve Gate 1 without the
operator's physical-geometry confirmation.

### Gate 2 — Candidate Staging, Paused

Only after Gate 1 passes and staging is explicitly approved:

- copy the hash-verified candidate under a new, versioned filename;
- verify its remote SHA256 after copying;
- do not change gains, offsets, IMU remaps, action scale, phase timing, or the
  baseline policy;
- start the runtime paused and confirm no target motion.

### Gate 3 — Suspended `x=0`

Requires a separate explicit approval after reviewing Gates 0–2. Run suspended
only, capture JSONL telemetry and terminal logs, then stop and analyze before
any nonzero command.

Pass requires:

- coherent near-stationary behavior;
- pitch-chain p95 tracking preferably `<0.05 rad`, acceptable `<0.08 rad`;
- no sustained post-startup pitch error `>0.10 rad`;
- no saturation bursts, repeated write errors, or visible twitch/asymmetry.

The stage-specific runner defaults to plan-only and contains no nonzero or
grounded mode:

```bash
bash scripts/collect_grounded_rate165_gate3_x0.sh
```

Its `--run` mode requires a fresh reviewed Gate-2 snapshot, physical-presence
flag, exact typed confirmation, live candidate/config/runtime hash checks, and
an absent walker process. It runs exactly 15 seconds and always attempts
torque-off cleanup.

### Gate 4 — Suspended `x=0.08`

Requires another explicit approval and only follows a reviewed Gate 3 pass.
Use the same telemetry/terminal capture and the same tracking/error stops.
Operator must report whether the suspended gait is coherent and symmetric.

### Gate 5 — Grounded Replay

Blocked. It may be proposed only after suspended dynamic tracking passes and a
new grounded-test plan is reviewed. This packet does not authorize it.

## Evidence To Return After Each Approved Stage

- config/policy hash snapshot;
- physical-pose comparison notes or photos retained outside git as appropriate;
- telemetry JSONL path;
- terminal log path;
- analyzer Markdown/JSON;
- operator visual note;
- exact stop condition, if any.

Commit summaries and decisions, not bulky raw telemetry by default.

## Current Boundary

No SSH, deployment, configuration write, policy copy, home-pose command,
suspended replay, or grounded motion has been performed in preparing this
packet. The next authorized action must be named explicitly by the operator;
approval of one gate does not approve later gates.
