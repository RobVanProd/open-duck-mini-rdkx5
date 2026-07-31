# Phase 2 Stage A Rate175 T4 Session Loss

status: `HOLD_COLAB_SESSION_LOST_BEFORE_CHECKPOINT`
generated_at: `2026-07-06T09:45:00Z`

Offline only. No robot, SSH, deploy, grounded replay, or runtime behavior change was performed.

## What Ran

The valid Stage A rate175 workflow was launched on a fresh Colab T4 session:

- session: `open-duck-t4-stagea`
- hardware: `Tesla T4`
- remote run: `/content/open_duck_training_phase2_stage_a_narrow_cli/smoke_20260706T093240Z_gpu`
- task: `flat_terrain_backlash`
- pushes: `disabled`
- terrain heightfield: `none`
- timesteps requested: `163840`
- PPO envs: `64`
- corrected actuator bridge: `enabled`
- restore checkpoint: `outputs/analysis/ppo_bc_command_conditioned_rate175_step0_checkpoint`
- restore-policy KL scale: `4.0`
- behavior prior MLP: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz`
- behavior prior scale: `-0.6`

## Last Live Evidence

The live manifest downloaded before session loss reported:

- status: `RUNNING`
- elapsed: `540.04s`
- return code: `None`
- stdout confirmed observation size `101`
- stdout confirmed the 14-actuator Open Duck Mini v2 order
- stdout confirmed `Enabled restore-policy KL loss: scale=4.0`
- stdout reached `STEP: 0 reward: 43.062255859375 reward_std: 39.42291259765625`
- stdout confirmed `Skipping checkpoint/export at step 0; export_min_step=1`
- no exported checkpoint lines were present
- no step after `0` was observed

## Failure

After the `STEP: 0` live check, the Colab runtime disappeared:

```text
[colab] Session 'open-duck-t4-stagea' not found.
[colab] No active sessions found on server.
```

The local `colab exec` process remained blocked after the remote session disappeared and was interrupted locally. No remote artifact bundle or checkpoint could be downloaded.

## Decision

`HOLD_COLAB_SESSION_LOST_BEFORE_CHECKPOINT`

This run is useful evidence that the valid Stage A command starts correctly on T4 and reaches the first PPO evaluation from the true rate175 warm-start, but it produced no checkpoint and cannot be swept or promoted.

Next step remains the same: rerun the valid Stage A rate175 workflow on a stable Colab T4 session, then sweep exported checkpoints. Prefer the retry launcher's detached console mode so a disappearing hosted runtime is recorded by polling rather than leaving a local `colab exec` wait behind. Do not substitute this partial run or the CPU smoke for a Phase 2 gate.
