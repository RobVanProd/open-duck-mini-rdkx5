# Phase 2 Command-Gated Zero0020 Full-8 Source Decision

status: `HOLD_COMMAND_GATED_SOURCE_SEED5_FORWARD_LUNGE`

This is offline analysis only. It did not train, SSH, deploy, run robot tests, run grounded replay, or change runtime behavior.

## Candidate

- policy: `policy/candidates/phase2_parent_pair_lateral_seed7_weighted_command_gated_zero0020_20260705/candidate.onnx`
- policy_sha256: `f3d5d735e96cf88bfe037bd4c6c1289eebc5d25bcc7722416f62dcee292866d0`

## Full x=0.08 z=0.0075 Rough+Push Gate

- gate_md: `outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_FULL8_X008_Z0075_PUSH_GATE.md`
- gate_json: `outputs/analysis/phase2_command_gated_zero0020_full8_x008_z0075_push_gate.json`
- pass_count: `7/8`
- fall_count: `1`
- duration_complete_count: `7`
- mean_vx_m_s: `0.0393`
- mean_track_ratio: `0.4907`
- mean_single_support_pct: `21.4700`
- mean_double_support_pct: `78.2926`
- max_p95_velocity_excess_rad_s: `0.0000`
- max_instant_velocity_excess_rad_s: `0.0000`
- max_tracking_p95_rad: `0.1977`

| seed | status | samples | vx | track_ratio | pitch_p95 | height_min | vel_excess_p95 | max_tracking_p95 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0272 | 0.3403 | 0.1737 | 0.1581 | 0.0000 | 0.1859 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0254 | 0.3170 | 0.1876 | 0.1581 | 0.0000 | 0.1907 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0269 | 0.3367 | 0.1894 | 0.1581 | 0.0000 | 0.1888 |
| 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0238 | 0.2975 | 0.1776 | 0.1581 | 0.0000 | 0.1860 |
| 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0244 | 0.3052 | 0.1830 | 0.1581 | 0.0000 | 0.1835 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 158 | 0.1367 | 1.7083 | 0.8743 | -0.0058 | 0.0000 | 0.1977 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0232 | 0.2896 | 0.1917 | 0.1581 | 0.0000 | 0.1868 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0265 | 0.3311 | 0.1724 | 0.1581 | 0.0000 | 0.1895 |

## Seed 5 Failure

- failure_trace_md: `outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_SEED5_FAILURE_TRACE.md`
- failure_trace_json: `outputs/analysis/phase2_command_gated_zero0020_seed5_failure_trace.json`
- failure_mode_md: `outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_SEED5_FAILURE_MODE.md`
- trace_analysis_md: `outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_SEED5_TRACE_ANALYSIS.md`
- mode: `FORWARD_LUNGE_PITCHOVER`
- trace_failure_surface: `HEIGHT_COLLAPSE`
- reasons: `['forward_lunge_velocity', 'pitch_forward', 'low_base_height']`
- first_reverse_tick: `45`
- first_low_height_tick: `150`
- first_done_tick: `157`
- seed5_track_ratio: `1.7083`
- seed5_body_pitch_p95_rad: `0.8743`
- seed5_max_pitch_vel_p95_rad_s: `1.5927`
- seed5_p95_velocity_excess_rad_s: `0.0000`

## Decision

`HOLD_COMMAND_GATED_SOURCE_SEED5_FORWARD_LUNGE`

The graph-level command-gated candidate is a useful 7/8 in-envelope behavior source, but it is not full-stage robust. The compact five-seed gate missed seed 5. Seed 5 fails by over-progressing into a forward lunge/pitchover while staying inside the corrected velocity envelope.

Do not use this compact-pass candidate as a full Phase 2 source without a seed-5 recovery branch or a router/wrapper source that covers seed 5. Since x=0.08 already fails full 8, the x=0.0 full-8 gate was not rerun for this decision.
