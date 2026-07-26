# T6 corrected-gate torso-COM robustness screen

- Status: `PASS_T6_NO_FROZEN_ROBUST_SURVIVOR`
- Decision: `EARN_AUTOMATIC_CONFIGURATION_RESPONSE_MECHANISM_REVIEW`
- Cells: `64/64`
- Selected survivor: `None`
- Result SHA-256: `0a1000dc370ab04b830ad6c06301e558f88983d4aa382786618be35f8f33252c`

| candidate | green cells | green pair | tracking p95 | min vx | min ratio | current run | overload run | peak torque | peak current |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `V121` | 0/16 | `False` | 0.14862397313117984 | -0.3518881556681461 | -4.569976047638261 | 3 | 3 | 1.8467826843261719 | 2.353992806317871 |
| `V123` | 0/16 | `False` | 0.15696418285369873 | -0.41399077645037324 | -5.594469952032071 | 4 | 5 | 1.88555908203125 | 2.4034189580938063 |
| `V128` | 0/16 | `False` | 0.1524039030075073 | -0.3837141164214067 | -5.185325897586577 | 4 | 4 | 1.9868431091308594 | 2.5325201637802657 |
| `V177` | 1/16 | `False` | 0.14925726652145385 | -0.32158057741297963 | -4.137453149719928 | 5 | 5 | 1.9068431854248047 | 2.430548639730189 |

The condition is the pre-existing R2 `TORSO_COM_X_NEG` endpoint (`-0.05 m`), selected before this screen because it was the first failure of the prior winner after six R2 passes.

Tracking, zero saturation, and zero measured-rate excess are explicit replacement-quality goals where T4 showed the old baseline can fail; they are not relabeled as generic feasibility claims. Servo protection uses the manufacturer-derived 100-tick duration rules from T5.

This CPU-only result does not authorize training, robot access, Gate 5, torque, or motion.
