# Candidate Checkpoint Sweep

Offline checkpoint selection sweep. This does not SSH, deploy, train,
or touch the robot.

commands: `[0.0, 0.08]`
bridge_mode: `fitted`
duration_s: `1.0`
velocity_envelope_rad_s: `[2.25, 3.75]`
min_promote_vx_m_s: `0.02`
min_promote_ratio: `0.25`
run: `True`

## Results

| policy | command_x | status | samples | termination | max_pitch_vel_p95 | envelope | max_tracking_p95 | track_ratio | mean_local_vx |
|---|---:|---|---:|---|---:|---|---:|---:|---:|
| `best` | 0.000 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.1618 | `BELOW_MEASURED_ENVELOPE` | 0.1878 | NA | 0.0037 |
| `best` | 0.080 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.9304 | `BELOW_MEASURED_ENVELOPE` | 0.2219 | 0.2793 | 0.0223 |
| `relabel_weight3` | 0.000 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 1.6506 | `BELOW_MEASURED_ENVELOPE` | 0.1911 | NA | 0.0010 |
| `relabel_weight3` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 3.4542 | `INSIDE_MEASURED_ENVELOPE` | 0.2175 | -0.2154 | -0.0172 |

## Interesting Checkpoints

- `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate/candidate.onnx` command `0.080`: vx `0.0223`, ratio `0.2793`, vel_p95 `1.9304`, tracking_p95 `0.2219`

## Promotion Decisions

| policy | decision | pass_count | duration_complete | max_vel_p95 | max_tracking_p95 | max_sat_pct | positive_ratio_mean |
|---|---|---:|---:|---:|---:|---:|---:|
| `best` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/2 | 2/2 | 1.9304 | 0.2219 | 0.0000 | 0.2793 |
| `relabel_weight3` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/2 | 2/2 | 3.4542 | 0.2175 | 0.0000 | -0.2154 |

### Hold Reasons

- `best`: command 0: HOLD_CANDIDATE_TRACKING; command 0.08: HOLD_CANDIDATE_TRACKING
- `relabel_weight3`: command 0: HOLD_CANDIDATE_TRACKING; command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS; command 0.08: track ratio -0.2154 < 0.2500; command 0.08: mean vx -0.0172 < 0.0200

## Interpretation

- A passing robot candidate still requires the normal x=0.0 and x=0.08
  candidate gates. This sweep is only for checkpoint selection.
- `PASS_PROMOTE_CANDIDATE_CHECKPOINT` means all requested commands
  passed their candidate gates in this compact sweep. It is still not
  robot approval; run the full multi-seed x=0.0 and x=0.08 gates first.
- If no checkpoint shows meaningful in-envelope motion, the next
  training change should add a teacher-action or trust-region
  continuity mechanism rather than another small scalar reward tweak.
