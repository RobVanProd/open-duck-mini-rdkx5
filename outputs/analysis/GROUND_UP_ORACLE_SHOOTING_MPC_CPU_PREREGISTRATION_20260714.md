# Ground-Up Oracle Shooting MPC CPU Preregistration

status: `PREREGISTERED_BEFORE_PROBE`

## Purpose

Test whether a learned-policy-free, oracle-dynamics receding-horizon controller
can create the missing closed-loop propulsion source. This is a source probe,
not policy training and not an offline winner evaluation.

## Frozen mechanism

- pure MuJoCo CPU dynamics from `flat_terrain_backlash`;
- fitted actuator delay/lag/rate bridge from
  `fixed_target_p30_actuator_fit_20260712.json`;
- action scale `0.25 rad`, 50 Hz control, environment substeps unchanged;
- exact-command projected reference is only the proposal center and residual
  regularizer, not the executed teacher;
- cross-entropy shooting over leg actions, replanned from current state;
- horizon `8` control ticks, action block `2` ticks;
- population `64`, elite count `8`, iterations `4`, initial standard deviation
  `0.20`, minimum standard deviation `0.03`;
- pitch-chain and other joint action changes are clipped to the frozen measured
  velocity limits before dynamics rollout.

The frozen objective is:

`100*dx + 2*final_vx - 25*abs(dy) - 12*(roll^2+pitch^2) - 3*yaw^2 - 150*height_shortfall^2 - 0.25*reference_residual_MSE - 0.10*action_delta_MSE - 100*fall`.

No weight, horizon, population, elite, seed, or constraint is tuned from probe
results.

## Frozen probe

- command x=`0.074`, y/yaw=`0`;
- seeds `100/101`;
- duration `1.08 s`;
- deterministic RNG stream per seed;
- home/reference phase `0`;
- noise and pushes disabled.

The source advances to a longer teacher gate only if both seeds complete,
produce positive world displacement and positive mean forward velocity, show
bilateral contact transitions, avoid action saturation, and have zero measured
joint-rate excess. Any lesser result is a source-probe hold, not a training
authorization. Training reward is not used.

Local CPU only. No Colab, local GPU, iGPU, onboard GPU, RDK-X5, robot, torque,
or motor access is authorized.
