# Phase 2 C7 Trace Diagnostic And Swing-Balance Plumbing

status: `PASS_SWING_BALANCE_PLUMBING`

## Scope

Offline sim/tooling only. No robot, SSH, deploy, grounded replay, runtime
behavior change, or policy overwrite was performed.

## C7 Trace Diagnostic

C7 found a useful early checkpoint, `c7_35120`, but the 8-seed `z=0.002`
terrain screen only passed `5/8` seeds. A compact trace comparison was run for
one passing seed and one low-progress seed:

```text
policy: c7_35120
passing seed: 2
low-progress seed: 4
trace output root: outputs/analysis/phase2_stage_c7_35120_trace_pass_fail_cpu
```

Summary:

| seed | status | track ratio | single support | double support | support transitions | left swing segments | right swing segments | mean swing peak |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2 | `PASS_CANDIDATE_SIM_GATE` | 0.3577 | 18.8% | 81.2% | 33 | 3 | 7 | 0.0090 m |
| 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1918 | 4.0% | 96.0% | 13 | 0 | 2 | 0.0045 m |

Interpretation:

- The failing seed is not failing because of actuator envelope or falling.
- It almost never leaves double support.
- It never produces a left-foot swing segment during the sampled rollout.
- The few right-foot swing events are tiny.
- Even the passing seed is still mostly a low-clearance, one-sided shuffle.

This identifies the next target more sharply than C6: the missing behavior is
balanced alternating swing usage, not only lower tracking error.

## New Default-Off Hook

Added a default-off `forward_swing_balance` cost in the Playground:

```text
playground/common/rewards.py
playground/open_duck_mini_v2/joystick.py
playground/open_duck_mini_v2/runner.py
```

The hook tracks accumulated per-foot swing steps during a forward command
window and penalizes left/right swing imbalance after a configurable grace
period. It is inactive by default.

New runner flags:

```text
--forward_swing_balance_scale
--forward_swing_balance_grace_steps
```

RDK wrapper/eval plumbing:

```text
tools/run_actuator_bridge_training_smoke.py
tools/closed_loop_sim_eval.py
tools/plan_staged_curriculum_training.py
```

New wrapper flags:

```text
--forward-swing-balance-scale
--forward-swing-balance-grace-steps
```

Tiny CPU smoke:

```text
outputs/analysis/forward_swing_balance_plumbing_smoke/smoke_20260628T142238Z_cpu
status: PASS_SMOKE_RUN
elapsed_s: 63.21
```

The smoke proves the new flags reach the training runner and execute. It is not
a candidate and not evidence of improved walking.

## Next

Use this hook only in a short gate-selected C8 terrain run. The purpose should
be narrow:

- keep C7-style frequent checkpoint export,
- preserve the corrected actuator envelope,
- test whether swing-balance pressure prevents the one-sided double-support
  collapse seen in seed 4,
- screen by terrain metrics rather than final training reward.

Do not run any C7/C8 terrain policy on hardware unless it later clears the
full corrected gates.
