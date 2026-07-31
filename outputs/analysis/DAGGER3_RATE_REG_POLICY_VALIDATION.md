# DAgger-3 Rate-Reg Policy Validation

status: `HOLD_DAGGER3_TRACKING_RATE_REGRESSION`

This is an offline validation artifact. It did not SSH, deploy, run robot
tests, or change robot runtime behavior.

## Inputs

The DAgger-3 manifest adds the rate-reg DAgger-2 standard-evaluator visited
states relabeled by the blend teacher:

```text
relabel artifact: outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER2_RATE_REG_STANDARD_RELABEL_BLEND.md
manifest: outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER3_MANIFEST.md
dataset_id: 80ea809b021b6b9a
entries: 25
samples: 9268
```

The resulting MLP smoke exported:

```text
outputs/analysis/source_vx_selector_trace_dagger3_mlp128_rate_reg_candidate/candidate.onnx
```

BC smoke:

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER3_MLP128_RATE_REG_ONNX_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
```

## Standard Gate

Strict task-matched standard evaluator:

```text
outputs/analysis/DEPLOYABLE_SOURCE_VX_DAGGER3_RATE_REG_VALIDATION_FITTED_BACKLASH.md
outputs/analysis/deployable_source_vx_dagger3_rate_reg_validation_fitted_backlash.json
task: flat_terrain_backlash
command: straight x=0.08
bridge: fitted
duration: 10s
seeds: 0-7
```

Result:

| policy | runs | falls | duration complete | mean vx | mean track ratio | sent vel p95 range | tracking p95 range | result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `dagger3_rate_reg` | 8 | 0 | 8 | 0.0420 | 0.5255 | 3.7121-3.8488 | 0.2623-0.2767 | `HOLD_CANDIDATE_TRACKING` |

## Comparison

Compared with the DAgger-2 rate-reg standard gate:

```text
DAgger-2 rate-reg:
  mean vx: 0.0364 m/s
  mean track ratio: 0.4550
  sent vel p95: 3.6172-3.6824 rad/s
  tracking p95: 0.2419-0.2472 rad

DAgger-3 rate-reg:
  mean vx: 0.0420 m/s
  mean track ratio: 0.5255
  sent vel p95: 3.7121-3.8488 rad/s
  tracking p95: 0.2623-0.2767 rad
```

DAgger-3 improves command tracking but regresses target-rate and tracking
margin. It is not a promotion candidate.

## Decision

Do not run stress bridge or robot validation.

The next deployable-policy step should target the same tradeoff more directly:

```text
increase on-policy coverage without reintroducing target-rate spikes
make tracking/target-rate part of the student objective or PPO fine-tuning loop
rerun the task-matched fitted gate before stress or robot gates
```

This result supports a PPO-from-BC/warm-start branch more than another pure BC
relabel pass: the supervised DAgger path can move the progress/rate point along
the curve, but the fitted actuator tracking remains far outside the gate.
