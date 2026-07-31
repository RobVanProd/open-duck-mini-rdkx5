# Phase 2 Home-Reset z0.0026 A100 Decision

status: `HOLD_A100_CONTINUATION_REGRESSED`

## Setup

- source candidate: `policy/candidates/corrected_bridge_cmd_conditioned_rate175_20260627/candidate.onnx`
- source candidate sha256: `63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e`
- warm-start checkpoint: `outputs/analysis/phase2_restore_checkpoints/ppo_bc_command_conditioned_rate175_step0_checkpoint`
- source fidelity checkpoint: `outputs/analysis/ppo_bc_command_conditioned_rate175_step0_export_fidelity.json`
- Colab hardware: `A100`
- JAX/JAXLIB pin: `0.7.2`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.0026`
- reset contract: `home-support` for local gates; training reset randomization forwarded as zero jitter / unit qpos multiplier.
- robot/SSH/deploy/grounded replay: `not run`

## Produced Candidates

Two A100 smoke runs were produced because the first detached launch continued after the CLI appeared to drop; the second `colab exec` launch also completed.

| run | checkpoint | sha256 |
|---|---:|---|
| detached | 40960 | `eca50b0dfca0876673eca67b7739d821c608ed1047378c1dda2b3cfa069c3763` |
| detached | 81920 | `8dcdfb6aca7fd667d88aea4ff4bd31e76dc8f593cbac9b49ff0577004e311588` |
| detached | 122880 | `b25a7b6d366d45a535e02f2a267d7a3ccc3c5ffec86fec8c528c8395c25dc407` |
| exec | 40960 | `42a755ca3cb23fa7ceca8f768157b1dcc3816ac759b51610983ad86148899816` |
| exec | 81920 | `d010c5664466d0f60bb1ebc95ea79551b2874263af25e81eeba1e42fe280d49c` |
| exec | 122880 | `5f0c208f989fbf17abae913d94ab8c44fdd7b1e057be837ce0bb9b041aa0a841` |

## Full Gate On Latest Exec Candidate

Artifact:

- `outputs/analysis/PHASE2_HOME_RESET_Z0026_FROM_RATE175_A100_EXEC_X008_HOME_SUPPORT_GATE.md`
- `outputs/analysis/phase2_home_reset_z0026_from_rate175_a100_exec_x008_home_support_gate.json`

Result for `exec_122880`, `x=0.08`, 15s, seeds 0-7:

- falls: `0/8`
- duration complete: `8/8`
- mean vx: `0.0122 m/s`
- track ratio: `0.1519`
- max pitch sent target velocity p95: `3.7343 rad/s`
- p95 corrected-envelope excess: `1.4843 rad/s`
- max tracking p95: `0.2109 rad`
- single support: `6.67%`
- double support: `93.33%`

This is not promotable: it is too slow and over the corrected per-joint velocity envelope.

## Checkpoint Screen

Artifact:

- `outputs/analysis/PHASE2_HOME_RESET_Z0026_FROM_RATE175_A100_CHECKPOINT_SCREEN_X008_5S.md`
- `outputs/analysis/phase2_home_reset_z0026_from_rate175_a100_checkpoint_screen_x008_5s.json`

5s, seed 0, `x=0.08`, same bridge/task/reset:

| candidate | result | mean vx | track ratio | max pitch vel p95 | p95 vel excess | note |
|---|---|---:|---:|---:|---:|---|
| detached_40960 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0041 | 0.0507 | 1.8848 | 0.0000 | stable standstill/double support |
| detached_81920 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 0.2235 | 2.7935 | 5.2400 | 2.9900 | moves by falling/over-driving |
| detached_122880 | `HOLD_CANDIDATE_ACTION_SATURATION` | 0.0393 | 0.4915 | 5.2400 | 2.9900 | over-envelope/saturated |
| exec_40960 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0036 | 0.0455 | 2.0724 | 0.0000 | stable standstill/double support |
| exec_81920 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 0.2256 | 2.8200 | 5.2400 | 2.9900 | moves by falling/over-driving |
| exec_122880 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0110 | 0.1373 | 3.3742 | 1.1242 | slow and over-envelope |

## Decision

The home-reset A100 continuation did not improve the Phase 2 candidate. It preserved a stable double-support/low-progress basin at early checkpoints and drifted into over-envelope falling or saturation at later checkpoints.

Do not promote any checkpoint from this run. The next recipe should not repeat this continuation unchanged. It needs an objective that increases single-support swing/advance while preserving the corrected per-joint envelope, or a separate label/oracle repair before PPO continuation.
