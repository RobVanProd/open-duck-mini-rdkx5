# Phase 2 Health-Gated Router Gate

status: `PASS_HEALTH_GATED_ROUTER_COMPACT`

## Executive Summary

The eval-only speculative health-gated router selects a passing branch for every compact z=0.0075 rough+push seed from prefix-observable data.

This is offline eval-only analysis. It did not train, SSH, deploy, run robot tests, change runtime behavior, or run grounded replay. Seed ID is not used as a routing feature.

## Router Config

- prefix_ticks: `100`
- knn_k: `3`
- policy_onehot_scale: `5.0`
- pitch_guard_limit_rad: `0.2`
- pitch_guard_scale: `1.0`
- target_track_ratio: `0.35`
- policies: `iter24, iter25, iter26, iter27`

## Routed Gate

| seed | selected policy | selected status | raw score | adjusted score | pass | track ratio | mean vx | pitch p95 | base min |
|---:|---|---|---:|---:|---|---:|---:|---:|---:|
| `0` | `iter24` | `PASS_CANDIDATE_SIM_GATE` | `1.0` | `1.0` | `True` | `0.3256336280421237` | `0.0260506902433699` | `0.1922094015681199` | `0.15907274186611176` |
| `1` | `iter25` | `PASS_CANDIDATE_SIM_GATE` | `0.7380391135430341` | `0.7236758902194371` | `True` | `0.3566823099642837` | `0.028534584797142694` | `0.17388582504197614` | `0.15785591304302216` |
| `2` | `iter24` | `PASS_CANDIDATE_SIM_GATE` | `1.0` | `1.0` | `True` | `0.327782184196379` | `0.02622257473571032` | `0.1822142898701311` | `0.1590012162923813` |
| `6` | `iter25` | `PASS_CANDIDATE_SIM_GATE` | `0.7245902223395964` | `0.7024264504397564` | `True` | `0.32731479393599633` | `0.026185183514879706` | `0.19036020118540972` | `0.15800926089286804` |
| `7` | `iter24` | `PASS_CANDIDATE_SIM_GATE` | `1.0` | `1.0` | `True` | `0.3437347055155138` | `0.02749877644124111` | `0.186292488087811` | `0.15648280084133148` |

## Candidate Scores

### Seed `0`

| policy | raw score | adjusted score | pass | status | prefix pitch max | track ratio |
|---|---:|---:|---|---|---:|---:|
| `iter24` | `1.0` | `1.0` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.18545603452916268` | `0.3256336280421237` |
| `iter25` | `0.37775528568343325` | `0.37775528568343325` | `False` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `0.18817862702090807` | `0.7229463779811859` |
| `iter26` | `0.24946886860765113` | `0.24946886860765113` | `False` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `0.18764896934846298` | `0.7814772069923164` |
| `iter27` | `0.0` | `0.0` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.18746103639170672` | `0.3394942984527006` |

### Seed `1`

| policy | raw score | adjusted score | pass | status | prefix pitch max | track ratio |
|---|---:|---:|---|---|---:|---:|
| `iter24` | `0.6185981253928443` | `0.5985960822495918` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.22000204314325247` | `0.3584399078651586` |
| `iter25` | `0.7380391135430341` | `0.7236758902194371` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.21436322332359692` | `0.3566823099642837` |
| `iter26` | `0.47022433446290635` | `0.4569535719373826` | `False` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `0.21327076252552377` | `-0.0009370998738384968` |
| `iter27` | `0.22030884026748052` | `0.15387375974788972` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.2664350805195908` | `0.38298989929971866` |

### Seed `2`

| policy | raw score | adjusted score | pass | status | prefix pitch max | track ratio |
|---|---:|---:|---|---|---:|---:|
| `iter24` | `1.0` | `1.0` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.18545603452916268` | `0.327782184196379` |
| `iter25` | `0.6717679848767448` | `0.6717679848767448` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.18817862702090807` | `0.38158110062725725` |
| `iter26` | `0.3188568913680842` | `0.3188568913680842` | `False` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `0.18764896934846298` | `-0.5101039650904644` |
| `iter27` | `0.38613843255750524` | `0.38613843255750524` | `False` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `0.18841937311267293` | `-0.4822901207182487` |

### Seed `6`

| policy | raw score | adjusted score | pass | status | prefix pitch max | track ratio |
|---|---:|---:|---|---|---:|---:|
| `iter24` | `0.7188176838069882` | `0.6835847626656211` | `False` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `0.23523292114136707` | `-0.5659199241796159` |
| `iter25` | `0.7245902223395964` | `0.7024264504397564` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.22216377189983993` | `0.32731479393599633` |
| `iter26` | `0.0` | `-0.02038772111807291` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.22038772111807292` | `0.3491434641809368` |
| `iter27` | `0.7268402531931905` | `0.6793391024110571` | `False` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `0.2475011507821333` | `0.9697169494164626` |

### Seed `7`

| policy | raw score | adjusted score | pass | status | prefix pitch max | track ratio |
|---|---:|---:|---|---|---:|---:|
| `iter24` | `1.0` | `1.0` | `True` | `PASS_CANDIDATE_SIM_GATE` | `0.19690431260364002` | `0.3437347055155138` |
| `iter25` | `0.7089355037223812` | `0.7089355037223812` | `False` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `0.19456532614450173` | `0.8326688606868939` |
| `iter26` | `0.0` | `0.0` | `False` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `0.18930007326276427` | `0.9271370372924468` |
| `iter27` | `0.6285618302214923` | `0.6222560270817399` | `False` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `0.20630580313975233` | `0.014057792998319617` |

## Next

- Build a real online wrapper only if this router behavior needs to be replayed without precomputed traces.
- Do not start Phase 2 DR from the router itself; use it to generate behavior-preservation rollouts or train a single policy parent.
