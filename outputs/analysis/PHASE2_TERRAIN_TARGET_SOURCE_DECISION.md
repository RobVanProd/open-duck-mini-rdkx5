# Phase 2 Terrain Target-Source Decision

status: `HOLD_TERRAIN_TARGET_SOURCE_NOT_READY`

## Context

Phase 2 Stage C exposed a consistent terrain/carpet failure mode:

- the corrected-bridge candidate remains actuator-safe
- flat / low-friction transfer is plausible
- rough terrain and medium carpet show stepping without enough effective foot lift / advance
- scalar terrain rewards so far retreat into low progress or double support

Recent holds:

- `C7`: useful transient, but not seed-robust on terrain
- `C8`: swing-balance scalar pressure worsened progress
- action gain `1.05/1.10`: stayed in-envelope but worsened progress and did not recover the planted seed
- `C9`: forward-swing-advance hook worked, but trained checkpoints retreated to low progress and seed 4 stayed planted

## New Preflight

I ran the existing finite-horizon foot-placement MPC teacher against `rough_terrain_backlash`
as a bounded target-source preflight. This was offline only: no robot, SSH,
deployment, runtime change, or training.

Command shape:

```text
task: rough_terrain_backlash
command_x: 0.08
duration: 3.0 s
seeds: 2,4
platform: cpu
teacher target velocity limit: 2.5 rad/s
stance-relative lateral: enabled
hold switch until stable: enabled
swing min advance: 0.005 m
swing knee: 0.14 rad
```

Artifacts:

- `outputs/analysis/PHASE2_FOOT_PLACEMENT_MPC_ROUGH_PREFLIGHT.md`
- `outputs/analysis/PHASE2_FOOT_PLACEMENT_MPC_ROUGH_PREFLIGHT_SCORE_100.md`
- `outputs/analysis/PHASE2_FOOT_PLACEMENT_MPC_ROUGH_PREFLIGHT_SCORE_150.md`
- `outputs/analysis/PHASE2_FOOT_PLACEMENT_MPC_ROUGH_PREFLIGHT_GATE.md`

## Result

The probe ran, but no seed-robust target source was found:

```text
probe status: PASS_FOOT_PLACEMENT_MPC_PROBE_RAN
100-sample score: HOLD_NO_SEED_ROBUST_TARGETS
150-sample score: HOLD_NO_SEED_ROBUST_TARGETS
gate: HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET
```

Best candidate family:

```text
seed 2 mean vx: 0.0046-0.0079 m/s
seed 4 mean vx: 0.0030 m/s or fall/reverse depending initial stance
sent target velocity p95: <= 2.5 rad/s
dominant failures: low_forward_velocity, double_support_dominates,
                   too_little_single_support, single_support_not_balanced
```

The important signal is that this target source is actuator-safe and laterally
calm, but it does not create sustained forward stepping. It repeats the same
double-support / low-progress terrain failure instead of providing a stronger
teacher.

## Decision

Do not promote the current foot-placement MPC teacher as a Phase 2 target source.
Do not start BC/PPO from this rough-terrain preflight. Do not run another scalar
terrain-reward stage that can be satisfied by standing, low progress, or double
support.

Next offline branch should target one of these structural fixes:

1. Build a hard step-transition target source whose gate cannot be satisfied
   without each foot producing swing segments, forward relative-foot excursion,
   and touchdown advance.
2. Re-mine / synthesize a higher-clearance alternating-step source from the
   working corrected-bridge walker, then evaluate it on rough terrain before
   training.
3. Add a reviewed teacher/evaluator gate that treats double-support dwell and
   missing per-foot swing segments as hard failures before PPO sees the target.

The current blocker is target manifold / stepping structure, not actuator
envelope, not global action amplitude, and not another scalar reward coefficient.
