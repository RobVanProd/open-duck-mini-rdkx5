# Movement Bootstrap V15 A100 No-Sentinel Summary

status: `HOLD_REMOTE_NO_SENTINEL_EXPORT_HANDOFF`

## Context

V15 phase 1 was launched on A100 as an offline no-bridge gait-discovery run:

```text
recipe: movement_bootstrap_v15
phase: phase1_no_bridge_high_entropy_gait_discovery
session: open-duck-a100-v15
robot_touched: false
```

The run disappeared without writing the workflow `.exit` sentinel or artifact
bundle. The Colab session reported idle and the remote log stopped growing, so
the local workflow guard stopped with:

```text
HOLD_REMOTE_NO_SENTINEL
```

## Recovered Artifacts

Available recovered files:

```text
outputs/analysis/movement_bootstrap_v15_a100_phase1_no_sentinel/stdout.txt
outputs/analysis/movement_bootstrap_v15_a100_phase1_no_sentinel/stderr.txt
outputs/analysis/movement_bootstrap_v15_a100_phase1_no_sentinel/smoke_manifest.start.json
outputs/analysis/movement_bootstrap_v15_a100_phase1_no_sentinel/2026_06_24_070440_0.onnx
```

Step-0 ONNX SHA256:

```text
6c19d288a7f187ee3e2b06a90cf5527b9eafd37e8030b8ab8f17ba4f41317493
```

Only the step-0 checkpoint/export existed. There was no later checkpoint and no
completed smoke manifest.

## Log Finding

The trainer reached `STEP: 0`, saved a checkpoint, and entered ONNX export:

```text
STEP: 0 reward: -188.18649291992188 reward_std: 167.86959838867188
Saving checkpoint (step: 0): ...
=== EXPORT ONNX ===
Tensorflow prediction: [...]
```

There is no Python traceback in stderr. The log stops immediately after the
step-0 export sequence, which makes this an infrastructure/export-handoff
failure rather than a policy-quality result.

## Follow-Up Fix

The follow-up patch makes ONNX export safer for cloud staged training:

- TensorFlow ONNX export is CPU-only by default in `Open_Duck_Playground`.
- The Playground runner exposes `--export_min_step`.
- The RDK staged planner defaults to `--export-min-step 1`, skipping only the
  fragile step-0 checkpoint/ONNX export while preserving later candidate
  exports.

## Interpretation

This run does not evaluate V15. Do not use the step-0 ONNX as a restore anchor
or robot candidate.

Robot validation remains blocked.
