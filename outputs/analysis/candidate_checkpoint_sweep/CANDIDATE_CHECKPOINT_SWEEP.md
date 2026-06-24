# Candidate Checkpoint Sweep

Offline checkpoint selection sweep. This does not SSH, deploy, train,
or touch the robot.

commands: `[0.08]`
bridge_mode: `fitted`
duration_s: `5.0`
velocity_envelope_rad_s: `[2.25, 3.75]`
run: `False`

## Results

| policy | command_x | status | samples | termination | max_pitch_vel_p95 | envelope | max_tracking_p95 | track_ratio | mean_local_vx |
|---|---:|---|---:|---|---:|---|---:|---:|---:|
| `movement_bootstrap_v7_checkpoint_anchor_20260623_candidate` | 0.080 | `DRY_RUN` | NA | `None` | NA | `UNKNOWN` | NA | NA | NA |
| `movement_bootstrap_v8_overshoot_stabilized_standstill_20260623_candidate` | 0.080 | `DRY_RUN` | NA | `None` | NA | `UNKNOWN` | NA | NA | NA |
| `movement_bootstrap_v9_progress_balanced_standstill_20260623_candidate` | 0.080 | `DRY_RUN` | NA | `None` | NA | `UNKNOWN` | NA | NA | NA |

## Interesting Checkpoints

- None met the configured interesting-motion criteria.

## Interpretation

- A passing robot candidate still requires the normal x=0.0 and x=0.08
  candidate gates. This sweep is only for checkpoint selection.
- If no checkpoint shows meaningful in-envelope motion, the next
  training change should add a teacher-action or trust-region
  continuity mechanism rather than another small scalar reward tweak.
