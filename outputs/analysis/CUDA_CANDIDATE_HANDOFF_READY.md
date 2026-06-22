# CUDA Candidate Handoff Ready

generated_at: `2026-06-22T18:45:00Z`

## Status

The repo is ready for the next CUDA/Colab candidate run, but not another
blind repeat of the current reward recipe.

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
- Current headless path: `tools/run_colab_cli_cuda_workflow.py` uploads local
  repo tarballs through `google-colab-cli`, avoids GitHub token prompts, and
  pins `jax/jaxlib==0.7.2`.
- Patched Colab L4 closed-loop eval rerun: `PASS_CLOSED_LOOP_REPRODUCTION`
  with `worker_returncode=0`, `gpu/cuda:0`, and non-empty worker JSON.
- Colab CLI 50k candidate run: exported a 101/14 ONNX and passed `x=0.0`, but
  held at `x=0.08` with `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`.
- Colab CLI 300k strengthened candidate run: exported step `307200`, passed
  the actuator-safe parts of the `x=0.08` gate, but again held for low forward
  progress. The fitted/stress mean forward velocity was approximately zero.
- Archived `verify_scratch/odm_phase_b` checkpoint sweep on Colab L4: five
  selected compatible ONNX checkpoints all held at `x=0.08` for
  `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`.

Small committed summary:

```text
outputs/analysis/PHASE_B_CHECKPOINT_SWEEP_SUMMARY.md
```

Raw Colab artifacts remain ignored under:

```text
outputs/analysis/colab_cli/phase_b_eval_20260622T173551Z/
```

## Why Manual CUDA Is Still Required

- Browser automation is blocked by Google's `This browser or app may not be
  secure` sign-in rejection.
- Local `7900 XTX` ROCm/MJX still holds at the raw Open Duck Playground
  `mjx_env.step(...)` path.
- CPU pilots validate plumbing but repeatedly learn smooth near-standing
  behavior instead of nonzero forward-command tracking.

## Next Command

Before launching another candidate, update the training objective/curriculum so
near-zero forward velocity is not a good solution for `x=0.08`. The current
recipe can make policies smooth enough for actuator gates while still failing
locomotion.

The next recipe should use the Playground runner's default-off forward-progress
term and a stricter tracking shape:

```text
tracking_sigma=0.0025
forward_progress_scale=2.0
forward_progress_deadband=0.02
tracking_lin_vel_scale=12.0
tracking_ang_vel_scale=0.0
target_rate_scale=-0.001
action_rate_scale=-0.1
action_magnitude_scale=-0.05
alive_scale=0.5
imitation_scale=0.25
lin_vel_x=[0.04, 0.12]
```

June 22 CUDA candidate follow-up:

- `open_duck_mini_actuator_bridge_cli_20260622T202101Z` trained to step
  `307200` and held offline: `x=0.0` fell/terminated and `x=0.08` had near-zero
  forward progress.
- `open_duck_mini_actuator_bridge_cli_20260622T205753Z` trained to step
  `614400` with yaw tracking disabled, but still held offline: all trained
  checkpoints from `153600` onward failed the `x=0.0` gate; the final checkpoint
  also held at `x=0.08` with near-zero/negative forward tracking.
- The exported sample actions saturated after the first training checkpoint.
  The next recipe should penalize action magnitude, not only action rate,
  because a constant saturated action can have low action-rate cost.

Local CPU smoke validation for this recipe passed on June 22, 2026:

```text
status: PASS_SMOKE_RUN
step: 320
reward: 1.6719996929168701
output_dir: /tmp/open_duck_actuator_bridge_smoke/smoke_20260622T184905Z_cpu
```

The smoke ONNX exports remain temporary validation artifacts only; they are not
candidate policies and are not approved for robot testing.

After the reward/curriculum patch, generate the current one-cell CUDA workflow
from `main`:

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

For an agent/headless Colab session, prefer the staged CLI path:

```bash
python3 tools/run_colab_cli_cuda_workflow.py --workflow eval --run
python3 tools/run_colab_cli_cuda_workflow.py --workflow smoke --run
python3 tools/run_colab_cli_cuda_workflow.py --workflow candidate-only --run
```

Move one line at a time only after the previous artifact gate passes. This route
uploads local repo tarballs and does not clone from GitHub inside Colab.

The generated cell now:

- pins the known-good CUDA dependency path, including `jax/jaxlib==0.7.2`
  and `playground==0.0.5`
- uses the stricter nonzero-command recipe above so another candidate cannot
  pass offline actuator gates by standing nearly still at `x=0.08`
- exposes command-curriculum knobs so a follow-up candidate can set
  `--candidate-zero-command-probability 0.0` and
  `--candidate-command-resample-steps 600` if the historical 10% zero-command
  sampling is still biasing learning toward standing
- runs the baseline closed-loop actuator bridge reproduction with
  `--jax-platform gpu` and `--sim-preflight-timeout-s 600`
- runs CUDA smoke training
- runs CUDA candidate training
- gates the candidate at `x=0.0` and `x=0.08`
- packages metadata against both candidate gates
- writes one downloadable artifact bundle and tries to trigger a Colab browser
  download:
- records repo commits, dirty-file counts, package versions, `pip_freeze.txt`,
  and `nvidia_smi.txt` in the evidence bundle without importing JAX/MJX runtime
  from the EXIT trap
- uses one selected `PYTHON_BIN` for installs, checks, training, gates, and
  subprocess env instantiation
- uses `GIT_ASKPASS` only if `GITHUB_TOKEN` or `GH_TOKEN` is already set;
  otherwise it attempts public repo access and fails clearly if a repo is private
- records nonzero `exit_status` correctly if setup/training exits early

```text
/content/open_duck_cuda_artifacts_<timestamp>.tar.gz
```

The generated cell prints:

```text
CUDA_ARTIFACT_BUNDLE /content/open_duck_cuda_artifacts_<timestamp>.tar.gz
CUDA_ARTIFACT_BUNDLE_SHA256 <hash>
CUDA_ARTIFACT_BUNDLE_SHA256_FILE /content/open_duck_cuda_artifacts_<timestamp>.tar.gz.sha256
CUDA_ARTIFACT_DOWNLOAD_TRIGGERED /content/open_duck_cuda_artifacts_<timestamp>.tar.gz
CUDA_ARTIFACT_SHA256_DOWNLOAD_TRIGGERED /content/open_duck_cuda_artifacts_<timestamp>.tar.gz.sha256
```

If the browser download is skipped or fails, download the printed
`CUDA_ARTIFACT_BUNDLE` and `CUDA_ARTIFACT_BUNDLE_SHA256_FILE` paths manually.

## Import Command

After downloading the bundle:

```bash
python3 tools/ingest_latest_cuda_artifact.py
```

The ingest helper searches common download locations for the newest bundle,
verifies the neighboring sidecar when present, and skips already-imported
bundles by SHA256. If the bundle is elsewhere, pass `--bundle`.

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
