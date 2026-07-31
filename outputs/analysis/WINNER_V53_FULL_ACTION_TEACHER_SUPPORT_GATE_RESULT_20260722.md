# Winner-v53 full-action-teacher support-gate result

- Status: `HOLD_WINNER_V53_FULL_ACTION_TEACHER_SUPPORT_GATE`
- Decision: `DO_NOT_SELECT_WINNER_V52_DEPLOYMENT_POLICY`
- Result SHA-256: `6fb272a5147dc67074a8196467504717ef7a70b422b355f5c6d7252c7ab41579`
- Selected checkpoint: `null`
- Robot clearance: `false`
- Formal main cells / held-out repeats: `248 / 64`
- Locomotion training / robot or RDK access: `0 / 0`

## Frozen decision

The unchanged all-or-nothing gate evaluated both V52 persistence checkpoints.
The half checkpoint passed `110 / 124` main cells and the final checkpoint
passed `112 / 124`. Therefore `all_248_main_cells_pass` is false. The
preregistered fixed-endpoint rule selects nothing on a hold; neither checkpoint
may be promoted as the closest result.

## Checks that pass at both checkpoints

- exactly `124` main cells per checkpoint;
- all `32` held-out repeats are bit-exact;
- all `16` held-out contexts separate P30 from P31/34;
- learned held-out prediction MSE is strictly below the constant baseline for
  both plants;
- every previous-action chain is exact;
- every JAX/ONNX hidden-state error is at most `1e-7`;
- all `12` sensor/transport cells per checkpoint pass;
- current, torque, overcurrent, base-height, contact, finite-value, and ABI
  gates do not set the hold.

## Failing support population

Every failure is a core variable-configuration cell with a negative-pitch
roll/pitch termination. Both actuator plants fail the same configuration IDs.
No sensor/transport condition fails.

| checkpoint | update | failing configuration IDs | failed cells | termination ticks |
|---|---:|---|---:|---|
| half | 403 | `COM_X_NEG`, `COM_CORNER_00`, `COM_CORNER_01`, `COM_CORNER_03`, `DISCOVERY_03`, `HELDOUT_04`, `HELDOUT_09` | 14 | `30–62` |
| final | 453 | `COM_X_NEG`, `COM_CORNER_01`, `COM_CORNER_03`, `DISCOVERY_03`, `HELDOUT_04`, `HELDOUT_09` | 12 | `30–73` |

`COM_CORNER_00` recovers at the final checkpoint, but the final checkpoint is
still a hold. Terminal pitch spans approximately `-0.3557` to `-0.3878 rad`;
roll remains small. The common failure across P30 and P31/34 makes the
plant-specific pitch fit an unlikely sole cause.

## Predictor/context evidence

At the final checkpoint, learned normalized prediction MSE is
`0.12194854535828924` on P30 and `0.11918281653846612` on P31/34, versus
constant baselines `0.24278438576438519` and `0.24046331853195957`.
The minimum final hidden-state context separation remains
`0.0003934204578399658`, well above `1e-7`.

## Authority

This hold authorizes no deployment checkpoint, asset freeze, runtime update,
Gate 5, robot clearance, X5/robot access, serial/GPIO/I2C, torque, or motion.
The next action must be separately preregistered causal diagnosis; the frozen
V53 population and thresholds are not widened or rerun.
