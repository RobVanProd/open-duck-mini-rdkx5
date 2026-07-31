# Stage A No-Behavior-Prior Direct-Outcome Result

Date: 2026-07-11

Status: **NO CHECKPOINT PASSED BOTH COMPACT GATES; BRANCH CLOSED**

The preregistered one-factor Colab T4 experiment replayed the authoritative
Stage A recipe with behavior-prior loss disabled and every other registered
training setting preserved. Training completed successfully and emitted steps
81,920, 163,840, and 245,760.

| step | training reward | x=0 status | x=0.08 status | x=0.08 vx | ratio | tracking p95 |
|---:|---:|---|---|---:|---:|---:|
| 81,920 | 57.1185 | PASS | low-progress hold | 0.01671 | 0.20884 | 0.21211 |
| 163,840 | 57.8771 | PASS | tracking hold | 0.02200 | 0.27498 | 0.21690 |
| 245,760 | 58.1289 | PASS | tracking hold | 0.02227 | 0.27836 | 0.21644 |

No checkpoint passed both required commands, so the preregistered seeds 40-71
expansion was not run. Higher training reward did not produce a passing compact
outcome. Relative to the prior-selected step 163,840 baseline, removing the
behavior prior reduced x=0.08 forward velocity while leaving the failing
tracking magnitude essentially unchanged. The behavior-prior penalty was not
the sole bottleneck.

The Colab session was stopped after artifact download to preserve credits. No
local GPU, robot, deployment, or hardware runtime was used.

Primary artifact:

- `outputs/analysis/colab_cli_stage_a_no_prior_direct_outcome/open-duck-t4-stagea-no-prior-phase2-stage-a-narrow-20260711T210422Z/artifact/open_duck_colab_cli_phase2-stage-a-narrow_20260711T210524Z/phase2_stage_a_narrow_rate175_cuda_checkpoint_sweep/candidate_checkpoint_sweep.json`
