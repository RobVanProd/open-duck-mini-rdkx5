# A100 V16 Tiny Restore Pass / Gate Hold Summary

status: `PASS_A100_TINY_RESTORE_TRAINING_EXPORT_HOLD_TOY_POLICY_GATES`

## Context

After the local CPU restored V16 smoke passed, a fresh A100 Colab session was
created to rerun the same tiny restored V16 phase-1 path through the headless
Colab workflow.

This was an offline infrastructure smoke, not a real policy-training attempt:

```text
recipe: movement_bootstrap_v16
restore: policy/candidates/movement_bootstrap_v5_phase1_trainable_recovery_20260623/checkpoint_2026_06_23_205634_368640
stop_after_phase: 1
timesteps_scale: 0.001
num_timesteps: 120
phase_gate: disabled
ppo_num_envs: 4
ppo_num_evals: 1
episode_length: 50
unroll_length: 5
batch_size: 4
minibatches: 1
updates_per_batch: 1
```

## Result

The A100 restored training/export path completed and produced a final artifact
bundle:

```text
run_dir: outputs/analysis/colab_cli/open-duck-a100-staged-curriculum-20260624T113629Z
artifact: open_duck_colab_cli_staged-curriculum_20260624T113643Z_artifacts.tar.gz
training_manifest: PASS_SMOKE_RUN
platform: gpu
candidate_sha256: c81a9fe92bf726725273ce87389a4edd7aff012a59b09fbbf00a4de0dc42b5a9
candidate_onnx_size_bytes: 883946
```

The generated toy candidate correctly held sim gates and is not robot-safe:

```text
x=0.0 gate:  HOLD_CANDIDATE_FALL_OR_TERMINATION
x=0.08 gate: HOLD_CANDIDATE_FALL_OR_TERMINATION
```

Important gate metrics:

```text
x=0.0:
  fitted samples: 74, termination: fall_or_nan
  stress samples: 77, termination: fall_or_nan
  max pitch tracking p95: 0.1688 rad
  max abs body pitch p95: 1.2376 rad
  min base height: 0.0253 m

x=0.08:
  vanilla samples: 76, termination: fall_or_nan, track_ratio: 2.6791
  fitted samples: 51, termination: fall_or_nan, track_ratio: 3.7301
  stress samples: 750, termination: duration_complete, track_ratio: 0.0294
  max pitch tracking p95: 0.2583 rad
  max sent target velocity p95: 2.2603 rad/s
  min base height: 0.0279 m
```

## Interpretation

This clears the previous A100 post-step-0/no-sentinel concern for the tiny
restored V16 path. The workflow can now:

```text
1. create a fresh A100 session,
2. upload the repo and Playground,
3. restore the V5 checkpoint,
4. run V16 phase-1 training on GPU,
5. export ONNX,
6. run x=0 and x=0.08 sim gates,
7. download final artifacts.
```

The 120-step candidate itself is intentionally invalid and should not influence
robot decisions. The next offline action is a full V16 phase-1 A100 run with the
multi-seed phase gate enabled.

No robot tests, SSH, deployment, runtime behavior changes, or policy deployment
were performed.
