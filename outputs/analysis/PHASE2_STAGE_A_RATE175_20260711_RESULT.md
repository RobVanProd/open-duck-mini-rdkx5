# Phase 2 Stage A Rate175 Colab Result

status: `HOLD_STAGE_A_TRACKING_GATE`
generated_at: `2026-07-11T03:00:40Z`

Offline only. No robot, SSH, deploy, grounded replay, local GPU, or runtime
behavior change was performed.

## Run

- workflow: `phase2-stage-a-narrow`
- accelerator: Colab T4
- training return code: `0`
- elapsed training time: `900.105858279` seconds
- restore checkpoint: `ppo_bc_command_conditioned_rate175_step0_checkpoint`
- restore-policy KL scale: `4.0`
- behavior-prior scale: `-0.6`
- behavior-prior Huber delta: `0.05`
- actionable training warnings: `0`

## Checkpoints

| step | reward | reward std | sha256 |
|---:|---:|---:|---|
| 81920 | 56.105675 | 36.301289 | `1a4544a09c006db21f0f12be5795b2efd5971d26d2216d3db02e1d3fd7f62339` |
| 163840 | 57.847050 | 37.805481 | `7f00297b33cc470f5371dde0ce3f8fdf4f529f9c3cc68743cad1343082539960` |
| 245760 | 57.527058 | 37.918053 | `4d9e41cae487a32dd93075c74985f2f693b6f46b852aecd05dab06b2f64fe229` |

## Compact Corrected-Bridge Sweep

All checkpoints passed the one-second `x=0.0` compact gate and remained below
the measured pitch-chain velocity envelope. None passed both required commands.

| step | x=0.08 status | mean vx | tracking ratio | pitch velocity p95 | tracking p95 |
|---:|---|---:|---:|---:|---:|
| 81920 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0136 | 0.1700 | 1.5657 | 0.2143 |
| 163840 | `HOLD_CANDIDATE_TRACKING` | 0.0298 | 0.3724 | 1.5012 | 0.2177 |
| 245760 | `HOLD_CANDIDATE_TRACKING` | 0.0219 | 0.2742 | 1.5346 | 0.2170 |

## Decision

Step 163840 is the best diagnostic checkpoint because it has the strongest
forward progress and command-tracking ratio, but it is explicitly not promoted.
Do not run robot validation or a larger promotion gate from this result.

The evidence closes another scalar reward tweak as the next move. Before any
additional training, specify and review a teacher-action or trust-region
continuity mechanism intended to preserve actuator tracking while retaining the
forward-progress gain. Pre-register its acceptance gates against this result.

## Evidence

- Colab retry report:
  `outputs/analysis/phase2_stage_a_rate175_colab_20260710_retry2/PHASE2_STAGE_A_RATE175_COLAB_RETRY.md`
- post-run checkpoint report:
  `outputs/analysis/phase2_stage_a_rate175_colab_20260710_retry2/PHASE2_STAGE_A_POSTRUN_STATUS.md`
- downloaded training and sweep artifact root:
  `outputs/analysis/colab_cli_stage_a_rate175_prior/open-duck-t4-stagea-phase2-stage-a-narrow-20260711T020114Z/artifact/open_duck_colab_cli_phase2-stage-a-narrow_20260711T020137Z`
