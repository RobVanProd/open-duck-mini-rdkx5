# Seed Recovery Neighbor Relabel

status: `PASS_SEED_RECOVERY_NEIGHBOR_RELABEL_READY`

Offline recovery-teacher curation. It keeps failing-seed observations and
uses same-tick neighbor actions as labels. It does not train, deploy, SSH,
run robot tests, or change runtime behavior.

## Inputs

- failing_trace: `outputs/analysis/phase2_z0075_seed_diverse_recovery_rate150_failed_seed_traces/iter7_seed_diverse_recovery_rate150/seed_002/trace.jsonl`
- neighbor_trace: `outputs/analysis/phase2_z0075_seed_diverse_recovery_rate150_seed0_pass_trace/iter7_seed_diverse_recovery_rate150/seed_000/trace.jsonl`

## Settings

- tick_min: `74`
- tick_max: `153`
- sample_weight: `1.5`
- max_target_velocity_rad_s: `1.5`
- capped_joints: `['left_hip_pitch', 'left_knee', 'left_ankle', 'right_hip_pitch', 'right_knee', 'right_ankle']`

## Summary

- output_trace: `outputs/analysis/phase2_z0075_iter9_late_lunge_neighbor_recovery/lunge_neighbor_relabel/iter7_seed_diverse_recovery_rate150/seed_002/trace.jsonl`
- dataset_id: `63f55ad721b88a5f`
- samples_out: `80`
- missing_neighbor_ticks: `0`
- capped_action_components: `30`
- contact_counts: `{'00': 2, '01': 4, '10': 13, '11': 61}`

## Gate

- Output JSONL is a generated artifact and should remain ignored unless explicitly approved.
- This is source material for offline BC/DAgger diagnostics, not a candidate policy.
