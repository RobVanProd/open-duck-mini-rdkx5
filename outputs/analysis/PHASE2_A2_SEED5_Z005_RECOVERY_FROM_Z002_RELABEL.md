# Seed Recovery Neighbor Relabel

status: `PASS_SEED_RECOVERY_NEIGHBOR_RELABEL_READY`

Offline recovery-teacher curation. It keeps failing-seed observations and
uses same-tick neighbor actions as labels. It does not train, deploy, SSH,
run robot tests, or change runtime behavior.

## Inputs

- failing_trace: `outputs/analysis/phase2_a2_seed5_z005_x000_2s_fullobs_trace.jsonl`
- neighbor_trace: `outputs/analysis/phase2_a2_seed5_z002_x000_2s_fullobs_trace.jsonl`

## Settings

- tick_min: `20`
- tick_max: `60`
- sample_weight: `4.0`
- max_target_velocity_rad_s: `2.0`
- capped_joints: `['left_hip_pitch', 'left_knee', 'left_ankle', 'right_hip_pitch', 'right_knee', 'right_ankle']`

## Summary

- output_trace: `outputs/analysis/phase2_a2_seed5_z005_recovery_from_z002_relabel_trace.jsonl`
- dataset_id: `4512f72ad420d9ae`
- samples_out: `41`
- missing_neighbor_ticks: `0`
- capped_action_components: `0`
- contact_counts: `{'00': 2, '01': 1, '10': 1, '11': 37}`

## Gate

- Output JSONL is a generated artifact and should remain ignored unless explicitly approved.
- This is source material for offline BC/DAgger diagnostics, not a candidate policy.
