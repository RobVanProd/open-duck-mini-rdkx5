# Closed-Loop Snippet Branch Decision

status: `HOLD_STITCH_RUNS_TOO_SHORT`

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

## Stitch Branch Result

The planned stitch/relabeling source was implemented as:

```text
tools/plan_closed_loop_snippet_stitching.py
outputs/analysis/CLOSED_LOOP_SNIPPET_STITCH_PLAN.md
outputs/analysis/closed_loop_snippet_stitch_plan.json
```

It starts from the 10-tick passing snippets, merges overlapping or nearby
passing windows, re-evaluates the merged spans with the same motion/contact
criteria, and checks whether any trace reaches 25 or 50 passing ticks.

Result:

| command cell | short pass windows | pass stitch runs | max passing stitch span |
|---|---:|---:|---:|
| upstream nearest turn | 76 | 55 | 12 ticks |
| straight `x=0.04` | 3 | 2 | 12 ticks |
| straight `x=0.08` | 63 | 27 | 18 ticks |

Aggregate:

```text
short pass windows: 142
stitch runs: 86
passing stitch runs: 84
traces with >=25-tick pass runs: 0
traces with >=50-tick pass runs: 0
max passing stitch span: 18 ticks
```

Answer:

```text
No. Under the current criteria, short safe snippets cannot yet be sequenced
into 25-50 tick windows without losing the pass condition.
```

This means the snippets remain useful as local support/phase evidence, but
they are not a direct BC/export source. The next offline branch needs a real
continuity mechanism or a different closed-loop imitation route.

The full-observation stance-timing comparison adds the command-cell context:

```text
outputs/analysis/PUBLISHED_POLICY_STANCE_TIMING_COMPARISON.md
```

| command cell | mean vx | single support | single alternations | single dvx @ 0.1s | pitch p95 |
|---|---:|---:|---:|---:|---:|
| straight `x=0.04` | 0.0019 m/s | 3.65% | 1.50 | -0.0155 m/s | 0.8647 rad/s |
| straight `x=0.08` | 0.0640 m/s | 49.40% | 17.63 | 0.0030 m/s | 3.2849 rad/s |
| upstream nearest turn | 0.0540 m/s | 44.80% | 16.25 | 0.0042 m/s | 3.2396 rad/s |

That means straight `x=0.04` is not a good first walking gate for imitation.
The published policy mostly stands there. The closed-loop stance-transfer
mechanism appears in the moving command cells and should be the source of the
next imitation/selector target.

The safe-vs-unsafe rule contrast then compared passing full-observation
10-tick windows with moving windows rejected for high pitch-chain target rate:

```text
outputs/analysis/CLOSED_LOOP_WINDOW_RULE_CANDIDATES.md
```

| bucket | windows | mean vx | single support | pitch p95 | right knee p95 | action delta p95 |
|---|---:|---:|---:|---:|---:|---:|
| pass safe moving single | 330 | 0.0721 m/s | 46.79% | 3.2896 rad/s | 2.1407 rad/s | 0.1678 |
| reject high-rate moving | 1233 | 0.0667 m/s | 53.10% | 4.7046 rad/s | 4.0445 rad/s | 0.2053 |

The selector problem is therefore sharper than "find single support." Safe and
unsafe moving windows have similar forward speed and single-support occupancy.
The key separator is knee-rate management during stance transfer, especially
right-knee target velocity.

## Next Branch Options

Use this result to avoid another isolated-snippet training run. Viable next
offline directions are:

1. Build a continuity generator that explicitly bridges between safe snippets
   and then re-score 25/50 tick windows before training.
2. Mine BEST_WALK closed-loop state-action rules from the moving command cells
   instead of target snippets, especially contact/CoM timing and right-knee
   rate management.
3. Train/evaluate a recurrent or state-conditioned selector over safe local
   actions, gated on 25-50 tick closed-loop rollout before ONNX export.

Recommended next branch:

```text
PLAN_KNEE_RATE_AWARE_CLOSED_LOOP_SELECTOR
```

The next offline artifact should prototype a selector that chooses only from
moving-command windows with:

```text
single-support / stance-transfer present
pitch-chain p95 <= 3.75 rad/s
right-knee p95 kept near the passing-window distribution
```

Then replay or score 25-50 tick continuity before any student training.

## Stop Rules

- Do not train directly from full BEST_WALK traces.
- Do not train directly from isolated 10-tick snippets.
- Do not use straight `x=0.04` as the first walking pass/fail gate.
- Do not relax the right-knee envelope to make snippets longer.
- Do not run robot validation.
- Do not SSH, deploy, or change runtime behavior.
