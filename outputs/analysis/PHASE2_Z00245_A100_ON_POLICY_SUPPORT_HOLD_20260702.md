# Phase 2 z=0.00245 A100 On-Policy Support Hold

status: `HOLD_Z00245_ON_POLICY_SUPPORT_LOW_PROGRESS`
timestamp_utc: `2026-07-02T08:52:25Z`

## Summary

The pinned A100 Colab path can train/export the z=0.00245 on-policy support
recipe. The earlier `HOLD_REMOTE_NO_SENTINEL` was a Colab CLI polling artifact:
the remote training job continued after the local helper misread the session as
idle, produced final manifests, and exported checkpoints.

The resulting full-run checkpoints are not promotable. A local compact CPU sweep
against the corrected bridge shows all three checkpoints are stable and
in-envelope, but x=0.08 forward progress remains below the compact promotion
threshold.

No robot, SSH, deploy, grounded replay, or runtime behavior change was performed.

## A100 Evidence

- session: `open-duck-a100-phase2-z00245`
- workflow: `phase2-z0025-boundary`
- run artifact bundle: `outputs/analysis/colab_cli/open-duck-a100-phase2-z00245-phase2-z0025-boundary-20260702T082113Z/open_duck_colab_cli_phase2-z0025-boundary_20260702T082142Z_artifacts.tar.gz`
- artifact bundle sha256: `952e81c3893ae157eb853105a22f1b8a43c1e6f887862e2b95429e70ddd70488`
- remote exit status in bundle: `exit_status=0`
- full run manifest status: `PASS_SMOKE_RUN`
- full run elapsed: `780.06 s`

Exported full-run checkpoints:

| step | onnx | sha256 |
|---:|---|---|
| 40960 | `2026_07_02_082559_40960.onnx` | `b466b5fdcf6c02e75ea72b56886310ae7b1a3ee036c98dab0a534dc4d5f8ed2c` |
| 81920 | `2026_07_02_082857_81920.onnx` | `3652e8868acb0f98a8e150eb881759be6ddb24a7bbb1055e47d85de8a6c12e68` |
| 122880 | `2026_07_02_082918_122880.onnx` | `c7f1e3b227d5fb56067ef2a6512127a480ea38b0d9a744dab559389e8aa2e0e7` |

## Compact Sweep

- sweep markdown: `outputs/analysis/phase2_z00245_on_policy_support_fullrun_compact_sweep/CANDIDATE_CHECKPOINT_SWEEP.md`
- sweep json: `outputs/analysis/phase2_z00245_on_policy_support_fullrun_compact_sweep/candidate_checkpoint_sweep.json`
- sweep json sha256: `4fb162ca6e8fbb5c8bc2535efa6ff0fb41edcdf3539378ef3d46a7001d6850cf`
- commands: `0.0,0.08`
- duration: `1.0 s`
- bridge: corrected fitted bridge
- platform: local CPU

| checkpoint | x=0.0 | x=0.08 | max pitch vel p95 | max tracking p95 | x=0.08 track ratio | x=0.08 mean vx |
|---|---|---|---:|---:|---:|---:|
| `40960` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 1.4225 | 0.2133 | 0.2200 | 0.0176 |
| `81920` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 1.4523 | 0.2142 | 0.1823 | 0.0146 |
| `122880` | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 1.4154 | 0.2127 | 0.2174 | 0.0174 |

All compact x=0.08 screens stayed below the corrected per-joint velocity
envelope and had zero action saturation. The hold is low forward progress plus a
small tracking miss, not over-envelope motion.

## Decision

Do not promote any z=0.00245 on-policy support checkpoint from this run.

This result is directionally useful because it did not reintroduce over-envelope
motion, but the policy is too conservative for the Phase 2 robustness objective.
The next policy-producing step should increase motion while preserving the
corrected envelope, rather than adding another generic safety penalty.
