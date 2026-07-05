# Full-8 Router Source Rich-Context Parent Decision

status: `HOLD_FULL8_RICH_CONTEXT_PARENT_SEED5_LUNGE`

The full-8 selected source fits cleanly but does not compress into a single static rich-context phase-modulated parent; seed 5 still lunges/falls under the hard screen.

This is offline behavior-preservation evidence. It did not train PPO/DR, deploy, SSH, run robot tests, grounded replay, or change runtime behavior.

## Inputs

- source_manifest: `outputs/analysis/phase2_full8_router_source_selected_manifest.json`
- train_report: `outputs/analysis/phase2_full8_router_source_rich_context_parent.json`
- candidate_onnx: `outputs/analysis/phase2_full8_router_source_rich_context_parent/candidate.onnx`
- candidate_onnx_sha256: `9891f1927ab3f6e8c6a6c9a2dfcfb0fe06873a26c068840f1c1b818360a75fe1`
- gate: `outputs/analysis/phase2_full8_router_source_rich_context_parent_x008_seed0_5_7_gate.json`

## Fit

- fit_status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`
- samples: `6000`
- MAE: `0.001977`
- p95_abs_error: `0.005375`
- target_rate_p95_rad_s: `1.4451`
- target_rate_max_rad_s: `1.8839`
- ONNX max_abs_error: `0.00000030`

## Gate Result

- seeds: `[0, 5, 7]`
- pass_count: `2/3`
- falls: `1`
- mean_vx_m_s: `0.0654`
- mean_track_ratio: `0.8178`
- max_p95_velocity_excess_rad_s: `0.0000`
- max_instant_velocity_excess_rad_s: `0.0000`

| seed | status | samples | termination | vx | track_ratio | pitch_p95 | base_min | p95_excess | max_excess |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0264 | 0.3306 | 0.2130 | 0.1582 | 0.0000 | 0.0000 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 149 | `fall_or_nan` | 0.1421 | 1.7761 | 0.8855 | 0.0014 | 0.0000 | 0.0000 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0277 | 0.3468 | 0.1729 | 0.1582 | 0.0000 | 0.0000 |

## Decision

Do not promote this parent and do not launch Phase 2 DR from it. The selected-source route works as separate branch behavior, but static rich-context compression still loses the seed-5 stabilizing branch.

## Next Recommendation

Move to an explicit branch-preserving wrapper/router objective or trainable mixture that keeps the seed-5 branch separate through the gate, then distill only after the wrapper clears full-8 and x=0.0 semantics.
