# Next Closed-Loop Snippet Branch

status: `PLAN_SNIPPET_STITCHING_WITH_RATE_REJECTION`

This is an offline branch decision. It does not train, deploy, SSH, run robot
tests, or change runtime behavior.

## Evidence

Published BEST_WALK command comparison:

```text
outputs/analysis/PUBLISHED_POLICY_COMMAND_PROPULSION_COMPARISON.md
```

Key result:

| command | moving seeds | envelope-safe seeds | mean vx | single support | max pitch p95 |
|---|---:|---:|---:|---:|---:|
| straight x=0.04 | 0 / 8 | 8 / 8 | 0.0019 m/s | 3.65% | 2.9633 rad/s |
| upstream nearest turn | 7 / 8 | 1 / 8 | 0.0540 m/s | 44.80% | 5.2400 rad/s |
| straight x=0.08 | 7 / 8 | 0 / 8 | 0.0640 m/s | 49.40% | 5.2400 rad/s |

Closed-loop template extraction:

```text
outputs/analysis/PUBLISHED_POLICY_COMMAND_CLOSED_LOOP_TEMPLATE.md
```

Key result:

| command | moving in envelope | moving single-support in envelope | pitch p95 |
|---|---:|---:|---:|
| straight x=0.04 | 4.65% | 1.25% | 2.3441 rad/s |
| upstream nearest turn | 63.70% | 28.90% | 4.9472 rad/s |
| straight x=0.08 | 70.55% | 32.80% | 5.1961 rad/s |

Closed-loop teacher window mining:

```text
outputs/analysis/CLOSED_LOOP_TEACHER_WINDOW_MINE.md
outputs/analysis/CLOSED_LOOP_TEACHER_WINDOW_MINE_10T.md
```

Key result:

| window | status | passing windows |
|---|---|---:|
| 25 ticks / 0.50s | `HOLD_INSUFFICIENT_CLOSED_LOOP_WINDOWS` | 0 / 1104 |
| 10 ticks / 0.20s | `PASS_CURATED_CLOSED_LOOP_WINDOWS_FOUND` | 142 / 2904 |

Passing 10-tick snippets by command:

```text
upstream nearest turn: 76
straight x=0.08: 63
straight x=0.04: 3
```

## Interpretation

BEST_WALK contains brief closed-loop, moving, single-support, envelope-safe
snippets. It does not provide sustained 25-tick envelope-safe walking windows
under the current gates.

That means:

```text
do not clone full BEST_WALK traces
do not treat straight x=0.04 as the first walking gate
do not treat BEST_WALK as already actuator-envelope-safe when it moves
```

The useful signal is narrower:

```text
short safe snippets show the local support/phase pattern to preserve
high-rate right-knee burst windows show what to reject or relabel
continuity between snippets is the missing mechanism
```

## Next Branch

Build a snippet-stitching / relabeling source that:

1. Starts from the 10-tick passing snippets.
2. Rejects windows where pitch-chain p95 exceeds `3.75 rad/s`.
3. Tracks which contact phase and command cell each snippet came from.
4. Adds transition/continuity constraints before BC/export.
5. Scores candidate stitched windows at 25 and 50 ticks before any student
   training.

Minimum next artifact:

```text
outputs/analysis/CLOSED_LOOP_SNIPPET_STITCH_PLAN.md
outputs/analysis/closed_loop_snippet_stitch_plan.json
```

The stitch plan should answer:

```text
Can short safe snippets be sequenced into 25-50 tick windows without
reintroducing right-knee target-rate bursts or losing forward motion?
```

## Stop Rules

- Do not train directly from full BEST_WALK traces.
- Do not train directly from isolated 10-tick snippets.
- Do not use straight `x=0.04` as the first walking pass/fail gate.
- Do not relax the right-knee envelope to make snippets longer.
- Do not run robot validation.
- Do not SSH, deploy, or change runtime behavior.
