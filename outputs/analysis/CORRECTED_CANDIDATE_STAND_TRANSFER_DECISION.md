# Corrected Candidate Stand Transfer Decision

status: `PASS_STAND_SUSPENDED_TRANSFER_WITH_READ_WARNINGS`

## Candidate

```text
policy: policy/candidates/corrected_bridge_cmd_conditioned_rate175_20260627/candidate.onnx
policy_sha256: 63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e
duck_config_sha256: 131a7b8fce1107b14f4727562f44f9e17324caf7fc22512ad7115911f050991b
robot_policy_copy: /home/sunrise/corrected_bridge_cmd_conditioned_rate175_20260627.onnx
robot_policy_copy_sha256: 63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e
```

The candidate was copied to the robot under a new filename. The baseline
`/home/sunrise/BEST_WALK_ONNX_2.onnx` was not overwritten.

## Scope

These were stand/suspended telemetry runs only:

- no grounded replay
- no tuning
- no gains, offsets, IMU remaps, action scale, phase timing, policy overwrite,
  or `duck_config.json` change
- telemetry logging enabled
- torque/runtime stopped at end of each run

## x=0.0 Stand Run

Artifacts:

```text
raw telemetry: outputs/first_evidence/20260628T010359Z_corrected_candidate_x0_stand/corrected_candidate_x0_stand.jsonl
terminal log: outputs/first_evidence/20260628T010359Z_corrected_candidate_x0_stand/terminal.log
summary: outputs/analysis/CORRECTED_CANDIDATE_HW_X0_STAND_ANALYSIS.md
gate: outputs/analysis/CORRECTED_CANDIDATE_HW_X0_STAND_SUSPENDED_GATE.md
target velocity: outputs/analysis/CORRECTED_CANDIDATE_HW_X0_TARGET_VELOCITY.md
```

Summary:

```text
samples: 747
command: x=0.0
max pitch-chain sent velocity p95: 0.2310 rad/s
max pitch-chain tracking p95: 0.0145 rad
post-startup max tracking error: 0.0235 rad
post-startup tracking p95: 0.0176 rad
action saturation: 0%
write errors: 0
read checksum increments: 18
dt spikes > 0.03 s: 0
```

The strict suspended replay gate reports `HOLD_CONTROL_IMPACT` only because the
read retry rate is above its red threshold. The read increments did not
correlate with post-startup tracking spikes, write errors, dt spikes, action
saturation, or rate-limit activation. Treat this as a read-bus warning, not a
control failure.

## x=0.08 Stand Run

Artifacts:

```text
raw telemetry: outputs/first_evidence/20260628T010517Z_corrected_candidate_x008_stand/corrected_candidate_x008_stand.jsonl
terminal log: outputs/first_evidence/20260628T010517Z_corrected_candidate_x008_stand/terminal.log
summary: outputs/analysis/CORRECTED_CANDIDATE_HW_X008_STAND_ANALYSIS.md
gate: outputs/analysis/CORRECTED_CANDIDATE_HW_X008_STAND_SUSPENDED_GATE.md
target velocity: outputs/analysis/CORRECTED_CANDIDATE_HW_X008_TARGET_VELOCITY.md
```

Summary:

```text
samples: 747
command: x=0.08
suspended gate: WARN_PROCEED_WITH_CAUTION
max pitch-chain sent velocity p95: 0.4065 rad/s
max pitch-chain target velocity p95 from target analyzer: 0.3950 rad/s
max pitch-chain tracking p95: 0.0222 rad
post-startup max tracking error: 0.0235 rad
post-startup tracking p95: 0.0213 rad
action saturation: 0%
rate limit active: 0%
write errors: 0
read checksum increments: 6
dt spikes > 0.03 s: 0
```

The `x=0.08` run is the first hardware transfer evidence that the corrected
candidate commands a trackable waveform on the stand. Its target velocities are
far below the corrected bridge per-joint limits and far below the old upstream
`BEST_WALK_ONNX_2` suspended waveform.

## Decision

The candidate transfers to stand/suspended hardware telemetry for `x=0.0` and
`x=0.08` without dynamic pitch-chain tracking failure.

Grounded replay is still not automatically approved. The next decision should
be a human review of:

- operator visual notes from these stand runs,
- whether read checksum warnings are acceptable or need bus cleanup first,
- whether to run a first grounded test at this slow candidate speed under a
  catch rig / immediate cutoff procedure.

Do not change runtime gains, offsets, action scale, phase timing, or policy
files as part of this decision.
