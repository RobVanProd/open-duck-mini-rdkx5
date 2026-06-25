# V24 L4 Partial Run Summary

status: `HOLD_V24_TRANSITION_PROPULSION_FAILED_GATE`

## Executive Summary

`movement_bootstrap_v24` completed training on a Colab L4 and exported the
184320-step ONNX, but the x=0.04 vanilla seed gate failed before the Colab
runtime disappeared. Six seed results were recovered; all six held with
`HOLD_CANDIDATE_FALL_OR_TERMINATION`.

This is not a robot candidate. No robot tests, SSH, deployment, runtime
behavior changes, or policy deployment were performed.

## Run

- session: `open-duck-l4-v24`
- local run dir: `outputs/analysis/colab_cli/open-duck-l4-v24-staged-curriculum-20260625T165454Z`
- remote workflow: `open_duck_colab_cli_staged-curriculum_20260625T165508Z`
- recipe: `movement_bootstrap_v24`
- phase: `phase1_transition_propulsion_probe`
- training backend: CUDA / Colab L4
- training status: `PASS_SMOKE_RUN`
- gate command: `x=0.04`
- gate bridge mode: `vanilla`
- gate seeds requested: `0-7`
- gate seeds recovered: `0-5`
- remote status: `HOLD_REMOTE_NO_SENTINEL`

## Candidate

| ONNX | sha256 |
|---|---|
| `2026_06_25_170539_61440.onnx` | `09977dac836d4547dfc369fa3194c55095a7c26e4476a1811dc9b52596426483` |
| `2026_06_25_170836_122880.onnx` | `0c2480a832c27078d3129b692f37e45517edb5bc145eb18829442c0c52c017ee` |
| `2026_06_25_170843_184320.onnx` | `84bc62cffb5972711769dc4be73c7bcfc1986795d8482cc6c0b2a976d27cbf58` |

The gate evaluated the final 184320-step ONNX.

## Recovered Seed Gate

| seed | status | samples | termination | mean vx m/s | track ratio | base height min m | pitch p95 rad | pitch vel p95 rad/s | tracking p95 rad | action sat % |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 70 | `fall_or_nan` | -0.0020 | -0.0497 | 0.1537 | 0.0187 | 0.3266 | 0.0664 | 0.0 |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | -0.0894 | -2.2339 | 0.1063 | 0.0073 | 0.5042 | 0.2251 | 0.0 |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 70 | `fall_or_nan` | 0.0046 | 0.1157 | 0.1526 | 0.0091 | 0.4162 | 0.0898 | 0.0 |
| 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 70 | `fall_or_nan` | -0.0186 | -0.4661 | 0.1588 | 0.0714 | 0.5264 | 0.1033 | 0.0 |
| 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 149 | `fall_or_nan` | 0.0072 | 0.1798 | 0.1513 | 0.0188 | 0.1308 | 0.0475 | 0.0 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 43 | `fall_or_nan` | -0.3412 | -8.5312 | 0.0616 | 0.0552 | 0.7949 | 0.2345 | 0.0 |

## Interpretation

V24 was designed to fix the V23 double-support standstill by coupling contact
transition reward to forward progress and adding a double-support dwell cost.
The recovered seed gate shows that the resulting candidate was still
insufficient:

- `6/6` recovered seeds fell or terminated.
- Mean local velocity was near-zero or negative for every recovered seed.
- Action saturation stayed at `0%`.
- Pitch-chain target velocity stayed low, far below the measured actuator
  envelope.

So this hold is not an actuator-envelope failure. It is another support /
propulsion failure: the policy still does not produce coherent low-command
forward locomotion across seeds.

An additional reward-term activation audit found an observability hold:

```text
artifact: outputs/analysis/V24_REWARD_TERM_ACTIVATION_AUDIT.md
status: HOLD_REWARD_TERMS_MISSING
missing configured terms:
  forward_contact_transition
  forward_double_support
  forward_double_support_dwell
  forward_single_support
```

The training manifest and reward override file requested these terms, but the
recovered eval reward summaries did not expose them. The behavioral gate failure
is still valid, but do not claim the recovered gate observed the transition /
dwell terms firing without a trace that contains those reward metrics.

## Artifact Recovery

The Colab runtime disappeared before writing a final sentinel or full 0-7 seed
summary. A partial artifact bundle was recovered and checksum-verified locally:

```text
outputs/analysis/colab_cli/open-duck-l4-v24-staged-curriculum-20260625T165454Z/recovered/open_duck_v24_l4_partial_artifacts.tar.gz
sha256: 2b65bc26b9558a24a7a5abb7563eade65fcbd86c76d80bf8a2601746d87924f4
```

The large recovered tarball and extracted raw artifacts are intentionally not
committed. This summary records the small durable evidence.

## Next Decision

Do not rerun V24 unchanged. Before launching another long PPO run, fix or
explain reward-term observability for any newly configured contact terms.
Current evidence points toward one of:

- a richer closed-loop teacher/optimizer that explicitly chooses stance side,
  body placement, foot placement, and push timing;
- an imitation / demonstration path that can hold a coherent single-support
  stepping behavior;
- a targeted reward audit showing whether the current transition reward is
  actually reachable before termination.
