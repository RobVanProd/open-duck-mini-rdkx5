# T4 BEST_WALK baseline versus all current gates

- Status: `BASELINE_FAILS_CURRENT_FEASIBILITY_GATES`
- Cells: `32/32`
- Failed gate rows: `13`
- Result SHA-256: `33c3dda14a8f64c6da862a9b2a48d3fce0a224e7590395044f150f796ec70894`

## Condition summary

| condition | complete | falls | mean vx | mean |vx| | mean track | min track | tracking p95 | p95 vel excess | max vel excess | action sat % | pitch p95 | height min | reward min |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `x0.000_vanilla` | 8/8 | 0 | 0.0002470016365235418 | 0.0011826240327521892 | None | None | 0.03802767992019653 | 0.0 | 3.239999294281006 | 0.0 | 0.016723472896325708 | 0.1451917439699173 | 0.5523635945518811 |
| `x0.000_fitted` | 8/8 | 0 | 0.0002869891929687872 | 0.0011239510587362311 | None | None | 0.03981090784072872 | 0.0 | 3.239999294281006 | 0.0 | 0.013209535293021449 | 0.14509877562522888 | 0.5502287725806236 |
| `x0.080_vanilla` | 8/8 | 0 | 0.06964585096726539 | 0.06964585096726539 | 0.8705731370908173 | 0.8087895926461595 | 0.20788586139678955 | 2.489999294281006 | 3.239999294281006 | 0.0 | 0.07916602437068551 | 0.14513236284255981 | 0.5606631521582603 |
| `x0.080_fitted` | 8/8 | 0 | 0.03794585570929333 | 0.03794585570929333 | 0.47432319636616666 | 0.3588247251874842 | 0.2668792486190796 | 2.489999294281006 | 3.239999294281006 | 0.4 | 0.10597808050713095 | 0.14522682130336761 | 0.49071075677871706 |

## Gate reconciliation

| condition | source | metric | gate | observed | pass | required action |
|---|---|---|---|---:|---|---|
| `x0.000_vanilla` | `coded_candidate_gate` | `max_action_saturation_pct` | lte 1.0 | 0.0 | `True` | `None` |
| `x0.000_vanilla` | `coded_candidate_gate` | `max_pitch_tracking_p95_rad` | lte 0.2 | 0.03802767992019653 | `True` | `None` |
| `x0.000_vanilla` | `coded_candidate_gate` | `max_p95_velocity_limit_excess_rad_s` | lte 0.0 | 0.0 | `True` | `None` |
| `x0.000_vanilla` | `coded_candidate_gate` | `max_instant_velocity_limit_excess_rad_s` | lte 0.0 | 3.239999294281006 | `False` | `RELAX_TO_BASELINE_OR_RELABEL_STRETCH` |
| `x0.000_vanilla` | `coded_candidate_gate` | `max_abs_body_pitch_p95_rad` | lte 0.25 | 0.016723472896325708 | `True` | `None` |
| `x0.000_vanilla` | `coded_candidate_gate` | `min_base_height_m` | gte 0.12 | 0.1451917439699173 | `True` | `None` |
| `x0.000_vanilla` | `coded_candidate_gate` | `min_reward_mean` | gte 0.3 | 0.5523635945518811 | `True` | `None` |
| `x0.000_vanilla` | `documented_semantic_x000` | `duration_complete_count` | eq 8 | 8 | `True` | `None` |
| `x0.000_vanilla` | `documented_semantic_x000` | `fall_count` | eq 0 | 0 | `True` | `None` |
| `x0.000_vanilla` | `documented_semantic_x000` | `mean_abs_vx_m_s` | lte 0.005 | 0.0011826240327521892 | `True` | `None` |
| `x0.000_vanilla` | `documented_semantic_x000` | `max_p95_velocity_limit_excess_rad_s` | lte 0.0 | 0.0 | `True` | `None` |
| `x0.000_fitted` | `coded_candidate_gate` | `max_action_saturation_pct` | lte 1.0 | 0.0 | `True` | `None` |
| `x0.000_fitted` | `coded_candidate_gate` | `max_pitch_tracking_p95_rad` | lte 0.2 | 0.03981090784072872 | `True` | `None` |
| `x0.000_fitted` | `coded_candidate_gate` | `max_p95_velocity_limit_excess_rad_s` | lte 0.0 | 0.0 | `True` | `None` |
| `x0.000_fitted` | `coded_candidate_gate` | `max_instant_velocity_limit_excess_rad_s` | lte 0.0 | 3.239999294281006 | `False` | `RELAX_TO_BASELINE_OR_RELABEL_STRETCH` |
| `x0.000_fitted` | `coded_candidate_gate` | `max_abs_body_pitch_p95_rad` | lte 0.25 | 0.013209535293021449 | `True` | `None` |
| `x0.000_fitted` | `coded_candidate_gate` | `min_base_height_m` | gte 0.12 | 0.14509877562522888 | `True` | `None` |
| `x0.000_fitted` | `coded_candidate_gate` | `min_reward_mean` | gte 0.3 | 0.5502287725806236 | `True` | `None` |
| `x0.000_fitted` | `documented_semantic_x000` | `duration_complete_count` | eq 8 | 8 | `True` | `None` |
| `x0.000_fitted` | `documented_semantic_x000` | `fall_count` | eq 0 | 0 | `True` | `None` |
| `x0.000_fitted` | `documented_semantic_x000` | `mean_abs_vx_m_s` | lte 0.005 | 0.0011239510587362311 | `True` | `None` |
| `x0.000_fitted` | `documented_semantic_x000` | `max_p95_velocity_limit_excess_rad_s` | lte 0.0 | 0.0 | `True` | `None` |
| `x0.080_vanilla` | `coded_candidate_gate` | `max_action_saturation_pct` | lte 1.0 | 0.0 | `True` | `None` |
| `x0.080_vanilla` | `coded_candidate_gate` | `max_pitch_tracking_p95_rad` | lte 0.2 | 0.20788586139678955 | `False` | `RELAX_TO_BASELINE_OR_RELABEL_STRETCH` |
| `x0.080_vanilla` | `coded_candidate_gate` | `max_p95_velocity_limit_excess_rad_s` | lte 0.0 | 2.489999294281006 | `False` | `RELAX_TO_BASELINE_OR_RELABEL_STRETCH` |
| `x0.080_vanilla` | `coded_candidate_gate` | `max_instant_velocity_limit_excess_rad_s` | lte 0.0 | 3.239999294281006 | `False` | `RELAX_TO_BASELINE_OR_RELABEL_STRETCH` |
| `x0.080_vanilla` | `coded_candidate_gate` | `max_abs_body_pitch_p95_rad` | lte 0.25 | 0.07916602437068551 | `True` | `None` |
| `x0.080_vanilla` | `coded_candidate_gate` | `min_base_height_m` | gte 0.12 | 0.14513236284255981 | `True` | `None` |
| `x0.080_vanilla` | `coded_candidate_gate` | `min_reward_mean` | gte 0.3 | 0.5606631521582603 | `True` | `None` |
| `x0.080_vanilla` | `coded_candidate_gate` | `min_seed_track_ratio` | gte 0.25 | 0.8087895926461595 | `True` | `None` |
| `x0.080_vanilla` | `documented_promotion_x008` | `duration_complete_count` | eq 8 | 8 | `True` | `None` |
| `x0.080_vanilla` | `documented_promotion_x008` | `fall_count` | eq 0 | 0 | `True` | `None` |
| `x0.080_vanilla` | `documented_promotion_x008` | `mean_track_ratio` | gte 0.5 | 0.8705731370908173 | `True` | `None` |
| `x0.080_vanilla` | `documented_promotion_x008` | `max_pitch_tracking_p95_rad` | lte 0.2 | 0.20788586139678955 | `False` | `RELAX_TO_BASELINE_OR_RELABEL_STRETCH` |
| `x0.080_vanilla` | `documented_promotion_x008` | `max_p95_velocity_limit_excess_rad_s` | lte 0.0 | 2.489999294281006 | `False` | `RELAX_TO_BASELINE_OR_RELABEL_STRETCH` |
| `x0.080_fitted` | `coded_candidate_gate` | `max_action_saturation_pct` | lte 1.0 | 0.4 | `True` | `None` |
| `x0.080_fitted` | `coded_candidate_gate` | `max_pitch_tracking_p95_rad` | lte 0.2 | 0.2668792486190796 | `False` | `RELAX_TO_BASELINE_OR_RELABEL_STRETCH` |
| `x0.080_fitted` | `coded_candidate_gate` | `max_p95_velocity_limit_excess_rad_s` | lte 0.0 | 2.489999294281006 | `False` | `RELAX_TO_BASELINE_OR_RELABEL_STRETCH` |
| `x0.080_fitted` | `coded_candidate_gate` | `max_instant_velocity_limit_excess_rad_s` | lte 0.0 | 3.239999294281006 | `False` | `RELAX_TO_BASELINE_OR_RELABEL_STRETCH` |
| `x0.080_fitted` | `coded_candidate_gate` | `max_abs_body_pitch_p95_rad` | lte 0.25 | 0.10597808050713095 | `True` | `None` |
| `x0.080_fitted` | `coded_candidate_gate` | `min_base_height_m` | gte 0.12 | 0.14522682130336761 | `True` | `None` |
| `x0.080_fitted` | `coded_candidate_gate` | `min_reward_mean` | gte 0.3 | 0.49071075677871706 | `True` | `None` |
| `x0.080_fitted` | `coded_candidate_gate` | `min_seed_track_ratio` | gte 0.25 | 0.3588247251874842 | `True` | `None` |
| `x0.080_fitted` | `documented_promotion_x008` | `duration_complete_count` | eq 8 | 8 | `True` | `None` |
| `x0.080_fitted` | `documented_promotion_x008` | `fall_count` | eq 0 | 0 | `True` | `None` |
| `x0.080_fitted` | `documented_promotion_x008` | `mean_track_ratio` | gte 0.5 | 0.47432319636616666 | `False` | `RELAX_TO_BASELINE_OR_RELABEL_STRETCH` |
| `x0.080_fitted` | `documented_promotion_x008` | `max_pitch_tracking_p95_rad` | lte 0.2 | 0.2668792486190796 | `False` | `RELAX_TO_BASELINE_OR_RELABEL_STRETCH` |
| `x0.080_fitted` | `documented_promotion_x008` | `max_p95_velocity_limit_excess_rad_s` | lte 0.0 | 2.489999294281006 | `False` | `RELAX_TO_BASELINE_OR_RELABEL_STRETCH` |

## Required context

- `docs/DUCK_STATUS.md` records that a step-0 random-init export passed x=0.0 while every trained checkpoint from step 153600 onward failed it. This is an objective diagnostic, not a numeric gate modification.
- This offline table does not deploy a policy or authorize robot testing.
