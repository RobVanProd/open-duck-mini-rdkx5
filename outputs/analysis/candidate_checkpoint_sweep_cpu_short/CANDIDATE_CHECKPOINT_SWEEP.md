# Candidate Checkpoint Sweep

Offline checkpoint selection sweep. This does not SSH, deploy, train,
or touch the robot.

commands: `[0.08]`
bridge_mode: `fitted`
duration_s: `1.0`
velocity_envelope_rad_s: `[2.25, 3.75]`
run: `True`

## Results

| policy | command_x | status | samples | termination | max_pitch_vel_p95 | envelope | max_tracking_p95 | track_ratio | mean_local_vx |
|---|---:|---|---:|---|---:|---|---:|---:|---:|
| `movement_bootstrap_v7_checkpoint_anchor_20260623_candidate` | 0.080 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.9357 | `BELOW_MEASURED_ENVELOPE` | 0.2449 | 1.8356 | 0.1469 |
| `movement_bootstrap_v8_overshoot_stabilized_standstill_20260623_candidate` | 0.080 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 2.1929 | `BELOW_MEASURED_ENVELOPE` | 0.2391 | 0.2539 | 0.0203 |
| `movement_bootstrap_v9_progress_balanced_standstill_20260623_candidate` | 0.080 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 2.1496 | `BELOW_MEASURED_ENVELOPE` | 0.2369 | 0.9129 | 0.0730 |

## Interesting Checkpoints

- `policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/candidate.onnx` command `0.080`: vx `0.1469`, ratio `1.8356`, vel_p95 `1.9357`, tracking_p95 `0.2449`
- `policy/candidates/movement_bootstrap_v9_progress_balanced_standstill_20260623/candidate.onnx` command `0.080`: vx `0.0730`, ratio `0.9129`, vel_p95 `2.1496`, tracking_p95 `0.2369`
- `policy/candidates/movement_bootstrap_v8_overshoot_stabilized_standstill_20260623/candidate.onnx` command `0.080`: vx `0.0203`, ratio `0.2539`, vel_p95 `2.1929`, tracking_p95 `0.2391`

## Interpretation

- A passing robot candidate still requires the normal x=0.0 and x=0.08
  candidate gates. This sweep is only for checkpoint selection.
- If no checkpoint shows meaningful in-envelope motion, the next
  training change should add a teacher-action or trust-region
  continuity mechanism rather than another small scalar reward tweak.
