# Phase 2 Spike-Local Recovery Windows

status: `PASS_PHASE2_SPIKE_RECOVERY_WINDOWS_READY`

Offline-only curation for Phase 2 z=0.0075 recovery. It keeps failed-seed
observations and smooths only selected pitch-chain action deltas; it does
not copy same-tick neighbor trajectories and does not train or touch the robot.

## Inputs

- failure_modes_json: `outputs/analysis/phase2_z0075_late_lunge_rate150_failure_modes.json`
- fit_json: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- output_trace_dir: `outputs/analysis/phase2_z0075_iter10_spike_local_recovery`

## Settings

- sample_weight: `1.35`
- limit_fraction: `0.85`
- lunge_tail_ticks: `80`
- reverse_head_ticks: `60`
- spike_radius: `8`
- excess_tolerance_rad_s: `0.02`
- lunge_delta_scale: `0.82`
- reverse_delta_scale: `0.7`
- action_scale: `0.25`
- dt_s: `0.02`
- output_mode: `phase2_spike_local_recovery`

## Corrected Pitch-Chain Limits

| joint | limit rad/s |
|---|---:|
| `left_hip_pitch` | 2.5000 |
| `left_knee` | 3.2500 |
| `left_ankle` | 2.7500 |
| `right_hip_pitch` | 2.2500 |
| `right_knee` | 2.7500 |
| `right_ankle` | 2.0000 |

## Summary

- seeds: `7`
- samples_out: `559`
- dataset_id: `36ffcea123bef3dd`

| seed | mode | ticks | samples | reasons | max_excess | changed joints |
|---:|---|---:|---:|---|---:|---|
| 0 | `ACTUATOR_ENVELOPE_EXCESS` | 70-149 | 80 | `{'envelope_spike': 11, 'late_lunge_tail': 80}` | 0.1199 | left_ankle:79, left_hip_pitch:79, left_knee:79, right_ankle:79, right_hip_pitch:79, right_knee:79 |
| 1 | `ACTUATOR_ENVELOPE_EXCESS` | 500-579 | 80 | `{'envelope_spike': 12, 'late_lunge_tail': 80}` | 1.0405 | left_ankle:79, left_hip_pitch:79, left_knee:79, right_ankle:79, right_hip_pitch:79, right_knee:79 |
| 2 | `FORWARD_LUNGE_PITCHOVER` | 74-153 | 80 | `{'late_lunge_tail': 80}` | 0.0000 | left_ankle:79, left_hip_pitch:79, left_knee:79, right_ankle:79, right_hip_pitch:79, right_knee:79 |
| 3 | `ACTUATOR_ENVELOPE_EXCESS` | 0-749 | 96 | `{'envelope_spike': 16, 'late_lunge_tail': 80}` | 0.2400 | left_ankle:79, left_hip_pitch:80, left_knee:79, right_ankle:80, right_hip_pitch:80, right_knee:80 |
| 4 | `FORWARD_LUNGE_PITCHOVER` | 197-276 | 80 | `{'envelope_spike': 12, 'late_lunge_tail': 80}` | 0.0537 | left_ankle:79, left_hip_pitch:79, left_knee:79, right_ankle:79, right_hip_pitch:79, right_knee:79 |
| 5 | `PRE_PUSH_REVERSE_PITCHBACK` | 0-45 | 46 | `{'early_reverse_head': 46}` | 0.0000 | left_ankle:45, left_hip_pitch:45, left_knee:45, right_ankle:45, right_hip_pitch:45, right_knee:45 |
| 6 | `ACTUATOR_ENVELOPE_EXCESS` | 4-424 | 97 | `{'envelope_spike': 33, 'late_lunge_tail': 80}` | 1.5385 | left_ankle:79, left_hip_pitch:80, left_knee:79, right_ankle:79, right_hip_pitch:79, right_knee:79 |

## Gate

- Raw JSONL snippets remain generated artifacts unless explicitly force-added.
- This curation is a candidate-data source only; promotion requires a trained
  ONNX candidate to pass the canonical corrected-bridge seed gate.
