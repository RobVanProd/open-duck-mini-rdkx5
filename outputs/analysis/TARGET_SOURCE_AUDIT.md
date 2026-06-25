# Target Source Audit

status: `HOLD_NO_TARGET_SOURCE_READY`

This summarizes compact target-source evidence. It does not run
simulation, training, SSH, deployment, or robot tests.

## Source Summary

| source | kind | status | robust_modes | curated_50 | sources | seed2_vx | seed2_vy95 | seed2_contact | seed2_trans | seed2_foot_z95 | rollout_falls | contact_mismatch |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| contact_break | primitive | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 70 | 1 | 0.0453 | 0.1028 | 98.0000 | 2 | NA | NA | NA |
| lift_pulse | primitive | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 59 | 1 | 0.0519 | 0.0937 | 98.0000 | 2 | NA | NA | NA |
| foot_clearance_probe | primitive | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 23 | 1 | 0.0565 | 0.1166 | 98.0000 | 2 | 0.0159 | NA | NA |
| reference_contact_gated_projected | reference | `HOLD_REFERENCE_TARGET_TERMINATES` | NA | 0 | 0 | NA | NA | NA | NA | NA | 7 | 69.4217 |
| reference_contact_synchronized_projected | reference | `HOLD_REFERENCE_TARGET_TERMINATES` | NA | 0 | 0 | NA | NA | NA | NA | NA | 7 | 4.3614 |

## Seed 2 Failures

| source | failures |
|---|---|
| contact_break | `single_contact_pattern_dominates` |
| lift_pulse | `single_contact_pattern_dominates` |
| foot_clearance_probe | `high_body_pitch, short_done_margin, single_contact_pattern_dominates, too_few_contact_transitions` |
| reference_contact_gated_projected | `NA` |
| reference_contact_synchronized_projected | `NA` |

## Recommendation

Build a contact-state or IK/reference target source. The current joint-space primitive family repeatedly preserves forward/lateral metrics but fails seed2 contact alternation.

## Gate

- Training remains blocked until a target source has robust 50-sample windows across seed_000 and seed_002.
- A source with only seed_000 curated windows is evidence, not permission to train.
- A reference rollout with low contact mismatch but falls/negative progress is not a BC target.
