# Support Reward Preflight

Purpose: verify that support-contact reward overrides are actually applied and
observable before launching a long cloud PPO run.

This is offline only. It does not train, SSH, deploy, touch the robot, or modify
runtime behavior.

## When To Run

Run this before any recipe that enables contact/support reward terms such as:

```text
forward_single_support
forward_double_support
forward_contact_transition
forward_double_support_dwell
```

The V24 run showed why this matters: the training plan and override JSON
contained these terms, but the closed-loop eval override allow-list initially
did not apply them, so the recovered gate could not observe them.

## Command

Use a tiny local CPU eval. It is slow to compile but cheap compared with a cloud
training run:

```bash
rm -rf /tmp/open_duck_support_reward_preflight

../envs/open-duck-playground/bin/python tools/eval_policy_with_actuator_bridge.py \
  --mode closed-loop-sim \
  --eval-role candidate \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --command-x 0.04 \
  --duration 0.2 \
  --seed 0 \
  --bridge-mode vanilla \
  --jax-platform cpu \
  --sim-preflight-timeout-s 300 \
  --closed-loop-timeout-s 300 \
  --reward-overrides-json outputs/analysis/movement_bootstrap_v24_transition_propulsion_plan.json \
  --reward-overrides-phase phase1_transition_propulsion_probe \
  --output-dir /tmp/open_duck_support_reward_preflight

python3 tools/audit_reward_term_activation.py \
  --reward-overrides-json outputs/analysis/movement_bootstrap_v24_transition_propulsion_plan.json \
  --reward-overrides-phase phase1_transition_propulsion_probe \
  --eval-path /tmp/open_duck_support_reward_preflight \
  --output-md /tmp/open_duck_support_reward_preflight/REWARD_TERM_ACTIVATION.md \
  --output-json /tmp/open_duck_support_reward_preflight/reward_term_activation.json
```

Adjust the `--reward-overrides-json` and `--reward-overrides-phase` values for
the specific recipe being tested.

## Pass / Hold

Pass:

```text
PASS_REWARD_TERMS_OBSERVED
```

or:

```text
WARN_REWARD_TERMS_ZERO
```

`WARN_REWARD_TERMS_ZERO` is acceptable for terms that are timing- or
contact-event-dependent in a very short smoke, as long as they are present in
the artifact.

Hold:

```text
HOLD_REWARD_TERMS_MISSING
```

Do not launch the long run if any newly introduced nonzero term is missing from
the eval artifact.

## Required Record

Record the preflight result in the run summary:

```text
reward activation status
reward override file
phase name
terms missing, if any
terms observed zero, if any
validation command
```

Do not commit `/tmp` outputs. Commit only a small summary under
`outputs/analysis/` if the preflight changes a project decision.
