# MLP Router Branch Trace

status: `PASS_ROUTER_BRANCH_B_NOT_DOMINANT`

Offline trace diagnostic only. It did not train, deploy, SSH, run robot tests, change runtime behavior, or run grounded replay.

## Inputs

- trace: `outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_tneg2_candidate_seed0_trace/full8_mlp_router_seed0_seed5_startup_cost_wide_tneg2/seed_000/trace.jsonl`
- gate_npz: `outputs/analysis/phase2_full8_mlp_router_gate_seed0_seed5_startup_cost_wide/gate_mlp.npz`
- samples: `166`
- termination: `fall_or_nan`

## Branch Selection

| window | samples | branch_b_pct | logit_p05 | logit_p50 | logit_p95 |
|---|---:|---:|---:|---:|---:|
| all | 166 | 39.75903614457831 | -5.904576413323957 | -1.4842543557500343 | 33.26315876461686 |
| first_ticks | 80 | 7.5 | -5.943177042625944 | -2.2019719059401712 | 0.7819168309550112 |
| tail_ticks | 80 | 70.0 | -5.8917059107712175 | 4.319596163689722 | 41.441923211499635 |
| push_ticks | 2 | 0.0 | -5.157053757695859 | -3.408747753309626 | -1.6604417489233931 |
| single_support | 18 | 50.0 | -7.023568676991724 | 0.12820149994424557 | 53.59429255960712 |
| double_support | 146 | 37.67123287671233 | -5.587754585591311 | -1.516678423734601 | 14.293888467044335 |
| reverse_vx | 26 | 19.230769230769234 | -6.784650608132602 | -2.6528749364542428 | 6.727715365537406 |

## Outcome

- mean_vx_m_s: `0.1265`
- base_height_min_m: `0.0083`
- body_pitch_abs_p95_rad: `0.8282`

## Decision

The failed trace is not dominated by branch B selection; debug the branch-A policy dynamics or mixed transition instead.
