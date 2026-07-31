# Phase 2 Health-Gated Router Gate

status: `HOLD_HEALTH_GATED_ROUTER_PARTIAL`

## Executive Summary

The health-gated router improves coverage but does not clear all compact seeds.

This is offline eval-only analysis. It did not train, SSH, deploy, run robot tests, change runtime behavior, or run grounded replay. Seed ID is not used as a routing feature.

## Router Config

- prefix_ticks: `100`
- knn_k: `3`
- policy_onehot_scale: `5.0`
- pitch_guard_limit_rad: `0.2`
- pitch_guard_scale: `1.0`
- target_track_ratio: `0.35`
- policies: `phase_mod_parent, rich_context_parent`

## Routed Gate

| seed | selected policy | selected status | raw score | adjusted score | pass | track ratio | mean vx | pitch p95 | base min |
|---:|---|---|---:|---:|---|---:|---:|---:|---:|
| `0` | `rich_context_parent` | `PASS_CANDIDATE_SIM_GATE` | `1.0` | `1.0` | `True` | `0.2896584582947374` | `0.023172676663578994` | `0.16610380076586062` | `0.15913419425487518` |
| `1` | `rich_context_parent` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `1.0` | `0.9926103048396793` | `False` | `1.727580875234233` | `0.13820647001873865` | `0.9035911121795815` | `-0.008957752026617527` |
| `2` | `rich_context_parent` | `PASS_CANDIDATE_SIM_GATE` | `1.0` | `1.0` | `True` | `0.2972285583576498` | `0.023778284668611982` | `0.17632146413894684` | `0.15685239434242249` |
| `6` | `phase_mod_parent` | `PASS_CANDIDATE_SIM_GATE` | `0.7235357311613375` | `0.6653722736749925` | `True` | `0.300907877489711` | `0.02407263019917688` | `0.18496016379104316` | `0.15717685222625732` |
| `7` | `phase_mod_parent` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `1.0` | `1.0` | `False` | `-0.523555816495597` | `-0.04188446531964776` | `0.17802859236138668` | `0.06727110594511032` |

## Candidate Scores

### Seed `0`

| policy | raw score | adjusted score | pass | status | prefix pitch max | track ratio |
|---|---:|---:|---|---|---:|---:|
| `phase_mod_parent` | `1.0` | `1.0` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.18644794142319335` | `0.2716031985068791` |
| `rich_context_parent` | `1.0` | `1.0` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.1869061640270405` | `0.2896584582947374` |

### Seed `1`

| policy | raw score | adjusted score | pass | status | prefix pitch max | track ratio |
|---|---:|---:|---|---|---:|---:|
| `phase_mod_parent` | `1.0` | `0.9805865732478095` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.2194134267521905` | `0.32303653006335176` |
| `rich_context_parent` | `1.0` | `0.9926103048396793` | `False` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `0.20738969516032077` | `1.727580875234233` |

### Seed `2`

| policy | raw score | adjusted score | pass | status | prefix pitch max | track ratio |
|---|---:|---:|---|---|---:|---:|
| `phase_mod_parent` | `0.6863587842136767` | `0.6863587842136767` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.18644794142319335` | `0.3284647713124286` |
| `rich_context_parent` | `1.0` | `1.0` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.18937902820604802` | `0.2972285583576498` |

### Seed `6`

| policy | raw score | adjusted score | pass | status | prefix pitch max | track ratio |
|---|---:|---:|---|---|---:|---:|
| `phase_mod_parent` | `0.7235357311613375` | `0.6653722736749925` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.25816345748634495` | `0.300907877489711` |
| `rich_context_parent` | `0.6100451798888803` | `0.5840098183282235` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.2260353615606568` | `0.31582110675808506` |

### Seed `7`

| policy | raw score | adjusted score | pass | status | prefix pitch max | track ratio |
|---|---:|---:|---|---|---:|---:|
| `phase_mod_parent` | `1.0` | `1.0` | `False` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `0.19411931007049268` | `-0.523555816495597` |
| `rich_context_parent` | `0.6163166918998642` | `0.6163166918998642` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.1897310259148833` | `0.33022713751136806` |

## Next

- Do not launch Phase 2 DR.
- Inspect failed routed seeds before adding router complexity.
