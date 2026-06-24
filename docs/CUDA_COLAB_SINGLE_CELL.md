# CUDA / Colab Single Cell

Last updated: 2026-06-24

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

For headless/private-repo runs, prefer the Colab CLI tarball workflow in
`tools/run_colab_cli_cuda_workflow.py`. It uploads the local RDK and Playground
worktrees directly and does not require a GitHub token inside the notebook.

The copy-paste notebook cell can still clone repos from GitHub. If either repo
is private, set `GITHUB_TOKEN` or `GH_TOKEN` in the Colab environment before
running the generated `%%bash` cell. The cell uses `GIT_ASKPASS` for
clone/fetch/pull and does not write the token into git remotes. It no longer
tries an interactive password prompt because Colab `%%bash` cells can fail on
`getpass`/TTY input. Do not hard-code tokens into committed docs.

## Preferred Headless Colab CLI Path

When `google-colab-cli` is authenticated and an `open-duck-l4` session is
running, use the local tarball workflow instead of cloning private repos from
inside the notebook:

```bash
python3 tools/run_colab_cli_cuda_workflow.py --workflow eval --run
```

Then run the smoke/candidate stages only after the previous gate passes:

```bash
python3 tools/run_colab_cli_cuda_workflow.py --workflow smoke --run
python3 tools/run_colab_cli_cuda_workflow.py --workflow candidate-only --run
```

### Candidate Checkpoint Sweep

Use this after a training sequence produces multiple preserved candidate
checkpoints and the final checkpoint may not be the best behavior. The workflow
uploads the local RDK and Playground worktrees, runs
`tools/sweep_candidate_checkpoints.py` on the CUDA session, and bundles only the
small sweep report artifacts. It does not train, deploy, SSH, or touch the
robot.

Plan first:

```bash
python3 tools/run_colab_cli_cuda_workflow.py --workflow checkpoint-sweep
```

Run on the connected Colab CUDA session:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow checkpoint-sweep \
  --session open-duck-l4 \
  --checkpoint-sweep-commands 0.08 \
  --checkpoint-sweep-duration 5 \
  --checkpoint-sweep-bridge-mode fitted \
  --run
```

Default policies are the preserved V7, V8, and V9 candidate ONNX files. Override
them with `--checkpoint-sweep-policies` when testing phase checkpoints or a new
candidate set.

If candidate training finishes but the Colab session disconnects during one of
the sim gates, do not rerun training just to recover the missing gate. Use the
eval-only workflow with the local ONNX downloaded from the partial artifact:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow candidate-eval-only \
  --candidate-existing-policy path/to/candidate.onnx \
  --candidate-training-manifest path/to/smoke_manifest.final.json \
  --candidate-name open_duck_mini_actuator_bridge_<run> \
  --run
```

This uploads only the local worktrees plus the selected ONNX/manifest, then
runs the `x=0.0` and `x=0.08` candidate gates. It does not train.

The CLI workflow uploads local RDK/Playground tarballs, pins
`jax/jaxlib==0.7.2`, writes a remote log/artifact bundle, downloads the bundle,
and does not require a GitHub token in Colab. This is the preferred route for
agents and unattended runs.

## Browser Notebook Fallback

Use this path when a Colab notebook is connected in the browser but
`google-colab-cli` cannot see an active session.

The next recommended fallback is diagnostic-only:

```bash
python3 tools/print_cuda_colab_cell.py \
  --training-smoke-diagnostic \
  --rdk-branch codex/colab-cli-cuda-workflow \
  --playground-branch codex/forward-progress-reward \
  --handoff-dir /home/lsd/robots/cuda_colab_diagnostic_handoff
```

Upload/open:

```text
/home/lsd/robots/cuda_colab_diagnostic_handoff/open_duck_cuda_smoke.ipynb
```

Then run its single cell in the manually authenticated CUDA/Colab notebook. It
runs only:

```text
00_python_jax_device
01_import_training_stack
02_smoke_dry_run
03_smoke_run
```

and skips baseline eval and candidate training.

The cell writes diagnostic output under:

```text
outputs/analysis/cuda_manual/training_smoke_startup_diagnostic
```

and packages it into the downloadable artifact bundle.

From the RDK repo:

```bash
python3 tools/print_cuda_colab_cell.py
```

The generated cell runs:

1. GPU/JAX visibility check
2. RDK and Playground fork checkout
3. CUDA dependency install, including `jax/jaxlib==0.7.2` and
   `playground==0.0.5`
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

If uploading a notebook is easier than copy/pasting a long cell, generate a
one-code-cell notebook:

```bash
python3 tools/print_cuda_colab_cell.py \
  --run-candidate \
  --notebook-output /tmp/open_duck_cuda_candidate.ipynb
```

Then upload or open that `.ipynb` in the already-authenticated CUDA/Colab
session and run its single cell.

Preferred local handoff bundle:

```bash
python3 tools/print_cuda_colab_cell.py \
  --run-candidate \
  --handoff-dir /home/lsd/robots/cuda_colab_handoff
```

That writes:

```text
/home/lsd/robots/cuda_colab_handoff/open_duck_cuda_candidate.ipynb
/home/lsd/robots/cuda_colab_handoff/open_duck_cuda_candidate_cell.txt
/home/lsd/robots/cuda_colab_handoff/CUDA_COLAB_HANDOFF.md
```

Use the notebook for Colab upload and keep the markdown handoff next to it for
the bundle download/import checklist.

The default candidate shape matches `docs/CUDA_BACKEND_TRAINING_RUNBOOK.md`.
It still does not approve robot testing; it only produces artifacts for review.
That candidate shape now includes opt-in reward and command-curriculum
overrides intended to avoid the smooth stand-still behavior seen in the local
CPU pilots.

The generated candidate recipe currently uses:

```text
tracking_sigma=0.0025
forward_progress_scale=2.0
tracking_lin_vel_scale=12.0
tracking_ang_vel_scale=0.0
target_rate_scale=-0.001
action_rate_scale=-0.1
action_magnitude_scale=-0.05
alive_scale=0.5
imitation_scale=0.25
lin_vel_x=[0.04, 0.12]
```

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
jax[cuda12]==0.7.2
jaxlib==0.7.2
playground==0.0.5
```

because the successful CUDA path used that stack. A newer unpinned JAX install
completed environment setup but broke Brax training through a removed
`jax.device_put_replicated` API.

The generated cell also defines `PYTHON_BIN` once near the top and passes that
same interpreter to every subprocess via `--env-python`. On Colab it prefers
`/usr/bin/python3`, which was the interpreter used by the successful CUDA
closed-loop eval, instead of relying on whichever `python` appears first in
`PATH`.

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
CUDA_ARTIFACT_BUNDLE_SHA256_FILE /content/open_duck_cuda_artifacts_<timestamp>.tar.gz.sha256
CUDA_ARTIFACT_DOWNLOAD_TRIGGERED /content/open_duck_cuda_artifacts_<timestamp>.tar.gz
CUDA_ARTIFACT_SHA256_DOWNLOAD_TRIGGERED /content/open_duck_cuda_artifacts_<timestamp>.tar.gz.sha256
```

Download that `.tar.gz` first. It includes the small analysis directory plus
candidate ONNX/manifests/stdout/stderr from the smoke and candidate runs. It
intentionally leaves large raw checkpoint files out of the bundle.

In Colab, the generated cell also makes a best-effort
`google.colab.files.download(...)` call after creating the bundle. If the
session is not Colab or the browser blocks the download, the cell prints
`CUDA_ARTIFACT_DOWNLOAD_SKIPPED` or `CUDA_ARTIFACT_DOWNLOAD_FAILED`; in that
case, download the printed `CUDA_ARTIFACT_BUNDLE` and
`CUDA_ARTIFACT_BUNDLE_SHA256_FILE` paths manually. To omit the download trigger
in generated cells, pass:

```bash
python3 tools/print_cuda_colab_cell.py --run-candidate --no-auto-download
```

The generated cell builds this bundle from an `EXIT` trap. Download the bundle
even if the notebook cell exits early or reports a command failure. The archive
contains `CUDA_CELL_EXIT_STATUS.txt` so the importer/reviewer can distinguish a
clean run from a partial evidence bundle. That file also records the RDK and
Playground repo URLs, branches, commits, dirty-file counts, Python/JAX/MuJoCo
package metadata when available, and the visible GPU name when `nvidia-smi` is
available. The bundle also includes `pip_freeze.txt` and `nvidia_smi.txt` when
those commands are available.

Import it locally with:

```bash
python3 tools/ingest_latest_cuda_artifact.py
```

The helper searches common download locations for the newest
`open_duck_cuda_artifacts_*.tar.gz`, verifies the neighboring `.sha256` sidecar
when present, skips bundles already imported by SHA256, and writes the review
summary under `outputs/analysis/cuda_imports/`. If the bundle is elsewhere,
pass `--bundle /path/to/open_duck_cuda_artifacts_<timestamp>.tar.gz`.

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
