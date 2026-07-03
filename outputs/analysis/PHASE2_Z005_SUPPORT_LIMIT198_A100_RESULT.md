# Phase 2 z=0.005 Support Limit198 A100 Result

status: `HOLD_Z005_SUPPORT_LOW_FORWARD_PROGRESS`
generated_at: `2026-07-03T17:47:11Z`

Offline-only A100 run. No robot test, SSH, deploy, grounded replay, or runtime
behavior change was performed.

## Run

- workflow: `phase2-z005-support`
- Colab session: `open-duck-phase2-a100`
- hardware: `A100`
- JAX pin: `0.7.2`
- restore checkpoint: `outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint`
- restore checkpoint used remotely: `/content/open-duck-mini-rdkx5/outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint`
- training status: `PASS_SMOKE_RUN`
- training elapsed: `750.047s`
- artifact bundle: `outputs/analysis/colab_cli/open-duck-phase2-a100-phase2-z005-support-20260703T163436Z/open_duck_colab_cli_phase2-z005-support_20260703T163548Z_artifacts.tar.gz`
- artifact sha256: `45652179cb0d62d9a2f462fd7c25956c438712283a4bb722b8ddf3e9f751465d`

## Training Outputs

| step | reward | ONNX sha256 |
|---:|---:|---|
| 40960 | 28.378294 | `31260d5efb629203556bbf8e22b6155c82b22567dcf33ece31be98f33afbe727` |
| 81920 | 28.327553 | `7d26c6f6cdc3df07931eedd0f8caa213f27616658ce381628f92913849d28aeb` |
| 122880 | 31.003510 | `ebde0f0802eaa154704fe22bedc6db2bfd617aea227e79afe22b93032b07acad` |

## Compact Checkpoint Sweep

The 1s corrected-bridge sweep rejected all checkpoints for promotion. All x=0.08
variants stayed below the measured velocity envelope but lost forward progress.

| checkpoint | x | status | max vel p95 | max tracking p95 | track ratio | mean vx |
|---|---:|---|---:|---:|---:|---:|
| `40960` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 1.1325 | 0.1889 | NA | -0.0089 |
| `40960` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 1.5730 | 0.3011 | 0.1780 | 0.0142 |
| `81920` | 0.000 | `PASS_CANDIDATE_SIM_GATE` | 1.0737 | 0.1877 | NA | -0.0068 |
| `81920` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 1.5993 | 0.3123 | 0.1449 | 0.0116 |
| `122880` | 0.000 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 1.1976 | 0.1907 | NA | -0.0077 |
| `122880` | 0.080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 1.4584 | 0.3077 | 0.0757 | 0.0061 |

Best available checkpoint: `40960`, but it is not promoted:
`HOLD_PARTIAL_CANDIDATE_CHECKPOINT`.

## Full Gate

The wrapper started the full 8-seed x=0.08 gate for checkpoint `40960`, but the
Colab runtime/CLI state was lost before final results could be downloaded. The
compact sweep already rejects the candidate, so this does not block the decision.

## Decision

Do not promote this z=0.005 support PPO continuation. It preserved the corrected
velocity envelope but regressed motion below the minimum compact sweep threshold.
The next training change should preserve teacher/live-oracle action structure or
single-support continuity, not add another scalar support/base-height reward tweak.
