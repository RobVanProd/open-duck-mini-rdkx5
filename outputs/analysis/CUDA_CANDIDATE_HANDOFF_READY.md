# CUDA Candidate Handoff Ready

generated_at: `2026-06-22T13:32:33Z`

## Status

The repo is ready for the next manual CUDA/Colab candidate run.

Recent handoff fixes merged:

- PR #40: `tools/eval_policy_with_actuator_bridge.py` accepts
  `--jax-platform {cpu,gpu,tpu}` and records the requested backend.
- PR #41: candidate packaging no longer treats a standalone target-velocity
  summary as required evidence.
- PR #42: imported CUDA artifact bundles produce a conservative review gate in
  `CUDA_ARTIFACT_IMPORT_SUMMARY.md`.
- PR #53: local ROCm host-loop closed-loop smoke passed for 10 ticks, but is
  too slow for full eval/training.
- PR #61: generated CUDA cells make a best-effort Colab browser download
  request for the artifact bundle.
- PR #62: local artifact import can verify the bundle SHA256 printed by the
  CUDA cell.
- PR #63: CUDA bundles record RDK/Playground commits in
  `CUDA_CELL_EXIT_STATUS.txt`; PR #66 keeps the metadata capture package-only
  so the failure trap does not reinitialize JAX/MJX.
- PR #65: CUDA bundles include `pip_freeze.txt` and `nvidia_smi.txt` so the
  package/runtime environment can be reviewed after import.
- PR #66: CUDA bundle status records package metadata with
  `importlib.metadata` instead of importing JAX/MJX runtime in the EXIT trap.
- Current generator: selects `PYTHON_BIN` once, prefers `/usr/bin/python3` on
  Colab, and passes it explicitly through `--env-python` for eval/training
  subprocesses.
- Current generator: can write an uploadable one-code-cell notebook with
  `--notebook-output`.
- Current generator: can write a complete local handoff directory with
  `--handoff-dir`, including notebook, raw cell text, and import checklist.

## Why Manual CUDA Is Still Required

- Browser automation is blocked by Google's `This browser or app may not be
  secure` sign-in rejection.
- Local `7900 XTX` ROCm/MJX still holds at the raw Open Duck Playground
  `mjx_env.step(...)` path.
- CPU pilots validate plumbing but repeatedly learn smooth near-standing
  behavior instead of nonzero forward-command tracking.

## Next Command

Generate the current one-cell CUDA workflow from `main`:

```bash
python3 tools/print_cuda_colab_cell.py --run-candidate
```

Or generate an uploadable notebook:

```bash
python3 tools/print_cuda_colab_cell.py \
  --run-candidate \
  --notebook-output /tmp/open_duck_cuda_candidate.ipynb
```

Preferred local handoff directory:

```bash
python3 tools/print_cuda_colab_cell.py \
  --run-candidate \
  --handoff-dir /home/lsd/robots/cuda_colab_handoff
```

Run the generated cell in the already-authenticated CUDA/Colab session.

The generated cell now:

- pins the known-good CUDA dependency path, including `playground==0.0.5`
- runs the baseline closed-loop actuator bridge reproduction with
  `--jax-platform gpu` and `--sim-preflight-timeout-s 600`
- runs CUDA smoke training
- runs CUDA candidate training
- gates the candidate at `x=0.0` and `x=0.08`
- packages metadata against the `x=0.08` gate
- writes one downloadable artifact bundle and tries to trigger a Colab browser
  download:
- records repo commits, dirty-file counts, package versions, `pip_freeze.txt`,
  and `nvidia_smi.txt` in the evidence bundle without importing JAX/MJX runtime
  from the EXIT trap
- uses one selected `PYTHON_BIN` for installs, checks, training, gates, and
  subprocess env instantiation

```text
/content/open_duck_cuda_artifacts_<timestamp>.tar.gz
```

The generated cell prints:

```text
CUDA_ARTIFACT_BUNDLE /content/open_duck_cuda_artifacts_<timestamp>.tar.gz
CUDA_ARTIFACT_BUNDLE_SHA256 <hash>
CUDA_ARTIFACT_DOWNLOAD_TRIGGERED /content/open_duck_cuda_artifacts_<timestamp>.tar.gz
```

If the browser download is skipped or fails, download the printed
`CUDA_ARTIFACT_BUNDLE` path manually.

## Import Command

After downloading the bundle:

```bash
python3 tools/import_cuda_artifact_bundle.py \
  /path/to/open_duck_cuda_artifacts_<timestamp>.tar.gz \
  --expected-sha256 <CUDA_ARTIFACT_BUNDLE_SHA256>
```

Start review from:

```text
outputs/analysis/cuda_imports/<timestamp>_<bundle>/CUDA_ARTIFACT_IMPORT_SUMMARY.md
```

## Review Gate

The importer reports one of:

```text
READY_FOR_SIM_GATE_REVIEW
INFO_SMOKE_ONLY
INFO_BASELINE_EVAL_ONLY
HOLD_CUDA_CELL_FAILED
HOLD_NO_CANDIDATE_PACKAGE
HOLD_NO_CANDIDATE_ONNX
HOLD_MISSING_CANDIDATE_GATE_X0
HOLD_MISSING_CANDIDATE_GATE_X008
or the candidate package/gate HOLD_* status
```

This is still an offline gate. It does not approve robot testing.

## Robot Safety

No robot tests, SSH, deploy, policy overwrite, suspended replay, or grounded
replay are approved by this handoff. Robot-side validation remains blocked
until a candidate passes sim gates and Rob explicitly approves the specific
suspended test.
