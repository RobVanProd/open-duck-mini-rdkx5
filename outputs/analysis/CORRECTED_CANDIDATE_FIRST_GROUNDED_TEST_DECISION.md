# Corrected Candidate First Grounded Test Decision

status: `HOLD_GROUNDED_REVIEW_REQUIRED`

## Scope

This was the first bounded grounded telemetry test of the corrected candidate.

```text
policy: /home/sunrise/corrected_bridge_cmd_conditioned_rate175_20260627.onnx
policy_sha256: 63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e
command_x: 0.08
max_runtime_seconds: 5
telemetry_every_n: 1
grounded: true
surface: office-chair plastic mat, later suspected too slippery by operator
no tuning: true
no BEST_WALK: true
```

The run exited normally through the runtime limit:

```text
remote_exit_code: 0
terminal: Starting -> Max runtime reached -> TURNING OFF
post-run process check: no walking process left running
```

## Artifacts

```text
raw telemetry:
  outputs/first_evidence/20260628T011648Z_corrected_candidate_x008_grounded_first/corrected_candidate_x008_grounded_first.jsonl

terminal log:
  outputs/first_evidence/20260628T011648Z_corrected_candidate_x008_grounded_first/terminal.log

analysis:
  outputs/analysis/CORRECTED_CANDIDATE_HW_X008_GROUNDED_FIRST_ANALYSIS.md
  outputs/analysis/corrected_candidate_hw_x008_grounded_first_analysis.json
  outputs/analysis/CORRECTED_CANDIDATE_HW_X008_GROUNDED_FIRST_TARGET_VELOCITY.md
```

## Telemetry Summary

```text
samples: 249
dt spikes > 0.03 s: 0
max dt: 0.02014 s
write errors: 0
read checksum increments: 12
action saturation: 0%
rate limit active: 0%
max pitch-chain sent velocity p95: 1.83 rad/s
max pitch-chain tracking p95: 0.106 rad
max pitch-chain tracking max: 0.149 rad
```

Pitch-chain target velocities stayed inside the corrected bridge envelope:

| joint | sent vel p95 | tracking p95 | lag |
|---|---:|---:|---:|
| left_hip_pitch | 1.5108 | 0.0743 | 4 ticks |
| left_knee | 1.8308 | 0.0970 | 3 ticks |
| left_ankle | 1.3701 | 0.0668 | 3 ticks |
| right_hip_pitch | 1.3175 | 0.0607 | 3 ticks |
| right_knee | 1.7261 | 0.0865 | 4 ticks |
| right_ankle | 1.1679 | 0.0572 | 4 ticks |

The low-command hardware analyzer reports `HOLD_TRACKING_P95_OVER_LIMIT`
because the grounded tracking p95 rose above its conservative threshold.

## Interpretation

This is a useful first-grounded transfer result, but it is not a pass for
continued grounded walking.

Positive signs:

- the policy hash was the corrected candidate
- the run completed its bounded 5 second runtime
- no write errors
- no action saturation
- no rate-limit activation
- target velocities remained in-envelope
- loop timing stayed clean

Hold reasons:

- operator later identified the test surface as an office-chair plastic mat and
  suspected it was too slippery
- grounded load increased pitch-chain tracking p95 from stand levels to about
  `0.10 rad`
- read checksum warnings persisted
- foot-contact telemetry was noisy during the grounded run
- operator visual notes have not yet been written into the artifact

## Decision

Do not run a second grounded test from this result alone.

Next required step:

```text
review operator visual notes/video + grounded telemetry
decide whether this was cautious stable motion, marginal dragging, or unstable contact
```

Only after that review should another grounded run be considered. Do not tune
gains, offsets, action scale, phase timing, IMU remaps, or policy files as a
reaction to this single run.
