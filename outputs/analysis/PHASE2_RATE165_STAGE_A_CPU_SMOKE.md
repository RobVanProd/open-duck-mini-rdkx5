# Phase 2 Rate165 Stage A CPU Smoke

status: `PASS_SMOKE_RUN`

## Purpose

Verify that the Phase 2 Stage A narrow flat/no-push training command starts
from the rate165 PPO-loc warm-start checkpoint, enables the corrected actuator
bridge, applies the planned narrow domain-randomization/noise settings, and can
export an updated PPO checkpoint/ONNX without touching the robot.

This is a tiny local CPU path check, not a candidate promotion and not a full
training run.

## Inputs

- restore checkpoint: `outputs/analysis/phase2_rate165_ppo_loc_warmstart_step0_checkpoint`
- behavior prior: `outputs/analysis/phase2_rate165_ppo_loc_warmstart_candidate/candidate_mlp.npz`
- task: `flat_terrain_backlash`
- env: `joystick`
- platform: `cpu`
- timesteps requested: `1024`
- PPO envs/evals: `4` / `1`
- actuator bridge: enabled
- bridge delay: `3-4` ticks
- bridge tau: `0.06-0.10 s`
- bridge velocity range: `2.0-3.25 rad/s`
- pushes: disabled

## Result

- final status: `PASS_SMOKE_RUN`
- return code: `0`
- elapsed: `90.01 s`
- step reached: `2048`
- final reported reward: `14.4284`
- final reported reward std: `2.0281`
- exported smoke ONNX:
  `outputs/phase2_domain_randomization/stage_a_rate165_local_cpu_smoke/smoke_20260703T113837Z_cpu/2026_07_03_073931_2048.onnx`
- exported smoke ONNX sha256:
  `4a034ce3f82d91e681baab823be8e9b69d64f9ed448db6c449e73b3c79362408`

## Provenance

Raw local smoke artifacts are intentionally kept under:

```text
outputs/phase2_domain_randomization/stage_a_rate165_local_cpu_smoke/smoke_20260703T113837Z_cpu
```

They are not a promoted candidate and are not required for the next full GPU
Stage A run.

## Interpretation

The Phase 2 Stage A command path is wired correctly for the rate165 warm-start:
the runner loads the 101-observation / 14-action joystick env, restores the
step-0 checkpoint, enables restore-policy KL, enables the corrected actuator
bridge, enables the behavior prior, applies narrow DR/noise ranges, and exports
after a short PPO update.

Next step remains the full Stage A narrow flat/no-push run on a GPU session,
followed by corrected-bridge gates before any Stage B/C/D escalation.
