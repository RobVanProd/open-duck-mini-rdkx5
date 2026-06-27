# PPO-Shape BC Warm-Start Candidate

status: `HOLD_PPO_SHAPE_TRACKING_GATE`

This is an offline analysis artifact. It did not SSH, deploy, run robot tests,
start PPO training, or change robot runtime behavior.

## Purpose

The DAgger-3 128x128 rate-reg student proved that a compact exported neural
student can preserve source-VX forward motion, but its hidden sizes do not match
the local Playground PPO policy network. The PPO policy network uses:

```text
policy_hidden_layer_sizes: (512, 256, 128)
value_hidden_layer_sizes: (512, 256, 128)
```

This artifact records a BC student trained with the PPO policy hidden-layer
shape so the next branch can focus on PPO warm-start parameter mapping instead
of guessing across architectures.

## Inputs

Manifest:

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER3_MANIFEST.md
dataset_id: 80ea809b021b6b9a
entries: 25
samples: 9268
```

PPO-shape BC candidate:

```text
outputs/analysis/source_vx_selector_trace_dagger3_mlp512_256_128_rate_reg_candidate/candidate.onnx
outputs/analysis/source_vx_selector_trace_dagger3_mlp512_256_128_rate_reg_candidate/candidate_mlp.npz
```

NPZ shape:

```text
norm: (2, 101)
w0/b0: (101,512) / (512,)
w1/b1: (512,256) / (256,)
w2/b2: (256,128) / (128,)
w3/b3: (128,14) / (14,)
```

## BC Smoke

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER3_MLP512_256_128_RATE_REG_ONNX_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
```

Smoke result:

```text
runs: 8
duration complete: 8
falls: 0
mean vx: about 0.0395 m/s
mean track ratio: about 0.494
smoke sent-target velocity p95: about 2.19-2.24 rad/s
smoke tracking p95: about 0.183-0.187 rad
```

## Standard Gate

Strict task-matched fitted bridge gate:

```text
outputs/analysis/DEPLOYABLE_SOURCE_VX_DAGGER3_PPO_SHAPE_VALIDATION_FITTED_BACKLASH.md
outputs/analysis/deployable_source_vx_dagger3_ppo_shape_validation_fitted_backlash.json
task: flat_terrain_backlash
command: straight x=0.08
bridge: fitted
duration: 10s
seeds: 0-7
```

Result:

| policy | runs | falls | duration complete | mean vx | mean track ratio | sent vel p95 range | tracking p95 range | result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `dagger3_ppo_shape` | 8 | 0 | 8 | 0.0396 | 0.4953 | 3.7842-3.8409 | 0.2570-0.2684 | `HOLD_CANDIDATE_TRACKING` |

## Comparison

Compared with the DAgger-3 128x128 rate-reg standard gate:

```text
DAgger-3 128x128 rate-reg:
  mean vx: 0.0420 m/s
  mean track ratio: 0.5255
  sent vel p95: 3.7121-3.8488 rad/s
  tracking p95: 0.2623-0.2767 rad

DAgger-3 PPO-shape 512/256/128 rate-reg:
  mean vx: 0.0396 m/s
  mean track ratio: 0.4953
  sent vel p95: 3.7842-3.8409 rad/s
  tracking p95: 0.2570-0.2684 rad
```

The PPO-shape student is not a better policy candidate. It is slightly lower on
forward progress, similar on target rate, and slightly better on fitted
tracking. Its value is that its hidden-layer shape matches the PPO policy
network, making it the current best substrate for warm-start plumbing.

## Evaluation Discrepancy To Resolve

The BC smoke and standard candidate gate disagree on target velocity and
tracking:

```text
BC smoke sent-target velocity p95: about 2.19-2.24 rad/s
standard gate sent-target velocity p95: 3.7842-3.8409 rad/s

BC smoke tracking p95: about 0.183-0.187 rad
standard gate tracking p95: 0.2570-0.2684 rad
```

Before trusting a PPO step-0 warm-start fidelity gate, compare the smoke replay
path and `run_candidate_seed_sweep.py` path for:

```text
normalization
action scaling
task/reset selection
target-stage instrumentation
bridge insertion point
rate-limit accounting
```

Do not start PPO until this mismatch is understood or the step-0 fidelity gate
uses exactly the same evaluator as the standard candidate gate.

## Decision

This candidate is not robot-ready and should not be sent through stress or robot
validation.

Next branch:

```text
PLAN_PPO_WARMSTART_PLUMBING_WITH_PPO_SHAPE_BC
```

Required next work:

```text
inspect PPO policy param PyTree
map PPO-shape BC weights into the policy mean network
initialize exploration/stddev parameters deliberately
leave value network freshly initialized
export or evaluate step-0 PPO policy
compare step-0 actions and closed-loop behavior against the PPO-shape BC ONNX
```

Stop if the initialized PPO policy does not reproduce the BC candidate before
any training updates.
