# Corrected Candidate Second-Surface Grounded Test Decision

status: `HOLD_INSUFFICIENT_FOOT_CLEARANCE_ON_CARPET`

## Scope

The operator reported the first grounded surface was an office-chair plastic
mat and was likely too slippery. The operator approved one repeated bounded
grounded test on another surface. The second surface was medium carpet.

```text
policy: /home/sunrise/corrected_bridge_cmd_conditioned_rate175_20260627.onnx
policy_sha256: 63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e
command_x: 0.08
max_runtime_seconds: 5
telemetry_every_n: 1
grounded: true
surface: medium carpet, operator-selected after suspected slip on chair mat
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
  outputs/first_evidence/20260628T012023Z_corrected_candidate_x008_grounded_second_surface/corrected_candidate_x008_grounded_second_surface.jsonl

terminal log:
  outputs/first_evidence/20260628T012023Z_corrected_candidate_x008_grounded_second_surface/terminal.log

analysis:
  outputs/analysis/CORRECTED_CANDIDATE_HW_X008_GROUNDED_SECOND_SURFACE_ANALYSIS.md
  outputs/analysis/corrected_candidate_hw_x008_grounded_second_surface_analysis.json
  outputs/analysis/CORRECTED_CANDIDATE_HW_X008_GROUNDED_SECOND_SURFACE_TARGET_VELOCITY.md
```

## Telemetry Summary

The second surface improved the hardware telemetry relative to the first
grounded surface, but the operator reported that the robot did not visibly walk
forward on the carpet. The robot appeared to be stepping, but the feet did not
lift enough to advance.

```text
samples: 249
dt spikes > 0.03 s: 0
max dt: 0.02014 s
write errors: 0
read checksum increments: 6
action saturation: 0%
rate limit active: 0%
max pitch-chain sent velocity p95: 1.21 rad/s
max pitch-chain tracking p95: 0.071 rad
```

Pitch-chain target velocities stayed inside the corrected bridge envelope:

| joint | sent vel p95 | tracking p95 | lag |
|---|---:|---:|---:|
| left_hip_pitch | 0.7508 | 0.0426 | 4 ticks |
| left_knee | 1.2104 | 0.0648 | 4 ticks |
| left_ankle | 0.9162 | 0.0512 | 3 ticks |
| right_hip_pitch | 0.5966 | 0.0282 | 3 ticks |
| right_knee | 0.8854 | 0.0452 | 4 ticks |
| right_ankle | 0.6623 | 0.0328 | 4 ticks |

The low-command hardware analyzer reports `PASS_LOWCOMMAND_HW_TELEMETRY_SUMMARY`.

## Comparison To First Surface

| metric | first surface | second surface |
|---|---:|---:|
| max pitch-chain sent velocity p95 | 1.83 rad/s | 1.21 rad/s |
| max pitch-chain tracking p95 | 0.106 rad | 0.071 rad |
| read checksum increments | 12 | 6 |
| action saturation | 0% | 0% |
| write errors | 0 | 0 |
| dt spikes > 0.03 s | 0 | 0 |

The surface change materially improved tracking and bus warning counts. This
supports the operator's suspicion that the office-chair plastic mat was a poor
contact condition for this low-command test.

However, the visual result matters more than the telemetry pass: on medium
carpet, the robot appeared to step but did not lift its feet enough to walk
forward. This means the candidate is trackable on the ground but is not yet a
successful grounded walking policy.

## Decision

This run clears the low-command grounded telemetry summary but fails the
operator visual walking check.

Do not extend duration or run another grounded test from this candidate as-is.
The next work should explain the mismatch:

- telemetry says the actuator waveform is trackable,
- visual evidence says the robot attempts stepping but does not lift/clear its
  feet enough to move forward on medium carpet.

Possible interpretations to test offline before more robot motion:

- candidate has too little foot clearance or step amplitude,
- candidate is too low-amplitude / too slow to overcome ground contact,
- carpet is too high-drag for this cautious gait,
- the gait produces mostly in-place shuffling rather than forward displacement,
- foot-contact/weight-transfer behavior differs from sim even though joint
  tracking is acceptable.

Operator visual result:

```text
first surface: office-chair plastic mat, likely too slippery
second surface: medium carpet
second surface visual result: stepping attempt, but insufficient foot lift to
  walk forward
```

No gains, offsets, action scale, phase timing, IMU remaps, or policy files
should be changed from this result.
