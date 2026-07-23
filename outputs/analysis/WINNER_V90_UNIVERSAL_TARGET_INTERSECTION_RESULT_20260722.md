# Winner-v90 universal-target intersection result

- Status: `PASS_WINNER_V90_UNIVERSAL_TARGET_INTERSECTION_AUDIT`
- Classification: `UNIVERSAL_STATIC_TARGETS_EXIST_IN_CAPTURED_GRID`
- Intersection size: `25`
- Selected candidate: `536`
- Selected mirrored coordinates: `[0.5, 0.25, 0.25]`
- Captured support passes: `30 / 30`
- Minimum valid ticks / sum valid ticks: `250 / 7500`
- Worst captured tilt / final gyro: `0.107803 rad / 0.001808 rad/s`
- New simulation / optimizer updates / artifacts / robot access: `0 / 0 / 0 / 0`
- Result SHA-256: `4c97d2ac41ca5d6000359217d25c8e8d17702fb4f329f70015bd5b1b1128f775`

The configuration-specific teacher labels were a selector artifact. Twenty-five
exact V41 grid targets belong to every one of the fifteen V42 feasible sets and
pass both actuator plants. The unchanged aggregate V41 key selects candidate
536 as the single prospective universal target.

This is captured-evidence selection, not a policy or deployment result. It
authorizes only a separately preregistered 124-cell CPU feasibility gate over
the complete model and sensor/transport population. `robot_clearance` remains
false.
