# Stage A Direct Joint-Target Tracking Result

Date: 2026-07-11

Status: **NO CHECKPOINT PASSED BOTH COMPACT GATES; BRANCH CLOSED**

The preregistered one-factor Colab T4 experiment replayed the authoritative
prior-enabled Stage A recipe and added only the data-calibrated six-pitch-joint
sent-target versus actual-position cost. Training completed successfully and
emitted steps 81,920, 163,840, and 245,760.

| step | training reward | x=0 status | x=0.08 status | x=0.08 vx | ratio | tracking p95 |
|---:|---:|---|---|---:|---:|---:|
| 81,920 | 56.6923 | pass | low-progress hold | 0.01757 | 0.21958 | 0.21274 |
| 163,840 | 57.8067 | pass | tracking hold | 0.02237 | 0.27959 | 0.21784 |
| 245,760 | 56.9045 | pass | tracking hold | 0.02120 | 0.26505 | 0.21703 |

No checkpoint passed both commands, so the registered seeds 40-71 expansion
was not run. The calibrated direct cost preserved the x=0 compact gate but did
not reduce x=0.08 tracking below 0.20 rad. At the two progress-complete
checkpoints, tracking was slightly worse than the no-prior comparison
(`0.21690` and `0.21644`) and remained in the same failing range as previous
Stage A experiments. This is evidence against the exact pitch-chain mean-cost
formulation at its frozen equal-contribution scale, not evidence for increasing
the scale after observing outcomes.

Close this exact formulation without tuning scale, delta, joint set,
aggregation, KL, or training length. The implementation remains default-off
and is not promoted into any canonical recipe. Colab was stopped after artifact
download to preserve credits.

Primary evidence:

- `outputs/analysis/colab_cli_stage_a_joint_target_tracking/open-duck-t4-stagea-joint-target-tracking-phase2-stage-a-narrow-20260711T234603Z/artifact/open_duck_colab_cli_phase2-stage-a-narrow_20260711T234627Z/phase2_stage_a_narrow_rate175_cuda_checkpoint_sweep/candidate_checkpoint_sweep.json`
- `outputs/analysis/colab_cli_stage_a_joint_target_tracking/open-duck-t4-stagea-joint-target-tracking-phase2-stage-a-narrow-20260711T234603Z/artifact/open_duck_colab_cli_phase2-stage-a-narrow_20260711T234627Z/phase2_stage_a_narrow_rate175_cuda_training_run_summary.json`

No local GPU, robot, SSH, deployment, grounded replay, or moving hardware test
was used.
