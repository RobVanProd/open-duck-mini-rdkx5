# Phase 2 B0F A100 Push-Local Preserve Plan

status: `PRE_REGISTERED_NOT_STARTED`

## Purpose

B0E showed that broad mild domain-randomization and push continuation from the
B0C parent regresses the moving `x=0.08` tracking margin instead of improving
robustness. B0F is a narrower follow-up: keep the B0C rough-terrain gait close
to its parent while exposing it to the specific frequent gentle-push condition
that currently blocks promotion.

This is offline sim/training only. No robot tests, SSH, deploy, grounded replay,
runtime behavior changes, or policy overwrite are in scope.

## Parent

```text
outputs/phase2_domain_randomization/stage_b0c_rough_z002_push_tracking_margin_from_b0_gpu/smoke_20260629T062042Z_gpu/2026_06_29_022725_245760
```

## Recipe

Named workflow:

```text
phase2-b0f
```

Key differences from B0E:

```text
num_timesteps: 80000
ppo_num_envs: 64
ppo_batch_size: 512
learning_rate: 0.000003
ppo_clip: 0.02
max_grad_norm: 0.1
restore_policy_kl_scale: 5.0
behavior_prior_scale: -1.0
actuator_tracking_scale: -0.01

push_interval: 1.0-2.0 s
push_magnitude: 0.03-0.08

friction: 0.95-1.05
mass: 0.995-1.005
torso_mass_delta: +/-0.005
com_jitter: 0.003 m
qpos_jitter: 0.003 rad
actuator_gain: 0.995-1.005
leg_geometry_jitter: 0.001
noise_level: 0.25
```

## Hypothesis

The remaining Phase 2 blocker is a local perturbation-recovery margin issue,
not a nominal gait issue. A smaller adaptation with frequent gentle pushes and
stronger behavior preservation may reduce push-induced target-rate/tracking
spikes without shifting the nominal no-push swing timing that already passes.

## Scale Probe

The first full-shape B0F launch at `128` envs died before writing normal runner
stdout/stderr or an exit sentinel. Two direct A100 probes were then run on the
same pinned dependency stack:

```text
8 env tiny probe:  returncode 0
64 env probe:      returncode 0
```

The named B0F workflow is therefore pinned to `64` envs / batch `512` for the
real run. This is a hardware/runtime scale adjustment, not a recipe change.

## Gate

Run checkpoint triage first:

```text
commands: 0.0,0.08
duration: 1 s
bridge: fitted corrected bridge
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.002
```

Promote to full gate only if the short triage does not regress the nominal
`x=0.08` pitch tracking plateau and does not reduce forward command tracking
below the B0C/B0E range.

Required full gates before any robot consideration:

```text
x=0.08 rough z=0.002 no push: 8/8 pass
x=0.0  rough z=0.002 no push: 8/8 pass
x=0.08 rough z=0.002 gentle push: 8/8 pass
x=0.0  rough z=0.002 gentle push: 8/8 pass
```

## Stop Conditions

Do not continue from B0F if:

- short gate `x=0.08` tracking stays at or above `0.22 rad`;
- track ratio drops below B0E's already-low `~0.31-0.35`;
- no-push swing geometry regresses;
- the run only improves fall count by freezing.

If B0F holds, return to eval-only perturbation localization or a policy
correction targeted at push recovery moments. Do not run another broad DR
continuation.
