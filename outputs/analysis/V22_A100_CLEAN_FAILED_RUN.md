# V22 A100 Clean Failed Run

status: `HOLD_A100_BACKEND_NO_SENTINEL`

## Context

This was a clean rerun of `movement_bootstrap_v22` after:

- adding the explicit V22 planner recipe,
- patching the Colab staged workflow to use a unique remote output root, and
- patching the Playground ONNX exporter to lazy-load TensorFlow and keep export
  CPU-side.

The run used a fresh `open-duck-a100` Colab session and did not touch the robot.

## Result

The remote driver disappeared without:

- exit sentinel,
- artifact bundle,
- checkpoint,
- ONNX export, or
- Python traceback.

The recovered logs show the run reached environment construction and PPO
configuration, then stopped before the first PPO progress line.

```text
remote_bundle_sha256: 1508c95113d7bd0f82af4298527b5eb7911261d317fd2348c427afc5ad56479d
run_dir: outputs/analysis/colab_cli/open-duck-a100-staged-curriculum-20260625T104307Z
recovered_import_dir: outputs/analysis/cuda_imports/v22_a100_clean_failed_20260625T104322Z
workflow: staged-curriculum
recipe: movement_bootstrap_v22
checkpoint produced: no
onnx produced: no
robot touched: no
```

## Interpretation

This is not a V22 training verdict. It is a backend/session failure before the
candidate could be evaluated.

The earlier partial A100 run remains the only V22 behavioral evidence so far,
and that partial checkpoint held at the x=0.04 trace gate. A full V22 verdict
still requires a completed training run and multi-seed gate.

## Next

Before another cloud launch, prefer one of:

- run the same V22 command on an L4, since V21 completed there,
- run a shorter V22 diagnostic with fewer timesteps to verify the clean path,
- add stronger remote no-sentinel recovery so partial logs are bundled
  automatically, or
- switch to a more stable training backend.
