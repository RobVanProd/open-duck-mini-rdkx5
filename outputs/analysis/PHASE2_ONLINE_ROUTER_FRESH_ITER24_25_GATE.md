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
- policies: `iter24, iter25`

## Routed Gate

| seed | selected policy | selected status | raw score | adjusted score | pass | track ratio | mean vx | pitch p95 | base min |
|---:|---|---|---:|---:|---|---:|---:|---:|---:|
| `0` | `iter24` | `PASS_CANDIDATE_SIM_GATE` | `1.0` | `1.0` | `True` | `0.3256336280421237` | `0.0260506902433699` | `0.1922094015681199` | `0.15907274186611176` |
| `1` | `iter25` | `PASS_CANDIDATE_SIM_GATE` | `0.731299427218782` | `0.7169362038951852` | `True` | `0.3566823099642837` | `0.028534584797142694` | `0.17388582504197614` | `0.15785591304302216` |
| `2` | `iter24` | `PASS_CANDIDATE_SIM_GATE` | `1.0` | `1.0` | `True` | `0.327782184196379` | `0.02622257473571032` | `0.1822142898701311` | `0.1590012162923813` |
| `6` | `iter24` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `1.0` | `0.9647670788586329` | `False` | `-0.5659199241796159` | `-0.04527359393436927` | `0.2186703042891423` | `0.06904956698417664` |
| `7` | `iter24` | `PASS_CANDIDATE_SIM_GATE` | `1.0` | `1.0` | `True` | `0.3437347055155138` | `0.02749877644124111` | `0.186292488087811` | `0.15648280084133148` |

## Candidate Scores

### Seed `0`

| policy | raw score | adjusted score | pass | status | prefix pitch max | track ratio |
|---|---:|---:|---|---|---:|---:|
| `iter24` | `1.0` | `1.0` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.18545603452916268` | `0.3256336280421237` |
| `iter25` | `0.7033081684918515` | `0.7033081684918515` | `False` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `0.18817862702090807` | `0.7229463779811859` |

### Seed `1`

| policy | raw score | adjusted score | pass | status | prefix pitch max | track ratio |
|---|---:|---:|---|---|---:|---:|
| `iter24` | `0.6319068078364075` | `0.611904764693155` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.22000204314325247` | `0.3584399078651586` |
| `iter25` | `0.731299427218782` | `0.7169362038951852` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.21436322332359692` | `0.3566823099642837` |

### Seed `2`

| policy | raw score | adjusted score | pass | status | prefix pitch max | track ratio |
|---|---:|---:|---|---|---:|---:|
| `iter24` | `1.0` | `1.0` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.18545603452916268` | `0.327782184196379` |
| `iter25` | `0.355176262565284` | `0.355176262565284` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.18817862702090807` | `0.38158110062725725` |

### Seed `6`

| policy | raw score | adjusted score | pass | status | prefix pitch max | track ratio |
|---|---:|---:|---|---|---:|---:|
| `iter24` | `1.0` | `0.9647670788586329` | `False` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `0.23523292114136707` | `-0.5659199241796159` |
| `iter25` | `0.7483041725777821` | `0.7261404006779422` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.22216377189983993` | `0.32731479393599633` |

### Seed `7`

| policy | raw score | adjusted score | pass | status | prefix pitch max | track ratio |
|---|---:|---:|---|---|---:|---:|
| `iter24` | `1.0` | `1.0` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.19690431260364002` | `0.3437347055155138` |
| `iter25` | `1.0` | `1.0` | `False` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `0.19456532614450173` | `0.8326688606868939` |

## Next

- Do not launch Phase 2 DR.
- Inspect failed routed seeds before adding router complexity.
