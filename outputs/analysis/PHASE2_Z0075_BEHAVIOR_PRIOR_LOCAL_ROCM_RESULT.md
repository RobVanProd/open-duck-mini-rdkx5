# Phase 2 z=0.0075 Behavior-Prior Local ROCm Result

status: `HOLD_BEHAVIOR_PRIOR_LOW_FORWARD_PROGRESS`

## Summary

The Iter21 behavior-prior post-push recipe was run locally on the 7900 XTX ROCm backend after Colab GPU allocation was unavailable. The run completed successfully and exported checkpoints/ONNX files at steps `40960`, `81920`, and `122880`.

The exported policies are not promotable. Triage corrected-bridge x=0.08 gates show the policies remain stable and in-envelope, but they produce almost no forward progress.

No robot tests, SSH, deployment, grounded replay, or runtime behavior changes were performed.

## Colab Allocation

- A100: rejected by backend quota/entitlement
- H100: rejected by backend quota/entitlement
- L4: rejected by backend quota/entitlement
- G4: rejected by backend quota/entitlement
- T4: backend returned Service Unavailable

## Local ROCm Training

- output_dir: `outputs/phase2_domain_randomization/stage_z0075_post_push_stability_local_rocm/smoke_20260704T184444Z_gpu`
- manifest: `outputs/phase2_domain_randomization/stage_z0075_post_push_stability_local_rocm/smoke_20260704T184444Z_gpu/smoke_manifest.final.json`
- manifest_sha256: `09619f3adb31584b752b3228919b4d6c30e013959df8c36d026642c49705c268`
- manifest_status: `PASS_SMOKE_RUN`
- returncode: `0`
- elapsed_s: `750.0285300349933`
- platform: `gpu`
- local_rocm_safe_env: `true`
- behavior_prior_enabled: `true`
- behavior_prior_mlp: `outputs/analysis/phase2_z0075_iter21_early_lunge_gain095_rate150_candidate/candidate_mlp.npz`
- behavior_prior_mlp_sha256: `71f520712a10613d3e2304a33cbcd641f6bb59fb0d5c1dc3e34a5c8fe93569b2`
- behavior_prior_scale: `-0.22`
- behavior_prior_huber_delta: `0.06`

## Checkpoints

| step | ONNX | sha256 | training reward |
|---:|---|---|---:|
| 40960 | `outputs/phase2_domain_randomization/stage_z0075_post_push_stability_local_rocm/smoke_20260704T184444Z_gpu/2026_07_04_145200_40960.onnx` | `0da8dadb8de5294d0d1dfb8a1847725021cb9390304495a889f2eea3e0aca06c` | 121.1477 |
| 81920 | `outputs/phase2_domain_randomization/stage_z0075_post_push_stability_local_rocm/smoke_20260704T184444Z_gpu/2026_07_04_145522_81920.onnx` | `09ee185eb3febf832babc94b1dd9a8d80a8ce302cd9f8b2e143ce0c139010793` | 148.7468 |
| 122880 | `outputs/phase2_domain_randomization/stage_z0075_post_push_stability_local_rocm/smoke_20260704T184444Z_gpu/2026_07_04_145636_122880.onnx` | `66639cca3cb530271225b58c0bf3e6690c6f71e8f4e6648944f99aa5e91cc160` | 90.9253 |

## Gate Triage

Gate settings:

- task: `rough_terrain_backlash`
- command_x: `0.08`
- terrain_hfield_z_scale: `0.0075`
- bridge: corrected fitted bridge
- jax_platform: `cpu`
- reset_mode: `home-support`
- reset_settle_ticks: `10`
- duration_s: `15`

| checkpoint | seeds tested | result | track ratio | mean vx m/s | max pitch tracking p95 rad | max sent target velocity p95 rad/s | velocity excess |
|---|---|---|---:|---:|---:|---:|---:|
| step40960 | 0, 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0238 | 0.0019 | 0.0519 | 0.2199 | 0.0 |
| step81920 | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0284 | 0.0023 | 0.0534 | 0.1823 | 0.0 |
| step122880 | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0276 | 0.0022 | 0.0489 | 0.1522 | 0.0 |

All tested checkpoints were stable and in-envelope, but the gait collapsed into near-standstill. The behavior-prior/post-push recipe improved backend execution but did not solve Phase 2 robustness.

## Interpretation

The local ROCm backend is now usable for this bounded Phase 2 training job after reboot: it completed 122880 timesteps and exported all checkpoints without ROCm fault. The recipe itself is not successful because the resulting policies preserve safety by suppressing motion.

This result points away from another behavior-prior PPO pass with the same restore-policy KL and reward balance. The next recipe should explicitly preserve the Iter21 moving behavior while applying push recovery pressure, or use a shorter/earlier checkpoint selection strategy that rejects low-progress collapse during training.
