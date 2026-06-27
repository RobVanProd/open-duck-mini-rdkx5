# A100 V16 Tiny Restore / Local CPU Follow-up Summary

status: `HOLD_A100_OR_COLAB_RUNTIME_AFTER_LOCAL_CPU_RESTORE_PASS`

## Context

After the full V16 phase-1 attempt reached only step 0 and produced no sentinel,
a tiny restored V16 run was launched to isolate workload size from checkpoint
restore/training-path issues.

Command shape:

```text
recipe: movement_bootstrap_v16
restore: policy/candidates/movement_bootstrap_v5_phase1_trainable_recovery_20260623/checkpoint_2026_06_23_205634_368640
stop_after_phase: 1
timesteps_scale: 0.001
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

The run reached the phase-1 runner and created partial files:

```text
smoke_manifest.start.json
stdout.txt
stderr.txt
events.out.tfevents...
```

`stdout.txt` showed:

```text
Observation size: 101
PPO params: {... num_envs: 4, num_timesteps: 120 ...}
Skipping checkpoint/export at step 0; export_min_step=1
```

No final manifest, ONNX, checkpoint, exit sentinel, or artifact bundle was
produced before the session was stopped. This reproduces the post-step-0 stall
even with a tiny workload.

## Local CPU Follow-up

The same tiny restored V16 phase-1 path was rerun locally on CPU after resolving
the restore checkpoint to an absolute path before invoking the Playground
runner.

Result:

```text
status: PASS_STAGED_CURRICULUM_RUN
platform: cpu
num_timesteps: 120
final_checkpoint: /tmp/open_duck_v16_tiny_cpu_fixed/01_phase1_v5_anchor_mild_bridge_consistency/smoke_20260624T113100Z_cpu/2026_06_24_073135_120
final_candidate_onnx: /tmp/open_duck_v16_tiny_cpu_fixed/01_phase1_v5_anchor_mild_bridge_consistency/smoke_20260624T113100Z_cpu/2026_06_24_073135_120.onnx
```

The generated local plan artifact is intentionally left out of git because
`outputs/analysis/*_PLAN.md` and `outputs/analysis/*_plan.json` are ignored.

## Interpretation

This points away from the V16 recipe and restored-checkpoint code path as the
primary cause. The restored V16 path can advance past step 0, checkpoint, and
export on local CPU after the absolute restore-path fix.

The remaining hold is specific to the A100/Colab/CUDA workflow or remote session
state. Before another full V16 A100 phase-1 launch, rerun a tiny A100 restored
smoke with the PID-aware poller and timeout-safe PID probe to confirm whether
the remote CUDA path still stalls after step 0.

No robot tests, SSH, deployment, runtime behavior changes, or policy deployment
were performed.
