# Phase 2 z=0.00245 Motion-Recovery A100 Result

status: `HOLD_Z00245_MOTION_RECOVERY_LOW_FORWARD_PROGRESS`

## Summary

The A100 motion-recovery run completed training and exported three checkpoints,
but the compact corrected-bridge checkpoint sweep did not promote any
checkpoint. All three checkpoints remained inside the corrected velocity
envelope and completed the short `x=0.0` / `x=0.08` evals, but all held at
`x=0.08` for low forward progress.

This closes the small scalar-progress-pressure retry. The next aligned branch
should use teacher-action / trust-region / live-oracle continuity rather than
another small scalar reward nudge.

No robot test, SSH, deploy, grounded replay, or runtime behavior change was
performed.

## Run Identity

- local branch head: `977092e790766654e14af32f4e0aa0942276a684`
- Colab session: `open-duck-a100-phase2-z00245`
- workflow: `phase2-z0025-boundary`
- remote workflow id: `open_duck_colab_cli_phase2-z0025-boundary_20260702T225135Z`
- training dir: `/content/open_duck_training_phase2_z0025_boundary_cli/smoke_20260702T225504Z_gpu`
- recovered artifact bundle sha256: `8684153880a555be32571cf68862d3447f61fb0b7c4a5763b7d986b5c854de49`
- recovered artifact bundle size: `4608519` bytes
- JAX pin: `0.7.2`
- remote GPU: A100

## Training Recipe

Warm-start:

```text
outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520
```

Key overrides:

```text
terrain_hfield_z_scale: 0.0025
num_timesteps: 122880
ppo_num_envs: 64
ppo_batch_size: 512
restore_policy_kl_scale: 3.0
target_rate_scale: -0.005
actuator_tracking_scale: -0.005
forward_progress_scale: 5.0
command_progress_scale: 4.0
command_progress_shortfall_scale: -12.0
command_progress_required_ratio: 0.55
push_enable: false
corrected bridge: delay 3 ticks, velocity range 2.0-3.25 rad/s
```

Training exported:

| step | ONNX sha256 |
|---:|---|
| 40960 | `05148a0c556542d898393365a31ab4ce43e84e0440c0883302e7fd3f9635c0d4` |
| 81920 | `2413e72fe998fee194570dde5fcf50438cfa72b30e1f9a6492749d3ebcee8d53` |
| 122880 | `36f236cef8bdd709249801d0d47d7e7281b86bcce7ca5cfe59813b316fce9a01` |

## Compact Checkpoint Sweep

Stable copied artifacts:

```text
outputs/analysis/phase2_z00245_motion_recovery_a100_20260702/checkpoint_sweep/CANDIDATE_CHECKPOINT_SWEEP.md
outputs/analysis/phase2_z00245_motion_recovery_a100_20260702/checkpoint_sweep/candidate_checkpoint_sweep.json
outputs/analysis/phase2_z00245_motion_recovery_a100_20260702/selected_checkpoint.json
outputs/analysis/phase2_z00245_motion_recovery_a100_20260702/training_run_summary.md
outputs/analysis/phase2_z00245_motion_recovery_a100_20260702/training_run_summary.json
```

Sweep settings:

```text
commands: 0.0, 0.08
duration_s: 1.0
bridge_mode: fitted
jax_platform: cpu
velocity_envelope_rad_s: 2.0-3.25
min_promote_vx_m_s: 0.02
min_promote_ratio: 0.25
```

Results:

| checkpoint | x=0.0 | x=0.08 | x=0.08 track ratio | x=0.08 mean vx | max pitch vel p95 | max tracking p95 |
|---|---|---|---:|---:|---:|---:|
| 40960 | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.2339 | 0.0187 | 1.4191 | 0.2138 |
| 81920 | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1660 | 0.0133 | 1.4132 | 0.2113 |
| 122880 | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1684 | 0.0135 | 1.4296 | 0.2160 |

Selected checkpoint:

```text
selection_status: HOLD_PARTIAL_CANDIDATE_CHECKPOINT
selection_reason: best_available_but_not_promoted
selected: 40960
promote: false
```

The best available checkpoint still failed the configured compact promotion
thresholds:

```text
track ratio 0.2339 < 0.2500
mean vx 0.0187 < 0.0200
```

## Full Seed Gate

The remote driver started the full 8-seed, 15s `z=0.0025`, `x=0.08` no-push
gate on the best partial checkpoint. The Colab session was then lost with
404/401 before a final seed-gate artifact or exit sentinel was recoverable.

This does not weaken the compact-sweep hold: no checkpoint met the compact
motion criteria required to justify promotion. Treat the full seed gate as
interrupted infrastructure evidence, not as a policy result.

## Decision

`HOLD_Z00245_MOTION_RECOVERY_LOW_FORWARD_PROGRESS`

The run confirms that reducing target-rate and actuator-tracking penalties
while increasing scalar progress pressure did not recover enough forward motion
at the z=0.00245 boundary. It stayed comfortably in-envelope, but it remained
too slow to promote.

Do not run robot validation from these checkpoints. Do not repeat another small
scalar-progress-pressure tweak as the next branch. The next offline branch
should use a continuity mechanism that preserves the walking behavior directly,
such as teacher-action behavior prior, trust-region continuity, or live-oracle
DAgger, and then re-run the same corrected-bridge gates.
