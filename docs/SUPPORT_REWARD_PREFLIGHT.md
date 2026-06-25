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

Use the helper. It runs a tiny local CPU eval and then audits the emitted reward
terms. It is slow to compile but cheap compared with a cloud training run:

```bash
python3 tools/run_support_reward_preflight.py \
  --reward-overrides-json outputs/analysis/movement_bootstrap_v24_transition_propulsion_plan.json \
  --reward-overrides-phase phase1_transition_propulsion_probe \
  --output-dir /tmp/open_duck_support_reward_preflight
```

Adjust the `--reward-overrides-json` and `--reward-overrides-phase` values for
the specific recipe being tested.

For lower-level debugging, call `tools/eval_policy_with_actuator_bridge.py`
and `tools/audit_reward_term_activation.py` separately, as the helper does.

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

## V24 Smoke

The helper was run against the V24 plan after the eval allow-list fix:

```text
artifact: outputs/analysis/SUPPORT_REWARD_PREFLIGHT_V24.md
status: WARN_REWARD_TERMS_ZERO
```

The support-contact terms were present. `forward_double_support_dwell` remained
zero in the short smoke, which is expected because it activates only after the
configured grace window.
