# Phase 2 Transition-Preserving Terrain Branch

status: `HOLD_REWARD_PPO_ERODES_SUPPORT_TRANSITION`

## Objective

Recover rough-terrain / carpet robustness without deleting the support
transition that creates forward motion.

This branch is offline-only. It does not authorize robot tests, SSH, deploy,
grounded replay, runtime behavior changes, or training from scratch.

## Evidence

The live-oracle terrain DAgger student recovered forward progress on
`rough_terrain_backlash` at `z=0.002`, but held on corrected tracking/envelope:

```text
iter2 seed 2: vx 0.0526 m/s, track ratio 0.6570, tracking p95 0.2533
iter2 seed 4: vx 0.0459 m/s, track ratio 0.5736, tracking p95 0.2527
```

A simple tracking-aware label filter then clipped pitch-chain oracle labels to
`2.25 rad/s`. It lowered the supervised target rate and reduced closed-loop
tracking pressure, but collapsed the terrain gait:

```text
tracking-aware seed 2: vx 0.0107 m/s, track ratio 0.1335, double support 90%
tracking-aware seed 4: vx 0.0105 m/s, track ratio 0.1314, double support 96%
```

Trace comparison shows the mechanism:

```text
iter2 single support: about 30-35%
tracking-aware single support: about 4-10%
```

The global label cap mostly damped the double-support preparation into
single-support transition. It made the gait calmer by removing the step.

## Hypothesis

The next student needs the iter2 support-transition structure, but with
closed-loop correction of the excess pitch-chain tracking/rate. Offline label
clipping is too blunt because the labels that look aggressive are also the
transition labels that create single support.

## Required Method

Use one of these mechanisms, in order:

1. Closed-loop PPO fine-tune from `iter2_live_oracle_bc` with a strong restore
   prior and explicit corrected per-joint envelope/tracking penalties.
2. Transition-aware relabeling that preserves double-support preparation and
   single-support timing, only editing labels whose closed-loop rollout
   actually exceeds the corrected per-joint envelope.
3. Phase/contact-conditioned student that can represent different actions for
   double-support preparation, left support, and right support, with the hard
   swing gate active.

Do not run another simple global label-rate filter or scalar terrain reward
sweep as the next branch.

Method 1 has now been smoke-tested and held for this scalar reward-side recipe
family. The PPO restore/export plumbing works, but tiny updates erased the
support transition even under a tight trust region. The next branch should move
to method 2 unless method 1 is structurally changed to protect transition
actions directly.

## Warm-Start Artifact

The transition-preserving PPO warm-start now exists locally:

```text
decision: outputs/analysis/PHASE2_TERRAIN_PPO_SHAPE_WARMSTART_DECISION.md
checkpoint: outputs/analysis/phase2_terrain_live_oracle_dagger_iter2_ppo_shape_step0_checkpoint
step0 ONNX: outputs/analysis/phase2_terrain_live_oracle_dagger_iter2_ppo_shape_step0.onnx
fidelity: PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY
```

It is not a candidate policy. Its rough-terrain `z=0.002` gate preserves
forward transition behavior but still holds on corrected tracking/envelope:

```text
seed 2/4 track ratio: 0.6652 / 0.5947
seed 2/4 max tracking p95: 0.2598 / 0.2533
seed 2/4 max velocity excess: 0.7987 / 0.8291
```

This is the restore point for branch method 1.

## PPO Smoke Result

Artifact:

```text
decision: outputs/analysis/PHASE2_TRANSITION_PRESERVING_PPO_SMOKE_DECISION.md
status: HOLD_REWARD_PPO_ERODES_SUPPORT_TRANSITION
```

Two tiny CPU PPO runs were tested from the restore checkpoint.

Normal trust-region smoke:

```text
timesteps: 80
learning_rate: 1e-5
restore_policy_kl_scale: 2.0
behavior_prior_scale: -0.02
seed 2/4 track ratio: 0.0516 / 0.1115
seed 2/4 single support: 3.2% / 0.8%
seed 2/4 double support: 96.8% / 99.2%
```

Lockdown trust-region smoke:

```text
timesteps: 80
learning_rate: 1e-6
restore_policy_kl_scale: 100.0
behavior_prior_scale: -0.10
seed 2/4 track ratio: 0.0548 / 0.1181
seed 2/4 single support: 3.2% / 2.0%
seed 2/4 double support: 96.8% / 98.0%
```

Both runs completed and exported ONNX models, but both collapsed to low-progress
double support. The apparent tracking improvement came from stopping the step,
not from learning a terrain-safe in-envelope gait. Do not launch longer runs of
this same scalar reward-PPO recipe.

## Transition-Protected Relabeling Result

Artifact:

```text
decision: outputs/analysis/PHASE2_TRANSITION_PROTECTED_RATE_LIMIT_DECISION.md
status: PARTIAL_PASS_TRACKING_PLATEAU_BROKEN_HOLD_SEED4_SWING
```

The next method protected all non-double-support samples and a 6-tick window
around foot-contact transitions, then rate-limited only sustained
double-support pitch-chain labels:

```text
protected samples: 488 / 500
changed ticks: 13
changed contact counts: {'11': 13}
```

The resulting diagnostic student moved the rough-terrain blocker forward:

```text
seed 2: PASS_CANDIDATE_SIM_GATE
  track ratio: 0.3641
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1876 rad
  single support: 22.8%

seed 4: HOLD_CANDIDATE_TERRAIN_SWING
  track ratio: 0.3184
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1914 rad
  single support: 10.8%
```

This breaks the prior tracking/envelope plateau on both seeds, but it is not a
deployable pass because seed 4 still fails swing/advance. The next branch should
keep transition-protected rate limiting and add seed-4 swing/advance weighting
or contact-phase-balanced labels.

Simple seed-4 sample weighting was tested next and held:

```text
decision: outputs/analysis/PHASE2_TRANSITION_PROTECTED_SEED4_WEIGHTED_DECISION.md
status: HOLD_SEED_WEIGHTING_REINTRODUCES_TRACKING_EXCESS
seed 2/4 track ratio: 0.5112 / 0.4184
seed 2/4 max velocity excess: 0.2465 / 0.2935 rad/s
seed 2/4 max tracking p95: 0.2202 / 0.2222 rad
seed 2/4 min swing segments: 7 / 6
```

The weighting recovered swing/advance but reintroduced corrected-envelope and
tracking failures. Do not continue naive seed weighting. The remaining branch
needs contact-phase-balanced labels or an explicit action-space correction that
keeps the swing gain while rejecting pitch-chain labels that exceed the
corrected bridge gate.

## Gate

Minimum rough-terrain diagnostic gate before any wider 8-seed run:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.002
bridge: corrected fitted bridge
command_x: 0.08
duration: 5 s
seeds: 2,4
falls: 0
track ratio: >= 0.50
max corrected velocity excess: 0
max tracking p95: <= 0.20 rad
min per-foot swing segments: >= 1
min per-foot rel-x range p95: >= 0.003 m
min per-foot swing peak lift: >= 0.005 m
double support: not above the live-oracle iter2 baseline by more than 10 percentage points
```

Promotion still requires the canonical corrected-bridge flat and rough gates,
including `x=0.0` command preservation, ONNX fidelity, and review. Robot
validation remains blocked.

## Falsifier

If a transition-preserving fine-tune keeps swing support structure but cannot
reduce tracking below `0.20 rad` or corrected-envelope excess to zero, the
terrain blocker is not label smoothing. Revisit the corrected bridge/terrain
contact model or accept that this gait needs a different support strategy.
