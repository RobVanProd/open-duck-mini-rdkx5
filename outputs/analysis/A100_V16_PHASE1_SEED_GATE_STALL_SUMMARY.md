# A100 V16 Phase-1 Seed Gate Stall Summary

status: `HOLD_A100_V16_PHASE1_SEED_GATE_STALL`

## Context

After the tiny restored V16 A100 smoke passed training/export and downloaded
artifacts, a full V16 phase-1 A100 run was launched.

Command shape:

```text
recipe: movement_bootstrap_v16
restore: V5 trainable checkpoint
stop_after_phase: 1
timesteps_scale: 1.0
phase_1_timesteps: 120000
phase_gate_seeds: 0-3
phase_gate_command_x: 0.08
phase_gate_bridge: vanilla
artifact_checkpoint_mode: latest
```

## Result

The remote log shows phase-1 training completed and the workflow entered the
multi-seed phase gate:

```text
phase_1_candidate:
  /content/open_duck_staged_curriculum_cli/01_phase1_v5_anchor_mild_bridge_consistency/smoke_20260624T120332Z_gpu/2026_06_24_121150_122880.onnx

gate_command:
  tools/run_candidate_seed_sweep.py --run
    --policies phase_01=<phase_1_candidate>
    --seeds 0-3
    --command-x 0.08
    --duration 5
    --bridge-mode vanilla
    --jax-platform gpu
```

The seed gate did not emit a result before the Colab session was lost. No final
artifact bundle, seed-gate markdown/json, or checkpoint archive was downloaded
for this full run.

Local surviving evidence:

```text
run_dir: outputs/analysis/colab_cli/open-duck-a100-staged-curriculum-20260624T120315Z
remote_log: remote_live.log
remote_pid: remote_workflow.pid
```

## Interpretation

This is not a V16 policy verdict. It proves the full phase-1 training reached
the seed-gate handoff, but the gate tooling was too opaque: while a seed was
running, the remote log had no per-seed start/finish markers and no partial
seed results.

Follow-up patch:

```text
tools/run_candidate_seed_sweep.py now:
- prints SEED_SWEEP_START / SEED_SWEEP_DONE per seed
- kills the full subprocess process group on timeout
- records HOLD_SEED_TIMEOUT when a seed times out
- writes candidate_seed_sweep.partial.json after every seed
```

Next offline action: rerun V16 phase 1 on A100 with the patched seed sweep.

No robot tests, SSH, deployment, runtime behavior changes, or policy deployment
were performed.
