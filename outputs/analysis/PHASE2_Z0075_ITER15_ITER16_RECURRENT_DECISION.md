# Phase 2 z=0.0075 Iter15/Iter16 Recurrent Diagnostic Decision

status: `HOLD_RECURRENT_BC_STABILIZES_BY_STANDSTILL`

This is offline sim/analysis only. It did not SSH, deploy, run robot tests,
grounded replay, or change runtime behavior.

## Question

Iter14 showed that a global action-gain reduction is too blunt: gain `0.95`
fixes the seed0 first-push lunge but regresses seed6 late in the run, and a
feed-forward student trained on the gain-0.95 seed0 pass trace does not transfer
that recovery behavior. The next question was whether a small stateful student
can distinguish these histories better than a memoryless map.

These recurrent ONNX exports are diagnostic only:

```text
inputs:  obs[1,101], h_in[1,96]
outputs: continuous_actions[1,14], h_out[1,96]
```

They are not robot-deployable without a runtime hidden-state adapter.

## Inputs

- manifest: `outputs/analysis/phase2_z0075_iter14_gain095_seed0_pass_merged_manifest.json`
- condition: rough `z=0.0075`, `home-support`, x=`0.08`, corrected fitted bridge, intermediate pushes
- fail/control seeds: `0,2,6`

## Iter15: Recurrent H96 S32 Rate150

- exported ONNX: `outputs/analysis/phase2_z0075_iter15_recurrent_h96_s32_rate150_candidate/candidate.onnx`
- ONNX sha256: `705b37c0c8da6c0d0445e388fb4337c1076eb546a1abf1b1427eefa5594377a6`
- NPZ sha256: `a2702d9e282663d24332dc1cd97776cc1680737412c0bc8f61fa1c17cdb19c5b`
- target-rate scale: `0.1`
- target-rate limit: `1.5 rad/s`

Fail-seed gate:

| seed | status | samples | mean vx | track ratio | pitch p95 | base min | p95 excess | max excess | single support | push success |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | 0.0014 | 0.0172 | 0.1030 | 0.1532 | 0.0000 | 2.7400 | 0.0000 | 0.9167 |
| 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | 0.0014 | 0.0180 | 0.1686 | 0.1532 | 0.0000 | 3.1175 | 0.0000 | 0.9231 |
| 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | 0.0012 | 0.0155 | 0.1038 | 0.1532 | 0.0000 | 2.7400 | 0.0000 | 0.9231 |

## Iter16: Recurrent H96 S32 Soft Rate Penalty

- exported ONNX: `outputs/analysis/phase2_z0075_iter16_recurrent_h96_s32_rate150_soft_candidate/candidate.onnx`
- ONNX sha256: `735f35fc91a0493006587ca19b64c34c2995441ef29f3f7dad4cb03594942459`
- NPZ sha256: `e9213a9ed3e25815cb7272ec1841d0b742e183e0ae1e5bfb9d23b55bdaff1e3d`
- target-rate scale: `0.02`
- target-rate limit: `1.5 rad/s`

Fail-seed gate:

| seed | status | samples | mean vx | track ratio | pitch p95 | base min | p95 excess | max excess | single support | push success |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | 0.0012 | 0.0156 | 0.0782 | 0.1533 | 0.0000 | 0.2905 | 0.0000 | 0.9167 |
| 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | 0.0010 | 0.0127 | 0.0727 | 0.1533 | 0.0000 | 0.2905 | 0.0000 | 0.9231 |
| 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | 0.0010 | 0.0129 | 0.0684 | 0.1533 | 0.0000 | 0.2905 | 0.0000 | 0.9231 |

## Decision

`HOLD_RECURRENT_BC_STABILIZES_BY_STANDSTILL`

The recurrent representation prevents the seed0 first-push lunge, but it does so
by converging to double-support standstill. Reducing the recurrent rate penalty
does not restore forward motion; it makes the standstill even quieter.

This falsifies "naive recurrent BC on the current manifest is enough." It does
not falsify state/history as useful, because the model demonstrably changes the
failure surface from lunge/fall to stable standstill. It does mean the next
branch needs a motion-preserving signal, not merely more hidden state.

## Next Recommendation

Do not add a runtime recurrent adapter from these artifacts. Do not promote
Iter15 or Iter16.

Next aligned options:

1. Add an explicit motion-preserving term or sampling balance to the recurrent
   BC objective so hidden state cannot satisfy the loss by double support.
2. Train a deployable feed-forward wrapper/classifier that attenuates only the
   seed0 first-push lunge state, with seeds 2 and 6 as hard pass controls.
3. If using live-oracle DAgger again, aggregate on-policy drift states from both
   sides of the tradeoff: full-gain seed0 lunge, gain-0.95 seed0 pass, and
   gain-0.95 seed6 late collapse.

The corrected actuator envelope remains fixed. Robot validation remains blocked.
