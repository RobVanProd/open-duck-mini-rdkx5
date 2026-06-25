# Next Offline Branch After V24

This note is an offline handoff. It does not authorize robot tests, SSH,
deployment, runtime changes, policy deployment, or training by itself.

## Current Decision

Status:

```text
HOLD_V24_TRANSITION_PROPULSION_FAILED_GATE
```

V24 is not a candidate and should not be rerun unchanged.

The corrected seed-0 trace says:

```text
artifact: outputs/analysis/V24_CORRECTED_SEED0_TRACE.md
command: x=0.04
samples: 70
status: LOW_PROGRESS_TERMINATION
mean local vx: -0.0008 m/s
track ratio: -0.0194
double support: 65 / 70 ticks
right-only support: 5 / 70 ticks
```

The support-contact reward terms are now observable after the eval allow-list
fix:

```text
artifact: outputs/analysis/V24_REWARD_OVERRIDE_ALLOWLIST_FIX.md
status: PASS_LOCAL_REWARD_TERMS_OBSERVED_AFTER_ALLOWLIST_FIX
```

So the live blocker is no longer "the eval cannot see the reward terms." The
live blocker is:

```text
the policy still does not learn coherent support transfer and propulsion.
```

## Ruled Out For The Next Branch

Do not spend the next long run on:

```text
rerun V24 unchanged
slightly larger forward_contact_transition_scale
slightly larger forward_double_support_dwell_scale
another single scalar support/contact reward tweak
another gate that grades only fall count
another run without reward activation preflight
```

V23 and V24 already showed that local scalar contact rewards can be configured
and observed, but they do not by themselves produce low-command stepping.

## Required Preflight

Before any support-contact PPO run:

```text
docs/SUPPORT_REWARD_PREFLIGHT.md
```

Required result:

```text
PASS_REWARD_TERMS_OBSERVED
```

or:

```text
WARN_REWARD_TERMS_ZERO
```

only if the zero terms are event/dwell terms that are present in the artifact
and reasonably expected to stay zero in a very short smoke.

Blocked result:

```text
HOLD_REWARD_TERMS_MISSING
```

## Recommended Branches

### Branch A: Closed-Loop Teacher / Optimizer

Goal:

```text
generate a seed-robust 100-150 tick stepping target before PPO
```

This branch should explicitly decide:

```text
stance side
body lateral placement
base height guard
pitch guard
swing-foot placement / clearance
stance push timing
support transition timing
```

Gate before training:

```text
PASS_WEIGHT_TRANSFER_TARGET
```

Minimum 100-tick target gate:

```text
seeds 0 and 2 pass
mean vx >= 0.04 m/s
local forward displacement >= 0.004 m
vy_abs_p95 <= 0.12 m/s
body_pitch_abs_p95 <= 0.35 rad
base_height_min >= 0.145 m
double_support_pct <= 75%
single_support_pct >= 20%
min_each_single_support_pct >= 5%
contact_transitions >= 2
sent_target_velocity_p95 <= 3.75 rad/s
joint_tracking_p95 <= 0.12 rad
```

If this target gate does not pass, do not launch PPO from the target source.

### Branch B: Demonstration / Imitation Path

Goal:

```text
start from an actual coherent stepping demonstration instead of asking PPO to
discover support transfer from scalar rewards
```

This branch should use one of:

```text
matched reference motion with verified command/contact compatibility
hand-authored low-command stepping demonstration
closed-loop teacher demonstration from Branch A
```

Minimum checks before training:

```text
reference command matches gate command
reference contact sequence includes useful left/right single support
reference target velocity stays inside measured actuator envelope
reference replay does not rely on one lucky seed
reward activation preflight passes
```

## Next Concrete Step

The next highest-information offline task is:

```text
pick Branch A or Branch B and produce a small reviewed plan artifact before
launching another cloud job.
```

For Branch A, update the teacher/optimizer plan around explicit stance-side,
foot-placement, and push-timing state.

For Branch B, find or construct a low-command stepping demonstration and audit
its command/contact/envelope compatibility before training.

Robot validation remains blocked until a candidate passes offline low-command
multi-seed gates.
