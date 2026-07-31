# Phase 2 B0F A100 Direct-Exec Hold

status: `HOLD_B0F_LOW_FORWARD_PROGRESS`

## Scope

This was an offline A100 sim/training run only. No robot tests, SSH, deploy,
grounded replay, runtime behavior changes, or policy overwrite were performed.

## Execution

The B0F push-local preserve recipe was rerun through the direct `colab exec`
workflow path after the raw-console path repeatedly lost the session. The
upload scope was reduced to the artifacts B0F actually needs:

- corrected actuator fit
- behavior-prior MLP NPZs
- B0C rough-terrain restore checkpoint

Training completed successfully on the A100:

```text
run_dir: /content/open_duck_training_phase2_b0f_cli/smoke_20260629T114523Z_gpu
returncode: 0
elapsed_s: 738.859
platform: gpu / cuda
```

Downloaded artifact bundle:

```text
outputs/analysis/colab_cli/open-duck-a100-phase2-b0f-20260629T114139Z/open_duck_colab_cli_phase2-b0f_20260629T114157Z_artifacts.latest.tar.gz
sha256: 37135fae56902879f719b4824be79d09faa793eb3887170307d4cb8f02295b38
size: 4.4M
```

The Colab driver produced complete training and checkpoint-sweep artifacts, but
the local `colab exec` process did not return after the final bundle was
available. The A100 session was stopped after the complete artifact was
downloaded. Treat this as a wrapper-return issue, not as a training or policy
result.

## ONNX Exports

| step | sha256 |
|---:|---|
| 40960 | `19d95393c538e04d09c0904126e43ac80af56470ec95e4c705eef32634670673` |
| 81920 | `178b8cba9a8386975db2207089a869ffe5a3b236e9a334518faeacead31b00b0` |
| 122880 | `bbb6f6b73d34951928c89700c99eab94f8bca2ba68e56f645c5d351c721d484b` |

## Checkpoint Sweep

All three checkpoints completed both x=0.0 and x=0.08 sweep commands, but none
were promotable.

| checkpoint | status | track ratio x=0.08 | max pitch tracking p95 | max sent vel p95 | action saturation |
|---|---|---:|---:|---:|---:|
| 40960 | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 0.2372 | 0.2214 | 1.5807 | 0.0% |
| 81920 | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 0.2215 | 0.2196 | 1.5725 | 0.0% |
| 122880 | `HOLD_PARTIAL_CANDIDATE_CHECKPOINT` | 0.2411 | 0.2189 | 1.5706 | 0.0% |

Selected best available checkpoint:

```text
step: 122880
sha256: bbb6f6b73d34951928c89700c99eab94f8bca2ba68e56f645c5d351c721d484b
selection_reason: best_available_but_not_promoted
```

Failure reasons for the selected checkpoint:

```text
command 0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
command 0.08: track ratio 0.2411 < 0.2500
command 0.08: mean vx 0.0193 < 0.0200
```

## Decision

B0F is not promoted. It remains in-envelope and non-saturating, but it does not
clear the corrected-bridge x=0.08 forward-progress gate and still sits above the
strict pitch-tracking target (`0.2189 rad` vs `0.20 rad`).

The direct A100 path is viable for producing training and gate artifacts, but
the `colab exec` wrapper needs a better return/timeout strategy after the
artifact bundle is complete.

Robot validation remains blocked.
