# Seed Recovery Neighbor Relabel

status: `PASS_SEED_RECOVERY_NEIGHBOR_RELABEL_READY`

Offline recovery-teacher curation. It keeps failing-seed observations and
uses same-tick neighbor actions as labels. It does not train, deploy, SSH,
run robot tests, or change runtime behavior.

## Inputs

- failing_trace: `outputs/analysis/phase2_seed5_capped_neighbor_trace_compare_x008/seed5_capped/seed_005/trace.jsonl`
- neighbor_trace: `outputs/analysis/phase2_seed5_capped_neighbor_trace_compare_x008/seed5_capped/seed_004/trace.jsonl`
- neighbor_trace: `outputs/analysis/phase2_seed5_capped_neighbor_trace_compare_x008/seed5_capped/seed_006/trace.jsonl`

## Settings

- tick_min: `0`
- tick_max: `24`
- sample_weight: `10.0`
- max_target_velocity_rad_s: `2.25`
- capped_joints: `['left_hip_pitch', 'left_knee', 'left_ankle', 'right_hip_pitch', 'right_knee', 'right_ankle']`

## Summary

- output_trace: `outputs/analysis/phase2_seed5_neighbor_recovery_traces/x008_seed5_neighbor_recovery/trace.jsonl`
- dataset_id: `08657e9c5dcf934f`
- samples_out: `25`
- missing_neighbor_ticks: `0`
- capped_action_components: `7`
- contact_counts: `{'00': 2, '10': 1, '11': 22}`

## Gate

- Output JSONL is a generated artifact and should remain ignored unless explicitly approved.
- This is source material for offline BC/DAgger diagnostics, not a candidate policy.
