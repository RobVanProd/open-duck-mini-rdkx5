# MLP Router Branch Trace

status: `PASS_ROUTER_BRANCH_B_NOT_DOMINANT`

Offline trace diagnostic only. It did not train, deploy, SSH, run robot tests, change runtime behavior, or run grounded replay.

## Inputs

- trace: `outputs/analysis/phase2_full8_mlp_router_seed0_startup_cost_candidate_seed5_trace/full8_mlp_router_seed0_startup_cost/seed_005/trace.jsonl`
- gate_npz: `outputs/analysis/phase2_full8_mlp_router_gate_seed0_startup_cost/gate_mlp.npz`
- samples: `158`
- termination: `fall_or_nan`

## Branch Selection

| window | samples | branch_b_pct | logit_p05 | logit_p50 | logit_p95 |
|---|---:|---:|---:|---:|---:|
| all | 158 | 25.949367088607595 | -13.94036068004743 | -5.030895495888174 | 13.07900935863668 |
| first_ticks | 80 | 0.0 | -15.969441455654147 | -8.154880517633169 | -2.693205070488663 |
| tail_ticks | 80 | 51.24999999999999 | -7.221162926112594 | 0.33677540305341547 | 19.96930667557483 |
| push_ticks | 2 | 0.0 | -11.403206488043768 | -6.265330782484366 | -1.1274550769249627 |
| single_support | 20 | 70.0 | -9.754130205099537 | 3.4254657231104915 | 24.31699885350145 |
| double_support | 137 | 18.97810218978102 | -14.43190302217698 | -5.400439298891568 | 6.931203161821955 |
| reverse_vx | 21 | 0.0 | -13.134469525516558 | -6.885820469146296 | -4.411211703260701 |

## Outcome

- mean_vx_m_s: `0.1298`
- base_height_min_m: `0.0149`
- body_pitch_abs_p95_rad: `0.8237`

## Decision

The failed trace is not dominated by branch B selection; debug the branch-A policy dynamics or mixed transition instead.
