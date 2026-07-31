# PPO BC Command-Conditioned DAgger Seed-5 Warm-Start Decision

status: `PASS_WARMSTART_INFRASTRUCTURE_READY_BUT_POLICY_STILL_HOLDS_X008_TRACKING`

This is an offline training-readiness result. It did not run robot tests, SSH,
deploy, change robot runtime behavior, or approve a robot candidate.

## Inputs

- BC NPZ: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate/candidate_mlp.npz`
- BC reference ONNX: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate/candidate.onnx`
- BC manifest: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_manifest.json`

## Warm-Start Artifact

- PPO checkpoint: `outputs/analysis/ppo_bc_command_conditioned_dagger_seed5_x0_step0_checkpoint`
- PPO step-0 ONNX: `outputs/analysis/ppo_bc_command_conditioned_dagger_seed5_x0_step0.onnx`
- fidelity report: `outputs/analysis/PPO_BC_COMMAND_CONDITIONED_DAGGER_SEED5_X0_STEP0_EXPORT_FIDELITY.md`

The PPO step-0 export matches the BC ONNX closely enough to use as a warm start:

```text
status: PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY
samples_checked: 2048
p95_abs_error: 0.000000119
max_abs_error: 0.000000358
```

## Step-0 Gates

The exported PPO step-0 ONNX preserves the current best DAgger-fixed behavior:

```text
x=0.0 fitted bridge:
  status: PASS_CANDIDATE_SIM_GATE
  pitch tracking p95 max: 0.0691 rad
  sent target velocity p95 max: 0.2964 rad/s

x=0.08 fitted bridge:
  status: HOLD_CANDIDATE_TRACKING
  mean vx: 0.0213 m/s
  track ratio: 0.2663
  pitch tracking p95 max: 0.1872 rad
  sent target velocity p95 max: 1.9571 rad/s
```

This is expected: the warm-start artifact is behavior-preserving. It fixes the
training starting point; it does not itself solve x=0.08 tracking.

## Restore Smoke

The first tiny CPU restore smoke failed only because the checkpoint path was
relative to the runner working directory:

```text
status: HOLD_SMOKE_RUN
error: checkpoint path does not exist
```

`tools/run_actuator_bridge_training_smoke.py` now resolves relative
`--restore-checkpoint-path` values against the RDK repo and resolves relative
`--output-root` values into the RDK repo before invoking the Playground runner.

The path-fixed restore smoke passed:

```text
status: PASS_SMOKE_RUN
num_timesteps: 16
saved checkpoint: step 20
reward: 3.6467
```

## Decision

The next valid branch is PPO fine-tuning from
`outputs/analysis/ppo_bc_command_conditioned_dagger_seed5_x0_step0_checkpoint`
with the fitted actuator bridge active. Grade it by the standard offline gates:

```text
must preserve:
  x=0.0 hard-seed stability

must improve:
  x=0.08 pitch-chain tracking p95

must not regress:
  action saturation
  fitted-envelope target velocity
  forward progress
  posture/base-height stability
```

Do not run robot validation until both x=0.0 and x=0.08 fitted-bridge sim gates
pass.
