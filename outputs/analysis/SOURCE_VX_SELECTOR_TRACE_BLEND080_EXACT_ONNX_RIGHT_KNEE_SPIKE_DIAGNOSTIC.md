# Exact Blend ONNX Right-Knee Spike Diagnostic

status: `HOLD_RIGHT_KNEE_CYCLIC_RATE_SPIKES`

This is an offline trace diagnostic for the exact blend ONNX candidate. It does not run robot tests, SSH, deploy, train, or change runtime behavior.

## Setup

- trace_jsonl: `outputs/analysis/source_vx_selector_trace_blend080_exact_onnx_right_knee_trace_seed3/trace.jsonl`
- policy: `outputs/analysis/source_vx_selector_trace_blend080_exact_onnx_candidate/candidate.onnx`
- task: `flat_terrain_backlash`
- command_x: `0.08`
- bridge_mode: `fitted`
- seed: `3`
- duration_s: `10`
- joint: `right_knee`

## Result

- samples: `500`
- max_sent_velocity_rad_s: `5.2400`
- events_over_3p75_rad_s: `62` (`12.42%` of target deltas)
- cluster_count: `32`
- cluster_sample_length_range: `1-3` ticks
- high_event_contacts: `{'11': 39, '10': 21, '01': 2}`
- all_contacts: `{'11': 292, '00': 2, '10': 90, '01': 116}`

## Top Events

| tick | time_s | sent_vel | pre_vel | action_delta/s | tracking | bridge | contacts | vx | pitch |
|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| 384 | 7.68 | 5.2400 | 5.9626 | 23.8502 | 0.2119 | 0.2336 | `11` | 0.0791 | 0.0881 |
| 414 | 8.28 | 5.2400 | 6.5121 | 26.0485 | 0.1965 | 0.2255 | `11` | 0.0836 | 0.0873 |
| 445 | 8.90 | 5.2400 | 6.7622 | 27.0488 | 0.1997 | 0.2263 | `11` | 0.0796 | 0.0647 |
| 476 | 9.52 | 5.2400 | 5.7104 | 22.8418 | 0.2299 | 0.2480 | `11` | 0.0583 | 0.0761 |
| 24 | 0.48 | 5.2400 | 5.2901 | 21.1604 | 0.1965 | 0.2339 | `11` | -0.0188 | -0.0021 |
| 53 | 1.06 | 5.2400 | 5.8981 | 23.5925 | 0.1445 | 0.1990 | `11` | 0.0833 | 0.0841 |
| 83 | 1.66 | 5.2400 | 5.7728 | 23.0914 | 0.2124 | 0.2380 | `11` | 0.0670 | 0.0731 |
| 87 | 1.74 | 5.2400 | 5.2436 | 20.9744 | 0.0783 | 0.0339 | `11` | 0.0420 | 0.0622 |
| 113 | 2.26 | 5.2400 | 5.9548 | 23.8192 | 0.2084 | 0.2391 | `11` | 0.0696 | 0.0770 |
| 143 | 2.86 | 5.2400 | 5.9446 | 23.7785 | 0.2067 | 0.2359 | `11` | 0.0773 | 0.0818 |
| 147 | 2.94 | 5.2400 | 5.2471 | 20.9883 | 0.0865 | 0.0262 | `11` | 0.0506 | 0.0737 |
| 203 | 4.06 | 5.2400 | 6.1695 | 24.6779 | 0.2018 | 0.2326 | `11` | 0.0798 | 0.0891 |

## Interpretation

- The right-knee over-envelope events are short repeated bursts, not a sustained high-rate command.
- Many bursts hit the runtime slew ceiling around `5.24 rad/s`, so a pre-rate target discontinuity is being clipped rather than smoothly followed.
- High-rate events occur mostly during double support (`11`), which makes this a gait-phase/target-continuity issue for the student rather than a pure swing-leg artifact.
- Next offline branch should preserve the blend forward motion while adding right-knee phase-continuity or per-joint target-rate selection pressure. Do not treat this as robot-ready.
