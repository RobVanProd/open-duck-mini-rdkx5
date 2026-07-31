# Phase 2 Gate-Aware Parent Iter1 Behavior-Prior Local Smoke Decision

status: `HOLD_BEHAVIOR_PRIOR_PARENT_REWARDED_FREEZE`

## Smoke

- smoke_dir: `outputs/phase2_domain_randomization/gate_aware_parent_iter1_behavior_prior_local_smoke/smoke_20260705T161023Z_gpu`
- smoke_manifest_final: `outputs/phase2_domain_randomization/gate_aware_parent_iter1_behavior_prior_local_smoke/smoke_20260705T161023Z_gpu/smoke_manifest.final.json`
- smoke_manifest_final_sha256: `625e41a9ba811165097252e7ef16c68c140dc30400dc156c0da4b32b7eb0ad52`
- smoke_status: `PASS_SMOKE_RUN`
- returncode: `0`
- robot_touched: `False`
- deploy_performed: `False`
- restore_policy_kl_scale: `8.0`
- behavior_prior_enabled: `True`
- behavior_prior_scale: `-0.35`
- behavior_prior_huber_delta: `0.04`
- behavior_prior_mlp_npz: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_bc_student/candidate_mlp.npz`

## Exports

| step | onnx | sha256 |
|---:|---|---|
| `15360` | `outputs/phase2_domain_randomization/gate_aware_parent_iter1_behavior_prior_local_smoke/smoke_20260705T161023Z_gpu/2026_07_05_121457_15360.onnx` | `8a5eb0baeecb01ae698109c2fdad9c5679a4d9980cf91bd9a95c6cce55d0b28d` |
| `30720` | `outputs/phase2_domain_randomization/gate_aware_parent_iter1_behavior_prior_local_smoke/smoke_20260705T161023Z_gpu/2026_07_05_121719_30720.onnx` | `292b1a61b0b659b3d3e85243d10112430e87c05a71df7dc4c6fa008e22185cd1` |
| `46080` | `outputs/phase2_domain_randomization/gate_aware_parent_iter1_behavior_prior_local_smoke/smoke_20260705T161023Z_gpu/2026_07_05_121757_46080.onnx` | `1ee6625b02ea8fe2b7c69923cabd5f734af5d3f397816873964a0ede537cbcd8` |

## Compact x=0.08 Gate

gate_md: `outputs/analysis/PHASE2_GATE_AWARE_PARENT_ITER1_BEHAVIOR_PRIOR_LOCAL_SMOKE_X008_GATE.md`
gate_json: `outputs/analysis/phase2_gate_aware_parent_iter1_behavior_prior_local_smoke_x008_gate.json`

| policy | pass | runs | falls | mean vx | mean track ratio | single support | double support | p95 vel excess | max tracking p95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter1bp_15360` | 0 | 5 | 0 | 0.0014 | 0.0178 | 0.0000% | 100.0000% | 0.0000 | 0.0470 |
| `iter1bp_30720` | 0 | 5 | 0 | 0.0015 | 0.0193 | 0.0000% | 100.0000% | 0.0000 | 0.0471 |
| `iter1bp_46080` | 0 | 5 | 0 | 0.0015 | 0.0192 | 0.0000% | 100.0000% | 0.0000 | 0.0496 |

## Interpretation

- The smoke completed and exported checkpoints, so this is not an environment/runtime failure.
- All compact x=0.08 rollouts completed duration without falls, but every rollout held for low forward progress.
- All exports spent 100% of the rollout in double support with 0% single support.
- Corrected p95 velocity excess was zero, so the rejection is not an actuator-envelope violation.
- Adding the state-conditioned behavior prior to restore-policy KL did not preserve the moving gait from the step-0 parent.

## Decision

`HOLD_BEHAVIOR_PRIOR_PARENT_REWARDED_FREEZE`

The behavior-prior PPO smoke did not improve on the step-0 parent and did not improve on the Iter0 restore-KL-only freeze. It produced stable planted double-support behavior with essentially zero forward progress.

Do not run the x=0.0 gate for these exports; the x=0.08 moving gate already rejects them. Do not scale this objective into Phase 2 domain-randomization training.

## Next Recommendation

Do not scale this PPO objective into Phase 2 DR. Move to a different behavior-preservation structure: explicit online router/wrapper training target, stronger branch-aware objective, or a non-PPO distillation route that is gated before any long DR run.
