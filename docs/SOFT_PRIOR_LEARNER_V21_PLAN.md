# Soft-Prior Learner V21 Plan

## Purpose

`movement_bootstrap_v21` is the first learner that uses the curated short
forward-motion fragments only as a weak closed-loop auxiliary prior.

This is not a target-label or behavior-cloning run. The policy must still earn
progress, posture, contact, and survival reward in the simulator.

## Why

Previous branches established:

```text
V18: cold-start PPO at x=0.04 still drifted backward or froze.
V19: raw reference imitation was command-mismatched.
V20: matched reference imitation still did not produce coherent multi-seed motion.
Primitive fragments: short in-envelope motion exists, but not enough for hard labels.
Soft-prior smoke: short forward motion appears, then freezes or goes lateral.
```

So the next bounded test is whether the fragment shape can help PPO discover
coherent low-command motion when used as a small penalty, not a controller.

## Recipe

Planner:

```bash
python3 tools/plan_staged_curriculum_training.py \
  --recipe movement_bootstrap_v21 \
  --output-md outputs/analysis/STAGED_CURRICULUM_TRAINING_PLAN_V21.md \
  --output-json outputs/analysis/staged_curriculum_training_plan_v21.json
```

Artifacts:

```text
outputs/analysis/STAGED_CURRICULUM_TRAINING_PLAN_V21.md
outputs/analysis/staged_curriculum_training_plan_v21.json
```

Phase 1:

```text
vanilla dynamics
x command: 0.035-0.045
soft_prior_scale: -0.025
soft_prior_config_json: outputs/analysis/soft_prior_fragment_config.json
multi-seed gate: x=0.04, vanilla
```

Phase 2:

```text
only after phase 1 passes
mild actuator bridge
x command: 0.035-0.045
soft_prior_scale: -0.015
multi-seed gate: x=0.04, fitted
```

## Gates

Grade V21 on behavior, not training reward:

```text
mean local vx > 0.02 m/s
positive track ratio
no reverse seed
standstill seeds reduced from V10/V18/V20 baselines
falls reduced or delayed without freezing
target velocity remains inside the fitted envelope
```

Hold states:

```text
HOLD_SOFT_PRIOR_LEARNER_FREEZE
HOLD_SOFT_PRIOR_LEARNER_REVERSE
HOLD_SOFT_PRIOR_LEARNER_LUNGE
HOLD_SOFT_PRIOR_LEARNER_COLLAPSE
HOLD_SOFT_PRIOR_LEARNER_ABOVE_ENVELOPE
```

## Non-Goals

```text
no robot tests
no SSH
no deploy
no x=0.08
no fitted-bridge gate until x=0.04 passes
no policy deployment
do not make V21 the default recipe
```
