# Phase 2 Stage A PPO-Loc Prior Smoke Decision

status: `HOLD_STAGE_A_SMOKE_POLICY_REGRESSED`

This is an offline Phase 2 domain-randomization pipeline check. It did not SSH,
deploy, run robot tests, touch the robot, or change robot runtime behavior.

## Inputs

- warm-start parent: `policy/candidates/phase2_health_routed_parent_phase_mod_rate150_20260706/candidate.onnx`
- parent status: `PASS_HEALTH_ROUTED_PARENT_READY_FOR_PHASE2_DR_WARMSTART`
- compatible behavior-prior NPZ: `outputs/analysis/phase2_health_routed_pass_parent_ppo_loc_rate150_prior/candidate_mlp.npz`
- compatible behavior-prior NPZ sha256: `a4898be376c496b7f8de96844cb64827ac26b19c575482c622d129bdaefe2e16`
- compatible behavior-prior ONNX: `outputs/analysis/phase2_health_routed_pass_parent_ppo_loc_rate150_prior/candidate.onnx`
- compatible behavior-prior ONNX sha256: `3bb1f33da245ee5e79df9ba55407e465e32ee4b56749c49be0dc5fa80f4dd0e6`

## Smoke Run

- smoke manifest: `outputs/phase2_domain_randomization/health_routed_parent_stage_a_ppo_loc_prior_smoke/smoke_20260706T032431Z_cpu/smoke_manifest.final.json`
- smoke manifest sha256: `d05d60f6755dc24e99e290e594a9022c07090c3be6a7ccc4c7eb97ead55c41b7`
- smoke status: `PASS_SMOKE_RUN`
- platform: `cpu`
- elapsed: `300.0785` s
- exported smoke ONNX: `outputs/phase2_domain_randomization/health_routed_parent_stage_a_ppo_loc_prior_smoke/smoke_20260706T032431Z_cpu/2026_07_05_232735_40960.onnx`
- exported smoke ONNX sha256: `bfe62f293a2fe8c8787632717edcc4642413b4f03b25a187ab5e3800628e21b2`

The first behavior-prior smoke attempt using the phase-modulated NPZ held before
training because the Playground runner expects the PPO-loc behavior-prior schema
(`norm`, layer weights, and biases). The PPO-loc prior above was trained from
the same routed parent manifest specifically to satisfy that runner contract.

## X=0.08 Screen

- screen report: `outputs/analysis/PHASE2_STAGE_A_PPO_LOC_PRIOR_SMOKE_X008_SEED0_SCREEN.md`
- screen JSON: `outputs/analysis/phase2_stage_a_ppo_loc_prior_smoke_x008_seed0_screen.json`
- screen JSON sha256: `18bd3518222229dcb542606f2c558e17455776e757fb89e4044ff8bd0f390b05`
- policy screened: exported smoke ONNX
- command: `x=0.08`
- task: `rough_terrain_backlash`
- terrain z scale: `0.0075`
- pushes: enabled, `0.075`-`0.125`
- bridge: corrected fitted bridge
- reset: `home-support`, settle ticks `10`
- seed: `0`

| metric | value |
|---|---:|
| gate status | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` |
| samples | `750` |
| termination | `duration_complete` |
| mean local vx | `0.0010` m/s |
| track ratio | `0.0125` |
| body pitch p95 | `0.0901` rad |
| base height min | `0.1598` m |
| max pitch target velocity p95 | `0.0997` rad/s |
| max tracking p95 | `0.0438` rad |
| velocity envelope excess | `0.0000` rad/s |
| single support | `0.0000` % |
| double support | `100.0000` % |
| min swing segments | `0` |

## Decision

The Stage A PPO smoke proves the training runner can execute with the compatible
behavior prior and corrected actuator bridge randomization. It does **not**
produce a usable candidate. The exported smoke checkpoint regressed to a quiet
standstill on the first task-matched x=0.08 rough+push screen.

Do not promote the smoke ONNX. Do not continue Phase 2 from the exported smoke
checkpoint.

Next Phase 2 work should preserve the passing parent behavior during training:

1. Use the PPO-loc prior as a behavior prior or restore/fidelity anchor, not as
   a replacement parent.
2. Add a step-0 or pre-update fidelity gate before PPO updates.
3. Reduce or stage PPO update strength so the first DR stage cannot erase
   single-support motion.
4. Gate any future checkpoint against the same x=0.08 and x=0.0 corrected-bridge
   rough+push screens before promotion.
