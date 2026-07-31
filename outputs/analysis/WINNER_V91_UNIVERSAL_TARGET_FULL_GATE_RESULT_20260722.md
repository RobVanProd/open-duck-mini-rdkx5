# Winner-v91 universal-target full-gate result

- Status: `PASS_WINNER_V91_UNIVERSAL_TARGET_FULL_GATE`
- Target candidate / coordinates: `536 / [0.5, 0.25, 0.25]`
- Core-model / sensor-transport passes: `112 / 12`
- Total support passes: `124 / 124`
- Maximum bounded-target action error: `0`
- Worst tilt / current / torque: `0.144712 rad / 1.830962 A / 1.436449 N.m`
- Worst final gyro / minimum base Z: `0.030830 rad/s / 0.15 m`
- Optimizer updates / artifacts / robot access: `0 / 0 / 0`
- Result SHA-256: `3d4611164c21bcf0ea8296f5faa0941580a99b61ed66b4b50d07d3c56735c41c`

The single universal target preserves the complete reviewed support contract,
including every model configuration, both actuator plants, and every
sensor/transport condition. This removes the need for configuration-specific
static action labels during calibration.

The result authorizes only a separately preregistered CPU mechanism contract
that combines this fixed graph-bounded calibration action with a response
observer. It selects no deployment checkpoint and leaves
`robot_clearance: false`.
