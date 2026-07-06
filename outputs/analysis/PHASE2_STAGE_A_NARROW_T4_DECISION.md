# Phase 2 Stage A Narrow T4 Decision

status: `HOLD_STAGE_A_NARROW_CHECKPOINT_REJECTED`
generated_at: `2026-07-06T08:02:00Z`

Offline only. No robot, SSH, deploy, grounded replay, or runtime behavior change was performed.

## Execution

- workflow: `phase2-stage-a-narrow`
- Colab session: `open-duck-t4-stagea`
- hardware: `Tesla T4`
- JAX/JAXLIB: `0.7.2 / 0.7.2`
- Brax: `0.14.2`
- MuJoCo/MJX: `3.9.0 / 3.9.0`
- Playground: `0.0.5`

## Transport Findings

- Detached Colab console mode lost the remote exit sentinel after training artifacts were produced.
- Plain `colab exec` reached the training command but hit CUDA OOM during MJX env construction.
- `colab exec` with `XLA_PYTHON_CLIENT_PREALLOCATE=false` and `XLA_PYTHON_CLIENT_MEM_FRACTION=0.50` completed a bounded Stage A diagnostic and packaged artifacts.
- The Stage A workflow now defaults to those T4-safe memory flags and clears the remote Stage A output root before training to avoid stale artifact mixing.

## Stage A Run

- remote run: `/content/open_duck_training_phase2_stage_a_narrow_cli/smoke_20260706T070404Z_gpu`
- local artifact root: `outputs/analysis/colab_cli_exec_smoke/open-duck-t4-stagea-phase2-stage-a-narrow-20260706T071729Z/extracted_artifacts/open_duck_colab_cli_phase2-stage-a-narrow_20260706T071755Z`
- training status: `PASS_SMOKE_RUN`
- return code: `0`
- elapsed: `1440.38s`
- reward steps:
  - `0`: `40.2120`
  - `81920`: `45.7926`
  - `163840`: `45.9004`
  - `245760`: `52.6605`

## Exported Checkpoints

| step | sha256 |
|---:|---|
| `81920` | `7945342301c8619e5515d3fb280d13e6a865224e6e0b909a7100604745f8b98c` |
| `163840` | `267ab535ab48a83a28520eca527b2e93490e0fb18310f42202b9c5615a415d91` |
| `245760` | `bbdb4a70e2d30ab1e9a8eca0758472e27f5671788f4a5558a9a2d4c05abc6c3e` |

## Checkpoint Triage

Triage command: `tools/sweep_candidate_checkpoints.py`, corrected bridge, fitted mode, CPU eval, commands `0.0,0.08`, duration `1.0s`.

| checkpoint | x=0.0 status | x=0.08 status | x=0.08 vx | x=0.08 track ratio | max pitch vel p95 | max tracking p95 | decision |
|---|---|---|---:|---:|---:|---:|---|
| `81920` | `HOLD_CANDIDATE_TRACKING` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `0.0147` | `0.1834` | `2.8246` | `0.2655` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` |
| `163840` | `HOLD_CANDIDATE_TRACKING` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `0.0168` | `0.2101` | `2.8254` | `0.2661` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` |
| `245760` | `HOLD_CANDIDATE_TRACKING` | `HOLD_CANDIDATE_TRACKING` | `0.0207` | `0.2581` | `3.3749` | `0.2664` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` |

## Decision

Stage A narrow DR can run on Colab T4 when using `colab exec` plus explicit XLA memory controls, but this Stage A run did not produce a promotable checkpoint. The latest checkpoint improved forward motion, but it exceeded the corrected velocity envelope and remained on the tracking plateau.

Next aligned work is a recipe adjustment that preserves the Stage A execution path while adding a stronger continuity/teacher constraint or reducing the DR/push difficulty. Do not promote any Stage A T4 checkpoint from this run to robot validation.
