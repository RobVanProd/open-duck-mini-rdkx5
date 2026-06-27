# Contact-Timed Reference Snippets

status: `HOLD_SOURCE_FRAGMENTS_DOUBLE_SUPPORT`

This audits curated low-command target windows for contact timing.
It does not run simulation, train, deploy, SSH, or touch the robot.

## Summary

- curation_json: `outputs/analysis/target_generator_dynamic_roll_lateral_fix_robust_modes_curation_50.json`
- manifest_json: `outputs/analysis/contact_timed_reference_snippets_manifest.json`
- entries: `9`
- pass_entries: `0`
- double_support_hold_entries: `9`
- contact_transitions_mean: `3.8889`
- single_support_pct_mean: `7.3333`
- double_support_pct_mean: `92.6667`

## Criteria

- min_mean_vx: `0.04`
- max_vy_abs_p95: `0.12`
- max_pitch_abs_p95: `0.35`
- min_base_height: `0.145`
- max_sent_velocity_p95: `3.75`
- min_single_support_pct: `20.0`
- min_each_single_support_pct: `5.0`
- max_double_support_pct: `75.0`
- min_contact_transitions: `2`

## Snippets

| id | status | reasons | ticks | vx | vy95 | pitch95 | height | single% | double% | trans | longest11 | sequence_preview |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| cdbc4efa2b19db62 | `HOLD_CONTACT_FRAGMENT` | `too_little_single_support, single_support_not_balanced, double_support_dominates` | 5-54 | 0.0401 | 0.0881 | 0.3167 | 0.1455 | 8.0000 | 92.0000 | 3 | 32 | `0101011111111111111111111111111111101111` |
| a0d2bef05974584b | `HOLD_CONTACT_FRAGMENT` | `too_little_single_support, single_support_not_balanced, double_support_dominates` | 5-54 | 0.0435 | 0.0910 | 0.2782 | 0.1458 | 6.0000 | 94.0000 | 2 | 32 | `1111111111111111111111111111110101011111` |
| 3e685b9f6658c91f | `HOLD_CONTACT_FRAGMENT` | `too_little_single_support, single_support_not_balanced, double_support_dominates` | 10-59 | 0.0417 | 0.0586 | 0.2950 | 0.1455 | 6.0000 | 94.0000 | 2 | 37 | `1111111111111111111101010111111111111111` |
| a3223fecee75c157 | `HOLD_CONTACT_FRAGMENT` | `too_little_single_support, double_support_dominates` | 5-54 | 0.0423 | 0.0889 | 0.3294 | 0.1469 | 12.0000 | 88.0000 | 5 | 35 | `0101011111111111111110101111101111111111` |
| e501ccdd19c42b18 | `HOLD_CONTACT_FRAGMENT` | `too_little_single_support, single_support_not_balanced, double_support_dominates` | 10-59 | 0.0411 | 0.0431 | 0.2476 | 0.1478 | 6.0000 | 94.0000 | 6 | 41 | `1111110111101111101111111111111111111111` |
| 13248f6e57891bfd | `HOLD_CONTACT_FRAGMENT` | `too_little_single_support, single_support_not_balanced, double_support_dominates` | 5-54 | 0.0410 | 0.0643 | 0.2417 | 0.1488 | 6.0000 | 94.0000 | 6 | 36 | `1111111111111111011110111110111111111111` |
| 049f91faaf0f89ce | `HOLD_CONTACT_FRAGMENT` | `too_little_single_support, single_support_not_balanced, double_support_dominates` | 5-54 | 0.0416 | 0.0716 | 0.2789 | 0.1466 | 10.0000 | 90.0000 | 3 | 32 | `0101111111111111111111111111111010101111` |
| b106a81e6738ba7f | `HOLD_CONTACT_FRAGMENT` | `too_little_single_support, single_support_not_balanced, double_support_dominates` | 5-54 | 0.0437 | 0.0736 | 0.2592 | 0.1475 | 6.0000 | 94.0000 | 4 | 29 | `1111111111111111111111111111111101011111` |
| c23b3f13d9cb14be | `HOLD_CONTACT_FRAGMENT` | `too_little_single_support, single_support_not_balanced, double_support_dominates` | 10-59 | 0.0403 | 0.0522 | 0.2596 | 0.1467 | 6.0000 | 94.0000 | 4 | 34 | `1111111111111111111111010111110111111111` |

## Interpretation

- If source fragments already contain clean single-support alternation, the next blocker is closed-loop policy/contact execution.
- If source fragments are mostly double support, the target generator must explicitly search for single-support/weight-transfer windows before PPO or BC.
- Do not launch training from snippets that fail this contact-timing audit.
