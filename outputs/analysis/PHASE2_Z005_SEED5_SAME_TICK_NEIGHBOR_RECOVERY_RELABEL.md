# Seed Recovery Neighbor Relabel

status: `PASS_SEED_RECOVERY_NEIGHBOR_RELABEL_READY`

Offline recovery-teacher curation. It keeps failing-seed observations and
uses same-tick neighbor actions as labels. It does not train, deploy, SSH,
run robot tests, or change runtime behavior.

## Inputs

- failing_trace: `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x008/student/seed_005/trace.jsonl`
- neighbor_trace: `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x008/student/seed_000/trace.jsonl`
- neighbor_trace: `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x008/student/seed_001/trace.jsonl`
- neighbor_trace: `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x008/student/seed_002/trace.jsonl`
- neighbor_trace: `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x008/student/seed_003/trace.jsonl`
- neighbor_trace: `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x008/student/seed_004/trace.jsonl`
- neighbor_trace: `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x008/student/seed_006/trace.jsonl`
- neighbor_trace: `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/rollouts_x008/student/seed_007/trace.jsonl`

## Settings

- tick_min: `0`
- tick_max: `55`
- sample_weight: `8.0`
- max_target_velocity_rad_s: `2.0`
- capped_joints: `['left_hip_pitch', 'left_knee', 'left_ankle', 'right_hip_pitch', 'right_knee', 'right_ankle']`

## Summary

- output_trace: `outputs/analysis/phase2_z005_seed5_same_tick_neighbor_recovery/seed_005/trace.jsonl`
- dataset_id: `5a3293ce22249030`
- samples_out: `56`
- missing_neighbor_ticks: `0`
- capped_action_components: `0`
- contact_counts: `{'00': 1, '01': 1, '10': 3, '11': 51}`

## Gate

- Output JSONL is a generated artifact and should remain ignored unless explicitly approved.
- This is source material for offline BC/DAgger diagnostics, not a candidate policy.
