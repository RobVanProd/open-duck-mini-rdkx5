# Pitch-Chain 4.3 PPO-Shape Rate Student Result

status: `HOLD_CANDIDATE_TRACKING`

This was an offline deployable-student probe. It did not SSH, deploy, run robot
tests, train PPO, or change robot runtime behavior.

## Purpose

The exact pitch-chain `4.3 rad/s` selector preserved forward motion but stayed
non-deployable and still held the fitted-bridge tracking gate. This probe tested
whether a PPO-shape feed-forward neural student could smooth that curated
selector into a deployable ONNX policy while preserving the fitted-bridge
multi-seed behavior.

## Inputs

- source manifest:
  `outputs/analysis/source_vx_selector_trace_pitch_chain_rate_limited_4p3_manifest.json`
- samples: `4000`
- BC tool: `tools/train_ppo_loc_bc_student.py`
- student hidden sizes: `[512, 256, 128]`
- activation: `swish`
- target-rate penalty: `0.1`
- target-rate limit: `3.75 rad/s`

Generated artifacts:

- fit report:
  `outputs/analysis/PITCH_CHAIN_4P3_PPO_SHAPE_RATE_STUDENT.md`
- gate report:
  `outputs/analysis/PITCH_CHAIN_4P3_PPO_SHAPE_RATE_STUDENT_MULTI_SEED_FITTED_BACKLASH.md`
- fit JSON:
  `outputs/analysis/pitch_chain_4p3_ppo_shape_rate_student.json`
- gate JSON:
  `outputs/analysis/pitch_chain_4p3_ppo_shape_rate_student_multiseed_fitted_backlash.json`

## Fit Result

The supervised fit was numerically clean:

```text
samples: 4000
MAE: 0.010959
p95 abs action error: 0.035272
target-rate p95: 2.296857 rad/s
target-rate max: 4.171165 rad/s
ONNX p95 verification error: 0.00000017
```

That only proves the ONNX matches the fitted feed-forward model. It does not
prove closed-loop deployability.

## Strict Fitted-Bridge Gate

Gate:

```text
task: flat_terrain_backlash
command_x: 0.08
bridge: fitted actuator model
duration: 10 s
seeds: 0-7
platform: CPU
```

Result:

| metric | value |
|---|---:|
| duration complete | 8 / 8 |
| falls | 0 / 8 |
| mean vx | 0.0393 m/s |
| mean track ratio | 0.4913 |
| max pitch velocity p95 range | 3.6035-3.7059 rad/s |
| max tracking p95 range | 0.2516-0.2561 rad |
| status | `HOLD_CANDIDATE_TRACKING` |

## Comparison

| candidate | mean vx | track ratio | pitch velocity p95 range | tracking p95 range | result |
|---|---:|---:|---:|---:|---|
| DAgger-3 PPO-shape student | 0.0396 | 0.4953 | 3.7842-3.8409 | 0.2570-0.2684 | hold |
| exact pitch-chain 4.3 selector | 0.0477 | 0.5965 | 4.1935-4.2879 | 0.2685-0.2794 | hold |
| pitch-chain 4.3 PPO-shape rate student | 0.0393 | 0.4913 | 3.6035-3.7059 | 0.2516-0.2561 | hold |

The student successfully reduced the pitch-chain velocity p95 into the fitted
envelope, and it slightly reduced fitted-bridge tracking error. The tradeoff was
lower forward progress, and the tracking plateau remained far above the
candidate gate.

## Decision

This closes simple feed-forward BC smoothing as a standalone fix.

```text
Do not robot-test this candidate.
Do not treat this as a deployable policy.
Do not run another simple clip/filter/feed-forward-BC branch without a new mechanism.
```

The next deployable-policy branch still needs gate-aware rollout correction, a
phase/recurrent mechanism for the stance-transition discontinuity, or PPO
fine-tuning that preserves the working selector behavior while directly
reducing fitted-bridge tracking.
