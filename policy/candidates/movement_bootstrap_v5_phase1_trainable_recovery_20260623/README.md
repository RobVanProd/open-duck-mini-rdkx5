# Movement Bootstrap V5 Phase-1 Trainable Recovery

This directory preserves the trainable checkpoint recovered from a one-phase
A100 rerun of `movement_bootstrap_v5`.

It is not a deployable robot policy.

## Why This Exists

The original v5 phase-1 ONNX proved that in-envelope forward motion exists, but
only the ONNX was preserved. That was not enough for continuation training. This
rerun stopped after phase 1 and preserved both:

- `candidate.onnx`
- `checkpoint_2026_06_23_205634_368640/`

## Policy Hash

```text
0b7d9c3b24ac047a0a7d5e2e2c15f8e03280a2e30389d4c102dd44a733ce03e5
```

## Gate Result

Offline candidate gates hold:

```text
x=0.0:  HOLD_CANDIDATE_FALL_OR_TERMINATION
x=0.08: HOLD_CANDIDATE_FALL_OR_TERMINATION
```

At `x=0.08` with the fitted bridge:

```text
fitted samples: 52
fitted termination: fall_or_nan
fitted mean local vx: 0.2989 m/s
fitted track ratio: 3.7362
max pitch-chain p95 target velocity: 1.7912 rad/s
max pitch tracking p95: 0.2553 rad
action saturation: 0%
```

Interpretation: this checkpoint moves in-envelope but is unstable. Use it only
as a trainable anchor for a continuity/trust-region stabilization experiment.

## Source

Recovered from:

```text
outputs/analysis/colab_cli/open-duck-a100-v5-phase1-recovery-staged-curriculum-20260623T204615Z/
```

The latest checkpoint directory was preserved by the Colab artifact manifest:

```text
checkpoint_artifact_manifest.json
```
