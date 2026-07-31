# Phase 2 Stage C7 Gate-Selected Terrain Decision

status: `HOLD_STAGE_C7_GATE_SELECTION_PARTIAL`

## Scope

Offline sim/training only. No robot, SSH, deploy, grounded replay, runtime
behavior change, or policy overwrite was performed.

## Why

C6 showed that reading only the final training checkpoint can hide the useful
part of a run: the PPO objective eventually retreats into double-support
shuffling. C7 kept the same basic C6 terrain recipe but exported frequent
intermediate checkpoints so selection could be based on corrected terrain gate
metrics rather than training reward or final checkpoint reward.

## Recipe

Warm-start:

```text
outputs/phase2_domain_randomization/stage_c3_terrain_z002_contact_from_c2_gpu/smoke_20260628T121159Z_gpu/2026_06_28_081839_245760
```

Training artifact:

```text
outputs/phase2_domain_randomization/stage_c7_terrain_z002_gate_selected_from_c3_gpu/smoke_20260628T132851Z_gpu
```

Key settings:

```text
restore_policy_kl_scale: 1.25
forward_single_support_scale: 0.30
forward_contact_transition_scale: 0.20
forward_double_support_dwell_scale: -0.05
forward_double_support_dwell_grace_steps: 8
forward_swing_clearance_scale: -0.0005
forward_swing_clearance_target_m: 0.020
target_rate_scale: -0.03
actuator_tracking_scale: -0.05
terrain_hfield_z_scale: 0.002
num_timesteps: 245760
ppo_num_evals: 8
```

Training completed:

```text
status: PASS_SMOKE_RUN
elapsed_s: 426.86
terrain XML restored: true
```

Local ROCm workaround used:

```text
XLA_FLAGS=--xla_gpu_autotune_level=0
XLA_PYTHON_CLIENT_PREALLOCATE=false
```

## Checkpoint Screen

Focused seed-0 terrain screen:

```text
outputs/analysis/PHASE2_STAGE_C7_TERRAIN_Z002_SCREEN_CPU.md
outputs/analysis/phase2_stage_c7_terrain_z002_screen_cpu.json
```

| checkpoint | status | tracking p95 | track ratio | velocity excess | min swing peak | single support | double support |
|---|---|---:|---:|---:|---:|---:|---:|
| `c7_0` | `HOLD_CANDIDATE_TRACKING` | 0.2046 | 0.4061 | 0.0000 | 0.0165 m | 20.8% | 79.2% |
| `c7_35120` | `PASS_CANDIDATE_SIM_GATE` | 0.1885 | 0.2606 | 0.0000 | 0.0104 m | 11.2% | 88.8% |
| `c7_70240` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1602 | 0.0499 | 0.0000 | 0.0207 m | 0.8% | 99.2% |
| `c7_105360` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1779 | 0.2295 | 0.0000 | 0.0121 m | 11.2% | 88.8% |
| `c7_140480` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1813 | 0.0633 | 0.0000 | 0.0207 m | 1.2% | 98.8% |
| `c7_175600` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1587 | 0.0536 | 0.0000 | 0.0206 m | 0.8% | 99.2% |
| `c7_210720` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.2024 | 0.2052 | 0.0000 | 0.0114 m | 10.0% | 90.0% |
| `c7_245840` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1924 | 0.1811 | 0.0000 | 0.0103 m | 6.4% | 93.6% |

Best transient checkpoint:

```text
checkpoint: c7_35120
onnx: outputs/phase2_domain_randomization/stage_c7_terrain_z002_gate_selected_from_c3_gpu/smoke_20260628T132851Z_gpu/2026_06_28_093051_35120.onnx
sha256: ee0b7013bf588b2aab4b8efe3c7ab10b1d8b901d786282717cda3b18b5c8b5d7
```

## Eight-Seed Terrain Screen

The best transient checkpoint was then screened across seeds `0-7`:

```text
outputs/analysis/PHASE2_STAGE_C7_35120_TERRAIN_Z002_8SEED_CPU.md
outputs/analysis/phase2_stage_c7_35120_terrain_z002_8seed_cpu.json
```

Result:

```text
passes: 5/8
falls: 0/8
duration_complete: 8/8
mean track ratio: 0.2671
mean vx: 0.0214 m/s
max corrected velocity excess: 0.0000 rad/s
max pitch-chain tracking p95: 0.1918 rad
mean min swing peak: 0.0105 m
mean single support: 11.4%
mean double support: 88.45%
```

Per-seed failures:

```text
seed 3: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS, track_ratio 0.1649
seed 4: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS, track_ratio 0.1918
seed 7: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS, track_ratio 0.2477
```

## Interpretation

C7 proves gate-selected checkpointing is useful: the early `35120` checkpoint
is better than the final C6/C7 checkpoints and avoids the final-reward
double-support collapse. However, it is still not a terrain robustness
candidate:

- it passes only `5/8` seeds on `z=0.002` terrain,
- it reduces tracking error by reducing motion relative to C3,
- mean swing peak is only `0.0105 m`, worse than the C3 baseline `0.0165 m`,
- mean double support remains very high at `88.45%`.

This does not solve the medium-carpet observation. The policy is still mostly a
low-clearance shuffle, just with cleaner corrected-bridge tracking.

## Next

Do not promote C7 and do not run it on hardware.

Keep gate-selected checkpointing for future terrain work, because it did find
the best transient point. The next branch should change the target being
optimized, not merely the scalar weights:

- generate or mine a higher-clearance stepping target,
- add a hard minimum step-clearance/step-advance constraint for nonzero command,
- or train a terrain-specific student from demonstrations that already contain
  higher-clearance swing rather than asking PPO to invent that gait by small
  scalar reward terms.
