# Phase 2 Stage A Colab Runbook Status

status: `HOLD_COLAB_GPU_ALLOCATION`
generated_at: `2026-07-06T10:23:43Z`

Offline only. No robot, SSH, deploy, grounded replay, training-result promotion,
or runtime behavior change was performed.

## Summary

The Stage A launcher now supports adopting a unique existing Colab CLI session
via `--adopt-existing-session --no-create`. A no-session preflight was run and
correctly returned `HOLD_NO_CREATE_SESSION_MISSING` without attempting
allocation.

Committed runbook:

```text
docs/PHASE2_STAGE_A_COLAB_RUNBOOK.md
```

Current allocation state:

- `colab sessions`: no active sessions
- T4: latest six-attempt detached retry held at `HOLD_SERVICE_UNAVAILABLE`
- A100: backend rejected accelerator
- L4: backend rejected accelerator

## Next Valid Command

When a browser-kept Colab CLI session is visible:

```bash
python3 tools/launch_phase2_stage_a_rate175_colab.py \
  --adopt-existing-session \
  --no-create \
  --run-workflow \
  --output-dir outputs/analysis/phase2_stage_a_rate175_colab_adopt_existing
```

Do not substitute CPU smoke for a Phase 2 gate.

