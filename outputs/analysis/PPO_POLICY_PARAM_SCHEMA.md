# PPO Policy Param Schema

status: `PASS_PPO_BC_SCHEMA_COMPATIBLE`

This is an offline schema inspection artifact. It did not train, deploy,
SSH, run robot tests, or change robot runtime behavior.

## PPO Contract

- observation size: `101`
- privileged observation size: `212`
- action size: `14`
- policy hidden sizes: `[512, 256, 128]`
- value hidden sizes: `[512, 256, 128]`
- distribution type: `tanh_normal`
- policy output size: `28`

The actor output is a tanh-normal distribution parameter vector. The
export path splits it into action location and scale logits, then exports
`tanh(loc)` as `continuous_actions`.

```text
hidden_3[:, 0:14]  -> action loc / deployable ONNX action before tanh
hidden_3[:, 14:28] -> scale logits for PPO exploration
```

## Policy Param Shapes

| param | shape | dtype |
|---|---:|---|
| `params/hidden_0/kernel` | `[101, 512]` | `float32` |
| `params/hidden_0/bias` | `[512]` | `float32` |
| `params/hidden_1/kernel` | `[512, 256]` | `float32` |
| `params/hidden_1/bias` | `[256]` | `float32` |
| `params/hidden_2/kernel` | `[256, 128]` | `float32` |
| `params/hidden_2/bias` | `[128]` | `float32` |
| `params/hidden_3/kernel` | `[128, 28]` | `float32` |
| `params/hidden_3/bias` | `[28]` | `float32` |

## Value Param Shapes

| param | shape | dtype |
|---|---:|---|
| `params/hidden_0/kernel` | `[212, 512]` | `float32` |
| `params/hidden_0/bias` | `[512]` | `float32` |
| `params/hidden_1/kernel` | `[512, 256]` | `float32` |
| `params/hidden_1/bias` | `[256]` | `float32` |
| `params/hidden_2/kernel` | `[256, 128]` | `float32` |
| `params/hidden_2/bias` | `[128]` | `float32` |
| `params/hidden_3/kernel` | `[128, 1]` | `float32` |
| `params/hidden_3/bias` | `[1]` | `float32` |

## BC NPZ

- path: `outputs/analysis/source_vx_selector_trace_dagger3_mlp512_256_128_rate_reg_candidate/candidate_mlp.npz`
- hidden sizes: `[512, 256, 128]`

| key | shape | dtype |
|---|---:|---|
| `norm` | `[2, 101]` | `float32` |
| `hidden_sizes` | `[3]` | `int64` |
| `w0` | `[101, 512]` | `float32` |
| `b0` | `[512]` | `float32` |
| `w1` | `[512, 256]` | `float32` |
| `b1` | `[256]` | `float32` |
| `w2` | `[256, 128]` | `float32` |
| `b2` | `[128]` | `float32` |
| `w3` | `[128, 14]` | `float32` |
| `b3` | `[14]` | `float32` |

## Compatibility

- hidden layers match: `True`
- output loc branch matches BC action output: `True`
- normalizer shape compatible: `True`

Recommended mapping:

```text
normalizer.mean['state'] <- bc.norm[0]
normalizer.std['state']  <- bc.norm[1]
policy.params.hidden_0   <- bc.w0/b0
policy.params.hidden_1   <- bc.w1/b1
policy.params.hidden_2   <- bc.w2/b2
policy.params.hidden_3[:, 0:14]  <- bc.w3/b3
policy.params.hidden_3[:, 14:28] <- fresh scale logits
value network <- fresh PPO init
```

## Decision

Do not train from this schema alone. The next gate is a step-0 fidelity
test that initializes PPO params from the BC NPZ, evaluates the resulting
deterministic policy, and proves it matches the BC candidate before any
PPO updates.
