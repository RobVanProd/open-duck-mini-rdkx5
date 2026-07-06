# Phase 2 Stage A Narrow CPU Smoke Decision

status: `PASS_PHASE2_STAGE_A_NARROW_CPU_SMOKE`

Offline CPU smoke only; no robot, SSH, deploy, grounded replay, or robot runtime changes.

## Run

- runner status: `PASS_SMOKE_RUN`
- run dir: `outputs/phase2_domain_randomization/phase_context_stage_a_narrow_cpu_smoke/smoke_20260706T064603Z_cpu`
- manifest: `outputs/phase2_domain_randomization/phase_context_stage_a_narrow_cpu_smoke/smoke_20260706T064603Z_cpu/smoke_manifest.final.json`
- manifest sha256: `0ad2188a877940f95025c51040bbb546e7ee149b4b0aac057b58b5c2cd4340f2`
- elapsed: `180.046` s
- return code: `0`
- platform: `cpu`
- JAX env: `{'JAX_PLATFORMS': 'cpu', 'JAX_PLATFORM_NAME': 'cpu'}`

## Restore / Policy Network

- restore checkpoint: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_health_routed_parent_phase_mod_rate150_step0_checkpoint`
- policy network: `{'phase_modulated_activation': 'swish', 'phase_modulated_context_hidden_sizes': '64', 'phase_modulated_context_indices': '6,99,100', 'phase_modulated_init_scale_logit': -2.0, 'phase_modulated_policy_hidden_sizes': '512,256', 'phase_modulated_scale': 0.5, 'ppo_policy_network': 'phase_modulated'}`

## Evidence

- Saving checkpoint (step: 0): /home/lsd/robots/open-duck-mini-rdkx5/outputs/phase2_domain_randomization/phase_context_stage_a_narrow_cpu_smoke/smoke_20260706T064603Z_cpu/2026_07_06_024643_0
- Saving checkpoint (step: 320): /home/lsd/robots/open-duck-mini-rdkx5/outputs/phase2_domain_randomization/phase_context_stage_a_narrow_cpu_smoke/smoke_20260706T064603Z_cpu/2026_07_06_024711_320
- STEP: 320 reward: 25.894550323486328 reward_std: 12.766319274902344

## Exported ONNX

- `outputs/phase2_domain_randomization/phase_context_stage_a_narrow_cpu_smoke/smoke_20260706T064603Z_cpu/2026_07_06_024643_0.onnx` sha256 `5d41eab6945f7e64e5b3d9c15ab38ba388ba38e616fd5c04bbf46f5b9237d626` size `885758`
- `outputs/phase2_domain_randomization/phase_context_stage_a_narrow_cpu_smoke/smoke_20260706T064603Z_cpu/2026_07_06_024711_320.onnx` sha256 `16f7c472d1fe8e6bb76529ece18a41686f55c4d2408f5bffa4cdcc3fa0215fca` size `885758`

## Next Work

- Run a real Stage A training job on GPU/Colab with the same phase-modulated restore path and narrow DR ranges.
- Gate the resulting checkpoint with corrected-bridge x=0.08 and x=0.0 full8 sweeps before widening DR.
