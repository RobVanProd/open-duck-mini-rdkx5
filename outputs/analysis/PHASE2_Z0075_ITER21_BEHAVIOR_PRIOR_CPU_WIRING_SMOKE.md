# Phase 2 z=0.0075 Iter21 Behavior-Prior CPU Wiring Smoke

status: `PASS_BEHAVIOR_PRIOR_WIRING_SMOKE`

## Summary

The Iter21 behavior-prior post-push recipe was run as a tiny local CPU smoke test after Colab GPU allocation failed. This was a wiring check only: it verifies that the behavior-prior arguments reach the Playground runner, that the PPO smoke can start, checkpoint, and export ONNX, and that no robot/deploy path is touched.

This is not a candidate quality gate and does not promote a policy.

## Inputs

- platform: `cpu`
- task: `rough_terrain_backlash`
- num_timesteps: `512`
- ppo_num_envs: `2`
- restore_checkpoint_path: `outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint`
- behavior_prior_mlp_npz: `outputs/analysis/phase2_z0075_iter21_early_lunge_gain095_rate150_candidate/candidate_mlp.npz`
- behavior_prior_mlp_sha256: `71f520712a10613d3e2304a33cbcd641f6bb59fb0d5c1dc3e34a5c8fe93569b2`
- behavior_prior_scale: `-0.22`
- behavior_prior_huber_delta: `0.06`
- terrain_hfield_z_scale: `0.0075`
- push range: `0.075..0.125`

## Result

- smoke_manifest_status: `PASS_SMOKE_RUN`
- returncode: `0`
- elapsed_s: `180.0513211020152`
- exported_smoke_onnx: `outputs/phase2_domain_randomization/stage_z0075_behavior_prior_wiring_cpu_smoke/smoke_20260704T183610Z_cpu/2026_07_04_143720_640.onnx`
- exported_smoke_onnx_sha256: `b3eb42f53b05a723f5df3988bf8f837b97bd74490c92a6f8fd79203f2868f1cd`
- final_manifest_sha256: `f1fbe6ca9733a2bdd30ac02f821e12dede7a9ddabe240bdd57bb86ede10595f0`

## Warnings

- `warp` / `mujoco_warp` were unavailable; the run used the normal MuJoCo/JAX path.
- `stderr.txt` contains repeated XLA CPU AOT host-feature warnings and JAX overflow warnings.
- The exported ONNX is from a 512-timestep CPU smoke and is not a candidate.

## Interpretation

The behavior-prior recipe is wiring-valid. The remaining Phase 2 blocker is execution capacity for the real run: Colab GPU allocation was unavailable, and local GPU resources/backend stability were not used for this smoke.

No robot tests, SSH, deployment, grounded replay, or runtime behavior changes were performed.

## Next Step

Retry the behavior-prior post-push recipe on a GPU Colab session or a clean local ROCm session, then evaluate any resulting checkpoint with the corrected-bridge multi-seed gates before promotion.
