# Phase 2 Stage A Colab Runbook Status

status: `HOLD_STAGE_A_CHECKPOINTS_MISSING`
generated_at: `2026-07-06T10:29:47Z`

Offline only. No robot, SSH, deploy, grounded replay, training-result promotion,
or runtime behavior change was performed.

## Summary

The Stage A launcher now supports adopting a unique existing Colab CLI session
via `--adopt-existing-session --no-create`, plus a bounded polling mode via
`--wait-for-existing-session`. A no-session short-wait preflight was run and
correctly returned `HOLD_WAIT_TIMEOUT` followed by
`HOLD_NO_CREATE_SESSION_MISSING` without attempting allocation.

Committed runbook:

```text
docs/PHASE2_STAGE_A_COLAB_RUNBOOK.md
```

Current allocation state:

- `colab sessions`: no active sessions
- T4: latest six-attempt detached retry held at `HOLD_SERVICE_UNAVAILABLE`
- A100: backend rejected accelerator
- L4: backend rejected accelerator

Post-run checkpoint state:

- artifact root: `outputs/analysis/colab_cli_stage_a_rate175_prior`
- exported ONNX checkpoints: `0`
- post-run report: `outputs/analysis/PHASE2_STAGE_A_POSTRUN_STATUS.md`

## Next Valid Command

When a browser-kept Colab CLI session is visible:

```bash
python3 tools/launch_phase2_stage_a_rate175_colab.py \
  --adopt-existing-session \
  --no-create \
  --run-workflow \
  --output-dir outputs/analysis/phase2_stage_a_rate175_colab_adopt_existing
```

To wait for a session to appear:

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

Do not substitute CPU smoke for a Phase 2 gate.
