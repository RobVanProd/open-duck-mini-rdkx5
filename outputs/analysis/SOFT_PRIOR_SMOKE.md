# Target Sequence Replay Smoke

status: `HOLD_SOFT_PRIOR_FREEZE`

This is an offline sequence-preservation diagnostic over curated target windows.
It replays target action tables in closed-loop sim; it is not PPO, BC training, or a deployable policy.

## Dataset

- manifest: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/target_dataset_manifest_dynamic_roll_lateral_fix_robust_modes.json`
- dataset_id: `47153f26ab48ef14`
- manifest_status: `PASS_TARGET_DATASET_MANIFEST_READY`
- policy_set: `aggregate`
- periodic_seam_correction: `False`
- soft_prior_config: `outputs/analysis/soft_prior_fragment_config.json`
- phase_adapter: `fixed_time`
- sequence_policies: `1`
- command_x: `0.0400`
- duration_s: `3.0000`
- seeds: `[0, 2]`

## Gates

- min_mean_vx_m_s: `0.0200`
- max_vy_abs_p95_m_s: `0.1200`
- max_body_pitch_abs_p95_rad: `0.2500`
- min_base_height_m: `0.1000`
- max_sent_velocity_p95_rad_s: `3.7500`

## Closed-Loop Sequence Replay

status: `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`

| policy | status | seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| soft_prior_pitch_chain_c4833a96744101d9 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_000 | 150 | duration_complete | 0.0115 | 0.2874 | 0.0513 | 0.2685 | 0.1477 | 0.3566 | 0.0720 |
| soft_prior_pitch_chain_c4833a96744101d9 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_002 | 150 | duration_complete | 0.0143 | 0.3579 | 0.0770 | 0.2830 | 0.1473 | 0.3566 | 0.0718 |

### Phase Adapter Summary

| policy | seed | holds/s | skips/s | contact_mismatch_pct | phase_bins |
|---|---|---:|---:|---:|---:|
| soft_prior_pitch_chain_c4833a96744101d9 | seed_000 | 0.0000 | 0.0000 | 3.3557 | 50 |
| soft_prior_pitch_chain_c4833a96744101d9 | seed_002 | 0.0000 | 0.0000 | 2.0134 | 50 |

### Policy Table Summary

| policy | source | prefix_len | window_len | entry_count | status |
|---|---|---:|---:|---:|---|
| soft_prior_pitch_chain_c4833a96744101d9 | outputs/analysis/soft_prior_fragment_config.json | 1 | 50 | 1 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` |

## Interpretation

- Passing this smoke would justify a sequence/phase-aware imitation learner.
- Failing this smoke means target timing alone is not enough; do not launch PPO from these windows.
- This diagnostic preserves rollout timing; it does not test a memoryless obs-to-action clone.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
