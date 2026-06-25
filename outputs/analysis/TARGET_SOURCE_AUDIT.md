# Target Source Audit

status: `PASS_TARGET_SOURCE_READY`
offline_imitation_smoke_permission: `True`
full_training_permission: `False`
robot_validation_permission: `False`

This summarizes compact target-source evidence. It does not run
simulation, training, SSH, deployment, or robot tests.

## Source Summary

| source | kind | status | robust_modes | curated_50 | sources | seed0_vx | seed0_vy95 | seed2_vx | seed2_vy95 | seed2_contact | seed2_trans | seed2_foot_z95 | rollout_falls | contact_mismatch |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| contact_break | primitive | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 70 | 1 | 0.0531 | 0.0665 | 0.0453 | 0.1028 | 98.0000 | 2 | NA | NA | NA |
| lift_pulse | primitive | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 59 | 1 | 0.0508 | 0.0633 | 0.0519 | 0.0937 | 98.0000 | 2 | NA | NA | NA |
| foot_clearance_probe | primitive | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 23 | 1 | 0.0475 | 0.1197 | 0.0565 | 0.1166 | 98.0000 | 2 | 0.0159 | NA | NA |
| dynamic_roll | primitive | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 42 | 2 | 0.0413 | 0.1234 | 0.0417 | 0.1110 | 94.0000 | 4 | 0.0123 | NA | NA |
| dynamic_roll_refine | primitive | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 3 | 2 | 0.0365 | 0.0667 | 0.0403 | 0.1122 | 94.0000 | 4 | 0.0118 | NA | NA |
| dynamic_roll_lateral_fix | primitive | `PASS_SEED_ROBUST_TARGETS` | 2 | 70 | 2 | 0.0416 | 0.0716 | 0.0437 | 0.0736 | 94.0000 | 4 | 0.0114 | NA | NA |
| reference_contact_gated_projected | reference | `HOLD_REFERENCE_TARGET_TERMINATES` | NA | 0 | 0 | NA | NA | NA | NA | NA | NA | NA | 7 | 69.4217 |
| reference_contact_synchronized_projected | reference | `HOLD_REFERENCE_TARGET_TERMINATES` | NA | 0 | 0 | NA | NA | NA | NA | NA | NA | NA | 7 | 4.3614 |

## Seed 2 Failures

| source | seed0_failures | seed2_failures |
|---|---|---|
| contact_break | `NA` | `single_contact_pattern_dominates` |
| lift_pulse | `NA` | `single_contact_pattern_dominates` |
| foot_clearance_probe | `NA` | `high_body_pitch, short_done_margin, single_contact_pattern_dominates, too_few_contact_transitions` |
| dynamic_roll | `high_lateral_velocity` | `NA` |
| dynamic_roll_refine | `low_forward_velocity` | `NA` |
| dynamic_roll_lateral_fix | `NA` | `NA` |
| reference_contact_gated_projected | `NA` | `NA` |
| reference_contact_synchronized_projected | `NA` | `NA` |

## Recommendation

Dynamic-roll lateral-fix cleared the strict target-source gate. Use it as the first candidate target source for a small reviewed offline imitation/BC smoke, while keeping robot validation blocked.

## Gate

- Target-source discovery is unblocked for a small offline imitation/BC smoke.
- Full PPO remains blocked until the smoke produces a closed-loop replay pass.
- Robot validation remains blocked.
- Do not treat a source-diverse dataset as hardware permission.
