# Phase 2 Stage A Colab Runbook

Last updated: 2026-07-06

## Scope

This runbook is for the current Phase 2 Stage A rate175 robustness run.
It is offline sim/training only:

- no robot
- no SSH
- no deploy
- no grounded replay
- no runtime behavior change

The Stage A run is only useful if it produces checkpoints that can be swept and
gated against the corrected actuator bridge. CPU smoke runs are wiring evidence
only and are not promotable.

## Current Stage A Inputs

- workflow: `phase2-stage-a-narrow`
- launcher: `tools/launch_phase2_stage_a_rate175_colab.py`
- workflow driver: `tools/run_colab_cli_cuda_workflow.py`
- warm start checkpoint:
  `outputs/analysis/ppo_bc_command_conditioned_rate175_step0_checkpoint`
- behavior prior:
  `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz`
- behavior prior scale: `-0.6`
- behavior prior Huber delta: `0.05`
- restore-policy KL scale: `4.0`
- corrected bridge gate remains authoritative

## Known Allocation Results

Current committed allocation evidence:

- `outputs/analysis/PHASE2_STAGE_A_RATE175_DETACHED_RETRY_STATUS.md`
- `outputs/analysis/PHASE2_STAGE_A_RATE175_A100_ALLOCATION_STATUS.md`
- `outputs/analysis/PHASE2_STAGE_A_RATE175_L4_ALLOCATION_STATUS.md`

Observed state:

- T4: six detached allocation attempts returned `HOLD_SERVICE_UNAVAILABLE`
- A100: backend rejected accelerator `A100`
- L4: backend rejected accelerator `L4`
- 2026-07-06 follow-up single probes:
  - T4: `HOLD_SERVICE_UNAVAILABLE`
  - A100: `HOLD_ACCELERATOR_REJECTED`
- 2026-07-06 local ROCm check:
  - Open Duck env still sees `rocm:0`
  - local ROCm Stage A was not started because another GPU workload was active
    (`train_dreamer.py --logdir ...run11_20260706_continued`)

No Stage A GPU checkpoint has been produced from these attempts.

## Preferred Path: Adopt An Existing Session

Before choosing a runtime, run the guard report:

```bash
python3 tools/report_phase2_runtime_availability.py
```

It records whether a Colab session is adoptable, whether local ROCm has active
GPU owner processes, and whether Stage A checkpoints already exist. Do not
start local ROCm Stage A if the report lists unrelated GPU owner processes.

If a Colab CLI session is already visible and kept alive by a browser tab, use
the adoption path. This avoids forcing the agent to allocate a new runtime.

Preflight without starting training:

```bash
python3 tools/launch_phase2_stage_a_rate175_colab.py \
  --adopt-existing-session \
  --no-create \
  --attempts 1 \
  --delay-s 0 \
  --output-dir outputs/analysis/phase2_stage_a_rate175_colab_adopt_preflight
```

Run Stage A on the adopted session:

```bash
python3 tools/launch_phase2_stage_a_rate175_colab.py \
  --adopt-existing-session \
  --no-create \
  --run-workflow \
  --output-dir outputs/analysis/phase2_stage_a_rate175_colab_adopt_existing
```

Bounded wait for a session, then run Stage A when it appears:

```bash
python3 tools/launch_phase2_stage_a_rate175_colab.py \
  --adopt-existing-session \
  --wait-for-existing-session \
  --wait-timeout-s 3600 \
  --wait-interval-s 30 \
  --no-create \
  --run-workflow \
  --output-dir outputs/analysis/phase2_stage_a_rate175_colab_wait_adopt
```

For unattended handoff, use the wrapper that polls the runtime guard and only
launches once a named Colab session is visible:

```bash
python3 tools/wait_and_launch_phase2_stage_a.py \
  --timeout-s 86400 \
  --interval-s 60 \
  --output-dir outputs/analysis/phase2_stage_a_wait_and_launch
```

If the intended next action is to wait for the local ROCm GPU to become free
instead of waiting only for Colab, use:

```bash
python3 tools/wait_and_launch_phase2_stage_a.py \
  --timeout-s 86400 \
  --interval-s 60 \
  --stop-when-local-rocm-free \
  --output-dir outputs/analysis/phase2_stage_a_wait_for_gpu_free
```

This mode does not start local training. It only exits at a safe handoff point
when `tools/report_phase2_runtime_availability.py` reports local ROCm has no
active GPU owner processes.

Dry-run the wrapper without launching:

```bash
python3 tools/wait_and_launch_phase2_stage_a.py \
  --dry-run \
  --output-dir outputs/analysis/phase2_stage_a_wait_and_launch_dryrun
```

The launcher will only adopt a unique locally tracked session from
`colab status`. It will not adopt orphaned server assignments shown as `?`.
If multiple named sessions are active, stop the extras or use the explicit
session path below.

## Explicit Session Path

If the session name is known:

```bash
python3 tools/launch_phase2_stage_a_rate175_colab.py \
  --session open-duck-t4-stagea \
  --no-create \
  --run-workflow \
  --output-dir outputs/analysis/phase2_stage_a_rate175_colab_named_existing
```

Use this only when `colab status -s open-duck-t4-stagea` shows the session.

## Allocate And Run Path

Allocation can consume Colab compute units and is disabled by default in the
launcher. Prefer the adopt-existing-session path above. Use this only when an
operator explicitly approves spending compute units:

```bash
python3 tools/launch_phase2_stage_a_rate175_colab.py \
  --session open-duck-t4-stagea \
  --accelerator T4 \
  --allow-colab-allocation \
  --attempts 6 \
  --delay-s 300 \
  --run-workflow \
  --output-dir outputs/analysis/phase2_stage_a_rate175_colab_retry_detached
```

A100 and L4 are not currently reliable for this account/runtime through the CLI
allocation path because the backend rejected both in the latest committed
checks.

## Success Criteria For This Runbook

The runbook has not succeeded until all of the following are true:

1. Stage A GPU training starts from the rate175 checkpoint and behavior prior.
2. At least one post-step checkpoint is exported and downloaded.
3. The checkpoint sweep runs against the corrected actuator bridge.
4. The selected checkpoint passes the required x=0.08 and x=0.0 corrected
   bridge gates for the current Stage A curriculum.
5. The selected checkpoint hash and gate artifacts are committed.

Until then, Phase 2 remains open and robot validation remains blocked.

## Post-Run Checkpoint Readiness

After any Stage A GPU run, first scan the artifact root:

```bash
python3 tools/report_phase2_stage_a_postrun_status.py
```

`tools/launch_phase2_stage_a_rate175_colab.py --run-workflow` runs this scan
automatically after the workflow command returns and records the result in its
retry JSON/markdown. Running the scanner manually is still useful when artifacts
are copied into the artifact root outside the launcher.

If the report returns `PASS_STAGE_A_CHECKPOINTS_READY`, run the
`sweep_command_shell` recorded in:

```text
outputs/analysis/phase2_stage_a_postrun_status.json
```

If it returns `HOLD_STAGE_A_CHECKPOINTS_MISSING`, the run did not produce a
usable checkpoint and must not advance to Stage B/C/D or robot validation.
