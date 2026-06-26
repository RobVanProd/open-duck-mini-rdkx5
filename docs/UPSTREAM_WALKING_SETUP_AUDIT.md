# Upstream Walking Setup Audit

This is an offline provenance audit. It does not train, deploy, SSH, or run
robot tests.

## Executive Summary

The upstream walking story is split across two repositories:

- `apirrone/Open_Duck_Playground` contains the training/eval environment,
  polynomial reference motion, and export scripts.
- `apirrone/Open_Duck_Mini` branch `v2` publishes the deployed
  `BEST_WALK_ONNX_2.onnx` policy used by the runtime.

The local `policy/BEST_WALK_ONNX_2.onnx` matches the local
`Open_Duck_Mini/BEST_WALK_ONNX_2.onnx` byte-for-byte by SHA256:

```text
3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067
```

GitHub reports the upstream `apirrone/Open_Duck_Mini:v2` file as:

```text
path: BEST_WALK_ONNX_2.onnx
size: 884177 bytes
git blob sha: 7e4536d90e35f9a3a886fb7584d489ad4894dfe0
download: https://raw.githubusercontent.com/apirrone/Open_Duck_Mini/v2/BEST_WALK_ONNX_2.onnx
```

The training checkpoint that produced that ONNX is not published in the
Playground repository, and the Playground repository has no GitHub releases.
The README's documented "Current win" command is:

```bash
uv run playground/open_duck_mini_v2/runner.py \
  --task flat_terrain_backlash \
  --num_timesteps 300000000
```

That means the next useful question is not another nearby teacher variant. It
is whether the published ONNX/reference/setup actually produces forward
propulsion in the expected upstream sim contract, especially the
`flat_terrain_backlash` task.

## Sources Checked

| Source | Finding |
|---|---|
| `/tmp/open_duck_playground_origin_main` | detached `origin/main` at `b9be205ac64488c23504ca42e5ec790337adeec3` |
| `Open_Duck_Playground/README.md` | documents imitation reference generation and `flat_terrain_backlash` 300M current-win command |
| `playground/open_duck_mini_v2/runner.py` | default task is `flat_terrain`; default timesteps are `150000000` |
| `playground/common/runner.py` | saves checkpoints and exports ONNX during PPO training |
| GitHub issue `apirrone/Open_Duck_Playground#8` | confirms 101 observation / 14 action training context and example checkpoint step `10813440` |
| GitHub PR `apirrone/Open_Duck_Playground#10` | merged export fix; body says a model was trained and checkpoint tested after the change |
| `Open_Duck_Mini_Runtime/README.md` | points deployment users to `Open_Duck_Mini:v2/BEST_WALK_ONNX_2.onnx` |
| `apirrone/Open_Duck_Mini:v2` | publishes `BEST_WALK_ONNX_2.onnx` but not its training checkpoint lineage |

## Upstream Reference Push-Effectiveness

The upstream polynomial reference key used for the nearest command is:

```text
x = 0.074
y = -0.037
yaw = -0.074
```

This was tested against the detached upstream-main Playground worktree using
the README's `flat_terrain_backlash` task:

```text
playground_path: /tmp/open_duck_playground_origin_main
task: flat_terrain_backlash
```

Artifact:

```text
outputs/analysis/REFERENCE_PUSH_EFFECTIVENESS_UPSTREAM_MAIN_BACKLASH_NEAREST.md
```

Result:

```text
status: HOLD_REFERENCE_CONTACT_MISMATCH
best reference-single future vx delta: -0.0051 m/s
```

Summary:

| mode | falls | mean vx | contact mismatch | ref-single future vx delta | ref-single vy p95 | ref-single pitch vel p95 |
|---|---:|---:|---:|---:|---:|---:|
| raw | 1/8 | -0.0500 | 66.9833% | -0.0390 | 0.1859 | 5.2400 |
| cycle projected | 0/8 | -0.0114 | 72.9500% | -0.0356 | 0.1713 | 5.2400 |
| contact synchronized projected | 1/8 | 0.0301 | 20.1366% | -0.0051 | 0.1696 | 5.2400 |

Interpretation:

```text
The README's backlash task improves some duration/stability metrics, but it
does not make the upstream reference's single-support windows create net
forward acceleration. The best 0.1s future-vx delta during reference single
support remains negative.
```

## Morphology / Reference File Audit

Artifact:

```text
outputs/analysis/UPSTREAM_SIM_MORPHOLOGY_AUDIT.md
```

Result:

```text
PASS_MORPHOLOGY_MATCHES_UPSTREAM_CODE_DRIFT_ONLY
```

Meaning:

```text
The local XML and polynomial reference file match upstream byte-for-byte.
The known drift is in code paths such as joystick.py and runner.py, not in the
MJCF/reference assets.
```

## Decision

Do not continue local teacher variants as the default next move. The current
evidence says:

```text
local teacher push primitives:
  do not produce robust positive forward impulse

matched x=0.04 reference:
  positive impulse only while violating lateral stability / target-rate limits

upstream nearest reference on flat_terrain:
  no positive reference-single future-vx delta

upstream nearest reference on flat_terrain_backlash:
  no positive reference-single future-vx delta
```

The first contact-physics substitution did not rescue this:

```text
outputs/analysis/CONTACT_PHYSICS_AUDIT.md
status: HOLD_CONTACT_FRICTION_SOLVER_NOT_SUFFICIENT
floor friction: 0.6 -> 1.5 0.01 0.0006
solver iterations: 1/5 -> 100/50
best reference-single future-vx delta: -0.0051 -> -0.0182 m/s
```

This does not prove stable forward walking is impossible. It does prove that
the currently tested reference/teacher action-target paths are not an
existence proof for stable, in-envelope, low-command walking.

## Published-Policy Sim Audit

The published-policy discriminator has now been run:

```text
outputs/analysis/PUBLISHED_POLICY_PROPULSION_AUDIT.md
status: PASS_POLICY_CLOSED_LOOP_FORWARD_MOTION
task: upstream-main flat_terrain_backlash
seeds: 8
duration complete: 8 / 8
moving seeds with track ratio >= 0.5: 7 / 8
mean local vx: 0.0540 m/s
mean single-support 0.1s future vx delta: +0.0042 m/s
```

This answers a different question than the reference rollouts:

```text
Does the published policy use closed-loop feedback to produce forward
propulsion that the open-loop/reference-target path does not?
```

Answer: yes. The upstream-main sim/morphology is not generally unable to walk.
The failed path is the open-loop/reference-target controller path. The next
offline branch should mine the published policy's closed-loop contact and
propulsion mechanism before returning to teacher generation.

The command-specific follow-up shows that this result is not uniform across
low-speed commands:

```text
outputs/analysis/PUBLISHED_POLICY_COMMAND_PROPULSION_COMPARISON.md
status: PASS_POLICY_COMMAND_PROPULSION_COMPARISON
```

Summary:

| command | moving seeds | envelope-safe seeds | mean local vx | single support | max pitch sent-target p95 |
|---|---:|---:|---:|---:|---:|
| straight `x=0.04` | 0 / 8 | 8 / 8 | 0.0019 m/s | 3.65% | 2.9633 rad/s |
| upstream nearest `x=0.074, y=-0.037, yaw=-0.074` | 7 / 8 | 1 / 8 | 0.0540 m/s | 44.80% | 5.2400 rad/s |
| straight `x=0.08` | 7 / 8 | 0 / 8 | 0.0640 m/s | 49.40% | 5.2400 rad/s |

This tightens the conclusion:

```text
BEST_WALK proves closed-loop walking exists in this sim contract.
It does not prove stable in-envelope walking at the moving command cells tested.
At straight x=0.04, BEST_WALK stays inside the envelope but mostly stands.
At x=0.08 and the upstream nearest turning key, BEST_WALK walks but uses
right-knee target rates near the 5.24 rad/s slew ceiling.
```

So straight `x=0.04` should not be treated as the first proof-of-walking gate.
It is better interpreted as a no/low-motion posture cell unless a policy has
independently demonstrated walking there. Future training/eval work should
start mechanism extraction from command cells where BEST_WALK actually enters
single support, while explicitly reducing the right-knee rate mechanism that
keeps those cells outside the measured actuator envelope.

The first closed-loop template extraction now compares those command cells:

```text
outputs/analysis/PUBLISHED_POLICY_COMMAND_CLOSED_LOOP_TEMPLATE.md
status: PASS_HAS_LOW_RATE_MOVING_TEACHER_WINDOWS
```

Summary:

| command cell | mean vx | single support | moving in envelope | moving single in envelope | pitch p95 |
|---|---:|---:|---:|---:|---:|
| straight `x=0.04` | 0.0019 m/s | 3.65% | 4.65% | 1.25% | 2.3441 rad/s |
| upstream nearest turn | 0.0540 m/s | 44.80% | 63.70% | 28.90% | 4.9472 rad/s |
| straight `x=0.08` | 0.0640 m/s | 49.40% | 70.55% | 32.80% | 5.1961 rad/s |

This says the moving BEST_WALK traces contain useful low-rate subwindows, but
the full closed-loop behavior is still dominated by high right-knee target-rate
bursts. The next teacher/candidate source should mine those moving
single-support in-envelope windows and reject or relabel the right-knee burst
windows, rather than copying the whole policy trace.

A dedicated window miner then tested whether those low-rate ticks form
contiguous teacher snippets:

```text
tools/mine_closed_loop_teacher_windows.py
```

Result:

| window | artifact | status | passing windows |
|---|---|---|---:|
| 25 ticks / 0.50s | `outputs/analysis/CLOSED_LOOP_TEACHER_WINDOW_MINE.md` | `HOLD_INSUFFICIENT_CLOSED_LOOP_WINDOWS` | 0 / 1104 |
| 10 ticks / 0.20s | `outputs/analysis/CLOSED_LOOP_TEACHER_WINDOW_MINE_10T.md` | `PASS_CURATED_CLOSED_LOOP_WINDOWS_FOUND` | 142 / 2904 |

The 10-tick passes come mainly from the moving command cells:

```text
upstream nearest turning key: 76
straight x=0.08: 63
straight x=0.04: 3
```

This means BEST_WALK has brief envelope-safe moving single-support snippets,
but not sustained 0.5s envelope-safe teacher windows under these criteria. The
next source should mine the short snippets as phase/contact evidence and add a
continuity mechanism, not clone full traces or assume the short snippets are a
complete walking dataset.

The follow-up stitch planner tested that continuity assumption directly:

```text
tools/plan_closed_loop_snippet_stitching.py
outputs/analysis/CLOSED_LOOP_SNIPPET_STITCH_PLAN.md
status: HOLD_STITCH_RUNS_TOO_SHORT
```

Result:

| command cell | short pass windows | pass stitch runs | max passing stitch span |
|---|---:|---:|---:|
| upstream nearest turn | 76 | 55 | 12 ticks |
| straight `x=0.04` | 3 | 2 | 12 ticks |
| straight `x=0.08` | 63 | 27 | 18 ticks |

No trace produced a passing 25-tick or 50-tick stitch run. That means the
closed-loop snippets are usable as local contact/phase evidence, but they are
not a ready imitation dataset. A BC/export step needs a new continuity source
or closed-loop selector before it is meaningful.

The full-observation foot-position traces then made the command-cell mechanism
split more concrete:

```text
tools/analyze_published_policy_stance_timing.py
outputs/analysis/PUBLISHED_POLICY_STANCE_TIMING_COMPARISON.md
```

| command cell | mean vx | single support | single alternations | single dvx @ 0.1s | pitch p95 |
|---|---:|---:|---:|---:|---:|
| straight `x=0.04` | 0.0019 m/s | 3.65% | 1.50 | -0.0155 m/s | 0.8647 rad/s |
| straight `x=0.08` | 0.0640 m/s | 49.40% | 17.63 | 0.0030 m/s | 3.2849 rad/s |
| upstream nearest turn | 0.0540 m/s | 44.80% | 16.25 | 0.0042 m/s | 3.2396 rad/s |

Straight `x=0.04` should stay a posture/no-motion diagnostic, not the first
walking target. The published policy's walking mechanism appears in the moving
command cells: alternating single support plus a small positive future
forward-velocity delta during single support. Any imitation or selector branch
should preserve that closed-loop stance-transfer pattern while reducing the
high-rate pitch-chain bursts.

The first safe-vs-unsafe window contrast then compared full-observation
10-tick windows that pass the movement/contact/envelope gate against moving
windows rejected for high pitch-chain target rate:

```text
tools/analyze_closed_loop_window_rule_candidates.py
outputs/analysis/CLOSED_LOOP_WINDOW_RULE_CANDIDATES.md
status: PASS_RULE_CONTRAST_READY
```

| bucket | windows | mean vx | single support | pitch p95 | right knee p95 | action delta p95 |
|---|---:|---:|---:|---:|---:|---:|
| pass safe moving single | 330 | 0.0721 m/s | 46.79% | 3.2896 rad/s | 2.1407 rad/s | 0.1678 |
| reject high-rate moving | 1233 | 0.0667 m/s | 53.10% | 4.7046 rad/s | 4.0445 rad/s | 0.2053 |

So safe and unsafe moving windows are not separated by forward speed or single
support alone. They are separated by pitch-chain target-rate, with the
right-knee and left-knee counts dominating the fastest-pitch-joint tally. The
next selector needs to preserve stance transfer while explicitly rejecting or
reshaping knee-rate bursts.

The first knee-rate-aware selector manifest applied that filter and then checked
stance/phase coverage:

```text
tools/build_knee_rate_selector_manifest.py
outputs/analysis/KNEE_RATE_SELECTOR_MANIFEST.md
status: HOLD_SELECTOR_MISSING_STANCE_SIDE
```

Coverage:

```text
entries: 313
phase bins: 5 / 8
double-majority windows: 178
right-stance majority windows: 135
left-stance majority windows: 0
```

This is a useful negative result. The current safe BEST_WALK windows are not a
balanced selector source. The missing left-stance side must be recovered,
symmetry-augmented and verified, or replaced with a different closed-loop
mechanism source before BC/export.

A targeted left-stance gap analysis showed that the side is present but unsafe:

```text
tools/analyze_left_stance_gap.py
outputs/analysis/LEFT_STANCE_GAP_ANALYSIS.md
status: WARN_LEFT_STANCE_EXISTS_BUT_NOT_IN_SELECTOR
```

Key split:

| contact group | windows | pass | pitch p95 | right knee p95 | left knee p95 |
|---|---:|---:|---:|---:|---:|
| center left / majority left | 388 | 0 | 5.1021 rad/s | 5.0757 rad/s | 2.6358 rad/s |
| center right / majority right | 362 | 102 | 3.6390 rad/s | 1.9382 rad/s | 3.6082 rad/s |

The missing left-stance selector source is therefore a right-knee burst problem
during left support, not an absence of left contact. The next branch should
recover or mirror left stance with explicit right-knee rate verification.

The recovery probe then applied a right-knee-only target-rate cap offline and
re-scored the same left-related windows:

```text
tools/analyze_left_stance_rate_recovery.py
outputs/analysis/LEFT_STANCE_RATE_RECOVERY.md
status: PASS_RIGHT_KNEE_RELABEL_RECOVERS_LEFT_STANCE
```

Result:

```text
right_knee_cap: 3.61 rad/s
left-related windows: 553
original pass windows: 1
relabeled pass windows: 343
relabeled pass pct: 62.03%
```

This makes right-knee relabeling the next concrete offline path. The next
source should combine original safe right-stance windows with relabeled
left-stance windows, then score stance/phase coverage and 25-50 tick continuity
before any BC/export.

The combined source now passes the manifest coverage gate:

```text
tools/build_relabelled_balanced_selector_manifest.py
outputs/analysis/RELABELLED_BALANCED_SELECTOR_MANIFEST.md
status: PASS_BALANCED_SELECTOR_SOURCE_READY
```

Coverage:

```text
entries: 672
phase bins: 8 / 8
left_stance: 273
right_stance: 135
double: 264
right_knee_rate_cap relabelled entries: 343
original entries: 329
```

This is only a source gate. The relabeled windows have not been stepped in sim,
and the manifest is not a training dataset until a 25-50 tick continuity/replay
gate passes.

The offline continuity score now passes that first non-sim sequence gate:

```text
tools/score_relabelled_selector_continuity.py
outputs/analysis/RELABELLED_SELECTOR_CONTINUITY_SCORE.md
status: PASS_SELECTOR_CONTINUITY_50_TICKS
```

Result:

```text
runs: 101
pass runs: 98
max passing span: 96 ticks
pass runs >=25 ticks: 20
pass runs >=50 ticks: 11
pass runs using relabel: 92
```

This makes the relabeled selector source ready for a bounded sim replay
prototype. It still should not be used for BC/export until the relabeled spans
are stepped in sim and pass contact, target-rate, tracking, and stability gates.

The first bounded replay reached a useful hold:

```text
outputs/analysis/RELABELLED_SELECTOR_REPLAY_MANIFEST.md
outputs/analysis/RELABELLED_SELECTOR_SEQUENCE_REPLAY_TOP3_5S.md
status: HOLD_SEQUENCE_REPLAY_TERMINATED
```

The top-three relabeled spans complete on seed 0 with bounded forward motion
inside the target-rate envelope, but all three terminate on seed 1 before the
selected relabeled window. This keeps BC/export blocked. The next offline
branch should test state-aligned replay or a closed-loop selector that can
recover from reset-state variation.

The divergence audit confirms this is not a relabeled-window problem yet:

```text
outputs/analysis/RELABELLED_SELECTOR_REPLAY_DIVERGENCE.md
status: HOLD_REPLAY_DIVERGES_BEFORE_SELECTOR_WINDOW
```

The replay traces diverge from their source traces before the selected window,
usually at tick 0. The next branch should not tune the relabeled span itself
until replay can either state-align to the source or select actions closed-loop.

Exact state alignment is blocked by the current trace contract:

```text
outputs/analysis/SELECTOR_STATE_ALIGNMENT_REQUIREMENTS.md
status: HOLD_STATE_ALIGNMENT_TRACE_CONTRACT_INCOMPLETE
```

The source traces do not contain full `qpos`, `qvel`, base quaternion, control
state, or motor-target/action-history state. The next offline step should
regenerate source traces with those fields or build a selector that uses the
current closed-loop observation instead of static replay.

## Non-Goals

- robot tests
- SSH or deployment
- grounded replay
- training or retraining
- changing runtime behavior
- changing gains, offsets, remaps, phase timing, action scale, or policy files
