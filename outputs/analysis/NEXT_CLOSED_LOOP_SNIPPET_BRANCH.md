# Closed-Loop Snippet Branch Decision

status: `PLAN_DEPLOYABLE_POLICY_VALIDATION_AND_WARMSTART`

This is an offline branch decision. It does not train, deploy, SSH, run robot
tests, or change runtime behavior.

## Superseding Decision

The closed-loop snippet and relabeled-selector sequence work should no longer be
treated as the active default branch. A later source-VX selector result proved
eight-seed, 10-second, in-envelope forward motion through the fitted actuator
bridge:

```text
outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_SOURCE_VX_BLEND080_100_SRCVX002_ALT_EXCLUDE_SEED4_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
moving seeds: 8 / 8
sent-target velocity p95: 2.2569-2.3622 rad/s
```

That selector is diagnostic and non-deployable, but it has done its feasibility
job. The active next branch is now:

```text
PLAN_DEPLOYABLE_POLICY_VALIDATION_AND_WARMSTART
```

Validate the deployable DAgger-2 ONNX candidates under stricter fitted/stress
bridge gates before any more selector tuning:

```text
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_candidate/candidate.onnx
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_rate_reg_candidate/candidate.onnx
```

See:

```text
outputs/analysis/SOURCE_VX_SELECTOR_POLICY_PIVOT.md
```

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

That prototype source was built as:

```text
tools/build_knee_rate_selector_manifest.py
outputs/analysis/KNEE_RATE_SELECTOR_MANIFEST.md
```

Result:

```text
status: HOLD_SELECTOR_MISSING_STANCE_SIDE
entries: 313
covered phase bins: 5 / 8
double-majority windows: 178
right-stance majority windows: 135
left-stance majority windows: 0
```

Relaxing the right-knee cap to the full envelope did not recover left-stance
coverage. Across all passing full-observation windows:

```text
center contacts:
  11: 200
  01: 129
  10: 1

majority contacts:
  11: 195
  01: 135
  10: 0
```

Updated decision:

```text
HOLD_ONE_SIDED_SELECTOR_SOURCE
```

Do not train from the current knee-rate-aware manifest. The next branch must
recover, mirror with verification, or replace the missing left-stance safe
mechanism before BC/export.

The left-stance gap analysis resolves which of those applies:

```text
outputs/analysis/LEFT_STANCE_GAP_ANALYSIS.md
status: WARN_LEFT_STANCE_EXISTS_BUT_NOT_IN_SELECTOR
left-related windows: 553 / 2904
```

Left stance is present but unsafe:

| group | windows | pass | pitch p95 | right knee p95 | left knee p95 |
|---|---:|---:|---:|---:|---:|
| center left / majority left | 388 | 0 | 5.1021 | 5.0757 | 2.6358 |
| center left / majority double | 94 | 1 | 5.0024 | 4.9303 | 2.1449 |
| center right / majority right | 362 | 102 | 3.6390 | 1.9382 | 3.6082 |

Updated next branch:

```text
PLAN_LEFT_STANCE_RIGHT_KNEE_RATE_RECOVERY
```

Do not treat this as a generic contact-coverage problem. The missing safe side
is specifically left support with a right-knee target-rate burst. Any mirrored
or recovered source must prove that the right-knee p95 is brought back into the
passing-window range before training/export.

The right-knee relabeling recovery probe did that offline:

```text
outputs/analysis/LEFT_STANCE_RATE_RECOVERY.md
status: PASS_RIGHT_KNEE_RELABEL_RECOVERS_LEFT_STANCE
right_knee_cap: 3.61 rad/s
```

Result:

| set | windows |
|---|---:|
| left-related windows | 553 |
| original pass windows | 1 |
| relabeled pass windows | 343 |
| relabeled pass pct | 62.03% |

By group:

| group | original pass | relabeled pass |
|---|---:|---:|
| center left / majority left | 0 / 388 | 242 / 388 |
| center left / majority double | 1 / 94 | 70 / 94 |
| center double / majority left | 0 / 64 | 31 / 64 |

Updated next branch:

```text
PLAN_RELABEL_BALANCED_SELECTOR_SOURCE
```

Build a balanced selector manifest that combines:

```text
original passing right-stance / double windows
right-knee-rate-relabelled left-stance windows
```

Then score phase/stance coverage and 25-50 tick continuity before any BC/export.
This is still offline only; the relabeled windows have not been stepped in sim.

The balanced source was built:

```text
outputs/analysis/RELABELLED_BALANCED_SELECTOR_MANIFEST.md
status: PASS_BALANCED_SELECTOR_SOURCE_READY
entries: 672
```

Coverage:

| category | entries |
|---|---:|
| left stance | 273 |
| right stance | 135 |
| double | 264 |
| right-knee relabelled | 343 |
| original | 329 |
| phase bins covered | 8 / 8 |

Updated next branch:

```text
PLAN_SELECTOR_CONTINUITY_REPLAY_GATE
```

The source is balanced enough to prototype, but not training-ready. The next
offline gate must score 25-50 tick continuity/replay from the manifest before
BC/export.

The non-sim continuity score now passes:

```text
outputs/analysis/RELABELLED_SELECTOR_CONTINUITY_SCORE.md
status: PASS_SELECTOR_CONTINUITY_50_TICKS
```

Summary:

| metric | value |
|---|---:|
| runs | 101 |
| pass runs | 98 |
| max passing span | 96 ticks |
| pass runs >=25 ticks | 20 |
| pass runs >=50 ticks | 11 |
| pass runs using relabel | 92 |

Updated next branch:

```text
PLAN_RELABELLED_SELECTOR_SIM_REPLAY
```

Run a bounded offline sim replay of the top relabeled selector spans. This
must still be no robot / no SSH / no deploy / no training. The replay gate
should check whether the right-knee relabeled target sequence remains stable
when stepped, not just when re-scored as a target sequence.

The first bounded sim replay is complete:

```text
outputs/analysis/RELABELLED_SELECTOR_REPLAY_MANIFEST.md
outputs/analysis/RELABELLED_SELECTOR_SEQUENCE_REPLAY_TOP3_5S.md
status: HOLD_SEQUENCE_REPLAY_TERMINATED
```

Top-three 5s CPU replay:

| seed | outcome |
|---:|---|
| 0 | all 3 spans complete 250 samples, vx 0.0440-0.0475 m/s, target velocity p95 2.54-3.04 rad/s |
| 1 | all 3 spans terminate at 33-38 samples before the selected window, with reverse/lateral/pitch failure |

Updated next branch:

```text
PLAN_STATE_ALIGNED_SELECTOR_REPLAY
```

Do not launch BC/export from this selector yet. The relabeled spans can step
from at least one reset seed, but the prefix/initial-state sensitivity means a
static sequence table is not seed robust. The next offline gate should either
state-align replay to the source span or build a closed-loop selector that can
recover from reset variation before entering the selected sequence.

The replay divergence audit confirms the prefix mismatch:

```text
outputs/analysis/RELABELLED_SELECTOR_REPLAY_DIVERGENCE.md
status: HOLD_REPLAY_DIVERGES_BEFORE_SELECTOR_WINDOW
```

All six checked replay traces diverge before their selected window. Five
diverge at tick 0; one diverges at tick 5. Seed 1 failures show contact
mismatch above 60% and lateral velocity error above 1.1 m/s p95 before
termination. This means the sequence table is not the immediate object to tune:
the source state is not being recreated from reset.

Exact state alignment is blocked by missing source-trace state:

```text
outputs/analysis/SELECTOR_STATE_ALIGNMENT_REQUIREMENTS.md
status: HOLD_STATE_ALIGNMENT_TRACE_CONTRACT_INCOMPLETE
```

The current traces do not include full `qpos`, `qvel`, full base quaternion,
control state, or motor-target/action-history state. Do not fake state-aligned
replay from pitch-only orientation and joint position. The next branch should
either regenerate source traces with full MJX state or build a closed-loop
selector over current observation/contact state.

## Stop Rules

- Do not train directly from full BEST_WALK traces.
- Do not train directly from isolated 10-tick snippets.
- Do not use straight `x=0.04` as the first walking pass/fail gate.
- Do not relax the right-knee envelope to make snippets longer.
- Do not run robot validation.
- Do not SSH, deploy, or change runtime behavior.
