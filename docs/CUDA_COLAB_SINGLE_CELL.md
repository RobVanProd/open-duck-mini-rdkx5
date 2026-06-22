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
9. optional CUDA candidate training
10. optional candidate sim gates at `x=0.0` and `x=0.08`
11. optional candidate package metadata
12. a single downloadable artifact bundle

To include the first candidate-training shape in the generated cell:

```bash
python3 tools/print_cuda_colab_cell.py --run-candidate
```

The default candidate shape matches `docs/CUDA_BACKEND_TRAINING_RUNBOOK.md`.
It still does not approve robot testing; it only produces artifacts for review.
That candidate shape now includes opt-in reward and command-curriculum
overrides intended to avoid the smooth stand-still behavior seen in the local
CPU pilots.

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
PASS_CANDIDATE_SIM_GATE
READY_FOR_SIM_GATE_REVIEW
```

or a documented `HOLD_*` status with enough evidence to decide the next config
change. The generated candidate cell now runs candidate-mode closed-loop sim
gates for both `x=0.0` and `x=0.08` before packaging. A candidate that is
stable but does not track nonzero forward commands must hold, for example
`HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`.
Generated CUDA eval commands pass `--jax-platform gpu` explicitly. Local CPU
candidate gates should pass `--jax-platform cpu` explicitly so they do not
accidentally select the blocked local ROCm backend.

The generated closed-loop eval commands also pass:

```text
--sim-preflight-timeout-s 600
```

Manual Colab L4 runs showed that the correct environment can take longer than
the default 90 seconds to instantiate after dependency installation. A preflight
timeout should not be mistaken for a policy/sim contract mismatch.

## Files To Bring Back

The generated cell now prints one bundle path plus its SHA256:

```text
CUDA_ARTIFACT_BUNDLE /content/open_duck_cuda_artifacts_<timestamp>.tar.gz
CUDA_ARTIFACT_BUNDLE_SHA256 <hash>
CUDA_ARTIFACT_DOWNLOAD_TRIGGERED /content/open_duck_cuda_artifacts_<timestamp>.tar.gz
```

Download that `.tar.gz` first. It includes the small analysis directory plus
candidate ONNX/manifests/stdout/stderr from the smoke and candidate runs. It
intentionally leaves large raw checkpoint files out of the bundle.

In Colab, the generated cell also makes a best-effort
`google.colab.files.download(...)` call after creating the bundle. If the
session is not Colab or the browser blocks the download, the cell prints
`CUDA_ARTIFACT_DOWNLOAD_SKIPPED` or `CUDA_ARTIFACT_DOWNLOAD_FAILED`; in that
case, download the printed `CUDA_ARTIFACT_BUNDLE` path manually. To omit the
download trigger in generated cells, pass:

```bash
python3 tools/print_cuda_colab_cell.py --run-candidate --no-auto-download
```

The generated cell builds this bundle from an `EXIT` trap. Download the bundle
even if the notebook cell exits early or reports a command failure. The archive
contains `CUDA_CELL_EXIT_STATUS.txt` so the importer/reviewer can distinguish a
clean run from a partial evidence bundle.

Import it locally with:

```bash
python3 tools/import_cuda_artifact_bundle.py \
  /path/to/open_duck_cuda_artifacts_<timestamp>.tar.gz \
  --expected-sha256 <CUDA_ARTIFACT_BUNDLE_SHA256>
```

That writes:

```text
outputs/analysis/cuda_imports/<timestamp>_<bundle>/CUDA_ARTIFACT_IMPORT_SUMMARY.md
outputs/analysis/cuda_imports/<timestamp>_<bundle>/cuda_artifact_import_summary.json
```

Start review from `CUDA_ARTIFACT_IMPORT_SUMMARY.md`. Its review gate reports:

```text
READY_FOR_SIM_GATE_REVIEW
INFO_SMOKE_ONLY
INFO_BASELINE_EVAL_ONLY
HOLD_CUDA_CELL_FAILED
HOLD_NO_CANDIDATE_PACKAGE
HOLD_MISSING_CANDIDATE_GATE_X0
HOLD_MISSING_CANDIDATE_GATE_X008
or the candidate package/gate HOLD_* status
```

If you cannot download the bundle, bring back these small summaries first:

```text
outputs/analysis/cuda_manual/POLICY_SIM_CONTRACT_AUDIT_CUDA.md
outputs/analysis/cuda_manual/CLOSED_LOOP_ACTUATOR_BRIDGE_EVAL.md
outputs/analysis/cuda_manual/<candidate>_training_run_summary.md
outputs/analysis/cuda_manual/<candidate>_candidate_gate_x0.md
outputs/analysis/cuda_manual/<candidate>_candidate_gate_x008.md
outputs/analysis/cuda_manual/<candidate>_policy_package.md
outputs/analysis/cuda_manual/<candidate>_policy_metadata.json
```

Do not commit or upload giant raw checkpoint directories unless explicitly
requested.

Training summaries separate actionable stderr lines from known environment
noise such as TensorFlow oneDNN notices, missing CUDA-driver messages during
CPU-only runs, and XLA CPU AOT feature-mismatch chatter. Treat actionable lines
as review signals; known-noise counts are recorded so logs remain auditable
without burying candidate status in repetitive backend messages.
