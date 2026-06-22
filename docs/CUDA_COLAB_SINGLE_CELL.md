# CUDA / Colab Single Cell

Last updated: 2026-06-22

## Purpose

Use this when a CUDA machine is available, for example Colab L4/A100, and the
local `7900 XTX` ROCm/MJX path is still blocked at Open Duck Playground
stepping.

This path is offline-only:

- no robot tests
- no SSH
- no deployment
- no overwrite of `policy/BEST_WALK_ONNX_2.onnx`
- no robot-side validation approval

## Generate The Cell

From the RDK repo:

```bash
python3 tools/print_cuda_colab_cell.py
```

The generated cell runs:

1. GPU/JAX visibility check
2. RDK and Playground fork checkout
3. CUDA dependency install, including `playground==0.0.5`
4. `mujoco_playground._src.collision` import check
5. training environment check
6. policy/sim contract audit
7. closed-loop baseline actuator bridge reproduction
8. CUDA smoke training

To include the first candidate-training shape in the generated cell:

```bash
python3 tools/print_cuda_colab_cell.py --run-candidate
```

The default candidate shape matches `docs/CUDA_BACKEND_TRAINING_RUNBOOK.md`.
It still does not approve robot testing; it only produces artifacts for review.

## Why This Exists

The browser automation path for Google login was blocked by Google's
`This browser or app may not be secure` warning. A manually authenticated Colab
session is therefore the reliable path. This generator avoids hand-copy errors
in notebook cells, especially heredoc indentation and dependency pinning.

Earlier Colab attempts failed when the package providing this import was not
available:

```python
import mujoco_playground._src.collision
```

The generated cell pins:

```text
playground==0.0.5
```

because the successful CUDA path used that dependency and verified the
`collision.py` import before running the Open Duck eval.

## Expected Gates

Smoke-only cell:

```text
PASS_POLICY_SIM_CONTRACT
PASS_CLOSED_LOOP_REPRODUCTION
PASS_SMOKE_RUN
```

Candidate cell:

```text
PASS_SMOKE_RUN
PASS_POLICY_CONTRACT
READY_FOR_SIM_GATE_REVIEW
```

or a documented `HOLD_*` status with enough evidence to decide the next config
change. A candidate that is stable but does not track nonzero forward commands
must hold, for example `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`.

## Files To Bring Back

Small summaries first:

```text
outputs/analysis/cuda_manual/POLICY_SIM_CONTRACT_AUDIT_CUDA.md
outputs/analysis/cuda_manual/CLOSED_LOOP_ACTUATOR_BRIDGE_EVAL.md
outputs/analysis/cuda_manual/<candidate>_training_run_summary.md
outputs/analysis/cuda_manual/<candidate>_policy_package.md
outputs/analysis/cuda_manual/<candidate>_policy_metadata.json
```

Do not commit or upload giant raw checkpoint directories unless explicitly
requested.
