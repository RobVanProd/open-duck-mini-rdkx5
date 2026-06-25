# Reference Contact Compatibility

This summarizes actual foot contacts from reference-target rollouts against
the foot-contact pattern encoded in the polynomial reference.

## Runs

| label | samples | mismatch_pct | actual 11 pct | ref 11 pct | actual 10 pct | ref 10 pct | actual 01 pct | ref 01 pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| reference_motion_rollout_v20_traces | 635 | 68.03 | 73.86 | 35.43 | 11.34 | 34.49 | 12.60 | 30.08 |
| reference_motion_rollout_v20_projected_traces | 664 | 67.77 | 75.90 | 35.54 | 11.30 | 35.69 | 11.14 | 28.77 |
| reference_motion_rollout_v20_projected_phase5_traces | 653 | 67.23 | 74.89 | 37.52 | 10.72 | 31.39 | 12.40 | 31.09 |
| reference_motion_rollout_v20_projected_phase19_traces | 555 | 67.57 | 74.41 | 38.38 | 11.17 | 34.77 | 12.43 | 26.85 |
| reference_motion_rollout_v20_contact_gated_projected_traces | 844 | 66.35 | 84.95 | 35.66 | 6.87 | 35.66 | 6.28 | 28.67 |

## Encoding Transform Check

| label | as_is | swap_lr | invert | swap_invert |
|---|---:|---:|---:|---:|
| reference_motion_rollout_v20_traces | 68.03 | 66.30 | 91.18 | 92.91 |
| reference_motion_rollout_v20_projected_traces | 67.77 | 66.27 | 92.02 | 93.52 |
| reference_motion_rollout_v20_projected_phase5_traces | 67.23 | 65.85 | 91.12 | 92.50 |
| reference_motion_rollout_v20_projected_phase19_traces | 67.57 | 65.41 | 90.99 | 93.15 |
| reference_motion_rollout_v20_contact_gated_projected_traces | 66.35 | 66.35 | 95.97 | 95.97 |

## Dominant Mismatch Pairs

| label | pair | pct |
|---|---|---:|
| reference_motion_rollout_v20_traces | `01->11` | 25.35 |
| reference_motion_rollout_v20_traces | `10->11` | 22.99 |
| reference_motion_rollout_v20_traces | `10->01` | 5.83 |
| reference_motion_rollout_v20_traces | `11->10` | 4.88 |
| reference_motion_rollout_v20_projected_traces | `10->11` | 25.75 |
| reference_motion_rollout_v20_projected_traces | `01->11` | 23.95 |
| reference_motion_rollout_v20_projected_traces | `11->10` | 6.17 |
| reference_motion_rollout_v20_projected_traces | `10->01` | 5.57 |
| reference_motion_rollout_v20_projected_phase5_traces | `01->11` | 24.66 |
| reference_motion_rollout_v20_projected_phase5_traces | `10->11` | 23.58 |
| reference_motion_rollout_v20_projected_phase5_traces | `11->10` | 6.58 |
| reference_motion_rollout_v20_projected_phase5_traces | `10->01` | 5.36 |
| reference_motion_rollout_v20_projected_phase19_traces | `10->11` | 25.41 |
| reference_motion_rollout_v20_projected_phase19_traces | `01->11` | 22.16 |
| reference_motion_rollout_v20_projected_phase19_traces | `11->10` | 6.13 |
| reference_motion_rollout_v20_projected_phase19_traces | `10->01` | 5.77 |
| reference_motion_rollout_v20_contact_gated_projected_traces | `10->11` | 29.86 |
| reference_motion_rollout_v20_contact_gated_projected_traces | `01->11` | 25.24 |
| reference_motion_rollout_v20_contact_gated_projected_traces | `11->10` | 3.44 |
| reference_motion_rollout_v20_contact_gated_projected_traces | `10->01` | 2.25 |

## Interpretation

- `11` means both feet in contact, `10` left-only, `01` right-only, `00` no contact.
- High mismatch means the reference contact schedule is not realized by the simulated body under the tested target path.
- Persistent double-support actual contacts while the reference expects single support points to contact/lateral/reference incompatibility.
