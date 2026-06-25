# V24 Reward Override Allow-List Fix

status: `PASS_LOCAL_REWARD_TERMS_OBSERVED_AFTER_ALLOWLIST_FIX`

## Summary

The first V24 reward activation audit found configured nonzero reward terms that
were missing from recovered candidate eval reward summaries:

```text
forward_contact_transition
forward_double_support
forward_double_support_dwell
forward_single_support
```

Root cause: `tools/closed_loop_sim_eval.py` used an explicit allow-list for
reward scale/config overrides, and that allow-list had not been extended for
the V23/V24 support-contact terms. The eval config recorded the terms from the
phase JSON, but the closed-loop eval env did not apply those override values.

This does not change the V24 behavioral result: the recovered candidate still
failed `6/6` recovered seeds with fall/termination. It does mean the recovered
gate should not be used to claim those newly configured terms were active in
eval.

## Patch

The eval allow-list now applies:

```text
forward_single_support_scale
forward_double_support_scale
forward_contact_transition_scale
forward_double_support_dwell_scale
forward_contact_transition_min_progress_ratio
forward_double_support_dwell_grace_steps
```

## Local Verification

A tiny local CPU closed-loop eval was run with the same V24 reward override
file after the patch:

```text
policy: policy/BEST_WALK_ONNX_2.onnx
command_x: 0.04
duration: 0.2 s
seed: 0
bridge: vanilla
platform: cpu
```

Reward activation audit result:

```text
status: WARN_REWARD_TERMS_ZERO
```

The previously missing terms were now present:

| term | status |
|---|---|
| `forward_contact_transition` | `OBSERVED_NONZERO` |
| `forward_double_support` | `OBSERVED_NONZERO` |
| `forward_single_support` | `OBSERVED_NONZERO` |
| `forward_double_support_dwell` | `OBSERVED_ZERO` |

`forward_double_support_dwell` remaining zero is expected for this short smoke
because the dwell cost only activates after the configured grace window.

## Decision

Before launching another support-contact PPO run, run a short local or cloud
reward activation smoke with the intended reward override file and require all
new nonzero terms to be present in eval artifacts. Do not rely only on the
phase JSON showing the values.

No robot tests, SSH, deployment, runtime behavior changes, or training were
performed by this verification.
