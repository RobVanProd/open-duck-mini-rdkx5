# Phase 2 Stage A Narrow T4 Decision

status: `HOLD_STAGE_A_FLAT_WRONG_WARMSTART_SUPERSEDED`
generated_at: `2026-07-06T08:36:00Z`

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

- The first detached Colab console attempt completed training but lost the remote exit sentinel after artifacts were produced.
- Plain `colab exec` reached the training command but hit CUDA OOM during MJX env construction.
- `colab exec` with `XLA_PYTHON_CLIENT_PREALLOCATE=false` and `XLA_PYTHON_CLIENT_MEM_FRACTION=0.50` is the working T4 path.
- A stale Colab T4 session had to be stopped and recreated before the corrected Stage A run.
- The prior T4 artifact used rough terrain/push difficulty and is superseded for Stage A curriculum decisions.

## Corrected Flat Run

This run corrected the Stage A surface and push curriculum, but it was later found to use the phase-modulated health-routed parent checkpoint instead of the Phase 1 `corrected_bridge_cmd_conditioned_rate175` trainable checkpoint required by the Phase 2 goal. Treat this as a useful Colab/T4 and recipe diagnostic, not as the final Stage A curriculum verdict.

- task: `flat_terrain_backlash`
- pushes: `disabled`
- terrain heightfield: `none`
- narrow DR: enabled
- corrected actuator bridge: enabled
- remote run: `/content/open_duck_training_phase2_stage_a_narrow_cli/smoke_20260706T081336Z_gpu`
- local artifact root: `outputs/analysis/colab_cli_stage_a_flat/open-duck-t4-stagea-phase2-stage-a-narrow-20260706T081244Z/extracted_artifacts/open_duck_colab_cli_phase2-stage-a-narrow_20260706T081308Z`
- training status: `PASS_SMOKE_RUN`
- return code: `0`
- elapsed: `870.09s`
- reward steps:
  - `0`: `42.9856`
  - `81920`: `54.6414`
  - `163840`: `51.1143`
  - `245760`: `51.4577`

## Exported Checkpoints

| step | sha256 |
|---:|---|
| `81920` | `30a7cf3a964a4cb9891db46b23aaebec214741871a678fe735d46321728dd28b` |
| `163840` | `99d4922bab86670f59b1ad1526af9a3685c7e4a4ffe0e9a11f83999ff18d5c28` |
| `245760` | `2ed742ac1af9ca71699d2ce029285e8debb67ce88389bbd29ac961b5fd14941d` |

## Checkpoint Triage

Triage command: `tools/sweep_candidate_checkpoints.py`, corrected bridge, fitted mode, CPU eval, commands `0.0,0.08`, duration `1.0s`.

| checkpoint | x=0.0 status | x=0.08 status | x=0.08 vx | x=0.08 track ratio | max pitch vel p95 | envelope | max tracking p95 | decision |
|---|---|---|---:|---:|---:|---|---:|---|
| `81920` | `HOLD_CANDIDATE_TRACKING` | `HOLD_CANDIDATE_TRACKING` | `0.0222` | `0.2781` | `3.3839` | `ABOVE_MEASURED_ENVELOPE` | `0.2651` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` |
| `163840` | `HOLD_CANDIDATE_TRACKING` | `HOLD_CANDIDATE_TRACKING` | `0.0213` | `0.2664` | `3.4042` | `ABOVE_MEASURED_ENVELOPE` | `0.2655` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` |
| `245760` | `HOLD_CANDIDATE_TRACKING` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `0.0154` | `0.1919` | `2.8349` | `INSIDE_MEASURED_ENVELOPE` | `0.2659` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` |

## Decision

The corrected flat/no-push curriculum runs successfully on Colab T4 with pinned JAX `0.7.2` and explicit memory controls, but this run is superseded for Phase 2 decision-making because it used the wrong warm-start lineage.

The early checkpoints preserve some forward motion but exceed the corrected velocity envelope and remain on the tracking plateau. The latest checkpoint stays inside the envelope but loses too much forward progress. Do not promote any checkpoint from this run to full gates or robot validation.

Next aligned work is to rerun Stage A with the Phase 1 `ppo_bc_command_conditioned_rate175_step0_checkpoint`, the matching default PPO network shape, and an explicit behavior-prior continuity hook. The failure is no longer Colab infrastructure; the remaining question is whether the true Phase 1 warm-start can survive narrow flat DR without collapsing back to the deployable-student tracking plateau.
