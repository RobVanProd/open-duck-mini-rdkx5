# Phase 2 Domain-Randomized Robustness Training

status: `HOLD_TASK_MATCHED_TRAINABLE_POLICY_MISSING`

## Objective

Harden the corrected-bridge Phase 1 candidate with curriculum domain
randomization while preserving:

- corrected actuator envelope compliance,
- command conditioning,
- `x=0.0` stillness,
- and the slow in-envelope `x=0.08` gait.

Robot validation is out of scope. No SSH, no deploy, no grounded replay.

## 2026-07-05 Trainable-Policy Branch Decision

The latest consolidated branch decision is:

```text
outputs/analysis/PHASE2_TRAINABLE_POLICY_BRANCH_DECISION.md
outputs/analysis/phase2_trainable_policy_branch_decision.json
```

Decision:

```text
HOLD_TASK_MATCHED_TRAINABLE_POLICY_MISSING
```

Phase 2 has in-envelope deployable walkers, but no current trainable PPO/DR
warm-start preserves the task-matched z=0.0075 rough-terrain intermediate-push
behavior. Long domain-randomization training should not launch until a
task-matched step-0 trainable policy clears that gate.

Current evidence:

- The deployable rate150 boundary candidate is useful but not promotable at the
  harder z=0.0075 intermediate-push boundary: `6/8` duration complete, `2/8`
  falls/terminations, mean track ratio `0.5622`, zero p95 corrected velocity
  excess.
- Iter24 is the latest useful live-oracle deployable analysis baseline: `4/5`
  compact z=0.0075 rough+push pass, with seed6 failing.
- Iter27 regressed the same BC-only live-oracle rung to `2/5`, so continuing
  that rung as-is is closed for now.
- Current PPO-compatible step-0 parents do not clear the task-matched gate:
  `limit198_step0` is `0/5`, `rate165_step0` is `0/5`, and the Iter24
  PPO-loc step0 is `2/5`.
- Full-observation trace analysis of the Iter24 PPO-loc step0 shows close
  manifest coverage and low nearest-action mismatch, so the regression is a
  closed-loop stability/representation issue rather than missing labels or
  local BC fit.

Required next condition before Phase 2 DR resumes: produce a trainable policy
class/objective whose step-0 export preserves the deployable behavior under the
canonical z=0.0075 rough+push corrected-bridge gate. Candidate next branches are
recurrent/hidden-state export, validation-aware mixture/ensemble diagnostics,
or PPO fine-tuning only after the task-matched behavior-preservation gate
passes.

## 2026-07-05 Policy Route Diagnostic

The first follow-up to the trainable-policy hold checked whether the existing
deployable candidates are complementary enough to justify a validation-aware
mixture/router branch:

```text
outputs/analysis/PHASE2_POLICY_ROUTE_DIAGNOSTIC.md
outputs/analysis/phase2_policy_route_diagnostic.json
```

Decision:

```text
PASS_ORACLE_ROUTE_EXISTS
```

The compact z=0.0075 rough+push seed set is oracle-coverable by existing
candidates:

- Iter24 passes seeds `0,1,2,7` and fails seed `6`.
- Iter25 passes seeds `1,2,6` and fails seeds `0,7`.
- Iter26 passes seed `6` only.
- Iter27 passes seeds `0,1` and regresses seeds `2,6,7`.

An oracle seed-level route covers seeds `0,1,2,6,7` with zero corrected
velocity-envelope excess. This is not deployable or trainable evidence because
seed id is not an allowed runtime input, but it establishes that the current
candidate family contains complementary behaviors. The next evidence-aligned
branch is therefore an offline observation/history-based router or mixture
diagnostic. It must select among existing candidates from available policy
observations/history, gate on the same z=0.0075 rough+push compact screen, and
only then produce rollouts for a trainable behavior-preservation target.

If no observation-based router clears the compact gate, skip further mixture
routing and move to a recurrent/hidden-state policy class or a different
optimization objective.

## 2026-07-05 Router Trace Readiness

Full-observation final-candidate traces were collected for the router branch:

```text
outputs/analysis/PHASE2_POLICY_ROUTE_TRACE_ITER24_27.md
outputs/analysis/phase2_policy_route_trace_iter24_27.json
outputs/analysis/PHASE2_POLICY_ROUTE_TRACE_ITER25_26.md
outputs/analysis/phase2_policy_route_trace_iter25_26.json
outputs/analysis/PHASE2_ROUTER_TRACE_READINESS.md
outputs/analysis/phase2_router_trace_readiness.json
```

Decision:

```text
PASS_ROUTER_TRACE_DATA_READY
```

The trace data covers final-candidate Iter24, Iter25, Iter26, and Iter27 over
the compact z=0.0075 rough+push seeds `0,1,2,6,7`, with full `obs_state` rows
and trace-file hashes recorded. The raw JSONL trace directories are local
analysis inputs and are large enough that this checkpoint commits the hashed
readiness report and compact sweep summaries rather than blindly adding the
entire trace corpus.

Next router work must remain offline and must not use seed id as a deployable
routing feature. The router has to choose from observation/history, pass the
same compact z=0.0075 rough+push gate, and only then generate a trainable
behavior-preservation target for Phase 2 DR.

## 2026-07-05 Observation Router Diagnostic

The offline observation/history router diagnostic was corrected to use the
trace directory policy labels (`iter24`, `iter25`, `iter26`, `iter27`) rather
than full ONNX paths when loading final-candidate trace rows:

```text
outputs/analysis/PHASE2_OBSERVATION_ROUTER_DIAGNOSTIC.md
outputs/analysis/phase2_observation_router_diagnostic.json
```

Decision:

```text
PASS_OBSERVATION_ROUTER_OFFLINE
```

The observation/history router improves over a single fixed candidate. The
expanded diagnostic checked prefixes `1,5,25,50,100,200` ticks and added a
non-seed pitch-health guard that penalizes candidates whose prefix body pitch
already exceeds `0.20 rad`. Best leave-one-seed-out result:

- prefix ticks: `100`
- kNN k: `3`
- policy-onehot scale: `5.0`
- pitch-guard scale: `1.0`
- pitch-guard limit: `0.20 rad`
- pass: `5/5`
- selected `iter24` for seeds `0,2,7`
- selected `iter25` for seeds `1,6`

The pitch guard is the difference between a near miss and a full offline route.
Without it, the best router picked failing `iter27` on seed `6` by a narrow
margin. With the guard, seed `6` switches to passing `iter25`:

- `iter27`: raw score `0.7268`, adjusted score `0.6793`, pitch excess
  `0.0475`, hold/fall, track ratio `0.9697`
- `iter25`: raw score `0.7246`, adjusted score `0.7024`, pitch excess
  `0.0222`, pass, track ratio `0.3273`

This is still diagnostic-only evidence. It does not justify launching Phase 2
DR yet, because the route has only been reconstructed from completed traces.
The next evidence-aligned work is an eval-only closed-loop router wrapper that
chooses among these candidate policies online without seed ID, using the same
100-tick prefix and pitch-health guard, then gates that wrapper on the
canonical z=0.0075 rough+push compact screen. Only if that online router gate
passes should it generate behavior-preservation rollouts for a trainable Phase
2 parent.

## 2026-07-05 Health-Gated Router Gate

The next router check applied the health-gated route to the final-candidate
full rollouts:

```text
outputs/analysis/PHASE2_HEALTH_GATED_ROUTER_GATE.md
outputs/analysis/phase2_health_gated_router_gate.json
```

Decision:

```text
PASS_HEALTH_GATED_ROUTER_COMPACT
```

This is an eval-only speculative router gate, not a deployable policy. It
treats the existing per-candidate traces as parallel prefix branches: score
each candidate from the first `100` ticks using leave-one-seed-out kNN plus the
prefix pitch guard, select a branch, then evaluate that selected branch's full
rollout. Seed ID is not used as a routing feature and the selected branch's
own pass/fail is not used during selection.

Result on compact z=0.0075 rough+push seeds:

| seed | selected policy | selected status | track ratio | mean vx |
|---:|---|---|---:|---:|
| `0` | `iter24` | `PASS_CANDIDATE_SIM_GATE` | `0.3256` | `0.0261` |
| `1` | `iter25` | `PASS_CANDIDATE_SIM_GATE` | `0.3567` | `0.0285` |
| `2` | `iter24` | `PASS_CANDIDATE_SIM_GATE` | `0.3278` | `0.0262` |
| `6` | `iter25` | `PASS_CANDIDATE_SIM_GATE` | `0.3273` | `0.0262` |
| `7` | `iter24` | `PASS_CANDIDATE_SIM_GATE` | `0.3437` | `0.0275` |

This reopens a narrow router/mixture path as a behavior-preservation target, but
it still does not authorize Phase 2 DR from the router itself. The next aligned
step is to use the selected branch traces to produce a single trainable
behavior-preserving parent, or to implement a true online parallel-prefix
wrapper only if the router behavior needs to be replayed without precomputed
traces.

## 2026-07-05 Health-Routed Parent Compression

The selected health-routed traces were converted into a compact BC manifest and
used to train two single-policy parents:

```text
outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_MANIFEST.md
outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_PPO_LOC.md
outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_GATE.md
outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_PHASE_MODULATED.md
outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_PHASE_MODULATED_GATE.md
outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_DECISION.md
```

Decision:

```text
HOLD_STATIC_PARENT_NOT_READY
```

The PPO-loc parent fit the labels but did not preserve the closed-loop behavior
under the compact z=0.0075 rough+push gate. The phase-modulated parent is much
better, passing seeds `0,1,2,6`, but seed `7` still fell at `300` samples with
reverse velocity. That makes it the best static compression attempt so far, but
not a valid Phase 2 domain-randomization warm start.

This result narrows the next branch: phase/context conditioning helps, but pure
static BC still leaves a seed-specific closed-loop failure. Phase 2 DR remains
blocked until live closed-loop correction or a memory/state policy clears the
compact behavior-preservation gate.

## 2026-07-05 Live-Correction Static Parent Check

The next check tested whether live-oracle relabeling on the student's own
visited states could rescue the static phase-modulated parent:

```text
outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_LIVE_CORRECTION_DECISION.md
outputs/analysis/phase2_health_routed_parent_live_correction_decision.json
```

Decision:

```text
HOLD_STATIC_PHASE_MODULATED_LIVE_CORRECTION
```

Two bounded live-correction attempts were run:

- focused seed-7 correction: seed `7` improved, but seed `1` regressed;
- full compact correction: aggregate manifest `3fbfc23526cdaaf6`, `8550`
  samples, but the retrained static parent regressed to `2/5` compact passes.

This closes the current static phase-modulated BC rescue path. Live relabeling
produces useful data, but compressing it back into the same static parent class
trades failures across seeds. The next branch should test observation history
or recurrent state before Phase 2 domain randomization resumes.

## 2026-07-05 Recurrent Parent Diagnostic

A stateful recurrent BC student was trained on the full compact live-oracle
aggregate:

```text
outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_RECURRENT_DECISION.md
outputs/analysis/phase2_health_routed_parent_recurrent_decision.json
```

Decision:

```text
HOLD_RECURRENT_BC_UNSTABLE
```

The recurrent export/fidelity smoke passed, but the compact gate failed `0/5`
with fast backward falls and p95 corrected velocity excess of `3.24 rad/s` on
every seed. Plain supervised recurrent BC is therefore worse than the static
phase-modulated parent and should not be pursued as another rate-only or
capacity-only tweak.

The next viable direction is a bounded history/online wrapper that preserves
the already-passing branch policies, or a later distillation path from such a
wrapper. Phase 2 DR remains blocked.

## 2026-07-05 Fresh Online Router Replay

The router branch was replayed from fresh branch rollouts rather than only the
earlier precomputed traces:

```text
outputs/analysis/PHASE2_ONLINE_ROUTER_FRESH_DECISION.md
outputs/analysis/phase2_online_router_fresh_decision.json
```

Decision:

```text
PASS_ONLINE_ROUTER_FRESH_COMPACT_SOURCE
```

Fresh Iter24/Iter25/Iter26/Iter27 rollouts confirmed the branch family still
contains compact-gate coverage. A two-branch `iter24,iter25` router held on
seed `6`, but the full four-branch prefix-health router selected passing
branches for all compact seeds:

```text
0 -> iter24
1 -> iter25
2 -> iter24
6 -> iter25
7 -> iter24
```

The selected fresh manifest is:

```text
outputs/analysis/phase2_online_router_fresh_selected_manifest.json
dataset_id: f2ecbdfab21ccafa
entries: 5
samples: 3750
```

This validates the router as an eval-only behavior-preservation source, but it
is still not a single deployable/trainable parent. Phase 2 DR remains blocked
until a parent or explicit wrapper objective preserves this routed behavior
under the compact corrected-bridge gate.

## 2026-07-05 Parent-Pair Lateral Student

The fresh router source was compressed into richer-context phase-modulated
parents. A first rich-context parent fit the fresh selected manifest cleanly
but only cleared `4/5` compact rough+push seeds:

```text
outputs/analysis/PHASE2_ONLINE_ROUTER_FRESH_RICH_CONTEXT_PARENT.md
outputs/analysis/PHASE2_ONLINE_ROUTER_FRESH_RICH_CONTEXT_PARENT_GATE.md
```

It fixed the old seed-`7` failure but regressed seed `1`. The previous
small-context phase-modulated parent was rerun with full traces and showed the
complementary pattern: seed `1` passed, seed `7` failed.

A lower-prefix-lateral parent-pair router selected passing source traces for all
compact seeds:

```text
outputs/analysis/PHASE2_ONLINE_ROUTER_PARENT_PAIR_LATERAL_METRIC_GATE.md
outputs/analysis/phase2_online_router_parent_pair_lateral_metric_gate.json
```

Those selected traces were converted into a manifest:

```text
outputs/analysis/phase2_online_router_parent_pair_lateral_selected_manifest.json
dataset_id: 6ccbb7ea49f243c6
entries: 5
samples: 3750
```

A seed-`7`-weighted rich-context student trained from that manifest became the
first single ONNX parent in this branch to clear the compact `x=0.08`
rough+push corrected-bridge gate:

```text
outputs/analysis/PHASE2_PARENT_PAIR_LATERAL_SEED7_WEIGHTED_STUDENT_DECISION.md
outputs/analysis/phase2_parent_pair_lateral_seed7_weighted_student_decision.json
```

Decision:

```text
HOLD_COMMAND_SEMANTICS_X0
```

Result:

- `x=0.08`: `5/5` compact seeds pass, zero corrected-envelope velocity excess.
- `x=0.0`: `3/5` compact seeds pass; seeds `1` and `6` fall, and pass seeds
  still drift forward.

This is meaningful progress but not a Phase 2 DR warm start. The parent
preserves the movement behavior at `x=0.08`, but it does not preserve command
semantics. Do not launch domain-randomized training from it until a
zero-command path or command-gated parent clears both compact gates.

## 2026-07-05 Command-Gated Compact Warm-Start

The zero-command blocker above was resolved with a deployable ONNX command gate:

```text
policy/candidates/phase2_parent_pair_lateral_seed7_weighted_command_gated_zero0020_20260705/candidate.onnx
sha256: f3d5d735e96cf88bfe037bd4c6c1289eebc5d25bcc7722416f62dcee292866d0
```

Routing:

```text
abs(obs[6]) <= 0.02 -> zero-action/home policy
abs(obs[6]) >  0.02 -> seed-7-weighted parent-pair lateral student
```

ONNX route verification passed with max action error `0.0`:

```text
outputs/analysis/phase2_parent_pair_lateral_seed7_weighted_command_gated_zero0020/onnx_gate_verify.json
```

The command-gated candidate passed the same compact corrected-bridge
rough+push screens:

```text
x=0.08: 5/5 pass, 0 falls, 0 velocity-envelope excess
x=0.0:  5/5 pass, 0 falls, mean vx 0.0008 m/s, 0 velocity-envelope excess
```

Decision artifact:

```text
outputs/analysis/PHASE2_PARENT_PAIR_LATERAL_SEED7_WEIGHTED_COMMAND_GATED_ZERO0020_DECISION.md
outputs/analysis/phase2_parent_pair_lateral_seed7_weighted_command_gated_zero0020_decision.json
```

This resolves `HOLD_COMMAND_SEMANTICS_X0` for the compact gate and makes the
command-gated candidate the next offline Phase 2 DR warm-start. It is still not
robot approval and does not complete the staged domain-randomization objective.

### Full-8 Source Gate Hold

The command-gated candidate was then checked against the full 8-seed
`x=0.08`, `z=0.0075`, rough-terrain intermediate-push screen:

```text
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_FULL8_SOURCE_DECISION.md
outputs/analysis/phase2_command_gated_zero0020_full8_source_decision.json
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_FULL8_X008_Z0075_PUSH_GATE.md
outputs/analysis/phase2_command_gated_zero0020_full8_x008_z0075_push_gate.json
```

Decision:

```text
HOLD_COMMAND_GATED_SOURCE_SEED5_FORWARD_LUNGE
```

Result:

```text
x=0.08 full 8-seed gate: 7/8 pass
failed seed: 5
mean track ratio: 0.4907
mean vx: 0.0393 m/s
max p95 corrected velocity excess: 0.0000 rad/s
max instantaneous corrected velocity excess: 0.0000 rad/s
```

Seed 5 was traced with full observations:

```text
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_SEED5_FAILURE_TRACE.md
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_SEED5_FAILURE_MODE.md
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_SEED5_TRACE_ANALYSIS.md
```

Seed-5 failure signature:

```text
mode: FORWARD_LUNGE_PITCHOVER / HEIGHT_COLLAPSE
samples: 158
track ratio: 1.7083
body pitch p95: 0.8743 rad
base height min: -0.0058 m
max pitch-chain sent-velocity p95: 1.5927 rad/s
p95 corrected velocity excess: 0.0000 rad/s
max corrected velocity excess: 0.0000 rad/s
first reverse tick: 45
first low-height tick: 150
first done tick: 157
```

The compact five-seed gate missed this seed-5 lunge/pitchover. The
command-gated ONNX remains a useful in-envelope behavior source, but it is not
full-stage robust and should not be treated as a completed Phase 2 source
without a seed-5 recovery branch or a router/wrapper source that covers seed 5.
Since the full `x=0.08` gate already fails, the full `x=0.0` gate was not rerun
for this decision.

### Rate160 z=0.0075 Intermediate-Push Transfer Hold

The earlier `phase_mod_rate160` candidate had passed a full `z=0.0026`
gentle-push screen, so it was re-tested against the actual hard boundary:
`x=0.08`, `z=0.0075`, rough terrain, intermediate pushes `0.075-0.125`,
corrected bridge, home-support reset, settle ticks `10`, seeds `0-7`.

Artifacts:

```text
outputs/analysis/PHASE2_RATE160_Z0075_INTERMEDIATE_PUSH_X008_FULL8_GATE.md
outputs/analysis/phase2_rate160_z0075_intermediate_push_x008_full8_gate.json
outputs/analysis/PHASE2_RATE160_Z0075_INTERMEDIATE_PUSH_X008_FULL8_DECISION.md
outputs/analysis/phase2_rate160_z0075_intermediate_push_x008_full8_decision.json
```

Decision:

```text
HOLD_RATE160_Z0075_INTERMEDIATE_PUSH_TARGET_VELOCITY_LOW_PROGRESS
```

Result:

```text
duration_complete: 8/8
falls: 0/8
HOLD_CANDIDATE_TARGET_VELOCITY: 7/8
HOLD_CANDIDATE_LOW_FORWARD_PROGRESS: 1/8
mean track ratio: 0.3218
mean vx: 0.0257 m/s
max p95 corrected velocity excess: 0.0000 rad/s
max instantaneous corrected velocity excess: 0.1379 rad/s
max tracking p95: 0.1935 rad
```

This candidate removes the command-gated source's seed-5 lunge/fall, but it
does so by trading into strict target-velocity holds and lower forward
progress. It is useful evidence that seed-5 stability exists, but it is not a
promotable Phase 2 source. Do not run `x=0.0` promotion gates for this
candidate unless a later wrapper removes the instantaneous envelope excess and
low-progress regression at `x=0.08`.

Seed 5 was then rerun with full-observation trace logging and compared against
the command-gated seed-5 lunge trace:

```text
outputs/analysis/PHASE2_RATE160_Z0075_INTERMEDIATE_PUSH_SEED5_TRACE.md
outputs/analysis/PHASE2_RATE160_Z0075_INTERMEDIATE_PUSH_SEED5_TRACE_ANALYSIS.md
outputs/analysis/PHASE2_COMMAND_GATED_VS_RATE160_SEED5_TRACE_COMPARE.md
outputs/analysis/PHASE2_COMMAND_GATED_VS_RATE160_SEED5_STABILITY_DECISION.md
```

Decision:

```text
PASS_SEED5_STABILITY_PATTERN_IDENTIFIED_NOT_PROMOTABLE
```

Comparison:

```text
command-gated seed5: 158 samples, vx 0.1367 m/s, abs pitch p95 0.8743, base height min -0.0058
rate160 seed5:       750 samples, vx 0.0282 m/s, abs pitch p95 0.1777, base height min 0.1577
common-window vx delta mean: -0.1076 m/s
common-window body-pitch delta mean: -0.1267 rad
first body-pitch divergence: tick 109
first base-height divergence: tick 145
```

This identifies a seed-5 stabilizing pattern but does not promote rate160.
The next source branch should transfer the anti-lunge/stability behavior into
the faster command-gated source without inheriting rate160's instantaneous
envelope excess or low-progress hold.

A narrow transfer dataset was prepared from that comparison:

```text
outputs/analysis/PHASE2_COMMAND_GATED_SEED5_RATE160_ANTILUNGE_RELABEL.md
outputs/analysis/phase2_command_gated_seed5_rate160_antilunge_relabel.json
outputs/analysis/PHASE2_COMMAND_GATED_SEED5_RATE160_ANTILUNGE_MANIFEST.md
outputs/analysis/phase2_command_gated_seed5_rate160_antilunge_manifest.json
outputs/analysis/PHASE2_COMMAND_GATED_SEED5_RATE160_ANTILUNGE_TRANSFER_DECISION.md
```

Decision:

```text
PASS_SEED5_RATE160_ANTILUNGE_TRANSFER_DATA_READY
```

The curation uses the existing early-lunge score definition
`obs[88,46,60,74,18]`, threshold `5.0`, and replaces selected command-gated
seed-5 failure actions with aligned rate160 seed-5 stable actions over ticks
`80-157`. It selected `24` samples, dataset id `aa55227d46236696`, with sample
weight `6.0`.

This is not a trained candidate. The next bounded step is to merge this
manifest into the command-gated/source data at low weight, train one student,
then gate seed 5 plus regression-control seeds before any full-8 rerun.

### Seed-5 Anti-Lunge Student Hold

The low-weight seed-5 anti-lunge transfer set was merged into the
command-gated source manifest and distilled into one PPO-loc MLP student:

```text
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_WITH_SEED5_RATE160_ANTILUNGE_MANIFEST.md
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_SEED5_RATE160_ANTILUNGE_PPO_LOC_BC_STUDENT.md
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_SEED5_RATE160_ANTILUNGE_STUDENT_X008_SEED0_5_7_GATE.md
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_SEED5_RATE160_ANTILUNGE_STUDENT_DECISION.md
```

Decision:

```text
HOLD_SEED5_ANTILUNGE_TRANSFER_REGRESSED
```

Result:

```text
merged dataset_id: b9d5821e5727ac77
fit status: PASS_PPO_LOC_BC_FIT_SMOKE
candidate ONNX sha256: 02ae0552547786aa975abaaed6a32e089751d72a958580eb26d031f107e65746
x=0.08 z=0.0075 rough+push seeds 0,5,7: 0/3 pass
falls: 3/3
seed 5: 153 samples, track ratio 1.6588, body pitch p95 0.8227, base height min 0.0091
seed 0: 686 samples, track ratio -0.0097, base height min 0.0814
seed 7: 488 samples, track ratio 0.7707, base height min -0.0014
max p95 corrected velocity excess: 0.0000 rad/s
max instantaneous corrected velocity excess: 1.4007 rad/s
```

The narrow transfer did not repair the target seed and also regressed both
regression-control seeds. Close this low-weight single-MLP transfer path. The
next source branch should change the preservation structure rather than add
another tiny seed-specific relabel: keep branch/router behaviors separate until
there is a better behavior-preserving parent, or use a stronger online
behavior-preservation objective before Phase 2 DR.

### Router-Family Seed-5 Coverage

After the low-weight anti-lunge compression failed, the existing router-family
candidates were screened directly on the newly exposed full-gate seed-5 failure:

```text
outputs/analysis/PHASE2_ROUTER_FAMILY_SEED5_Z0075_INTERMEDIATE_PUSH_SCREEN.md
outputs/analysis/phase2_router_family_seed5_z0075_intermediate_push_screen.json
outputs/analysis/PHASE2_ROUTER_FAMILY_SEED5_COVERAGE_DECISION.md
outputs/analysis/phase2_router_family_seed5_coverage_decision.json
```

Decision:

```text
PASS_ROUTER_FAMILY_SEED5_COVERAGE
```

Result under the same `x=0.08`, `z=0.0075`, rough-terrain,
intermediate-push, corrected-bridge screen:

```text
iter24: HOLD, 162 samples, track ratio 1.7128, body pitch p95 0.9002
iter25: PASS, 750 samples, track ratio 0.3924, body pitch p95 0.1779
iter26: PASS, 750 samples, track ratio 0.3765, body pitch p95 0.1668
iter27: PASS, 750 samples, track ratio 0.3461, body pitch p95 0.1729
velocity excess: 0.0000 p95 and 0.0000 instantaneous for all four rows
```

Seed 5 is covered by the branch family: `iter25`, `iter26`, and `iter27` all
complete it in envelope while `iter24` reproduces the lunge. The next useful
work is therefore an eval-only full-8 router/wrapper/source that keeps passing
branches separate long enough to cover all seeds, not another tiny seed-specific
single-MLP relabel.

### Full-8 Router Source Selected

The passing branch behavior was then materialized as full-observation source
traces:

```text
outputs/analysis/PHASE2_FULL8_ROUTER_SOURCE_COMMAND_GATED_TRACES.md
outputs/analysis/phase2_full8_router_source_command_gated_traces.json
outputs/analysis/PHASE2_FULL8_ROUTER_SOURCE_ITER25_SEED5_TRACE.md
outputs/analysis/phase2_full8_router_source_iter25_seed5_trace.json
outputs/analysis/PHASE2_FULL8_ROUTER_SOURCE_SELECTED_MANIFEST.md
outputs/analysis/phase2_full8_router_source_selected_manifest.json
outputs/analysis/PHASE2_FULL8_ROUTER_SOURCE_SELECTED_DECISION.md
outputs/analysis/phase2_full8_router_source_selected_decision.json
```

Decision:

```text
PASS_FULL8_ROUTER_SOURCE_SELECTED
```

Selected route:

```text
seeds 0,1,2,3,4,6,7 -> command_gated_zero0020
seed 5              -> iter25
```

Hard-screen result:

```text
x=0.08 z=0.0075 rough+push selected source: 8/8 pass
falls: 0
mean vx: 0.0261 m/s
mean track ratio: 0.3262
max body pitch p95: 0.1917 rad
min base height: 0.1581 m
max p95 corrected velocity excess: 0.0000 rad/s
max instantaneous corrected velocity excess: 0.0000 rad/s
manifest dataset_id: e395c159e077d118
manifest entries/samples: 8 / 6000
```

This is the current best full-8 behavior-preservation source, but it is not a
deployable runtime policy because the route is assembled from evaluated seed
coverage. Use it as the next behavior-preservation target. Phase 2 DR remains
blocked until a trainable parent or a deployable/eval-safe wrapper preserves
this behavior and also clears the `x=0.0` command-semantics gate.

### Full-8 Rich-Context Parent Hold

The selected full-8 source was compressed into a larger phase-modulated
rich-context parent:

```text
outputs/analysis/PHASE2_FULL8_ROUTER_SOURCE_RICH_CONTEXT_PARENT.md
outputs/analysis/phase2_full8_router_source_rich_context_parent.json
outputs/analysis/PHASE2_FULL8_ROUTER_SOURCE_RICH_CONTEXT_PARENT_X008_SEED0_5_7_GATE.md
outputs/analysis/phase2_full8_router_source_rich_context_parent_x008_seed0_5_7_gate.json
outputs/analysis/PHASE2_FULL8_ROUTER_SOURCE_RICH_CONTEXT_PARENT_DECISION.md
outputs/analysis/phase2_full8_router_source_rich_context_parent_decision.json
```

Decision:

```text
HOLD_FULL8_RICH_CONTEXT_PARENT_SEED5_LUNGE
```

The static parent fit the selected source cleanly:

```text
candidate sha256: 9891f1927ab3f6e8c6a6c9a2dfcfb0fe06873a26c068840f1c1b818360a75fe1
samples: 6000
MAE: 0.001977
p95 abs error: 0.005375
target-rate p95: 1.4451 rad/s
target-rate max: 1.8839 rad/s
ONNX max abs error: 0.00000030
```

The hard `x=0.08`, `z=0.0075`, rough-terrain, intermediate-push,
corrected-bridge screen over seeds `0,5,7` did not preserve the seed-5
stabilizing branch:

```text
seed 0: PASS, 750 samples, track_ratio 0.3306, body pitch p95 0.2130
seed 5: HOLD, 149 samples, track_ratio 1.7761, body pitch p95 0.8855, base min 0.0014
seed 7: PASS, 750 samples, track_ratio 0.3468, body pitch p95 0.1729
velocity excess: 0.0000 p95 and 0.0000 instantaneous
```

Do not promote this parent and do not launch Phase 2 domain randomization from
it. The selected-source route works as separate branch behavior, but static
rich-context compression still collapses the seed-5 branch into a lunge. The
next valid step is an explicit branch-preserving wrapper/router objective or a
trainable mixture that keeps the seed-5 behavior separate through the gate, not
another static BC compression.

### Full-8 Recurrent BC Hold

The same selected full-8 source was then fit with a stateful recurrent BC
student to test whether explicit hidden state preserves the routed branch
behavior that the static parent lost:

```text
outputs/analysis/PHASE2_FULL8_ROUTER_SOURCE_RECURRENT_H128_S64_RATE2P0.md
outputs/analysis/phase2_full8_router_source_recurrent_h128_s64_rate2p0.json
outputs/analysis/PHASE2_FULL8_ROUTER_SOURCE_RECURRENT_H128_S64_RATE2P0_X008_SEED0_5_7_GATE.md
outputs/analysis/phase2_full8_router_source_recurrent_h128_s64_rate2p0_x008_seed0_5_7_gate.json
outputs/analysis/PHASE2_FULL8_ROUTER_SOURCE_RECURRENT_H128_S64_RATE2P0_DECISION.md
outputs/analysis/phase2_full8_router_source_recurrent_h128_s64_rate2p0_decision.json
```

Decision:

```text
HOLD_FULL8_RECURRENT_BC_REVERSES_AND_SATURATES
```

The recurrent fit was acceptable as a supervised/export smoke:

```text
candidate sha256: 6fe1713ab1de5c4480a964b4a2e9b3d119f9b905f235c97806a8298e6b8a6b56
hidden_dim / sequence_length: 128 / 64
samples: 6000
MAE: 0.009001
p95 abs error: 0.022976
target-rate p95: 1.4556 rad/s
target-rate max: 2.3151 rad/s
ONNX max action error: 0.00000056
```

Closed-loop behavior was worse than the static rich-context parent. Under the
same hard `x=0.08`, `z=0.0075`, rough-terrain, intermediate-push,
corrected-bridge screen over seeds `0,5,7`, every seed fell at 63 samples:

```text
seed 0: HOLD, 63 samples, vx -0.2476 m/s, track_ratio -3.0944
seed 5: HOLD, 63 samples, vx -0.2461 m/s, track_ratio -3.0761
seed 7: HOLD, 63 samples, vx -0.2467 m/s, track_ratio -3.0841
pitch-chain p95 velocity excess: 3.2400 rad/s
instantaneous velocity excess: 3.2400 rad/s
```

Do not continue supervised-only recurrent compression on this source. Hidden
state alone did not preserve the branch behavior; it drove the policy into
reverse motion and the simulator slew ceiling. The next valid branch remains an
explicit branch-preserving wrapper/router or trainable mixture with closed-loop
validation pressure.

### Full-8 Obs-Linear Router Separability Hold

An ONNX packaging helper was added for future branch-preserving experiments:

```text
tools/compose_obs_linear_gated_onnx_policy.py
```

It composes two stateless policies behind a live observation-linear branch gate
while preserving the deployed contract:

```text
obs[1,101] -> continuous_actions[1,14]
```

Before composing the current selected branches, a separability diagnostic tested
whether the seed-5 `iter25` branch is linearly distinguishable from the
command-gated branch in stateless observation space:

```text
tools/report_phase2_full8_obs_linear_router_separability.py
outputs/analysis/PHASE2_FULL8_OBS_LINEAR_ROUTER_SEPARABILITY.md
outputs/analysis/phase2_full8_obs_linear_router_separability.json
```

Decision:

```text
HOLD_OBS_LINEAR_ROUTER_OVERLAP
```

Result:

```text
positive branch samples: 750
negative branch samples: 5250
positive selected: 62.00%
negative false selected: 56.59%
balanced accuracy: 52.70%
```

Do not build the current two-policy router with a stateless linear observation
gate. It would select the seed-5 branch on too many non-seed-5 states and is
therefore not a credible Phase 2 warm-start. The next router attempt needs a
nonlinear mixture/gate with closed-loop validation pressure, or a stateful
prefix router with an explicit runtime/eval contract.

### Full-8 MLP Router Candidate Hold

A nonlinear stateless observation gate was then tested:

```text
tools/report_phase2_full8_mlp_router_separability.py
tools/compose_obs_mlp_gated_onnx_policy.py
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEPARABILITY.md
outputs/analysis/phase2_full8_mlp_router_separability.json
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_CANDIDATE_X008_SEED0_5_7_GATE.md
outputs/analysis/phase2_full8_mlp_router_candidate_x008_seed0_5_7_gate.json
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_CANDIDATE_DECISION.md
outputs/analysis/phase2_full8_mlp_router_candidate_decision.json
```

Decision:

```text
HOLD_FULL8_MLP_ROUTER_SEED0_REGRESSION
```

The MLP gate separated source labels on a held-out per-trace split:

```text
test balanced accuracy: 95.81%
test positive selected: 94.67%
test negative false selected: 3.05%
gate_npz_sha256: 8192fc152205635f4ccdbd1d9972944659bca4782bf8dfe43241ae6228fc45c0
composed_candidate_sha256: 6251a528b878fbfa3637727bd6d8463cd08b291556b285fbfe3cfab40ede5697
```

The composed ONNX preserved the fixed deployed contract and verified exactly,
but the hard closed-loop screen over seeds `0,5,7` was only `2/3`:

```text
seed 0: HOLD, 321 samples, vx -0.0352 m/s, track_ratio -0.4394, base min 0.0705
seed 5: PASS, 750 samples, vx 0.0312 m/s, track_ratio 0.3897
seed 7: PASS, 750 samples, vx 0.0285 m/s, track_ratio 0.3556
velocity excess: 0.0000 p95 and 0.0000 instantaneous
```

This is the first stateless branch-preserving candidate that preserves the
seed-5 branch under the hard screen, but it is still not a Phase 2 DR warm-start
because it regresses seed 0. The next router attempt should keep the nonlinear
MLP-gate direction, but train the gate with closed-loop validation pressure or a
branch-cost objective rather than source-label classification alone.

The failed seed-0 rollout was then rerun with full observation tracing and the
saved MLP gate replayed over the trace:

```text
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_CANDIDATE_SEED0_TRACE_GATE.md
outputs/analysis/phase2_full8_mlp_router_candidate_seed0_trace_gate.json
tools/report_phase2_mlp_router_branch_trace.py
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_BRANCH_TRACE.md
outputs/analysis/phase2_full8_mlp_router_seed0_branch_trace.json
```

Decision:

```text
HOLD_ROUTER_STARTUP_BRANCH_B_ON_FAILED_TRACE
```

The seed-0 failure is not random branch churn. The MLP gate selects branch B
for `100%` of the first `80` ticks on seed 0, then flips mostly back to branch A
near the fall:

```text
all ticks branch B: 47.35%
first 80 ticks branch B: 100.00%
tail 80 ticks branch B: 3.75%
mean vx: -0.0352 m/s
base min: 0.0705 m
body pitch abs p95: 0.4680 rad
```

Next router training should penalize seed-0 startup branch-B selection directly
or use prefix validation pressure. Source-label classification alone is too
weak because it learns a gate that looks good on held-out trace labels but
fails the closed-loop seed-0 startup.

### Full-8 MLP Router Seed0 Startup-Cost Hold

The MLP-router classifier was extended to accept corrective traces:

```text
tools/report_phase2_full8_mlp_router_separability.py
  --extra-negative-trace
  --extra-negative-first-ticks
  --extra-negative-weight
```

The failed seed-0 trace from the prior MLP-router candidate was added as a
branch-A correction over the first `80` ticks with weight `50.0`:

```text
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_STARTUP_COST_SEPARABILITY.md
outputs/analysis/phase2_full8_mlp_router_seed0_startup_cost_separability.json
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_STARTUP_COST_X008_SEED0_5_7_GATE.md
outputs/analysis/phase2_full8_mlp_router_seed0_startup_cost_x008_seed0_5_7_gate.json
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_STARTUP_COST_DECISION.md
outputs/analysis/phase2_full8_mlp_router_seed0_startup_cost_decision.json
```

Decision:

```text
HOLD_FULL8_MLP_ROUTER_SEED0_FIX_REGRESSES_SEED5
```

The corrected classifier still passed the held-out separability thresholds:

```text
test balanced accuracy: 87.14%
test positive selected: 76.67%
test negative false selected: 2.38%
gate_npz_sha256: e663f806af55dde33295b169a445551515d8435da82b623738523fb2904f4861
candidate_sha256: b4a7e338eae789803ad132459df9e1b1b98c36172bed5845f8bbeff10fcaab36
```

The composed ONNX verified exactly, but the hard closed-loop screen over seeds
`0,5,7` was again only `2/3`:

```text
seed 0: PASS, 750 samples, vx 0.0298 m/s, track_ratio 0.3721, base min 0.1581
seed 5: HOLD, 158 samples, vx 0.1298 m/s, track_ratio 1.6227, base min 0.0149
seed 7: PASS, 750 samples, vx 0.0275 m/s, track_ratio 0.3438, base min 0.1581
velocity excess: 0.0000 p95 and 0.0000 instantaneous
```

This correction fixed the previous seed-0 regression, but it shifted the
closed-loop failure to seed 5. The router boundary is therefore movable, but a
one-sided scalar corrective trace is not a promotable solution. The next
router attempt needs a multi-constraint closed-loop-aware objective that keeps
seed 0 startup on branch A while preserving seed 5 startup/trajectory on
branch B. Do not start Phase 2 domain-randomization training until the
composed deployable candidate clears the canonical corrected-bridge gate.

### Full-8 MLP Router Seed0/Seed5 Startup-Cost Wide Hold

The failed seed-5 rollout from the seed0-startup-cost router was rerun with
full-observation tracing and replayed through the saved gate:

```text
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_STARTUP_COST_SEED5_TRACE_GATE.md
outputs/analysis/phase2_full8_mlp_router_seed0_startup_cost_seed5_trace_gate.json
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_STARTUP_COST_SEED5_BRANCH_TRACE.md
outputs/analysis/phase2_full8_mlp_router_seed0_startup_cost_seed5_branch_trace.json
```

The seed-5 trace showed the opposite startup error from seed 0:

```text
seed 5: HOLD, 158 samples, vx 0.1298 m/s, track_ratio 1.6227, base min 0.0149
all ticks branch B: 25.95%
first 80 ticks branch B: 0.00%
tail 80 ticks branch B: 51.25%
single-support branch B: 70.00%
double-support branch B: 18.98%
```

The router diagnostic was then extended to accept branch-B corrective traces:

```text
--extra-positive-trace
--extra-positive-first-ticks
--extra-positive-weight
```

A narrow symmetric `128,64` gate using seed 0 as branch-A correction and seed 5
as branch-B correction failed held-out separability:

```text
status: HOLD_MLP_ROUTER_OVERLAP
test balanced accuracy: 79.24%
test positive selected: 66.00%
test negative false selected: 7.52%
```

A wider `256,128,64` gate passed the trace-label thresholds:

```text
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_SEPARABILITY.md
outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_separability.json
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_X008_SEED0_5_7_GATE.md
outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_x008_seed0_5_7_gate.json
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_DECISION.md
outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_decision.json
```

Decision:

```text
HOLD_FULL8_MLP_ROUTER_SEED5_CLOSED_LOOP_LUNGE
```

The wide gate and composed ONNX verified:

```text
test balanced accuracy: 88.52%
test positive selected: 80.67%
test negative false selected: 3.62%
gate_npz_sha256: 1492635af6ca5a4c0a1b7d39077f29ec58bf3eae6fb4bb9f262e74ed3c07d36e
candidate_sha256: 29e9e05cf877c6ead2ae1e05e5d27c32faec1adc75122d516b6db679c9786f6c
onnx_verify_sha256: aa20259c72fc4c1b0b4e844059e8834f574312cd74c2544e8556de95ba7a54d0
```

The hard closed-loop screen remained `2/3`:

```text
seed 0: PASS, 750 samples, vx 0.0268 m/s, track_ratio 0.3348, base min 0.1591
seed 5: HOLD, 161 samples, vx 0.1296 m/s, track_ratio 1.6196, base min 0.0132
seed 7: PASS, 750 samples, vx 0.0254 m/s, track_ratio 0.3178, base min 0.1572
velocity excess: 0.0000 p95 and 0.0000 instantaneous
```

This closes the simple label-weighting variant: a wide stateless MLP gate can
fit the seed-0/seed-5 startup labels, but source-label classification still
does not produce stable closed-loop seed-5 behavior. The next attempt needs
rollout-level costs, a stateful/prefix router, or another closed-loop-aware
router objective. Do not promote another stateless source-label router solely
because its held-out branch labels separate.

### Full-8 MLP Router Threshold Tradeoff Hold

The wide symmetric gate's seed-5 failure was traced and replayed:

```text
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_SEED5_TRACE_GATE.md
outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_seed5_trace_gate.json
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_SEED5_BRANCH_TRACE.md
outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_seed5_branch_trace.json
```

The wide gate selected branch B for only `21.25%` of the first `80` seed-5
ticks. A single threshold diagnostic was therefore run at `threshold=-2.0`:

```text
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_TNEG2_X008_SEED5_GATE.md
outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_tneg2_x008_seed5_gate.json
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_TNEG2_X008_SEED0_7_GATE.md
outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_tneg2_x008_seed0_7_gate.json
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_TNEG2_DECISION.md
outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_tneg2_decision.json
```

Decision:

```text
HOLD_FULL8_MLP_ROUTER_THRESHOLD_TRADEOFF
```

Result:

```text
seed 5: PASS, 750 samples, vx 0.0316 m/s, track_ratio 0.3947, base min 0.1580
seed 0: HOLD, 166 samples, vx 0.1265 m/s, track_ratio 1.5808, base min 0.0083
seed 7: PASS, 750 samples, vx 0.0352 m/s, track_ratio 0.4396, base min 0.1562
velocity excess: 0.0000 p95 and 0.0000 instantaneous
```

Lowering the threshold fixes seed 5 but regresses seed 0 into the same lunge
and fall signature. This means the issue is not a global branch-B amount. It is
a seed/state-specific routing conflict that a scalar threshold cannot solve.
The next attempt should be closed-loop-aware or stateful/prefix-conditioned,
not another scalar threshold sweep.

### Full-8 MLP Router Live-Corrected Iter2 Hold

The `threshold=-2` seed-0 regression was rerun with full-observation tracing:

```text
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_TNEG2_SEED0_TRACE_GATE.md
outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_tneg2_seed0_trace_gate.json
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_TNEG2_SEED0_BRANCH_TRACE.md
outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_tneg2_seed0_branch_trace.json
```

A live-corrected iter2 stateless MLP gate was trained with:

```text
branch-A correction: prior seed-0 MLP-router failure, first 80 ticks, weight 50
branch-A correction: threshold=-2 seed-0 failure, first 80 ticks, weight 50
branch-B correction: seed-5 failure trace from seed0-startup-cost router, first 80 ticks, weight 50
```

Artifacts:

```text
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_LIVE_CORRECTED_ITER2_SEPARABILITY.md
outputs/analysis/phase2_full8_mlp_router_live_corrected_iter2_separability.json
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_LIVE_CORRECTED_ITER2_X008_SEED0_5_7_GATE.md
outputs/analysis/phase2_full8_mlp_router_live_corrected_iter2_x008_seed0_5_7_gate.json
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_LIVE_CORRECTED_ITER2_DECISION.md
outputs/analysis/phase2_full8_mlp_router_live_corrected_iter2_decision.json
```

Decision:

```text
HOLD_FULL8_MLP_ROUTER_LIVE_CORRECTION_REGRESSES_SEED7
```

The live-corrected gate still passed held-out source-label separability:

```text
test balanced accuracy: 88.43%
test positive selected: 80.00%
test negative false selected: 3.14%
gate_npz_sha256: 3e7d6797065d690acfa0217ffd8cce7dc2847aa8a5ba6aba2dc6fa9b6ea88615
candidate_sha256: 7192c7b193100ac60ad6a44d9167aa1337d24cde17a0e50a8a0662f78eaba6d9
onnx_verify_sha256: 95ad864bf5e2c747a8dc4cc392616e42c9518d896be4986d5195380d689343ec
```

The closed-loop screen regressed:

```text
seed 0: PASS, 750 samples, vx 0.0252 m/s, track_ratio 0.3149, base min 0.1588
seed 5: HOLD, 169 samples, vx 0.1257 m/s, track_ratio 1.5711, base min 0.0100
seed 7: HOLD, 605 samples, vx 0.0549 m/s, track_ratio 0.6863, base min 0.0106
velocity excess: 0.0000 p95 and 0.0000 instantaneous
```

This closes the stateless MLP-router label-correction sub-branch. Adding
closed-loop failure labels can move which seed fails, but it does not create a
stable deployable router. The next valid branch is a stateful/prefix router or
trainable closed-loop mixture with rollout-level cost, not more source-label or
single-threshold correction.

### Full-8 Router Threshold -1.8 Warm-Start Pass

The threshold probes bracketed the router conflict:

```text
threshold  0.0: seed 0 PASS, seed 5 HOLD, seed 7 PASS
threshold -2.0: seed 0 HOLD, seed 5 PASS, seed 7 PASS
```

The seed-0/seed-5 startup logit traces suggested a narrow midpoint. A targeted
`threshold=-1.8` candidate was composed and screened:

```text
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_TNEG1P8_X008_SEED0_5_7_GATE.md
outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8_x008_seed0_5_7_gate.json
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_TNEG1P8_X008_FULL8_GATE.md
outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8_x008_full8_gate.json
outputs/analysis/PHASE2_FULL8_MLP_ROUTER_SEED0_SEED5_STARTUP_COST_WIDE_TNEG1P8_X000_FULL8_GATE.md
outputs/analysis/phase2_full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8_x000_full8_gate.json
outputs/analysis/PHASE2_FULL8_ROUTER_TNEG1P8_CANDIDATE_DECISION.md
outputs/analysis/phase2_full8_router_tneg1p8_candidate_decision.json
```

Decision:

```text
PASS_PHASE2_ROUTER_WARMSTART_SIM_GATE
```

Candidate package:

```text
policy/candidates/phase2_full8_router_tneg1p8_20260705/candidate.onnx
sha256: f3e88820b87025788c97636599cd2caf6ef249f7cb7e50ddde31ff5c1c5457d0
package status: READY_FOR_SIM_GATE_REVIEW
```

The `x=0.08` corrected-bridge rough/push full-8 gate passed:

```text
8/8 PASS, 0 falls
mean vx: 0.0276 m/s
mean track ratio: 0.3456
mean body pitch p95: 0.1859 rad
mean base height min: 0.1580 m
p95 velocity excess: 0.0000 rad/s
max velocity excess: 0.0000 rad/s
```

The `x=0.0` command-preservation gate also passed:

```text
8/8 PASS, 0 falls
mean vx: 0.0007 m/s
double support: 100%
p95 velocity excess: 0.0000 rad/s
max velocity excess: 0.0000 rad/s
```

This is the current offline Phase 2 warm-start candidate. It is slow and not
robot-approved, but it clears the corrected-bridge x=0.08 and x=0.0 full-8
rough/push gates required before domain-randomized robustness work can resume.
Next offline step: start narrow DR from this candidate and preserve these two
gates at every stage.

### Full-8 Router Trainable Conversion Hold

Before launching domain-randomized PPO, the router candidate was tested as a
source for a PPO-compatible trainable warm-start. The router itself is an ONNX
composition, not an Orbax checkpoint, so it cannot be passed directly to the
Playground PPO restore path.

Full-observation traces were regenerated from the router:

```text
outputs/analysis/PHASE2_FULL8_ROUTER_TNEG1P8_TRACE_X008.md
outputs/analysis/phase2_full8_router_tneg1p8_trace_x008.json
outputs/analysis/PHASE2_FULL8_ROUTER_TNEG1P8_TRACE_X000.md
outputs/analysis/phase2_full8_router_tneg1p8_trace_x000.json
```

Both trace sweeps preserved the router gates:

```text
x=0.08: 8/8 PASS, 0 falls, mean vx 0.0276 m/s, velocity excess 0
x=0.0:  8/8 PASS, 0 falls, mean vx 0.0007 m/s, velocity excess 0
```

A compact BC manifest was built from the 16 traces:

```text
outputs/analysis/PHASE2_FULL8_ROUTER_TNEG1P8_BC_TRACE_MANIFEST.md
outputs/analysis/phase2_full8_router_tneg1p8_bc_trace_manifest.json
```

Two PPO-loc BC students were trained from that data:

```text
unweighted:
  fit p95 action error: 0.004127
  x=0.08 gate: 6/8 PASS, seeds 5 and 6 fell

seed56_weighted:
  fit p95 action error: 0.004912
  x=0.08 gate: 6/8 PASS, seeds 5 and 6 fell
```

Decision:

```text
HOLD_TRAINABLE_ROUTER_COMPRESSION_NOT_PROMOTABLE
```

Evidence:

```text
outputs/analysis/PHASE2_FULL8_ROUTER_TNEG1P8_TRAINABLE_CONVERSION_DECISION.md
outputs/analysis/phase2_full8_router_tneg1p8_trainable_conversion_decision.json
```

Do not launch domain-randomized PPO from either PPO-loc student. The current
router source remains useful and in-envelope, but a single memoryless PPO-loc
compression has not preserved the full-8 x=0.08 rough/push gate. The next
aligned trainable-warm-start branch needs a branch-aware/stateful conversion
or online DAgger using the captured full-observation router traces.

### Trainable Compression Hold

The command-gated ONNX was distilled into PPO-compatible single-MLP students
using the compact `x=0.08` and `x=0.0` traces as labels:

```text
outputs/analysis/phase2_command_gated_zero0020_bc_manifest.json
dataset_id: 24beb17ef0e1de02
samples: 7500
```

The unweighted PPO-loc MLP fit the labels well and preserved zero command, but
did not preserve the moving branch:

```text
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_PPO_LOC_BC_STUDENT.md
x=0.08 compact gate: 3/5 pass, failed seeds 0 and 7
x=0.0 compact gate: 5/5 pass
```

A bounded seed-0/7 weighted refit recovered seed 7 but moved the failure to
seed 2:

```text
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_SEED07_WEIGHTED_PPO_LOC_BC_STUDENT.md
x=0.08 compact gate: 3/5 pass, failed seeds 0 and 2
```

Decision:

```text
HOLD_TRAINABLE_COMPRESSION_MOVING_GATE
```

The graph-level command gate is the current compact eval candidate, but Phase 2
still lacks a PPO-compatible trainable warm-start checkpoint. Do not launch DR
training from the single-MLP compressions.

### Live-Oracle PPO-Loc Compression Hold

The failed PPO-loc compression was then used as the student in focused
live-oracle DAgger passes. These were offline only: the student was rolled out
through the corrected-bridge rough+push compact screen, student-visited states
were relabeled by the corrected command-gated teacher/oracle, and PPO-loc MLPs
were retrained from the aggregate manifests.

Iteration 1 targeted the original moving failures (`seed 0` and `seed 7`) and
preserved two zero-command traces:

```text
outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter1/LIVE_ORACLE_DAGGER_ITERATION.md
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_LIVE_ORACLE_ITER1_PPO_LOC_BC_STUDENT.md
x=0.08 compact gate: 4/5 pass, failed seed 6
x=0.0 compact gate: 5/5 pass
```

Iteration 2 targeted the remaining `seed 6` moving failure:

```text
outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2/LIVE_ORACLE_DAGGER_ITERATION.md
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_LIVE_ORACLE_ITER2_PPO_LOC_BC_STUDENT.md
x=0.08 compact gate: 4/5 pass, failed seed 6
```

Decision:

```text
HOLD_LIVE_ORACLE_PPO_LOC_SEED6_MOVING_GATE
```

Live-oracle correction improved the trainable compression from `3/5` to `4/5`
and preserved command semantics, but repeating the same single-MLP PPO-loc
correction did not close the moving gate. Phase 2 still lacks a trainable
warm-start checkpoint; do not launch domain-randomized PPO from these students.

Seed-6 analysis:

```text
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_LIVE_ORACLE_ITER2_SEED6_TRACE_ANALYSIS.md
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_LIVE_ORACLE_ITER2_SEED_MODE_ANALYSIS.md
```

The remaining seed-6 failure is `REVERSE_HEIGHT_COLLAPSE`: reverse motion starts
at tick `44`, low height occurs at tick `338`, and termination occurs at tick
`340`. Passing seeds and seed 6 have similar early action magnitude and
pitch-chain target velocity, so this is not just a globally quiet seed or an
envelope-excess issue. The next trainable-warm-start branch should inspect the
seed-6 state/phase branch behavior or move to a representation with stronger
branch/phase structure, rather than launch DR or repeat scalar weighting.

### Phase/Contact-Modulated Representation Hold

The next representation rung trained a shared-trunk phase/contact-modulated BC
student from the live-oracle iter2 aggregate while preserving the deployed ONNX
contract:

```text
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_LIVE_ORACLE_ITER2_PHASE_CONTACT_MODULATED_BC_STUDENT.md
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_LIVE_ORACLE_ITER2_PHASE_CONTACT_MODULATED_BC_STUDENT_X008_GATE.md
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_LIVE_ORACLE_ITER2_PHASE_CONTACT_MODULATED_DECISION.md
```

Decision:

```text
HOLD_PHASE_CONTACT_MODULATED_MOVING_GATE
```

The student used context indices `[6,97,98,99,100]` for command, foot-contact,
and phase modulation. It fit the labels cleanly (`p95 abs error 0.009653`,
ONNX max action error `6e-8`) and stayed inside the corrected velocity envelope,
but failed the canonical compact moving gate:

```text
x=0.08 compact z=0.0075 rough+push gate: 2/5 pass
passes: seeds 1,7
falls: seeds 0,2,6
p95 corrected velocity excess: 0 on all seeds
```

The failed seeds are lunge/fall failures rather than quiet or over-envelope
failures: seeds `0`, `2`, and `6` reach track ratios `1.41-1.68` before
falling, with body pitch p95 `0.72-0.91 rad`. Do not run the zero-command gate
or launch DR from this student; the moving gate already rejects it.

This closes the simple feed-forward phase/contact modulation rung for the
current live-oracle iter2 aggregate. The remaining trainable-parent gap is a
closed-loop stability/branching problem, not target-rate compliance or local BC
fit. The next branch should use a stronger branch-aware structure,
recurrent/hidden-state export, or an on-policy objective that directly
preserves the compact rough+push closed-loop gate.

### Recurrent BC Representation Hold

A bounded stateful recurrent BC diagnostic was then trained from the same
live-oracle iter2 aggregate:

```text
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_LIVE_ORACLE_ITER2_RECURRENT_H64_S32_BC_STUDENT.md
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_LIVE_ORACLE_ITER2_RECURRENT_H64_S32_BC_STUDENT_X008_GATE.md
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_LIVE_ORACLE_ITER2_RECURRENT_H64_S32_DECISION.md
```

Decision:

```text
HOLD_RECURRENT_BC_OVER_ENVELOPE_COLLAPSE
```

The recurrent contract was:

```text
obs[1,101], h_in[1,64] -> continuous_actions[1,14], h_out[1,64]
```

The fit smoke and ONNX fidelity passed, but the compact moving gate failed
decisively:

```text
x=0.08 compact z=0.0075 rough+push gate: 0/5 pass
all seeds fall at 57 samples
mean local vx: -0.3345 m/s
mean track ratio: -4.1817
max pitch-chain p95 velocity: 5.2400 rad/s
corrected p95 velocity excess: 3.2400 rad/s
max tracking p95: 0.2746 rad
```

This recurrent export is not robot-deployable without a hidden-state runtime
adapter, and it is not a useful sim warm start. Plain supervised recurrent BC
is worse than the feed-forward live-oracle PPO-loc result and worse than the
phase/contact modulation diagnostic. The current trainable-parent blocker is
not solved by adding hidden state to the same BC objective.

Close the plain BC compression family for this aggregate. The next aligned
branch should be a gate-aware/on-policy behavior-preservation objective or an
explicit branch/router mechanism trained against closed-loop gate outcomes, not
another one-shot BC compression variant.

### Gate-Aware PPO Parent Restore Point

The live-oracle iter2 PPO-loc student was converted into an actual PPO step-0
checkpoint so the next branch can start from a trainable policy state rather
than only an ONNX/NPZ artifact:

```text
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_LIVE_ORACLE_ITER2_PPO_LOC_STEP0_FIDELITY.md
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_LIVE_ORACLE_ITER2_PPO_LOC_STEP0_X008_GATE.md
outputs/analysis/PHASE2_COMMAND_GATED_ZERO0020_LIVE_ORACLE_ITER2_PPO_LOC_STEP0_X000_GATE.md
outputs/analysis/PHASE2_GATE_AWARE_PARENT_NEXT_BRANCH.md
```

Restore point:

```text
checkpoint: outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_step0_checkpoint
ONNX:       outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_step0.onnx
ONNX sha:   d7af39a6255f7303a742b07ac87333c503534c73bd5b16766fa2ad3f4ae1e28f
```

Step-0 action fidelity against the PPO-loc ONNX passed:

```text
p95 abs error: 0.00000003
max abs error: 0.00000007
```

Task-matched compact gate:

```text
x=0.08 z=0.0075 rough+push: 3/5 PASS, seed 1 fall, seed 7 target-velocity hold
x=0.0  z=0.0075 rough+push: 5/5 PASS, mean vx 0.0008 m/s
```

Decision:

```text
PLAN_GATE_AWARE_ON_POLICY_PARENT
```

This is the best current trainable restore point, but it is not a valid Phase 2
DR parent yet. It preserves command semantics and passes the hard seed `6`, but
the moving gate still has one lunge/fall and one instantaneous target-velocity
hold. The next authorized branch is a bounded gate-aware/on-policy
behavior-preservation iteration from this checkpoint, not another one-shot BC
compression and not a long DR run.

Required promotion gate before Phase 2 DR resumes:

```text
x=0.08 compact gate: 5/5 PASS_CANDIDATE_SIM_GATE, zero p95 and max corrected velocity excess
x=0.0  compact gate: 5/5 PASS_CANDIDATE_SIM_GATE, mean |vx| <= 0.005 m/s
```

### Gate-Aware PPO Parent Iter0 Hold

The bounded local ROCm gate-aware parent smoke was run from the PPO step-0
checkpoint:

```text
outputs/phase2_domain_randomization/gate_aware_parent_iter0_local_smoke/smoke_20260705T151050Z_gpu
outputs/analysis/PHASE2_GATE_AWARE_PARENT_ITER0_LOCAL_SMOKE_DECISION.md
outputs/analysis/phase2_gate_aware_parent_iter0_local_smoke_decision.json
```

The smoke completed and exported three ONNX checkpoints:

| step | sha256 |
|---:|---|
| `15360` | `8179d5686d3dc242c3a05f4d47747c62ab1e60256009605a1e65e0b6053acfc2` |
| `30720` | `9d246a73b1542e669e38b69094dbce6f1b998ae0ac1493f3dd09d6cdc3a5e84d` |
| `46080` | `a1fc8cc37925e469c1a9a85ca9e301343979065bbf3735678d7e0d3fc726cf0a` |

The compact x=0.08 corrected-bridge rough+push gate rejected all exports:

```text
outputs/analysis/PHASE2_GATE_AWARE_PARENT_ITER0_LOCAL_SMOKE_X008_GATE.md
outputs/analysis/phase2_gate_aware_parent_iter0_local_smoke_x008_gate.json
```

Result:

```text
iter0_15360: 0/5 pass, mean vx 0.0015 m/s, track ratio 0.0186
iter0_30720: 0/5 pass, mean vx 0.0015 m/s, track ratio 0.0193
iter0_46080: 0/5 pass, mean vx 0.0016 m/s, track ratio 0.0194
```

All 15 policy/seed rollouts completed duration without falling, but every run
held for low forward progress. The candidates spent `100%` of the rollouts in
double support with `0%` single support. Corrected p95 velocity excess was zero
for all exports, so this was not an envelope failure. It was a rewarded
standstill/freeze regression.

Decision:

```text
HOLD_GATE_AWARE_PARENT_REWARDED_FREEZE
```

This hits the pre-registered stop condition from
`PHASE2_GATE_AWARE_PARENT_NEXT_BRANCH`: the first bounded on-policy iteration
lowered the x=0.08 pass count below the step-0 `3/5` baseline. Do not run long
Phase 2 DR from these exports, and do not repeat the same restore-policy-KL
reward-side PPO objective. The next trainable-parent attempt must change the
behavior-preservation structure so PPO cannot improve reward by erasing the
moving gait.

### Gate-Aware PPO Parent Iter1 Behavior-Prior Hold

The next bounded local ROCm smoke kept the same PPO step-0 checkpoint but added
the state-conditioned behavior-prior teacher-action loss on top of restore-policy
KL:

```text
outputs/phase2_domain_randomization/gate_aware_parent_iter1_behavior_prior_local_smoke/smoke_20260705T161023Z_gpu
outputs/analysis/PHASE2_GATE_AWARE_PARENT_ITER1_BEHAVIOR_PRIOR_LOCAL_SMOKE_DECISION.md
outputs/analysis/phase2_gate_aware_parent_iter1_behavior_prior_local_smoke_decision.json
```

Smoke settings:

```text
restore_policy_kl_scale: 8.0
behavior_prior_enabled: true
behavior_prior_scale: -0.35
behavior_prior_huber_delta: 0.04
behavior_prior_mlp_npz: outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_bc_student/candidate_mlp.npz
```

The smoke completed and exported three ONNX checkpoints:

| step | sha256 |
|---:|---|
| `15360` | `8a5eb0baeecb01ae698109c2fdad9c5679a4d9980cf91bd9a95c6cce55d0b28d` |
| `30720` | `292b1a61b0b659b3d3e85243d10112430e87c05a71df7dc4c6fa008e22185cd1` |
| `46080` | `1ee6625b02ea8fe2b7c69923cabd5f734af5d3f397816873964a0ede537cbcd8` |

The compact x=0.08 corrected-bridge rough+push gate rejected all exports:

```text
outputs/analysis/PHASE2_GATE_AWARE_PARENT_ITER1_BEHAVIOR_PRIOR_LOCAL_SMOKE_X008_GATE.md
outputs/analysis/phase2_gate_aware_parent_iter1_behavior_prior_local_smoke_x008_gate.json
```

Result:

```text
iter1bp_15360: 0/5 pass, mean vx 0.0014 m/s, track ratio 0.0178
iter1bp_30720: 0/5 pass, mean vx 0.0015 m/s, track ratio 0.0193
iter1bp_46080: 0/5 pass, mean vx 0.0015 m/s, track ratio 0.0192
```

All 15 policy/seed rollouts completed duration without falling, but every run
held for low forward progress. The candidates spent `100%` of the rollouts in
double support with `0%` single support. Corrected p95 velocity excess was zero
for all exports, so this was not an actuator-envelope failure. It was again a
rewarded standstill/freeze regression.

Decision:

```text
HOLD_BEHAVIOR_PRIOR_PARENT_REWARDED_FREEZE
```

Adding the state-conditioned behavior prior did not preserve the moving gait
from the step-0 parent and did not improve on Iter0 restore-KL-only PPO. Do not
scale this objective into Phase 2 DR, and do not repeat restore-policy-KL plus a
teacher-action behavior prior as another scalar reward-side variant. The next
trainable-parent attempt needs a different behavior-preservation structure:
explicit online router/wrapper training target, stronger branch-aware objective,
or a non-PPO distillation route that is gated before any long DR run.

## 2026-07-05 Iter24 PPO-Loc Step-0 Diagnostic

After the live-oracle Iter24 candidate became the latest useful z=0.0075
baseline, a PPO-compatible `tanh(loc)` surrogate and Orbax step-0 checkpoint
were built from its aggregate manifest:

```text
outputs/analysis/PPO_LOC_ITER24_LIVE_ORACLE_SEED2_ACTIVE_RATE150_STUDENT.md
outputs/analysis/PPO_LOC_ITER24_LIVE_ORACLE_SEED2_ACTIVE_RATE150_STEP0_FIDELITY.md
outputs/analysis/PPO_LOC_ITER24_LIVE_ORACLE_SEED2_ACTIVE_RATE150_STEP0_DECISION.md
```

The step-0 export fidelity is excellent:

```text
p95 abs action error: 1.4156e-7
max abs action error: 2.9802e-7
```

However, the task-matched corrected-bridge rough+push compact gate regressed:

```text
outputs/analysis/PPO_LOC_ITER24_LIVE_ORACLE_SEED2_ACTIVE_RATE150_STEP0_X008_SEED0_1_2_6_7_SCREEN.md
```

Result:

- pass: seeds `1,2`
- hold/fall: seeds `0,6,7`
- max corrected velocity-envelope excess: `0`
- mean track ratio: `0.1160`

A follow-up full-observation trace replay on seeds `0,1,6,7` shows the
regression is not explained by missing manifest coverage or a local action-fit
failure:

```text
outputs/analysis/PPO_LOC_ITER24_STEP0_TRACE_FAILURE_DECISION.md
```

All traced seeds have low nearest-manifest distance and low nearest-action
mismatch against the Iter24 aggregate:

```text
nearest distance p95: 0.2228-0.3357
nearest action L1 p95: 0.0209-0.0271
```

Decision: do not launch long PPO/domain-randomization training from this
step-0 checkpoint as-is. Action fidelity and manifest coverage are insufficient
warm-start gates. The next aligned Phase 2 attempt must preserve behavior under
the task-matched corrected-bridge closed-loop gate before any large PPO/DR run,
or it must add an explicit closed-loop behavior-preservation/training structure
that survives seed perturbations.

## 2026-07-05 Task-Matched Trainable Warm-Start Screen

The older PPO-compatible `limit198` and `rate165` step-0 checkpoints were then
screened against the current z0.0075 rough+push gate to test whether either
could be reused as the trainable parent despite the Iter24 PPO-loc regression.

Artifact:

```text
outputs/analysis/PPO_TRAINABLE_WARMSTART_Z0075_PUSH_DECISION.md
outputs/analysis/ppo_trainable_warmstart_z0075_push_decision.json
outputs/analysis/PPO_TRAINABLE_WARMSTART_Z0075_PUSH_SCREEN.md
outputs/analysis/ppo_trainable_warmstart_z0075_push_screen.json
```

Gate:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.0075
reset_mode: home-support
reset_settle_ticks: 10
bridge: fitted corrected bridge
command_x: 0.08
pushes: 0.075-0.125, interval 1.0-1.5s
seeds: 0,1,2,6,7
```

Result:

- `limit198_step0`: `0/5` pass, `2/5` falls, mean track ratio `0.1630`,
  mean vx `0.0130 m/s`, zero p95 velocity excess but nonzero max corrected
  velocity spikes.
- `rate165_step0`: `0/5` pass, `3/5` falls, mean track ratio `1.1016`,
  mean vx `0.0881 m/s`, high early pitch/fall behavior on seeds `0,1,2`.
- `ppo_loc_iter24_step0`: still the prior `2/5` task-matched result and is
  also not promotable.

Decision: no existing PPO-compatible step-0 checkpoint clears the current
z0.0075 rough+push corrected-bridge screen. The earlier z0.0026/no-push `8/8`
step-0 gates are not transferable evidence for the current stage. Future PPO/DR
launches must first create a task-matched behavior-preserving warm-start whose
step-0 export clears this gate.

## 2026-07-03 Limit198 PPO-Loc Trainable Warm-Start

The current deployable Phase 2 baseline is:

```text
policy/candidates/phase2_iter2_right_ankle_limit198_rate165_20260703/candidate.onnx
```

That candidate is phase-modulated, so it cannot be directly restored into the
existing Brax PPO actor. A PPO-compatible `tanh(loc)` surrogate was trained
from the same limit198 manifest and converted into a step-0 PPO checkpoint.

Evidence:

```text
outputs/analysis/PHASE2_LIMIT198_PPO_LOC_WARMSTART_DECISION.md
outputs/analysis/PHASE2_LIMIT198_PPO_LOC_WARMSTART_STUDENT.md
outputs/analysis/PHASE2_LIMIT198_PPO_LOC_WARMSTART_STEP0_EXPORT_FIDELITY.md
outputs/analysis/PHASE2_LIMIT198_PPO_LOC_WARMSTART_STEP0_X008_GATE.md
outputs/analysis/PHASE2_LIMIT198_PPO_LOC_WARMSTART_STEP0_X0_GATE.md
```

Result:

- step-0 PPO ONNX sha256:
  `1dc894eebc144d790f1a6b4be6ada5a05e748f215f2053c72610347955deb3bb`
- x=0.08 corrected gate: `8/8`, track ratio `0.4151`,
  single support `28.1333%`, zero corrected velocity excess.
- x=0.0 corrected gate: `8/8`, mean vx `0.0001 m/s`, zero corrected
  velocity excess.

Decision: use
`outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint` as the
trainable warm-start for the next offline DR stage. Do not use the older
rate165 Stage A recipe; it already collapsed the gait into double support.

## 2026-07-03 Motion-Preservation CPU Smoke

After the A100 Stage A standstill regression, a tiny local CPU smoke tested a
stricter motion-preservation PPO recipe from the same corrected rate165
warm-start before spending another remote run.

Evidence:

```text
outputs/analysis/PHASE2_RATE165_MOTION_PRESERVE_CPU2240_RESULT.md
outputs/analysis/phase2_rate165_motion_preserve_cpu2240_result.json
outputs/analysis/PHASE2_RATE165_MOTION_PRESERVE_CPU2240_X008_COMPACT_GATE.md
outputs/analysis/PHASE2_RATE165_MOTION_PRESERVE_CPU2240_X0_COMPACT_GATE.md
```

Result:

- exported ONNX sha256:
  `6ec74a1e418e5725c351ffbb8dadc11b4f4619846d3c82be5c12048295cb157c`
- `x=0.08` compact gate: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
- mean local vx: `0.0032 m/s`
- track ratio: `0.0394`
- single support: `0%`
- double support: `100%`
- corrected velocity excess: `0`
- `x=0.0` compact gate: `PASS_CANDIDATE_SIM_GATE`

Decision: reject this exact motion-preservation PPO recipe. It preserves quiet
in-envelope behavior but immediately loses the walking warm-start by returning
to planted double support. Do not scale this recipe into another long A100 run.
The next offline training attempt must preserve single-support walking before
domain randomization escalation.

## 2026-07-03 Stage A Rate165 A100 Result

Stage A narrow flat/no-push DR was launched on Colab A100 from the verified
rate165 PPO-loc step-0 checkpoint. The run itself completed and exported
checkpoints/ONNX files through step `4,587,520`, but the exported policies do
not pass the corrected-bridge walking gate.

Evidence:

```text
outputs/analysis/PHASE2_STAGE_A_RATE165_NARROW_FLAT_RESULT.md
outputs/analysis/phase2_stage_a_rate165_narrow_flat_result.json
outputs/analysis/PHASE2_STAGE_A_RATE165_NARROW_FLAT_X008_GATE.md
outputs/analysis/phase2_stage_a_rate165_narrow_flat_x008_gate.json
outputs/analysis/PHASE2_STAGE_A_RATE165_CHECKPOINT_TRIAGE_SEED0.md
outputs/analysis/phase2_stage_a_rate165_checkpoint_triage_seed0.json
```

Result:

- final Stage A `x=0.08` gate: 8/8 duration complete, no falls, but
  `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`.
- mean local vx: `0.0007 m/s`
- track ratio: `0.0091`
- single support: `0%`
- double support: `100%`
- corrected velocity excess: `0`
- max tracking p95: `0.0385 rad`

Checkpoint triage on seed 0 showed the same low-progress standstill at every
exported checkpoint from `655,360` through `4,587,520`. The Stage A recipe is
therefore rejected; do not advance to Stage B/C/D from this run.

Interpretation: the current Stage A PPO/DR objective preserves safety by
collapsing the walking warm-start into the standstill basin. The next Phase 2
attempt must first preserve nonzero forward motion under the corrected bridge,
for example with a bounded behavior-preserving Stage A variant and an immediate
seed-0 checkpoint gate before spending another full A100 run.

## 2026-07-03 Corrected Rate165 Re-Anchor

The current Phase 2 DR warm-start is no longer the older Phase A2/rate175
lineage. It is the corrected live-oracle iteration-1 rate165 candidate and a
PPO-compatible distillation/checkpoint built from it:

```text
policy/candidates/phase2_corrected_live_oracle_iter1_rate165_20260703/candidate.onnx
outputs/analysis/phase2_rate165_ppo_loc_warmstart_candidate/candidate.onnx
outputs/analysis/phase2_rate165_ppo_loc_warmstart_step0_checkpoint
```

Evidence:

```text
outputs/analysis/PHASE2_RATE165_PPO_LOC_WARMSTART_MANIFEST.md
outputs/analysis/PHASE2_RATE165_PPO_LOC_WARMSTART_STUDENT.md
outputs/analysis/PHASE2_RATE165_PPO_LOC_WARMSTART_X008_GATE.md
outputs/analysis/PHASE2_RATE165_PPO_LOC_WARMSTART_X0_GATE.md
outputs/analysis/PHASE2_RATE165_PPO_LOC_WARMSTART_STEP0_EXPORT_FIDELITY.md
outputs/analysis/PHASE2_DOMAIN_RANDOMIZATION_AUDIT.md
outputs/analysis/PHASE2_DOMAIN_RANDOMIZATION_PLAN.md
```

The PPO-loc warm-start preserves the corrected-bridge candidate behavior under
the `rough_terrain_backlash`, `z=0.0026`, `home-support` gate:

- `x=0.08`: 8/8 duration complete, no falls, track ratio `0.3456`,
  max pitch-chain p95 velocity `1.6458 rad/s`, max tracking p95 `0.1822 rad`,
  zero corrected p95/max velocity excess.
- `x=0.0`: 8/8 duration complete, no falls, mean vx about `-0.0001 m/s`,
  max pitch-chain p95 velocity `0.0677 rad/s`, max tracking p95 `0.0312 rad`,
  zero corrected p95/max velocity excess.

The step-0 Orbax checkpoint export passed action fidelity against the PPO-loc
ONNX with p95 abs error `1.19e-7` and max abs error `2.68e-7`.

The later Stage A A100 result and CPU2240 motion-preservation smoke showed that
the current PPO/DR objective collapses this warm-start into planted double
support. Do not launch another scalar PPO/DR run from this recipe. The next
aligned offline action is a phase-aware/live-oracle student or another
training structure that preserves single-support walking before reintroducing
domain randomization.

Current status and next branch decision:

```text
outputs/analysis/PHASE2_CURRENT_STATUS.md
outputs/analysis/phase2_current_status.json
outputs/analysis/PHASE2_NEXT_BRANCH_DECISION.md
outputs/analysis/phase2_next_branch_decision.json
```

## Current Canonical Gate Ledger

Use the read-only curriculum ledger before advancing any Phase 2 stage:

```bash
python3 tools/report_phase2_curriculum_gate.py
```

Current ledger artifact:

```text
outputs/analysis/PHASE2_CURRICULUM_GATE_LEDGER.md
outputs/analysis/phase2_curriculum_gate_ledger.json
```

Current decision:

```text
stage_a2_z002_regression:
  PASS_STAGE

stage_z005_support:
  HOLD_STAGE
  held gates:
    z005_x008_nopush
    z005_x000_nopush
  missing evidence: none
```

Do not advance to `z=0.005` push, stronger terrain, or robot validation until
the `z=0.005` no-push gates pass under the corrected bridge and the regression
gates remain clear.

Current failure diagnostic:

```text
outputs/analysis/PHASE2_Z005_SEED5_FAILURE_DIAGNOSTIC.md
outputs/analysis/phase2_z005_seed5_failure_diagnostic.json
```

The current z=0.005 hold is seed-5 support collapse in both `x=0.08` and
`x=0.0`. It is backward-biased, double-support dominated, and occurs without
corrected-envelope velocity excess. Treat the next recipe as a terrain-support
and base-height-margin problem, not an actuator-rate problem.

Current next-run recipe:

```text
outputs/analysis/PHASE2_Z005_SUPPORT_NEXT_RECIPE.md
outputs/analysis/phase2_z005_support_next_recipe.json
```

Current hash manifest:

```text
outputs/analysis/PHASE2_ARTIFACT_MANIFEST.md
outputs/analysis/phase2_artifact_manifest.json
```

Use the artifact manifest when reviewing the exact corrected bridge,
warm-start checkpoint, candidate ONNX, stage-gate evidence, and promotion tools
that define the current Phase 2 state.

Current stage guard:

```text
outputs/analysis/PHASE2_STAGE_GUARD.md
outputs/analysis/phase2_stage_guard.json
```

Use the stage guard before launching any run or advancing any rung. It is the
current allowed/forbidden action matrix: z=0.005 support training is the next
authorized offline step once an A100/L4 Colab session is available; robot
validation, stronger terrain, and z=0.005 push remain blocked. It also checks
that the exact z=0.005 Colab package inputs, including the A2 restore
checkpoint, are present and included by the upload tar filter.

Current Colab package manifest:

```text
outputs/analysis/PHASE2_COLAB_PACKAGE_MANIFEST.md
outputs/analysis/phase2_colab_package_manifest.json
```

Use the package manifest to review the concrete hashes, sizes, and file counts
for the z=0.005 Colab package inputs before launching the remote workflow.
The Colab helper also supports `--package-only` to build and hash the local
RDK/Playground upload tarballs without contacting Colab.

Latest package-only evidence:

```text
outputs/analysis/PHASE2_COLAB_PACKAGE_ONLY_MANIFEST.md
outputs/analysis/phase2_colab_package_only_manifest.json
```

Current local fallback readiness:

```text
outputs/analysis/PHASE2_LOCAL_FALLBACK_READINESS.md
outputs/analysis/phase2_local_fallback_readiness.json
```

Use this read-only report when Colab is unavailable. The A100/L4 Colab path
remains the preferred Phase 2 training path. Local ROCm evidence is debug or
fallback evidence unless it clears the same canonical corrected-bridge gates
and the JAX/package version difference is reviewed explicitly.

Latest T4 Colab recovery decision:

```text
outputs/analysis/PHASE2_Z005_T4_RECOVERY_DECISION.md
outputs/analysis/phase2_z005_t4_recovery_decision.json
```

The T4 run completed training and exported ONNX checkpoints, but Colab was
lost before the post-training corrected-bridge gate completed. Treat the
recovered ONNX files as offline debug artifacts only. They are not deployable
and do not authorize robot testing.

Latest z=0.005 recovery-source decision:

```text
outputs/analysis/PHASE2_Z005_RECOVERY_DAGGER_NEXT_DECISION.md
outputs/analysis/phase2_z005_recovery_dagger_next_decision.json
```

The 141-sample seed-5 composite recovery BC smoke fit its labels cleanly
offline, but failed the short closed-loop `z=0.005`, seed-5, `x=0.0` support
gate with severe corrected-envelope velocity excess and high action
saturation. Treat fixed tiny-manifest BC as closed. The next authorized offline
step is a bounded live/on-policy z=0.005 recovery DAgger iteration from the
Phase A2 command-gated candidate, using the corrected z=0.0024 source
manifest, with immediate short seed-5 gates before any 8-seed or Colab scaling.

Latest bounded recovery-DAGger result:

```text
outputs/analysis/PHASE2_Z005_RECOVERY_DAGGER_ITER1_SEED5_SHORT_DECISION.md
outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short_decision.json
```

The bounded iteration produced a 6117-sample aggregate and a clean supervised
fit, but the short seed-5 z=0.005 gates still failed at both `x=0.0` and
`x=0.08`. The failure no longer saturates every pitch-chain joint like the
141-sample smoke, but it still falls before 2 seconds and moves backward. Do
not scale this student. The current z=0.0024 source is not strong enough to
relabel the z=0.005 seed-5 collapse into a passing support behavior; the next
source work should mine or train a passing intermediate-terrain support source
closer to z=0.005 before another DAgger fit.

Latest terrain-boundary source probe:

```text
outputs/analysis/PHASE2_STAGEA2_GAIN099_SEED5_TERRAIN_BOUNDARY_Z00255_SHORT_DECISION.md
outputs/analysis/phase2_stagea2_gain099_seed5_terrain_boundary_z00255_short_decision.json
outputs/analysis/PHASE2_STAGEA2_GAIN099_SEED5_TERRAIN_BOUNDARY_Z0027_SHORT_DECISION.md
outputs/analysis/phase2_stagea2_gain099_seed5_terrain_boundary_z0027_short_decision.json
outputs/analysis/PHASE2_STAGEA2_GAIN099_SEED5_TERRAIN_BOUNDARY_Z0030_SHORT_DECISION.md
outputs/analysis/phase2_stagea2_gain099_seed5_terrain_boundary_z0030_short_decision.json
```

The current Phase A2 gain099 candidate fails the short seed-5 support gate at
`z=0.00255`, `z=0.0027`, and `z=0.0030` for both `x=0.0` and `x=0.08`. This
brackets the usable source terrain between `z=0.0024` and `z=0.00255`; do not
use `z=0.00255+` traces as positive support labels.

Latest z=0.00245 support-recovery closure:

```text
outputs/analysis/PHASE2_Z00245_SUPPORT_RECOVERY_NEXT_DECISION_20260702.md
outputs/analysis/phase2_z00245_support_recovery_next_decision_20260702.json
```

The z=0.00245 boundary is now sharper than the older z=0.005 support hold. The
Phase A2 gain099 candidate cannot provide positive seed-5 source traces at
z=0.00245, and two bounded recovery fits from the z=0.0024 source manifest
failed closed-loop by saturation, over-envelope target rate, fall/termination,
or wrong-direction motion. Reset-settle also worsened the same seed-5 support
case.

Do not promote the z=0.00245 recovery students, do not use them as parents, and
do not repeat another one-shot BC fit on the same tiny two-trace recovery set.
The next valid offline branch must either optimize on-policy with the corrected
envelope active during the update or generate a structurally different
intermediate support target before fitting a student. The first gate remains a
short z=0.00245 seed-5 `x=0.0` support check; it must pass before any `x=0.08`,
8-seed, Colab-scale, or promotion gate.

Current on-policy recovery recipe:

```text
outputs/analysis/PHASE2_Z00245_ON_POLICY_SUPPORT_RECIPE.md
outputs/analysis/phase2_z00245_on_policy_support_recipe.json
```

This recipe reuses the existing `phase2-z0025-boundary` on-policy workflow with
`--phase2-terrain-hfield-z-scale 0.00245`, keeps the corrected envelope costs
active during optimization, and pins the seed-5-first short-gate order. It is
the next aligned offline policy-producing branch once a visible Colab GPU
session is available.

Package-only evidence for that exact launch command:

```text
outputs/analysis/colab_cli/open-duck-a100-phase2-z00245-phase2-z0025-boundary-20260702T081144Z/PACKAGE_ONLY_MANIFEST.md
outputs/analysis/colab_cli/open-duck-a100-phase2-z00245-phase2-z0025-boundary-20260702T081144Z/PACKAGE_ONLY_MANIFEST.json
```

This check built and hashed the RDK and Playground upload archives with tracked
RDK/Playground trees clean and JAX pinned to `0.7.2`. It did not upload, train,
SSH, deploy, or touch the robot.

Latest z=0.00245 A100 motion-recovery result:

```text
outputs/analysis/PHASE2_Z00245_MOTION_RECOVERY_A100_RESULT_20260702.md
outputs/analysis/phase2_z00245_motion_recovery_a100_result_20260702.json
outputs/analysis/phase2_z00245_motion_recovery_a100_20260702/checkpoint_sweep/CANDIDATE_CHECKPOINT_SWEEP.md
outputs/analysis/phase2_z00245_motion_recovery_a100_20260702/checkpoint_sweep/candidate_checkpoint_sweep.json
```

The A100 run completed training and exported checkpoints at `40960`, `81920`,
and `122880` steps from the Phase A2 warm-start with `z=0.0025`, corrected
bridge, no push, weaker target-rate/actuator-tracking penalties, and stronger
scalar forward-progress pressure. The compact corrected-bridge checkpoint sweep
did not promote any checkpoint. All three checkpoints passed the short `x=0.0`
eval and stayed well below the measured velocity envelope, but all held at
`x=0.08` for low forward progress:

```text
40960:  track_ratio=0.2339, mean_vx=0.0187, max_vel_p95=1.4191
81920:  track_ratio=0.1660, mean_vx=0.0133, max_vel_p95=1.4132
122880: track_ratio=0.1684, mean_vx=0.0135, max_vel_p95=1.4296
```

The best available checkpoint was `40960`, but it was explicitly
`HOLD_PARTIAL_CANDIDATE_CHECKPOINT` and not promotable. The remote driver then
started a full 8-seed, 15s `z=0.0025`, `x=0.08` no-push gate on that partial
checkpoint, but the Colab session was lost before a final seed-gate artifact or
exit sentinel was recoverable. This does not authorize promotion because the
compact checkpoint sweep had already failed the motion threshold.

Do not repeat another small scalar-progress-pressure nudge from this lineage.
The next valid offline branch should preserve the walking behavior directly
with teacher-action, trust-region, or live-oracle continuity, then re-run the
same corrected-bridge gates.

Superseded source-generation plan:

```text
outputs/analysis/PHASE2_TERRAIN_SUPPORT_SOURCE_NEXT_PLAN.md
outputs/analysis/phase2_terrain_support_source_next_plan.json
```

The next aligned branch is no longer another DAgger fit against the z=0.0024
source. It is a small terrain-support source-generation rung at `z=0.00245` or
`z=0.00250`, warm-started from Phase A2, with seed-5 `x=0.0` support survival
as the first gate. Only passing source traces may feed later DAgger.

This recipe continues from the last z=0.002 passing A2 checkpoint, keeps the
corrected bridge active, uses z=0.005 rough terrain with no push, and targets
the seed-5 support collapse directly:

- stronger base-height margin,
- explicit contact-support cost,
- stronger wrong-direction penalty,
- gentler double-support dwell pressure so zero-command support is not
  over-penalized,
- stronger restore-policy KL to preserve the z=0.002 gait.

Promotion still requires the z=0.005 no-push gates to pass at both `x=0.08`
and `x=0.0`, with the z=0.002 regression gates remaining clear.

The `phase2-z005-support` Colab workflow now runs the post-training gates and
then calls:

```bash
python3 tools/report_phase2_z005_post_training_gates.py <candidate_name>_post_training_seed_gates.json
```

Use that decision artifact as the promotion authority for this rung. A raw
checkpoint sweep or smoke pass is not promotable by itself.

## Phase 1 Anchor

```text
policy: policy/candidates/corrected_bridge_cmd_conditioned_rate175_20260627/candidate.onnx
sha256: 63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e
corrected bridge: outputs/analysis/actuator_response_fit_corrected_knee.json
corrected bridge sha256: 3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0
trainable warm-start checkpoint: outputs/analysis/ppo_bc_command_conditioned_rate175_step0_checkpoint
step-0 exported ONNX: outputs/analysis/ppo_bc_command_conditioned_rate175_step0.onnx
warm-start fidelity report: outputs/analysis/ppo_bc_command_conditioned_rate175_step0_export_fidelity.json
```

The carpet test showed the current policy is actuator-trackable on the ground
but does not lift/clear its feet enough to walk forward on medium carpet. Phase
2 should therefore treat robustness and terrain/contact margin as the target,
not actuator tracking alone.

## Trainable Warm-Start

The user constraint is correct: Phase 2 must warm-start from the Phase 1 gait,
not train from scratch.

The local Playground PPO runner warm-starts from a Brax/Orbax checkpoint via
`--restore_checkpoint_path`. A verified step-0 PPO checkpoint now exists for
the Phase 1 `rate175` candidate:

```text
checkpoint:
  outputs/analysis/ppo_bc_command_conditioned_rate175_step0_checkpoint

fidelity:
  status: PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY
  p95 abs error: 1.1920928955078125e-07
  max abs error: 3.2782554626464844e-07
```

This checkpoint was constructed from the Phase 1 BC MLP NPZ, exported through
the PPO ONNX path, and compared against the packaged Phase 1 ONNX before any
PPO updates. Use it as the trainable Phase 2 warm-start. Do not launch a
scratch PPO run and call it Phase 2.

## Existing Playground Hooks

The local Playground now provides the requested DR scaffolding:

- friction randomization in `playground/common/randomize.py`
- link mass and torso mass randomization
- torso COM jitter
- frictionloss and armature randomization
- actuator gain/bias scaling
- observation noise for joint position, joint velocity, gyro, accelerometer,
  and gravity
- action delay and IMU delay
- random planar push impulses to the floating base
- rough-terrain hfield scene via `rough_terrain_backlash`
- corrected actuator bridge hooks and runner CLI flags
- staged CLI overrides for friction, mass, COM, qpos jitter, actuator gain,
  push intervals/magnitudes, observation noise, and leg-geometry jitter
- default-off leg-link body-position geometry jitter

Missing or partial:

- stage advancement is not automated by corrected-bridge gates
- push recovery was not part of the original canonical no-push candidate gate;
  `tools/eval_policy_with_actuator_bridge.py` and
  `tools/run_candidate_seed_sweep.py` now expose explicit default-off
  `--eval-push-enable` controls and recovery metrics
- terrain curriculum now has an eval-only hfield vertical scale override via
  `--terrain-hfield-z-scale`; this creates a temporary scene XML for the worker
  and removes it after env construction, so the Playground checkout is not
  permanently modified
- the training smoke wrapper also accepts `--terrain-hfield-z-scale`; it backs
  up the selected task XML, patches the hfield z scale for the subprocess, and
  restores the original XML in `finally`

## Curriculum

Stage A:

- flat terrain
- narrow physics randomization
- no push
- corrected bridge near fitted range
- behavior prior strong enough to preserve gait

Stage A first run result:

```text
training artifact:
  outputs/phase2_domain_randomization/stage_a_narrow_flat_no_push_gpu/smoke_20260628T015607Z_gpu

decision:
  outputs/analysis/PHASE2_STAGE_A_DECISION.md

status:
  HOLD_STAGE_A_LOW_FORWARD_PROGRESS
```

The first Stage A run completed successfully as an offline GPU training job but
regressed command-conditioned walking. It passed `x=0.0` standing 8/8 and stayed
inside the corrected velocity envelope, but the final export held on `x=0.08`
forward progress across all 8 seeds. The PPO step-0 warm-start export still
matches the packaged Phase 1 candidate in closed-loop rollout, so the regression
comes from the Stage A PPO/DR update rather than a broken trainable checkpoint.

Do not advance to Stage B from this run. The next Stage A retry should preserve
the Phase 1 behavior more tightly before widening robustness:

- stronger restore-policy KL,
- lower learning rate,
- shorter horizon or more frequent checkpointing,
- stronger behavior prior or teacher-action continuity.

Stage A2 retry result:

```text
decision:
  outputs/analysis/PHASE2_STAGE_A2_DECISION.md

status:
  PASS_STAGE_A_GAIN099_PROMOTED_FOR_STAGE_B
```

A2 improved the failure mode. The 164k checkpoint completed `x=0.08` 8/8 with
no falls and no envelope excess, and passed `x=0.0` 8/8, but missed strict
tracking by `0.0004 rad` on one seed. A minimal 0.99 action-gain ONNX wrapper
fixed that tracking miss while preserving command conditioning:

```text
candidate:
  policy/candidates/phase2_stage_a2_gain099_20260628/candidate.onnx

candidate_sha256:
  a082be6cf5c486073523bbd0fba4ea3645dc448270ca0a8e28c4ce5a4e8d31c4

x=0.08:
  PASS_CANDIDATE_SIM_GATE 8/8
  mean track ratio: 0.3542
  max tracking p95: 0.1984 rad

x=0.0:
  PASS_CANDIDATE_SIM_GATE 8/8
  mean vx: 0.0004 m/s
```

This is a Stage A sim promotion, not robot approval. Stage B may proceed
offline from this lineage.

Stage B:

```text
decision:
  outputs/analysis/PHASE2_STAGE_B_DECISION.md

status:
  HOLD_STAGE_B_PUSH_DR_ERODES_FORWARD_MOTION
```

Two offline Stage B attempts were run from the trainable A2 164k checkpoint:

- `stage_b1_full_flat_gentle_push_from_a2_gpu`: full flat physics
  randomization plus gentle pushes. It completed training but regressed to
  near-standstill at `x=0.08`; best track ratio was `0.0467`.
- `stage_b0_mild_push_from_a2_gpu`: narrow randomization plus mild pushes. It
  completed training and preserved more motion, but still held with best raw
  track ratio `0.1898`. Constant gain wrappers up to `1.20` did not recover a
  passing gait; best gain result was `0.2176`.

Do not advance to rough terrain yet. The current blocker is preserving forward
motion while adding push/randomization robustness on flat terrain.

B0D tracking-margin continuation state:

```text
local ROCm discovery:
  PASS_LOCAL_ROCM_READY

local ROCm tiny B0D-shaped smoke:
  PASS_GPU_RECOVERY_SMOKE

local ROCm 64-env B0D scale-up:
  HOLD_LOCAL_ROCM_SCALE

local ROCm 32-env B0D continuation:
  HOLD_B0D_REGRESSED_MOTION_NO_TRACKING_GAIN

CPU path check:
  PASS_CPU_PATH_CHECK

CUDA handoff:
  HOLD_NO_ACTIVE_COLAB_SESSION
```

B0D is the next valid full training attempt from the B0C corrected-bridge
checkpoint. The earlier local ROCm run failed before any PPO step, but after
the workstation reset/firmware work the read-only ROCm report passed and a tiny
B0D-shaped GPU smoke reached PPO step 160. A 64-env local scale-up then failed
with `ROCM_ERROR_ILLEGAL_ADDRESS` before any PPO step. A 32-env local
continuation completed and exported checkpoints through step 61,440, but the
compact corrected-bridge checkpoint sweep held at `x=0.08` with tracking around
`0.219 rad` and track ratio around `0.26`. A matched compact sweep of the B0C
parent showed the same tracking p95 but better track ratio (`0.3035`), so B0D
as configured regressed motion without improving the compact tracking blocker.
A tiny CPU run also confirmed the command/checkpoint path is structurally
executable.

B0D should not be the next full attempt because the 32-env local continuation
regressed compact forward motion without improving the tracking miss. The next
full attempt is B0E: keep the B0C restore checkpoint, use a milder
actuator-tracking penalty, preserve stronger forward-progress terms, and run on
a visible CUDA/A100 Colab session with the pinned workflow and post-training
checkpoint sweep:

```bash
python3 tools/report_colab_session_status.py

python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow phase2-b0e \
  --session <visible-colab-session> \
  --candidate-name phase2_b0e_motion_preserving_tracking_cuda \
  --candidate-timeout-s 10800 \
  --candidate-checkpoint-sweep \
  --candidate-checkpoint-sweep-commands 0.0,0.08 \
  --candidate-checkpoint-sweep-duration 1.0 \
  --candidate-checkpoint-sweep-jax-platform cpu \
  --candidate-checkpoint-sweep-timeout-s 7200 \
  --run
```

Do not treat any B0D artifact as promotable until the corrected-bridge
rough-terrain gentle-push 8-seed gates are run and reviewed locally.

B0E motion-preserving tracking-margin attempt:

```text
artifact:
  outputs/analysis/PHASE2_B0E_LOCAL_ROCM_HOLD_DECISION.md

status:
  HOLD_LOCAL_ROCM_EVALUATOR_RESET
```

B0E was defined as a follow-up to B0D that keeps the B0C restore checkpoint but
uses a milder actuator-tracking penalty (`-0.015`) with stronger forward
progress terms. The intent was to preserve B0C's better compact `x=0.08` motion
while testing whether a smaller tracking-margin nudge could close the narrow
tracking miss.

Local ROCm attempts at both 32 envs and 16 envs failed before any PPO update or
checkpoint export, during Brax evaluator reset:

```text
jax.jit(eval_env.reset):
  rocblas_gemm_strided_batched_ex failed with rocblas_status_internal_error
```

This is a backend hold, not a policy result. Do not compare B0E against B0C/B0D
gate metrics yet, and do not keep retrying the same local ROCm path without a
backend change. A tiny CPU-only path check passed (`1` env, `20` timesteps,
PPO step `100`), confirming the B0E command wiring is structurally valid, but
that CPU check is not a policy result and is not promotable. The next valid B0E
paths are CUDA/A100 with the pinned workflow, CPU only for more command-plumbing
checks, or a local ROCm evaluator-reset fix.

Additional local ROCm scale diagnostic:

```text
artifact:
  outputs/analysis/PHASE2_B0E_LOCAL_GPU_PATH_CHECK_DECISION.md

status:
  PASS_B0E_GPU_1ENV_PLUMBING
```

A deliberately tiny B0E GPU path check (`1` env, `20` timesteps,
rough-terrain `z=0.002`) reached PPO step `100` and exported on local ROCm.
That narrows the B0E backend issue: 1-env ROCm works, while 16/32-env ROCm
fails during evaluator reset. The blocker is scale-dependent local ROCm
evaluator reset, not B0E recipe wiring. The 1-env checkpoint is not a policy
result and is not promotable.

B0E local ROCm scale matrix:

```text
artifact:
  outputs/analysis/PHASE2_B0E_LOCAL_GPU_SCALE_MATRIX_DECISION.md

status:
  HOLD_LOCAL_ROCM_SCALE_BOUNDARY_4_PASS_8_FAIL
```

The bounded local ROCm matrix found that B0E passes through 4 envs but fails at
8 envs before PPO with the same evaluator-reset `rocblas_status_internal_error`
seen at 16/32 envs:

```text
1 env: PASS_SMOKE_RUN, PPO step 100
2 env: PASS_SMOKE_RUN, PPO step 200
4 env: PASS_SMOKE_RUN, PPO step 400
8 env: HOLD_SMOKE_RUN before PPO
```

Four envs is not enough throughput for the requested Phase 2 robustness
training, so the next policy-producing run remains the pinned CUDA/A100
`phase2-b0e` workflow or a local ROCm backend fix. Do not promote smoke
checkpoints from this matrix.

B0E local ROCm memory-mitigation update:

```text
artifact:
  outputs/analysis/PHASE2_B0E_LOCAL_GPU_MEMFIX_DECISION.md

status:
  PASS_B0E_ROCM_MEMFIX_32ENV_PLUMBING

env:
  JAX_PLATFORM_NAME=gpu
  JAX_PLATFORMS=rocm
  XLA_PYTHON_CLIENT_PREALLOCATE=false
  XLA_PYTHON_CLIENT_MEM_FRACTION=0.50
```

With default allocation, B0E failed at 8 envs during evaluator reset. With the
memory cap above, the bounded B0E plumbing checks passed at 8, 16, and 32 envs,
reaching PPO/export at steps 800, 1600, and 3200 respectively.

This is not a policy result and none of those smoke checkpoints are promotable.
It does change the backend plan: local ROCm is now plausible for a bounded B0E
training run when launched with the memory cap, while the pinned CUDA/A100
`phase2-b0e` workflow remains the preferred high-throughput path whenever a
Colab session is visible.

B0E local ROCm full-shape follow-up:

```text
artifact:
  outputs/analysis/PHASE2_B0E_LOCAL_ROCM_FULLSHAPE_HOLD_DECISION.md

status:
  HOLD_B0E_ROCM_FULLSHAPE_EVALUATOR_RESET
```

The memory cap fixed tiny `episode_length=20` plumbing, but did not fix the
real 750-step evaluator graph. Full-shape B0E attempts at 32, 16, and 8 envs
all failed before PPO at `jax.jit(eval_env.reset)` with
`rocblas_status_internal_error`. A `ppo_num_evals=0` variant also failed at the
same evaluator construction path, so this stack does not bypass evaluator reset
when eval count is zero.

Decision: do not launch local ROCm policy-producing B0E runs on this path. The
next policy-producing run remains the pinned CUDA/A100 `phase2-b0e` workflow.

First A100 `phase2-b0e` launch:

```text
artifact:
  outputs/analysis/PHASE2_B0E_A100_HFIELD_TASK_HOLD_DECISION.md

status:
  HOLD_B0E_CUDA_WORKFLOW_TASK_MISMATCH_FIXED
```

The `open-duck-a100` session came up with CUDA/JAX ready (`jax==0.7.2`,
`jaxlib==0.7.2`, `brax==0.14.2`, `mujoco==3.9.0`, `mujoco-mjx==3.9.0`,
backend `gpu`, device `cuda:0`) and the policy/sim contract audit passed.
Training did not start because the Phase 2 CUDA recipe omitted
`--task rough_terrain_backlash`, causing the hfield override to be applied to
the default `flat_terrain` XML. The workflow now passes
`--task rough_terrain_backlash` explicitly. This is not a policy result.

Push-eval plumbing result:

```text
analysis:
  outputs/analysis/PHASE2_PUSH_EVAL_PLUMBING.md

status:
  PUSH_EVAL_MODE_ADDED
```

The canonical no-push candidate gate remains unchanged. Push perturbations are
now an explicit eval mode with event counts, recovery success rate, applied
velocity impulse magnitude, recovery-window pitch, and recovery-window base
height.

Stage A mild-push CPU gate:

```text
report:
  outputs/analysis/PHASE2_STAGE_A_PUSH_GATE_CPU.md

json:
  outputs/analysis/phase2_stage_a_push_gate_cpu.json

configuration:
  seeds: 0-7
  duration: 15 s
  command_x: 0.08
  push interval: 1.0-1.5 s
  push magnitude: 0.05-0.10

result:
  PASS_CANDIDATE_SIM_GATE 8/8
  falls: 0/8
  duration_complete: 8/8
  mean track ratio: 0.3533
  max tracking p95: 0.1975 rad
  max velocity excess: 0.0000 rad/s
  mean push recovery success: 0.9704
```

This establishes that the Stage A candidate already tolerates mild push
perturbations in evaluation. The Stage B training holds should be read as
training erosion of forward motion under push/randomization, not as proof that
mild pushes immediately break the Stage A gait. Local ROCm/MJX timed out a
one-second closed-loop push smoke after `600 s`, so local GPU should not be
used for correctness gates until that backend path is fixed.

Stage A moderate-push CPU gate:

```text
report:
  outputs/analysis/PHASE2_STAGE_A_PUSH_MODERATE_GATE_CPU.md

json:
  outputs/analysis/phase2_stage_a_push_moderate_gate_cpu.json

configuration:
  seeds: 0-7
  duration: 15 s
  command_x: 0.08
  push interval: 1.0-1.5 s
  push magnitude: 0.10-0.20

result:
  PASS_CANDIDATE_SIM_GATE 8/8
  falls: 0/8
  duration_complete: 8/8
  mean track ratio: 0.3467
  max tracking p95: 0.1964 rad
  max velocity excess: 0.0000 rad/s
  mean push recovery success: 0.9704
```

This confirms the promoted Stage A candidate has push margin in evaluation at
least through `0.20` impulse magnitude. The next Stage B training attempt
should focus on preserving this already-present behavior while adding physics
randomization, not on adding push perturbations as a first-order discovery
signal.

- flat terrain
- full physics randomization
- gentle pushes
- same corrected envelope gate

Stage C:

- existing rough hfield terrain
- full physics randomization
- gentle pushes

Stage A rough-terrain CPU gate:

```text
report:
  outputs/analysis/PHASE2_STAGE_A_ROUGH_TERRAIN_GATE_CPU.md

json:
  outputs/analysis/phase2_stage_a_rough_terrain_gate_cpu.json

configuration:
  seeds: 0-7
  duration: 15 s
  command_x: 0.08
  task: rough_terrain_backlash
  push: disabled

result:
  HOLD
  falls/terminations: 5/8
  duration_complete: 3/8
  mean track ratio: -0.5120
  max velocity excess: 0.0000 rad/s
```

This separates the next blocker cleanly: the promoted Stage A candidate has
flat-terrain push margin, but the existing rough hfield terrain breaks the gait
without requiring any target-velocity envelope violation. Terrain should
therefore enter through a gentler curriculum than the stock rough task, or via
training that preserves the Stage A flat gait while increasing foot clearance
and contact margin.

Scaled-terrain plumbing smoke:

```text
command:
  --task rough_terrain_backlash
  --terrain-hfield-z-scale 0.002

result:
  worker loaded the temporary scaled XML and removed it after env construction
```

Use this knob to measure a terrain-feasibility curve before training:

```text
flat terrain
rough_terrain_backlash --terrain-hfield-z-scale 0.002
rough_terrain_backlash --terrain-hfield-z-scale 0.005
stock rough_terrain_backlash       # hfield z scale 0.01
```

Training wrapper terrain override smoke:

```text
tool:
  tools/run_actuator_bridge_training_smoke.py --terrain-hfield-z-scale 0.002

artifact:
  outputs/analysis/terrain_training_override_smoke/

result:
  PASS_SMOKE_RUN
  destination_sha256_before == destination_sha256_restored
  Playground XML restored to stock hfield size 10 10 .01 0.1
```

Stage A z-scale `0.002` terrain gate:

```text
report:
  outputs/analysis/PHASE2_STAGE_A_TERRAIN_Z002_GATE_CPU.md

json:
  outputs/analysis/phase2_stage_a_terrain_z002_gate_cpu.json

result:
  NEAR_PASS
  duration_complete: 8/8
  falls: 0/8
  pass: 7/8
  one tracking miss: seed 7 max tracking p95 0.2001 rad
  mean track ratio: 0.4033
  max velocity excess: 0.0000 rad/s
```

This is the first useful terrain curriculum rung: it is stable across all
seeds and only misses the strict gate by `0.0001 rad` on one seed. Treat it as
the starting point for terrain hardening, not as a robot-ready terrain pass.

Stage A z-scale `0.005` terrain gate:

```text
report:
  outputs/analysis/PHASE2_STAGE_A_TERRAIN_Z005_GATE_CPU.md

json:
  outputs/analysis/phase2_stage_a_terrain_z005_gate_cpu.json

result:
  HOLD
  duration_complete: 7/8
  falls/terminations: 1/8
  pass: 2/8
  tracking holds: 5/8
  mean track ratio: -0.0485
  max velocity excess: 0.0000 rad/s
```

The terrain curve is now bracketed:

```text
flat: pass
z=0.002: near-pass, 8/8 upright, one 0.0001 rad tracking miss
z=0.005: hold, one fall and multiple tracking holds
z=0.010 stock rough: hard hold, 5/8 terminations
```

The next terrain-training rung should target z-scale `0.002` first, not `0.005`
or the stock rough hfield.

Stage C z-scale `0.002` terrain-training attempts:

```text
decision:
  outputs/analysis/PHASE2_STAGE_C_TERRAIN_Z002_DECISION.md

status:
  HOLD_STAGE_C_TERRAIN_Z002_TRACKING_MARGIN
```

Three narrow terrain fine-tunes were run offline on local ROCm and screened on
the same two-seed, five-second `z=0.002` terrain benchmark:

- `stage_c0_terrain_z002_preserve_from_a2_gpu`: terrain fine-tune with narrow
  DR and strong gait preservation.
- `stage_c1_terrain_z002_tracking_from_c0_gpu`: C0 warm-start with an
  actuator bridge tracking penalty.
- `stage_c2_terrain_z002_targetrate_from_c1_gpu`: C1 warm-start with target
  rate penalty.

All three training runs completed successfully and restored the temporary
terrain XML. None produced a promotable terrain candidate.

Best short-screen result:

```text
policy: c0_245760
seed 0: HOLD_CANDIDATE_TRACKING, tracking p95 0.2040 rad
seed 1: PASS_CANDIDATE_SIM_GATE, tracking p95 0.1965 rad
mean track ratio: 0.3965
mean vx: 0.0317 m/s
velocity excess: 0.0000 rad/s
```

C2's best tracking result was similar but still held:

```text
policy: c2_163840
seed 0: HOLD_CANDIDATE_TRACKING, tracking p95 0.2044 rad
seed 1: PASS_CANDIDATE_SIM_GATE, tracking p95 0.1941 rad
mean track ratio: 0.4070
mean vx: 0.0326 m/s
velocity excess: 0.0000 rad/s
```

Inspection shows the remaining miss is not falling, saturation, or corrected
velocity-envelope excess. It is a small terrain-induced joint-target tracking
margin, dominated on the screen by seed 0 and the left knee. Bridge tracking is
lower than the strict gate miss, so simply increasing the bridge tracking
penalty is not the right lever.

Stage C clearance instrumentation:

```text
decision:
  outputs/analysis/PHASE2_STAGE_C_TERRAIN_CLEARANCE_INSTRUMENTATION.md

screen:
  outputs/analysis/PHASE2_STAGE_C_TERRAIN_Z002_CLEARANCE_SCREEN_CPU.md

status:
  PASS_CLEARANCE_METRICS_ADDED
```

The closed-loop evaluator now reports passive foot-clearance and support
metrics from existing `foot_site_pos_m` and `foot_contacts` records. This does
not change policy stepping, reward, training, or gates.

Focused seed-0 z-scale `0.002` terrain comparison:

```text
a2_gain099:
  tracking p95: 0.2079 rad
  min swing peak lift: 0.0153 m
  single support: 17.6%
  double support: 82.4%

c0_245760:
  tracking p95: 0.2040 rad
  min swing peak lift: 0.0159 m
  single support: 16.8%
  double support: 83.2%

c2_163840:
  tracking p95: 0.2044 rad
  min swing peak lift: 0.0163 m
  single support: 17.2%
  double support: 82.8%
```

The terrain blocker is therefore consistent with a low-clearance shuffle:
mostly double support, very low swing peak, and little true single-support
time. The next Stage C training objective should target swing clearance and
double-support dwell directly while preserving the corrected envelope and the
strict tracking gate.

Stage C3 contact-timing fine-tune:

```text
decision:
  outputs/analysis/PHASE2_STAGE_C3_CONTACT_TIMING_DECISION.md

screen:
  outputs/analysis/PHASE2_STAGE_C3_TERRAIN_Z002_SCREEN_CPU.md

status:
  HOLD_STAGE_C3_CONTACT_TIMING_NOT_ENOUGH
```

C3 warm-started from the best C2 terrain checkpoint and added forward
single-support, double-support dwell, and contact-transition pressure while
keeping the corrected fitted bridge and `z=0.002` rough-terrain screen.
Training completed successfully and restored the temporary terrain XML.

The best screened checkpoint was `c3_245760`:

```text
tracking p95: 0.2046 rad
track ratio: 0.4061
velocity excess: 0.0000 rad/s
min swing peak lift: 0.0165 m
single support: 20.8%
double support: 79.2%
```

This moved support timing in the intended direction, but it did not clear the
strict `0.20 rad` tracking gate and did not materially raise swing height. C3
therefore does not promote a terrain candidate. The next useful Stage C step is
not another contact-timing-only retry; it should add an explicit swing
clearance/feet-height objective or a target-source change that raises the foot
while preserving corrected-envelope compliance and command conditioning.

Stage C4 clearance-reward plumbing:

```text
artifact:
  outputs/analysis/PHASE2_STAGE_C4_CLEARANCE_REWARD_PLUMBING.md

status:
  PASS_CLEARANCE_REWARD_PLUMBING
```

The Playground task now exposes a default-off `forward_swing_clearance` cost
that measures swing peak lift above each foot's last stance height and applies
only under nonzero forward command. This avoids world-height assumptions on
heightfield terrain. The RDK training wrapper forwards the matching
`--forward-swing-clearance-*` flags, and a tiny CPU smoke plus direct one-step
env activation check passed. No candidate was promoted.

The next Stage C run should be a C4 fine-tune from the best C2/C3 terrain
lineage with a mild clearance penalty, not a new contact-timing-only retry.

Stage C4 clearance run:

```text
decision:
  outputs/analysis/PHASE2_STAGE_C4_CLEARANCE_DECISION.md

screen:
  outputs/analysis/PHASE2_STAGE_C4_TERRAIN_Z002_SCREEN_CPU.md

status:
  HOLD_STAGE_C4_CLEARANCE_OVERDRIVES_GAIT
```

C4 warm-started from `c3_245760` and added a clearance cost with target lift
`0.03 m` and scale `-0.05`. Training completed and restored the terrain XML,
but the final checkpoint overcorrected:

```text
c4_245760:
  samples: 33
  termination: fall_or_nan
  tracking p95: 0.4266 rad
  track ratio: -6.0028
  corrected velocity excess: 3.2400 rad/s
  min swing peak lift: 0.0193 m
  single support: 81.8%
  double support: 9.1%
```

The clearance objective has leverage, but this setting destroyed the gait
instead of producing a stable higher-clearance shuffle. A weaker C4b retry was
attempted with scale `-0.005` and target `0.025 m`, but it failed before
training on the local ROCm path with `rocblas_status_internal_error` during JAX
evaluator reset. Treat C4b as a backend hold, not a policy result.

The next terrain attempt should stage the clearance pressure more gently and
preserve the C3 gait with stronger restore-policy/behavior prior pressure or
more frequent checkpoint screening.

Stage C5a clearance-preservation run:

```text
decision:
  outputs/analysis/PHASE2_STAGE_C5A_CLEARANCE_PRESERVE_DECISION.md

screen:
  outputs/analysis/PHASE2_STAGE_C5A_TERRAIN_Z002_SCREEN_CPU.md

status:
  HOLD_STAGE_C5A_RETREATS_TO_DOUBLE_SUPPORT
```

Two immediate follow-up runs after C4 failed before training with local ROCm
`rocblas_status_internal_error` during JAX evaluator reset. A basic JAX ROCm
matmul still passed. Retrying with:

```text
XLA_FLAGS=--xla_gpu_autotune_level=0
XLA_PYTHON_CLIENT_PREALLOCATE=false
```

allowed C5a to train, so use this as the local ROCm workaround for short
training attempts unless a cleaner backend fix is found.

C5a used stronger gait preservation and much weaker clearance pressure:

```text
restore_policy_kl_scale: 2.5
forward_swing_clearance_scale: -0.001
forward_swing_clearance_target_m: 0.022
```

It stayed stable and in-envelope, and reduced strict tracking p95 below
`0.20 rad`, but only by retreating into lower forward progress and even less
clearance:

```text
c5a_81920:
  tracking p95: 0.1946 rad
  track ratio: 0.2220
  corrected velocity excess: 0.0000 rad/s
  min swing peak lift: 0.0086 m
  single support: 9.6%
  double support: 90.4%
```

This is not a terrain candidate. It exposes a reward loophole: touchdown
clearance penalties can be avoided by reducing swing/transition behavior. The
next C-stage attempt should keep transition/single-support pressure active
while using very weak clearance pressure and moderate, not overwhelming,
restore-policy KL.

C6 tested that pairing:

```text
artifact: outputs/analysis/PHASE2_STAGE_C6_TRANSITION_CLEARANCE_DECISION.md
screen: outputs/analysis/PHASE2_STAGE_C6_TERRAIN_Z002_SCREEN_CPU.md
status: HOLD_STAGE_C6_TRANSITION_PRESSURE_RETREATS_TO_DOUBLE_SUPPORT
```

C6 completed a short GPU training run from the best C3 checkpoint using the
local ROCm workaround:

```text
XLA_FLAGS=--xla_gpu_autotune_level=0
XLA_PYTHON_CLIENT_PREALLOCATE=false
```

The recipe used moderate gait preservation, stronger single-support/contact
transition pressure than C3, and very weak clearance pressure:

```text
restore_policy_kl_scale: 1.25
forward_single_support_scale: 0.30
forward_contact_transition_scale: 0.20
forward_swing_clearance_scale: -0.0005
forward_swing_clearance_target_m: 0.020
num_timesteps: 81920
```

The final checkpoint stayed stable and in-envelope, but it regressed further
into a low-clearance double-support shuffle:

```text
c6_81920:
  tracking p95: 0.1654 rad
  track ratio: 0.0985
  corrected velocity excess: 0.0000 rad/s
  min swing peak lift: 0.0072 m
  single support: 4.0%
  double support: 96.0%
```

Decision: do not promote C6. The C-stage evidence now shows that scalar
clearance/contact-timing reward terms are being satisfied by reducing motion
rather than by producing higher-clearance stepping. The next terrain branch
needs gate-selected training or a target/teacher that explicitly contains
higher-clearance steps, not another small scalar PPO tweak.

C7 tested gate-selected terrain training:

```text
artifact: outputs/analysis/PHASE2_STAGE_C7_GATE_SELECTION_DECISION.md
checkpoint screen: outputs/analysis/PHASE2_STAGE_C7_TERRAIN_Z002_SCREEN_CPU.md
8-seed screen: outputs/analysis/PHASE2_STAGE_C7_35120_TERRAIN_Z002_8SEED_CPU.md
status: HOLD_STAGE_C7_GATE_SELECTION_PARTIAL
```

C7 reused the C6 recipe but exported frequent checkpoints (`ppo_num_evals: 8`)
so terrain metrics could select the best transient checkpoint instead of using
the final reward-selected checkpoint. This worked in a limited sense:
`c7_35120` passed the focused seed-0 `z=0.002` terrain screen while later
checkpoints regressed into low forward progress.

The best transient checkpoint:

```text
checkpoint: c7_35120
sha256: ee0b7013bf588b2aab4b8efe3c7ab10b1d8b901d786282717cda3b18b5c8b5d7
```

Eight-seed `z=0.002` screen:

```text
passes: 5/8
falls: 0/8
duration_complete: 8/8
mean track ratio: 0.2671
mean vx: 0.0214 m/s
max corrected velocity excess: 0.0000 rad/s
max pitch-chain tracking p95: 0.1918 rad
mean min swing peak lift: 0.0105 m
mean single support: 11.4%
mean double support: 88.45%
```

Decision: gate-selected checkpointing is useful and should remain part of
terrain work, but C7 is not a terrain robustness candidate. It improves
tracking relative to C3 by reducing motion and still produces a low-clearance,
mostly double-support shuffle. The next branch should change the target
manifold: mine or generate higher-clearance stepping demonstrations, or add a
hard step-clearance/step-advance constraint for nonzero command.

Follow-up C7 trace diagnostic:

```text
artifact: outputs/analysis/PHASE2_STAGE_C7_TRACE_AND_SWING_BALANCE_PLUMBING.md
status: PASS_SWING_BALANCE_PLUMBING
```

Comparing a passing C7 seed (`2`) to a low-progress seed (`4`) showed the
failure mechanism directly:

```text
seed 2: 18.8% single support, 33 support transitions, 3 left swing segments, 7 right swing segments
seed 4: 4.0% single support, 13 support transitions, 0 left swing segments, 2 right swing segments
```

The failing seed almost never exits double support and never swings the left
foot. A default-off `forward_swing_balance` hook was added to penalize
one-sided swing usage over a forward-command window, with RDK wrapper and eval
plumbing. A tiny CPU smoke passed. The next C-stage run may test this hook, but
it must still use gate-selected checkpoints and corrected terrain metrics.

C8 tested that hook:

```text
artifact: outputs/analysis/PHASE2_STAGE_C8_SWING_BALANCE_DECISION.md
screen: outputs/analysis/PHASE2_STAGE_C8_TERRAIN_Z002_SCREEN_CPU.md
status: HOLD_STAGE_C8_SWING_BALANCE_TOO_STRONG
```

C8 used the same C7-style gate-selected terrain recipe with:

```text
forward_swing_balance_scale: -0.05
forward_swing_balance_grace_steps: 20
```

It completed training, but all trained checkpoints held for low forward
progress on the focused seed-0 screen. The best trained checkpoint was worse
than C7's early transient:

```text
c7_35120 seed 0: track ratio 0.2606, single support 11.2%, min swing peak 0.0104 m
c8_35120 seed 0: track ratio 0.1819, single support 6.8%, min swing peak 0.0084 m
```

Decision: do not promote C8. The hook has leverage, but this balance pressure
pushes the policy toward lower motion rather than balanced stepping. Do not
increase this scalar pressure. Use it only with a target that first preserves
motion, or with a much weaker value after a higher-clearance target source is
available.

After C8, the evaluator was extended with passive swing-excursion metrics:

```text
artifact: outputs/analysis/PHASE2_TERRAIN_SWING_EXCURSION_METRICS.md
status: PASS_SWING_EXCURSION_METRICS_ADDED
```

The standard seed-sweep report now includes:

```text
min_swing_segments
min_rel_x_range_p95
```

The corrected C7 pass/fail trace comparison now reads:

```text
seed 2 pass: min_swing_segments 3, min_rel_x_range_p95 0.0059 m, track ratio 0.3577
seed 4 hold: min_swing_segments 0, min_rel_x_range_p95 0.0000 m, track ratio 0.1918
```

Future terrain gates should treat these as first-class diagnostics. A policy
that passes tracking by keeping one foot effectively planted is still a terrain
hold, even if actuator tracking p95 is below threshold.

The seed-sweep tool now also supports default-off hard terrain swing gates:

```text
artifact: outputs/analysis/PHASE2_TERRAIN_SWING_HARD_GATE_PLUMBING.md
status: PASS_TERRAIN_SWING_HARD_GATE_PLUMBING
flags:
  --min-swing-segments-per-foot
  --min-swing-rel-x-range-p95-m
  --min-swing-peak-lift-m
```

When these flags are set, a nominal `PASS_CANDIDATE_SIM_GATE` can be downgraded
to `HOLD_CANDIDATE_TERRAIN_SWING`. A downgrade-path validation intentionally
set `min_swing_peak_lift_m=0.02` and correctly downgraded C7 seed 2 from a
nominal pass to `HOLD_CANDIDATE_TERRAIN_SWING`.

Action-gain terrain diagnostic:

```text
artifact: outputs/analysis/PHASE2_TERRAIN_ACTION_GAIN_DIAGNOSTIC.md
status: HOLD_ACTION_GAIN_NOT_TERRAIN_FIX
tested gains: 1.05, 1.10
```

Small global action-gain increases on C7 `35120` do not fix the terrain/carpet
failure. At gain `1.05`, seed 2 still passed but seed 4 stayed planted with
`0` min swing segments, `0.0000 m` min relative-x swing range, `0.0016 m` min
swing peak lift, `0.8%` single support, and `99.2%` double support. At gain
`1.10`, even seed 2 regressed to low forward progress. Both tests stayed inside
the corrected velocity envelope, so the issue is stance/swing structure rather
than insufficient global action amplitude.

Forward swing-advance plumbing:

```text
artifact: outputs/analysis/PHASE2_FORWARD_SWING_ADVANCE_PLUMBING.md
status: PASS_FORWARD_SWING_ADVANCE_PLUMBING
```

The Playground and RDK training wrapper now expose a default-off
`forward_swing_advance` cost. It tracks each foot's forward position in the
body/IMU frame at stance and penalizes touchdown if the swing foot did not
advance at least the configured target distance in the commanded direction. A
tiny CPU smoke on `rough_terrain_backlash --terrain-hfield-z-scale 0.002`
passed with `forward_swing_advance_scale=-0.001`,
`forward_swing_advance_target_m=0.005`, and
`forward_swing_advance_huber_delta=0.002`.

Use this as a direct step-advance pressure in the next C-stage terrain branch,
with gate-selected checkpoints and the hard terrain swing gate enabled. Do not
increase global action gain as the terrain fix.

C9 tested the hook:

```text
artifact: outputs/analysis/PHASE2_STAGE_C9_SWING_ADVANCE_DECISION.md
screen: outputs/analysis/PHASE2_STAGE_C9_TERRAIN_Z002_SCREEN_CPU.md
status: HOLD_STAGE_C9_SWING_ADVANCE_RETREATS_TO_LOW_PROGRESS
```

C9 warm-started from C7 `35120` and added
`forward_swing_advance_scale=-0.01`, target `0.005 m`, and Huber delta
`0.002`. Training completed on local GPU and preserved corrected-envelope
compliance, but all trained checkpoints regressed the pass-like seed 2 to low
forward progress and never recovered the planted-foot seed 4. Seed 4 stayed at
`0` min swing segments for every checkpoint.

Decision: keep the hook, but do not promote C9 and do not simply increase
scalar swing-advance pressure. The next terrain branch needs a
higher-clearance alternating-step target source or a hard step-advance
constraint that cannot be satisfied by retreating into double support.

Terrain target-source preflight:

```text
artifact: outputs/analysis/PHASE2_TERRAIN_TARGET_SOURCE_DECISION.md
gate: outputs/analysis/PHASE2_FOOT_PLACEMENT_MPC_ROUGH_PREFLIGHT_GATE.md
status: HOLD_TERRAIN_TARGET_SOURCE_NOT_READY
```

The existing finite-horizon foot-placement MPC teacher was run as a bounded
rough-terrain target-source preflight on `rough_terrain_backlash`, seeds `2,4`,
for `3 s`, with a `2.5 rad/s` teacher-side velocity cap. It remained
actuator-safe and laterally calm. The target-source scorer now also supports
optional hard step-transition gates:

```text
min_swing_segments_per_foot: 1
min_swing_rel_x_range_p95_m: 0.003
min_swing_peak_lift_m: 0.005
```

With those gates enabled, the rough-terrain preflight scored:

```text
100-sample score: HOLD_NO_SEED_ROBUST_TARGETS
150-sample score: HOLD_NO_SEED_ROBUST_TARGETS
weight-transfer gate: HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET
best seed-2 vx: 0.0046-0.0079 m/s
seed-2 hard swing metrics: 1 segment, 0.0041-0.0051 m rel-x range,
                           0.0084-0.0093 m peak lift
seed-4 hard swing metrics: 0 segments, 0.0000 m rel-x range, no peak lift
dominant failures: low_forward_velocity, double_support_dominates,
                   too_little_single_support, single_support_not_balanced
```

This rules out the current MPC teacher as a ready terrain target source. The
next offline path should be structural: either a hard step-transition teacher
whose gate requires per-foot swing segments and touchdown advance, or a
higher-clearance alternating-step source re-mined from the corrected-bridge
walker before any further PPO/BC.

C7 terrain-height threshold check:

```text
artifact: outputs/analysis/PHASE2_STAGE_C7_35120_TERRAIN_Z001_SWING_GATE_CPU.md
status: HOLD_CANDIDATE_TERRAIN_SWING
```

The current best C7 checkpoint was re-evaluated at `terrain_hfield_z_scale=0.001`
with the same hard terrain swing gate. Seed 2 passed, but seed 4 still failed
the swing gate:

```text
seed 2: PASS, track ratio 0.3457, min swing segments 1,
        min rel-x range p95 0.0063 m
seed 4: HOLD, track ratio 0.2539, min swing segments 0,
        min rel-x range p95 0.0000 m
```

So the planted-seed failure is not only a `z=0.002` roughness-threshold issue.
It appears even at half roughness. The next stage should not keep reducing
terrain height as the main fix; it should make alternating swing/advance
structurally unavoidable across seeds.

Next branch spec:

```text
docs/PHASE2_NEXT_TERRAIN_STEP_BRANCH.md
status: PRE_REGISTERED_NOT_STARTED
```

This branch closes scalar terrain reward sweeps for now. It requires a hard
step-transition source/candidate gate before another PPO/BC run.

Stage D:

- rough hfield terrain
- stronger pushes
- still reject any policy exceeding corrected per-joint envelope

## Gate

Every stage must pass before advancing:

```text
x=0.08:
  seeds: 8/8
  falls: 0
  corrected velocity excess: 0.0
  max pitch-chain tracking p95 <= 0.20 rad
  track ratio >= 0.40

x=0.0:
  seeds: 8/8
  falls: 0
  mean |vx| <= 0.005 m/s
```

Additional required reports:

- mean speed / track ratio
- push recovery success rate
- terrain success rate
- foot clearance / swing peak
- per-foot swing segment count and relative-foot excursion
- action saturation
- per-joint target velocity vs corrected envelope

## Current Packaged Candidate

The current best offline Phase 2 sim candidate is the packaged gain-0.99 ONNX:

```text
candidate:
  policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx

candidate_sha256:
  209b85a75cf9cbbcf10df573c1b530921943a72e81082111889c15f63a9a2c7b

source_candidate:
  policy/candidates/phase2_stagea2_seed5_recovery_command_gated_20260628/candidate.onnx

transform:
  final ONNX output action scale = 0.99
```

This is a real deployable ONNX packaging step, not an evaluator-side gain. The
scale check passed exactly:

```text
artifact:
  policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/onnx_scale_verify.json

status:
  PASS_ONNX_OUTPUT_SCALE_VERIFY
```

Corrected-bridge rough `z=0.002` gates:

```text
artifact:
  outputs/analysis/PHASE2_STAGEA2_GAIN099_PACKAGED_CANDIDATE_DECISION.md

status:
  PASS_PACKAGED_GAIN099_ROUGH_Z002_PUSH_AND_NOPUSH_SIM_GATES

x=0.08, no push:
  PASS 8/8
  mean track ratio: 0.4053
  max tracking p95: 0.1975 rad
  max velocity excess: 0.0000 rad/s

x=0.0, no push:
  PASS 8/8
  mean vx: 0.0007 m/s
  max tracking p95: 0.0663 rad

x=0.08, gentle push:
  PASS 8/8
  mean track ratio: 0.4104
  mean push success: 0.9704
  max tracking p95: 0.1944 rad
  max velocity excess: 0.0000 rad/s

x=0.0, gentle push:
  PASS 8/8
  mean vx: 0.0007 m/s
  mean push success: 0.9704
  max tracking p95: 0.0687 rad
```

This candidate is therefore the current best reviewed rough `z=0.002`
gentle-push offline sim candidate. It is not robot-approved and does not
complete the full Phase 2 terrain curriculum.

Rougher terrain boundary:

```text
artifact:
  outputs/analysis/PHASE2_STAGEA2_GAIN099_TERRAIN_Z005_BOUNDARY.md

status:
  HOLD_TERRAIN_Z005_SEED5_FALL

configuration:
  task: rough_terrain_backlash
  terrain_hfield_z_scale: 0.005
  command_x: 0.08
  pushes: disabled

result:
  PASS 7/8
  seed 5 fall at 56 samples
  seed 5 mean vx: -0.2654 m/s
  seed 5 base height min: 0.0677 m
  max velocity excess: 0.0000 rad/s
```

Focused seed-5 trace analysis:

```text
artifact:
  outputs/analysis/PHASE2_STAGEA2_GAIN099_Z005_SEED5_TRACE_ANALYSIS.md
json:
  outputs/analysis/phase2_stagea2_gain099_z005_seed5_trace_analysis.json

status:
  HOLD_TERRAIN_Z005_SEED5_BACKWARD_PITCH_COLLAPSE
```

The failing seed stays inside the corrected actuator gate:

```text
max pitch-chain sent velocity p95:     1.9284 rad/s
max pitch-chain tracking p95:          0.1533 rad
corrected envelope excess:             0.0000 rad/s
```

The failure is instead a support/contact timing boundary:

```text
double support:       91.1%
single support:        7.1%
body pitch min:       -1.4489 rad
last local vx:        -1.4738 m/s
```

Next Phase 2 work should target seed-5 rough-terrain support timing and
backward-pitch reversal between `z=0.002` and `z=0.005`, not actuator-envelope
relaxation or global action-gain increases.

The next z=0.005 support-stability recipe has been pinned and CPU-plumbed:

```text
artifact:
  outputs/analysis/PHASE2_STAGEA2_GAIN099_Z005_SUPPORT_STABILITY_NEXT_RUN.md
json:
  outputs/analysis/phase2_stagea2_gain099_z005_support_stability_next_run.json

status:
  PASS_Z005_SUPPORT_STABILITY_RECIPE_CPU_PLUMBING
```

This tiny CPU check restored the Stage A2 trainable checkpoint, patched
`rough_terrain_backlash` to `z=0.005`, used the corrected bridge range
`2.0-3.25 rad/s`, reached PPO step 20, saved a temporary checkpoint under
`/tmp`, and restored the Playground XML hash afterward. It is not a policy
result. Use the recipe only as the next bounded GPU training run when a stable
CUDA/A100 or equivalent session is available.

The Colab helper exposes this as an explicit workflow:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow phase2-z005-support \
  --session <visible-colab-session> \
  --candidate-name phase2_z005_support_stability_cuda \
  --candidate-checkpoint-sweep \
  --candidate-checkpoint-sweep-commands 0.0,0.08 \
  --candidate-checkpoint-sweep-duration 1.0 \
  --candidate-checkpoint-sweep-jax-platform cpu \
  --candidate-timeout-s 10800 \
  --run
```

Plan-only generation now writes the remote driver locally for review. A dry-run
inspection confirmed the generated workflow uses:

```text
restore checkpoint:
  stage_a2_preserve_narrow_flat_no_push_gpu/.../2026_06_27_232221_491520
push mode:
  --no-push-enable
terrain:
  --terrain-hfield-z-scale 0.005
corrected bridge:
  delay 3-3 ticks
  tau 0.06-0.14 s
  velocity limit 2.0-3.25 rad/s
  per-joint variation 0.10
```

The `phase2-z005-support` remote driver now automatically runs full
post-training seed gates on the selected ONNX after the optional short
checkpoint sweep. These gates are offline sim only and are bundled even if one
gate holds:

```text
z=0.005 immediate target:
  x=0.08 no-push, 8 seeds, 15s
  x=0.0  no-push, 8 seeds, 15s

z=0.002 regression checks:
  x=0.08 no-push, 8 seeds, 15s
  x=0.0  no-push, 8 seeds, 15s
  x=0.08 gentle-push, 8 seeds, 15s
  x=0.0  gentle-push, 8 seeds, 15s
```

Expected remote artifacts:

```text
outputs/analysis/phase2-z005-support/
  phase2_z005_support_stability_cuda_post_training_seed_gates.json
  phase2_z005_support_stability_cuda_POST_TRAINING_SEED_GATES.md
  phase2_z005_support_stability_cuda_<gate_name>_seed_gate/
```

Promotion still requires reviewing the full-duration seed gates. The
one-second checkpoint sweep is only a checkpoint selector, not a robustness
gate and not a robot-validation approval.

### z=0.005 Local ROCm Attempt

Artifact:

```text
outputs/analysis/PHASE2_Z005_SUPPORT_LOCAL_ROCM_HOLD.md
outputs/analysis/phase2_z005_support_local_rocm_hold.json
```

Status:

```text
HOLD_FULL_LOCAL_ROCM_COMPILE_NO_PROGRESS
```

With no active Colab/A100 session visible, bounded local ROCm attempts of the
same `phase2-z005-support` recipe were launched. The first full-shape attempt
forced `HSA_OVERRIDE_GFX_VERSION=11.0.0` and failed before any PPO step or ONNX
export:

```text
returncode: -6
stderr: Check failed: Failed setting context: hipError_t(719)
```

A basic JAX ROCm arithmetic test immediately after the abort still passed, and
a no-override tiny same-recipe smoke reached PPO step `320`, exported ONNX, and
returned `PASS_SMOKE_RUN`. The full-shape no-override run then stayed GPU-busy
for more than 12 minutes without reaching first checkpoint or moving its output
files, so it was interrupted and recorded as a local full-shape practicality
hold. No child process was left running and the terrain XML restored to hash
`879768817f5ae5d2c01b5494f855686bb10d1ec444a404efeced8f5766574ffc`.

Treat this as backend evidence, not a policy result. For local ROCm, do not set
`HSA_OVERRIDE_GFX_VERSION`. For the actual policy-producing run, use the pinned
A100/Colab workflow when a visible session is available.

### z=0.005 Local ROCm Command-Buffer Result

Artifact:

```text
outputs/analysis/PHASE2_Z005_LOCAL_ROCM_COMMAND_BUFFER_RESULT.md
outputs/analysis/phase2_z005_local_rocm_command_buffer_result.json
```

Status:

```text
HOLD_LOCAL_8ENV_LOW_FORWARD_PROGRESS
```

A reduced local ROCm run with `8` envs and `20480` timesteps failed without
extra XLA flags due to GPU graph capture:

```text
rocblas_gemm_strided_batched_ex failed with rocblas_status_internal_error
```

The same reduced run completed when command buffers were disabled:

```text
XLA_FLAGS=--xla_gpu_enable_command_buffer=
HSA_OVERRIDE_GFX_VERSION unset
checkpoints: 7680, 15360, 23040
status: PASS_SMOKE_RUN
```

The workaround did not make the local ROCm path reliable for longer training.
An `8`-env `81920`-timestep attempt with the same command-buffer flag failed
before the first PPO step during evaluator reset:

```text
output_dir: outputs/phase2_domain_randomization/stage_z005_support_local_rocm_no_override_8env_81920_nocmdbuf/smoke_20260629T170558Z_gpu
status: HOLD_SMOKE_RUN
error: rocblas_gemm_strided_batched_ex failed with rocblas_status_internal_error
```

`tools/run_actuator_bridge_training_smoke.py` now has a recorded local ROCm
environment preset so local attempts do not depend on unrecorded shell state:

```text
--platform gpu
--local-rocm-safe-env
```

That preset expands to:

```text
--jax-platforms rocm
--xla-flags=--xla_gpu_enable_command_buffer=
--xla-python-client-preallocate false
--xla-python-client-mem-fraction 0.60
--unset-hsa-override-gfx-version
```

These values are written to each run manifest under `subprocess_env`. Keep using
the pinned A100/Colab path for policy-producing Phase 2 runs unless a local ROCm
run with these recorded settings clears the full post-training gates.

The latest ONNX from that run was then checked on the immediate `z=0.005`,
`x=0.08`, corrected-bridge gate. Seed 0 already held on low forward progress:

```text
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
track_ratio: 0.2234
mean vx: 0.0179 m/s
max tracking p95: 0.1948 rad
```

The reduced local run is therefore useful backend evidence but not a policy
promotion. Do not robot-test it. The next policy-producing attempt should still
use the pinned A100/Colab `phase2-z005-support` workflow when a visible session
is available, or a local ROCm recipe explicitly built around the command-buffer
workaround and then gated from scratch.

## Current Terrain-Step Status

Existing-trace hard-step rescoring found a useful split:

```text
artifact: outputs/analysis/PHASE2_EXISTING_TRACE_HARD_STEP_SOURCE_RESCORE.md
status: PASS_HARD_STEP_SOURCE_FOUND
best source: live-oracle DAgger iteration 1 flat fitted-bridge traces
seed 2: mean vx 0.0571, sent vel p95 2.2257, tracking p95 0.1818
seed 4: mean vx 0.0544, sent vel p95 2.2291, tracking p95 0.1809
```

That confirms the flat corrected-bridge trace library contains hard-step windows
for both seeds. However, the corresponding live-oracle iteration 0 candidate
does not transfer to `rough_terrain_backlash` at
`terrain_hfield_z_scale=0.001`:

```text
artifact: outputs/analysis/PHASE2_LIVE_ORACLE_ITER0_TERRAIN_Z001_SWING_GATE_CPU.md
status: HOLD_CANDIDATE_TRACKING
seed 2: max pitch vel p95 3.5739, velocity excess 0.8239, tracking p95 0.2545
seed 4: max pitch vel p95 3.5845, velocity excess 0.8345, tracking p95 0.2590
```

Window-level terrain rescoring found the missing source signal:

```text
artifact: outputs/analysis/PHASE2_LIVE_ORACLE_ITER0_TERRAIN_Z001_WINDOW_SOURCE_SCORE.md
status: PASS_TERRAIN_WINDOW_SOURCE
seed 2: mean vx 0.0560, sent vel p95 2.1892, tracking p95 0.1764
seed 4: mean vx 0.0493, sent vel p95 1.9976, tracking p95 0.1714

artifact: outputs/analysis/PHASE2_LIVE_ORACLE_ITER0_TERRAIN_Z002_WINDOW_SOURCE_SCORE.md
status: PASS_TERRAIN_WINDOW_SOURCE
seed 2: mean vx 0.0558, sent vel p95 2.0902, tracking p95 0.1788
seed 4: mean vx 0.0532, sent vel p95 2.2194, tracking p95 0.1704
```

Current Phase 2 branch state: terrain-safe hard-step windows exist at both
`z=0.001` and `z=0.002`, but the full candidate still contains bad segments
that exceed the corrected envelope/tracking gate. Next work should build a
terrain-window source manifest or live-oracle relabel pass from those windows,
then train/fine-tune against that curated source rather than promoting the raw
policy.

Canonical curated source manifest:

```text
outputs/analysis/PHASE2_TERRAIN_SAFE_HARD_STEP_SOURCE_MANIFEST.md
outputs/analysis/phase2_terrain_safe_hard_step_source_manifest.json
status: PASS_TERRAIN_SAFE_HARD_STEP_SOURCE_MANIFEST
```

A first 400-sample terrain-window BC smoke fit was intentionally small and
diagnostic:

```text
artifact: outputs/analysis/PHASE2_TERRAIN_SAFE_HARD_STEP_BC_STUDENT.md
fit status: PASS_PPO_LOC_BC_FIT_SMOKE
fit p95 action error: 0.008626
ONNX fidelity p95 error: 0.00000022

closed-loop artifact:
outputs/analysis/PHASE2_TERRAIN_SAFE_HARD_STEP_BC_STUDENT_TERRAIN_Z002_GATE_CPU.md
closed-loop status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
seed 2: vx 0.0048, track ratio 0.0596, max velocity excess 2.7400
seed 4: vx 0.0059, track ratio 0.0742, max velocity excess 2.7400
```

This confirms the known compression problem: a small memoryless BC model can fit
the curated slice actions, but closed-loop rollout collapses to low progress and
over-envelope target spikes. Do not promote this BC ONNX. The next student step
needs live relabel/DAgger or memory/phase, not plain 400-sample BC.

A small recurrent BC diagnostic was also run on the same 400-sample manifest:

```text
artifact: outputs/analysis/PHASE2_TERRAIN_SAFE_HARD_STEP_RECURRENT_BC_STUDENT.md
fit status: PASS_RECURRENT_BC_FIT_SMOKE
fit p95 action error: 0.040416

closed-loop artifact:
outputs/analysis/PHASE2_TERRAIN_SAFE_HARD_STEP_RECURRENT_BC_STUDENT_TERRAIN_Z002_GATE_CPU.md
closed-loop status: HOLD_CANDIDATE_FALL_OR_TERMINATION
seed 2: fall at 84 samples, mean vx -0.1820, max velocity excess 3.2400
seed 4: fall at 46 samples, mean vx -0.3372, max velocity excess 3.2400
```

This falsifies the cheapest recurrence-only rescue on the tiny terrain-window
dataset. The source windows are valid, but the student needs more on-policy/live
coverage or a teacher/relabel loop, not just a small recurrent fit to four
snippets.

The terrain live-oracle DAgger loop was then enabled for rough-terrain hfield
scale and hard x=0.08 swing gates:

```text
tool update: tools/run_live_oracle_dagger_iteration.py
new args: --terrain-hfield-z-scale,
          --min-swing-segments-per-foot,
          --min-swing-rel-x-range-p95-m,
          --min-swing-peak-lift-m
```

Three bounded offline iterations were run from the failed terrain BC student:

```text
artifact: outputs/analysis/PHASE2_TERRAIN_LIVE_ORACLE_DAGGER_DECISION.md
status: HOLD_TERRAIN_LIVE_ORACLE_DAGGER_TRACKING_PLATEAU

iter 0: seed 2 froze in-envelope; seed 4 still over tracking/envelope
iter 1: progress recovered, but tracking/envelope held
iter 2: stronger progress, same tracking/envelope plateau
```

Best current live-oracle result on `rough_terrain_backlash`, `z=0.002`,
corrected bridge, seeds `2,4`:

```text
iter 2 seed 2: vx 0.0526, track ratio 0.6570,
               velocity excess 0.8704, tracking p95 0.2533
iter 2 seed 4: vx 0.0459, track ratio 0.5736,
               velocity excess 0.8938, tracking p95 0.2527
```

Current interpretation: live/on-policy relabel coverage fixes the standstill
side of the failure, but the current oracle labels remain too aggressive for
the corrected terrain gate. Do not run more identical DAgger iterations as the
next move. The next branch should make the relabel/training target
tracking-aware: filter or rate-limit oracle labels, or switch to PPO fine-tuning
with explicit corrected-envelope penalties.

Later transition-preserving diagnostics narrowed the rough-terrain blocker
further. Transition-protected rate limiting broke the tracking/envelope plateau
but left seed 4 planted. Targeted right-swing/contact-phase work then recovered
the local seed-4 rough swing, but the branch exposed a command-independent
seed-5 early-state failure.

The latest feed-forward representation diagnostic is recorded here:

```text
decision:
  outputs/analysis/PHASE2_SEED5_EARLY_STATE_CONTACTPHASE_DECISION.md

status:
  HOLD_CONTACTPHASE_SEED5_STILL_FALLS
```

Adding contact bits to the phase/command modulation context
(`obs[6,97,98,99,100]`) preserved the deployable `obs[1,101] -> action[1,14]`
contract and improved some rough-terrain distribution details, but it did not
recover the seed-5 early-state failure:

```text
x=0.08 rough z=0.002: 5/8 pass
seed 5 x=0.08: fall/reverse hold
seed 5 x=0.0: fall at 43 samples
```

This closes the cheapest contact-conditioned feed-forward rung. The next
useful branch needs explicit state/history or a recovery teacher for seed 5's
first contact transition, not another minor BC weighting/context tweak.

A stateful recurrent diagnostic was also run on the same seed-5 aggregate:

```text
decision:
  outputs/analysis/PHASE2_SEED5_EARLY_STATE_RECURRENT_DECISION.md

status:
  HOLD_RECURRENT_SEED5_STILL_FALLS
```

The recurrent ONNX is diagnostic-only (`obs,h_in -> action,h_out`) and is not
robot-deployable. It still fell on seed 5 at x=0.08 rough z=0.002 after 48
samples with negative velocity and corrected-envelope excess. This closes the
cheap memory-only test on the current dataset; the next useful branch is a
recovery teacher/relabel pass for seed 5's first contact transition.

## References

Verified from arXiv:

- `2512.01996`, *Learning Sim-to-Real Humanoid Locomotion in 15 Minutes*:
  supports the broad recipe of massive parallel humanoid RL, randomized
  dynamics, rough terrain, and push perturbations on Unitree G1 / Booster T1.
- `2502.12152`, *Learning Getting-Up Policies for Real-World Humanoid Robots*:
  supports an easy-to-hard two-phase refinement idea for real-world G1
  deployment under varied terrains and surfaces.

Reference caveat:

- `2511.12390` resolves to neural teleoperation, not the concrete locomotion DR
  range paper described in the prompt.
- `2505.17627` resolves to H2-COMPACT co-manipulation with randomized payloads
  and friction, not a pure per-episode locomotion DR recipe.

The requested numeric ranges are therefore carried as project-configured ranges
for this branch: friction `0.5-1.25`, mass `+/-10%`, small COM perturbations,
control latency, observation noise, push perturbations, and easy-to-hard
terrain. Do not cite `2511.12390` or `2505.17627` as direct support for those
exact locomotion ranges without a later primary-source check.

## Stage-A2 / Seed5-Recovery Command Gate

Artifact:

```text
decision:
  outputs/analysis/PHASE2_SEED5_NEIGHBOR_RECOVERY_STAGEA2_COMMAND_GATED_DECISION.md

candidate:
  policy/candidates/phase2_stagea2_seed5_recovery_command_gated_20260628/candidate.onnx

candidate_sha256:
  d0cec0b9dcc666416f0ecc8383a51367529273013d912b26399339e2c4b1c3e6

status:
  PASS_ROUGH_TERRAIN_NO_PUSH_HOLD_GENTLE_PUSH_ENVELOPE
```

The seed5 neighbor-recovery contact/phase student fixed the rough `x=0.08`
hard seed but failed rough `x=0.0`. A deployable ONNX command gate was then
tested:

```text
abs(obs[6]) <= 0.02:
  policy/candidates/phase2_stage_a2_gain099_20260628/candidate.onnx

abs(obs[6]) > 0.02:
  outputs/analysis/phase2_seed5_neighbor_recovery_contactphase_bc_student/candidate.onnx
```

The wrapper preserves the deployed `obs[1,101] -> continuous_actions[1,14]`
contract and verified with zero action error against the selected branch.

No-push rough-terrain result (`rough_terrain_backlash`, `z=0.002`, corrected
bridge, 5 s, seeds 0-7):

```text
x=0.08: PASS_CANDIDATE_SIM_GATE 8/8
  falls: 0/8
  mean vx: 0.0332 m/s
  mean track ratio: 0.4150
  max pitch-chain p95 target velocity: 2.4109 rad/s
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1984 rad
  min swing peak lift: 0.0108 m

x=0.0: PASS_CANDIDATE_SIM_GATE 8/8
  falls: 0/8
  mean vx: 0.0024 m/s
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1056 rad
```

Gentle-push rough-terrain diagnostic (`push interval 1.0-1.5 s`, magnitude
`0.05-0.10`) showed stability but not a clean moving promotion:

```text
x=0.08: HOLD_CANDIDATE_TARGET_VELOCITY
  falls: 0/8
  mean push recovery success: 0.9062
  max velocity excess: 0.0212 rad/s
  max tracking p95: 0.1964 rad

x=0.0: PASS_CANDIDATE_SIM_GATE 8/8
  falls: 0/8
  mean push recovery success: 0.9062
  max velocity excess: 0.0000 rad/s
```

Interpretation: this is the first command-conditioned deployable-shape
rough-terrain `z=0.002` no-push pass in this branch. It is not yet a robust
push candidate because the moving gentle-push gate has a small corrected
envelope excess on one seed. The next Phase 2 step should reduce perturbation
target-rate margin or fine-tune from this command-gated artifact with push
perturbations active.

Command-scale diagnostic:

```text
artifact:
  outputs/analysis/PHASE2_SEED5_NEIGHBOR_RECOVERY_STAGEA2_COMMAND_SCALE_0P99_DIAGNOSTIC.md

status:
  HOLD_CMDSCALE_FIXES_PUSH_ENVELOPE_BREAKS_NOPUSH_SWING
```

A high-command `0.99` scale cleared the `x=0.08` gentle-push envelope hold:

```text
x=0.08 gentle push: PASS_CANDIDATE_SIM_GATE 8/8
  mean track ratio: 0.4029
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1985 rad
```

But the same scaled wrapper failed the standard no-push terrain swing gate:

```text
x=0.08 no push: HOLD_CANDIDATE_TERRAIN_SWING
  seed 3 min swing rel-x p95 range: 0.0025 m
  required: 0.0030 m
```

Therefore global high-command attenuation is not the promotion fix. The next
step should preserve no-push swing geometry while adding perturbation-specific
target-rate margin.

Additional eval-only gain screens bracketed the same tradeoff:

```text
gain 0.997 x=0.08 gentle push:
  HOLD_CANDIDATE_TARGET_VELOCITY on seed 5
  HOLD_CANDIDATE_TRACKING on seed 7

gain 0.995 x=0.08 gentle push:
  HOLD_CANDIDATE_TRACKING on seed 7
  max tracking p95 0.2005 rad
```

Full-horizon eval-only gain diagnostic:

```text
artifact:
  outputs/analysis/PHASE2_GAIN099_EVAL_ONLY_ROUGH_PUSH_15S_DECISION.md

status:
  PASS_EVAL_ONLY_GAIN099_ROUGH_PUSH_15S_NOT_DEPLOYABLE

policy_action_gain:
  0.99

x=0.08 rough z=0.002 gentle push, 15 s:
  PASS_CANDIDATE_SIM_GATE 8/8
  falls: 0/8
  mean track ratio: 0.4104
  max pitch-chain p95 target velocity: 2.3950 rad/s
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1944 rad
  mean push success: 0.9704

x=0.0 rough z=0.002 gentle push, 15 s:
  PASS_CANDIDATE_SIM_GATE 8/8
  falls: 0/8
  mean vx: 0.0007 m/s
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.0687 rad
  mean push success: 0.9704
```

This is the strongest rough-terrain gentle-push diagnostic so far, but it is
not a deployable promotion because `policy_action_gain=0.99` is an evaluator
multiplier. The next deployable check is to package a real gain-0.99 candidate
or remove the evaluator-only multiplier, then re-run the canonical no-push and
gentle-push gates.

Packaged gain-0.99 candidate:

```text
candidate:
  policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx

candidate_sha256:
  209b85a75cf9cbbcf10df573c1b530921943a72e81082111889c15f63a9a2c7b

decision:
  outputs/analysis/PHASE2_STAGEA2_GAIN099_PACKAGED_CANDIDATE_DECISION.md

status:
  PASS_PACKAGED_GAIN099_ROUGH_Z002_PUSH_AND_NOPUSH_SIM_GATES
```

The `0.99` action scale was baked into the ONNX graph and verified:

```text
policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/onnx_scale_verify.json
status: PASS_ONNX_OUTPUT_SCALE_VERIFY
max_abs_error: 0.0
```

The packaged candidate was then re-gated with `policy_action_gain=1.0`:

```text
x=0.08 no-push rough z=0.002, 15 s:
  PASS_CANDIDATE_SIM_GATE 8/8
  falls: 0/8
  mean track ratio: 0.4053
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1975 rad

x=0.0 no-push rough z=0.002, 15 s:
  PASS_CANDIDATE_SIM_GATE 8/8
  falls: 0/8
  mean vx: 0.0007 m/s
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.0663 rad

x=0.08 gentle-push rough z=0.002, 15 s:
  PASS_CANDIDATE_SIM_GATE 8/8
  falls: 0/8
  mean track ratio: 0.4104
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1944 rad
  mean push success: 0.9704

x=0.0 gentle-push rough z=0.002, 15 s:
  PASS_CANDIDATE_SIM_GATE 8/8
  falls: 0/8
  mean vx: 0.0007 m/s
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.0687 rad
  mean push success: 0.9704
```

This is the current best offline Phase 2 sim candidate. Do not continue scalar
gain sweeps. Further work should either advance terrain/push curriculum from
this packaged candidate or prepare a reviewed suspended hardware validation
plan; grounded replay remains blocked.

Terrain boundary probe:

```text
artifact:
  outputs/analysis/PHASE2_STAGEA2_GAIN099_TERRAIN_Z005_BOUNDARY.md

status:
  HOLD_TERRAIN_Z005_SEED5_FALL

x=0.08 rough z=0.005 no-push, 15 s:
  PASS_CANDIDATE_SIM_GATE: 7/8
  HOLD_CANDIDATE_FALL_OR_TERMINATION: 1/8
  fall seed: 5
  fall samples: 56
  seed5 mean vx: -0.2654 m/s
  seed5 base height min: 0.0677 m
  max velocity excess: 0.0000 rad/s
```

This confirms the next curriculum boundary: the packaged gain-0.99 candidate is
robust at rough `z=0.002`, but not at `z=0.005`. The next training/eval branch
should target seed-5 rougher-terrain stability rather than increasing actuator
margin or continuing scalar gain sweeps.

## B0E A100 Corrected-Task Run

Artifact:

```text
outputs/analysis/PHASE2_B0E_A100_CORRECTED_TASK_HOLD_DECISION.md
```

Status:

```text
HOLD_B0E_A100_TRACKING_REGRESSION
```

After fixing the CUDA workflow task mismatch, `phase2-b0e` ran on the
`open-duck-a100` A100 session with `rough_terrain_backlash`, corrected bridge,
mild domain randomization, mild pushes, observation noise, and terrain hfield
`z=0.002`. Training completed and exported checkpoints at `81920`, `163840`,
and `245760` steps.

The remote driver became idle during checkpoint sweep without writing its exit
sentinel, so a manual salvage bundle was downloaded:

```text
outputs/analysis/colab_cli/open-duck-a100-phase2-b0e-20260629T092705Z/open_duck_colab_cli_phase2-b0e_20260629T092941Z_manual_salvage.tar.gz
sha256 e683711390fa0997ee3a77970e342981b27c4981d7b7316244eaed2b9f3272c4
```

Short corrected-bridge gate triage:

```text
81920:
  x=0.0  PASS_CANDIDATE_SIM_GATE
  x=0.08 HOLD_CANDIDATE_TRACKING
        track ratio 0.3493
        max pitch tracking p95 0.2208 rad
        max sent velocity p95 1.5536 rad/s
        velocity excess 0.0000 rad/s

163840:
  x=0.0  PASS_CANDIDATE_SIM_GATE
  x=0.08 HOLD_CANDIDATE_TRACKING
        track ratio 0.3402
        max pitch tracking p95 0.2209 rad
        max sent velocity p95 1.5695 rad/s
        velocity excess 0.0000 rad/s

245760:
  x=0.0  PASS_CANDIDATE_SIM_GATE
  x=0.08 HOLD_CANDIDATE_TRACKING
        track ratio 0.3117
        max pitch tracking p95 0.2208 rad
        max sent velocity p95 1.5582 rad/s
        velocity excess 0.0000 rad/s
```

Decision: do not promote B0E. It is stable and in-envelope in the short gate,
but it regresses the moving `x=0.08` tracking margin above the `0.20 rad`
threshold and later checkpoints reduce forward command tracking rather than
recover it. The next robustness attempt should not continue longer from B0E;
use the previous B0C terrain candidate as the gait-preserving baseline and
either isolate perturbation failures with eval-only diagnostics or apply a
smaller adaptation with stronger behavior preservation.

## B0F Pre-Registration

Artifact:

```text
outputs/analysis/PHASE2_B0F_A100_PUSH_LOCAL_PRESERVE_PLAN.md
```

Status:

```text
PRE_REGISTERED_NOT_STARTED
```

B0F is a deliberately smaller follow-up to B0E. It restores the B0C
rough-terrain parent, narrows physics/noise randomization, strengthens behavior
preservation, lowers the PPO learning rate, and trains against frequent gentle
pushes. The goal is not broad DR yet; the goal is to learn a local
perturbation-recovery correction without moving the nominal no-push gait off
the existing pass boundary.

After the `128`-env B0F shape died before writing normal runner artifacts, two
direct A100 probes showed the recipe is valid at smaller scale:

```text
8 env tiny probe:  returncode 0
64 env probe:      returncode 0
```

The named B0F workflow is therefore pinned to `64` envs / batch `512`.

If B0F holds at the same `~0.22 rad` short-gate tracking plateau or reduces
forward command tracking below B0E, do not continue from it. Return to
eval-only perturbation localization or a more explicit push-recovery policy
correction.

### B0F A100 Session Hold

Artifact:

```text
outputs/analysis/PHASE2_B0F_A100_SESSION_LOSS_HOLD_DECISION.md
```

Status:

```text
HOLD_B0F_A100_SESSION_LOST
```

B0F was not trained to a candidate checkpoint. The recipe passed direct
8-env and 64-env A100 probes, but full B0F attempts through the current Colab
session/wrapper path repeatedly died or lost the named session after printing
the training manifest and before writing normal runner stdout/stderr or ONNX
exports. This is a cloud execution-path hold, not a robot result and not a
candidate-policy result.

Next attempt should avoid the detached Colab console path, reduce upload/state
size, or use another stable CUDA runtime before evaluating B0F.

### B0F A100 Direct-Exec Hold

Artifact:

```text
outputs/analysis/PHASE2_B0F_A100_DIRECT_EXEC_HOLD_DECISION.md
```

Status:

```text
HOLD_B0F_LOW_FORWARD_PROGRESS
```

The B0F push-local preserve recipe was rerun on A100 using a direct
`colab exec` path and a reduced upload bundle. Training completed successfully
and produced three checkpoints (`40960`, `81920`, `122880`). All checkpoints
completed both x=0.0 and x=0.08 corrected-bridge sweep commands, but none were
promoted.

The best available checkpoint was step `122880`
(`bbb6f6b73d34951928c89700c99eab94f8bca2ba68e56f645c5d351c721d484b`), but it
held at x=0.08:

```text
track ratio: 0.2411 < 0.2500
mean vx: 0.0193 < 0.0200
max pitch tracking p95: 0.2189 rad
max sent velocity p95: 1.5706 rad/s
action saturation: 0.0%
```

B0F is therefore not a robot candidate. It is in-envelope and non-saturating,
but still below the forward-progress gate and above the strict pitch-tracking
target.

### B0C LK097 Push-Localized Near-Pass

Artifact:

```text
outputs/analysis/PHASE2_B0C_LK097_PUSH_LOCALIZATION_DECISION.md
```

Status:

```text
HOLD_B0C_LK097_PUSH_LOCAL_LEFT_KNEE_MARGIN
```

After the B0F hold, the best current robustness line is still the earlier B0C
left-knee-scale `0.97` candidate:

```text
policy:
  outputs/analysis/phase2_b0c_245_leftknee_scale097_candidate/candidate.onnx

policy_sha256:
  4985f1bccaa68838d006104fb380c50a2f06d8627ff8990564f178c0b0ad7f87
```

A focused seed-4 trace was run under the same rough-terrain `z=0.002` plus
gentle-push conditions that produced the 7/8 near-pass. The candidate remained
upright, in-envelope, and non-saturating:

```text
gate_status: HOLD_CANDIDATE_TRACKING
track_ratio: 0.4285
mean_vx: 0.0343 m/s
progress_x: 0.0423 m
max_pitch_tracking_p95: 0.2013 rad
threshold: 0.2000 rad
max_sent_target_velocity_p95: 1.8002 rad/s
max_velocity_limit_excess: 0.0000 rad/s
action_saturation: 0.0%
body_pitch_abs_p95: 0.1402 rad
base_height_min: 0.1506 m
termination: duration_complete
```

The miss is localized to the left knee:

```text
left_knee joint_tracking_p95: 0.2013 rad
left_knee sent_vel_p95: 1.6354 rad/s
left_knee bridge_tracking_p95: 0.1022 rad
left_knee lag_ticks: 4
```

Push correlation:

```text
push ticks: 57, 115, 173, 231
left_knee high-error ticks near push: 13/13 within +/-25 ticks
left_knee high-error ticks not near push: 0/13
```

Decision: do not continue B0F, scalar gain sweeps, or global target-rate
clipping. The next valid Phase 2 correction should start from the `lk097`
near-pass line and target the localized push-recovery window: preserve the
nominal rough-terrain gait, add push-state or post-push tracking-margin
correction, focus on left-knee recovery, and re-gate on the corrected bridge
rough `z=0.002` gentle-push 8-seed screen before broadening DR.

### Push-Recovery Tracking Hook

Artifact:

```text
outputs/analysis/PHASE2_PUSH_RECOVERY_TRACKING_HOOK.md
```

Status:

```text
PASS_PUSH_RECOVERY_TRACKING_HOOK_PLUMBING
```

The Playground joystick env and RDK training wrapper now expose a default-off
push-recovery actuator-tracking cost. It uses the existing sent-vs-applied
actuator target mismatch, but applies it only for a configurable window after
push impulses and can restrict the cost to selected actuator indices.

RDK wrapper flags:

```text
--push-recovery-actuator-tracking-scale
--push-recovery-actuator-tracking-huber-delta
--push-recovery-tracking-window-steps
--push-recovery-tracking-joint-indices
```

A tiny CPU smoke from the B0C restore checkpoint passed with:

```text
push_recovery_actuator_tracking_scale: -0.02
push_recovery_actuator_tracking_huber_delta: 0.03
push_recovery_tracking_window_steps: 25
push_recovery_tracking_joint_indices: 3
status: PASS_SMOKE_RUN
```

This does not promote a policy. It only creates the missing localized lever for
the next Phase 2 run: preserve the `lk097` rough-terrain gait while improving
left-knee post-push recovery margin, then re-gate on corrected bridge rough
`z=0.002` gentle-push 8-seed screens.

The named A100 workflow for that follow-up is:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow phase2-b0g \
  --session <visible-a100-session> \
  --candidate-checkpoint-sweep \
  --candidate-checkpoint-sweep-commands 0.0,0.08 \
  --candidate-checkpoint-sweep-duration 1.0 \
  --candidate-checkpoint-sweep-jax-platform cpu \
  --run
```

At the time this hook was added, no active Colab session was available, so B0G
was not launched.

### B0G Local ROCm Smoke

Artifact:

```text
outputs/analysis/PHASE2_B0G_20480_LOCAL_ROCM_HOLD_DECISION.md
```

Status:

```text
HOLD_B0G_20480_TRACKING_REGRESSION
```

A bounded local ROCm B0G smoke was run on the RX 7900 XTX with the new
push-recovery left-knee tracking hook enabled:

```text
jax: 0.8.2
ppo_num_envs: 32
ppo_episode_length: 100
step: 20480
onnx_sha256: 70fde5e93cfe7252ef14d8c953e9015051cde1747806f24adf2274f022491473
status: PASS_SMOKE_RUN
```

The exported ONNX was gated on CPU for rough `z=0.002` gentle-push `x=0.08`
8-seed correctness:

```text
passes: 4/8
tracking holds: 4/8
falls: 0/8
mean track ratio: 0.4423
mean vx: 0.0354 m/s
max tracking p95: 0.2046 rad
max velocity excess: 0.0000 rad/s
mean push recovery success: 0.9062
```

This is backend progress but not policy progress. The local 7900 XTX can run a
small B0G shape with the hook, but the resulting checkpoint regressed the gate
relative to the B0C `lk097` 7/8 near-pass, and seed 4 remained at the same
`~0.2013 rad` tracking miss. Do not promote B0G `20480` and do not replace the
`lk097` line with it. A full B0G attempt still belongs on the pinned A100
workflow when a visible Colab session is available, or on local ROCm only with
the caveat that the local stack is JAX `0.8.2`, not the pinned A100 `0.7.2`.

### Local ROCm Post-B0G Backend Hold

Artifact:

```text
outputs/analysis/PHASE2_LOCAL_ROCM_POST_B0G_BACKEND_HOLD.md
```

Status:

```text
HOLD_LOCAL_ROCM_POST_B0G_NODEVICE
```

After the B0G smoke and CPU gate, the local ROCm backend stopped initializing:

```text
JAX_PLATFORMS=cpu:  PASS, jax 0.8.2 cpu [CpuDevice(id=0)]
JAX_PLATFORMS=rocm: failed call to hipInit: HIP_ERROR_NoDevice
rocm-smi: _amdgpu_device_initialize: amdgpu_query_gpu_info_init failed
```

`/dev/kfd` and `/dev/dri/renderD*` were still present and the user remained in
the `render` group, so this is a local backend/device state hold rather than a
permission miss. The stuck `rocm-smi` diagnostic was killed and no training or
eval process was left running.

Do not launch further local ROCm policy-producing jobs in this state. Use CPU
only for correctness gates and trace analysis, and use the pinned A100/Colab
`phase2-b0g` path for the next policy-producing attempt when a visible session
is available.

### z=0.00245 A100 On-Policy Support Hold

Artifact:

```text
outputs/analysis/PHASE2_Z00245_A100_ON_POLICY_SUPPORT_HOLD_20260702.md
```

Status:

```text
HOLD_Z00245_ON_POLICY_SUPPORT_LOW_PROGRESS
```

The pinned A100 path successfully trained and exported the z=0.00245
on-policy-support recipe. The earlier `HOLD_REMOTE_NO_SENTINEL` was a Colab CLI
polling artifact: the remote job continued after the local helper misread the
session as idle. The recovered artifact bundle has `exit_status=0` and contains
the full-run checkpoints at `40960`, `81920`, and `122880`.

A compact local CPU sweep on the corrected bridge found no promotable checkpoint.
All three checkpoints passed the x=0.0 screen and stayed below the corrected
velocity envelope at x=0.08 with zero saturation, but all three under-moved:

```text
40960:  track_ratio 0.2200, mean vx 0.0176 m/s, max tracking p95 0.2133 rad
81920:  track_ratio 0.1823, mean vx 0.0146 m/s, max tracking p95 0.2142 rad
122880: track_ratio 0.2174, mean vx 0.0174 m/s, max tracking p95 0.2127 rad
```

Do not promote these checkpoints and do not use them for robot validation. This
run is useful backend evidence and a safe-policy hold, but it did not recover
enough x=0.08 motion for the Phase 2 robustness objective.

### z=0.00245 Motion-Recovery Next Recipe

Artifact:

```text
outputs/analysis/PHASE2_Z00245_MOTION_RECOVERY_NEXT_RECIPE.md
```

Status:

```text
PASS_Z00245_MOTION_RECOVERY_RECIPE_READY
```

The next bounded recipe keeps the same z=0.00245 terrain rung, A2 warm-start,
corrected bridge, no-push setup, and corrected-envelope gates. It changes only
the motion pressure needed to address the current hold:

```text
forward_progress_scale:              4.0 -> 5.0
command_progress_scale:              3.0 -> 4.0
command_progress_shortfall_scale:    -8.0 -> -12.0
command_progress_required_ratio:     0.45 -> 0.55
target_rate_scale:                   -0.01 -> -0.005
actuator_tracking_scale:             -0.005 unchanged
```

Acceptance is intentionally narrow: the compact x=0.08 checkpoint sweep must
find at least one checkpoint with track ratio >= 0.25 and mean vx >= 0.02 m/s
while staying below the corrected envelope, and any promoted checkpoint still
requires the full corrected-bridge x=0.0/x=0.08 8-seed gates before robot
consideration.

Falsifier: if this run remains in-envelope but still under-moves at x=0.08,
stop the scalar progress-pressure path and switch to a behavior-prior,
teacher-continuity, or live-oracle data mechanism rather than another generic
support/safety penalty.

Package-only readiness was recorded at:

```text
outputs/analysis/colab_cli/open-duck-a100-phase2-z00245-phase2-z0025-boundary-20260702T090043Z/PACKAGE_ONLY_MANIFEST.md
```

The package check built the upload archives and verified the pinned JAX `0.7.2`
workflow inputs without uploading, training, SSH, deploy, or robot access.

### z=0.0025 Support Baseline Reconciled

Artifact:

```text
outputs/analysis/PHASE2_Z0025_COMMAND_GATED_BESTREC70_RATE1P9_TARGETLIMITED0999_STRONGER_PUSH_DECISION_20260701.md
```

Status:

```text
PASS_Z0025_SUPPORT_POCKET
```

The current z=0.0025 baseline is the target-limited command-gated candidate:

```text
outputs/analysis/phase2_z0025_command_gated_bestrec70_rate1p9_targetlimited0999_candidate/candidate.onnx
sha256: 6ba399528c6bc7543e0a5a3a43c30b0804357a4b98e21d723cbb5188e446b2a2
```

It passes the corrected-bridge `rough_terrain_backlash`, z=0.0025, stronger-push
gates at both x=0.08 and x=0.0 with 8/8 duration-complete seeds, zero falls,
zero corrected-envelope excess, and mean x=0.08 track ratio `0.3821`. Do not
continue z=0.0025-only support repair unless a later promoted candidate
regresses this rung.

### z=0.0026 Support-Transfer Hold

Artifacts:

```text
outputs/analysis/PHASE2_TARGETLIMITED0999_Z0026_SUPPORT_TRANSFER_DECISION_20260702.md
outputs/analysis/PHASE2_Z0026_TEACHER_CONTINUITY_81920_FULL_GATE_X008.md
outputs/analysis/PHASE2_Z0026_TEACHER_CONTINUITY_81920_SEED5_FAILURE_ANALYSIS_20260702.md
outputs/analysis/PHASE2_Z0026_SEED5_SUPPORT_RECOVERY_DIAGNOSTIC_20260702.md
```

Status:

```text
HOLD_Z0026_MOVING_COMMAND_SUPPORT_TRANSFER
```

The z=0.0026 blocker is now isolated to moving-command support transfer, not
zero-command reset stability and not actuator over-commanding. The target-limited
z=0.0025 baseline survives a short z=0.0026 x=0.0 seed-5 screen in-envelope, but
fails z=0.0026 x=0.08 seed 5 by reverse velocity and base-height collapse.

The preserved teacher-continuity `81920` checkpoint is the closest z=0.0026
parent: it passes 7/8 full x=0.08 seeds at z=0.0026, with seed 5 as the lone
fall. The seed-5 trace stays inside the corrected pitch-chain velocity envelope
and fails by planted double support, backward drift, then base-height collapse.
The broad `phase2-z005-support` recovery direction is closed for this failure:
it stabilized the short screen by producing backward low-progress double-support
behavior.

### z=0.0026 Seed-5 Motion-Support Next Recipe

Artifact:

```text
outputs/analysis/PHASE2_Z0026_SEED5_MOTION_SUPPORT_NEXT_RECIPE.md
```

Status:

```text
PASS_Z0026_SEED5_MOTION_SUPPORT_RECIPE_READY
```

The next bounded run warm-starts from:

```text
outputs/analysis/phase2_restore_checkpoints/phase2_z0026_teacher_continuity_81920
tree_sha256: 4646f7d84260f7f4669e1cbfdc9b677da8999fea9df2d7a6651e184da0d8ae0c
```

It keeps terrain at z=0.0026, pushes disabled, corrected bridge active, and the
teacher-continuity trust region. It keeps the inherited mild teacher-continuity
contact terms, but does not return to the broad `phase2-z005-support` recipe.
The explicit new pressure is narrow anti-reverse and base-height/pitch:

```text
forward_wrong_direction_scale:              -6.0
forward_wrong_direction_allowed_reverse:    0.005
base_height_scale:                          -0.45
forward_pitch_scale:                        -0.35
forward_pitch_rate_scale:                   -0.07
```

Acceptance is deliberately strict: seed 5 must stop reversing without losing the
7 passing seeds, and the promoted checkpoint must pass full z=0.0026 x=0.0 and
x=0.08 corrected-bridge gates before any higher terrain rung or robot-side work.
If the run removes the seed-5 fall by backing up, freezing, or drifting at x=0.0,
this repair direction is falsified rather than promoted.

### z=0.0026 Seed-5 Motion-Support Repair Hold

Artifact:

```text
outputs/analysis/PHASE2_Z0026_SEED5_MOTION_SUPPORT_REPAIR_DECISION_20260703.md
```

Status:

```text
HOLD_Z0026_REPAIR_DID_NOT_RECOVER_SEED5
```

The A100 run completed with the pinned JAX `0.7.2` stack and exported checkpoints
at `40960`, `81920`, and `122880`, but the decisive local seed-5 z=0.0026 x=0.08
short screen failed for all three:

```text
40960:  fall at 65 samples, vx=-0.2219 m/s, track_ratio=-2.7736, vel_excess=0
81920:  fall at 65 samples, vx=-0.2262 m/s, track_ratio=-2.8270, vel_excess=0
122880: fall at 64 samples, vx=-0.2184 m/s, track_ratio=-2.7300, vel_excess=0
```

The latest checkpoint trace is still `REVERSE_HEIGHT_COLLAPSE`: reverse begins at
tick `10`, low height at tick `62`, done at tick `63`, with `52/64` ticks in
double support and no corrected-envelope velocity excess. Do not promote these
checkpoints. The Colab session was stopped after artifact recovery to avoid
continuing a remote sweep that could not approve the run.

This closes the narrow scalar anti-reverse/base-height repair direction. The
next step should inspect seed 5's state/contact manifold directly against the
seven passing z=0.0026 seeds and identify the first divergent support variable
before tick 10, rather than spending another A100 run on the same scalar
penalty family.

### z=0.0026 Seed-5 Initial Support Manifold Hold

Artifact:

```text
outputs/analysis/PHASE2_Z0026_SEED5_INITIAL_SUPPORT_DIVERGENCE_DECISION_20260703.md
```

Status:

```text
HOLD_Z0026_INITIAL_SUPPORT_MANIFOLD
```

The seed-5 divergence happens at reset, before meaningful policy action. In a
paired trace of the preserved teacher-continuity `81920` checkpoint, seed 0
starts with right-foot contact `[0, 1]` and completes the 2 s screen with
positive mean vx, while seed 5 starts with no foot contact `[0, 0]`, the right
foot about `5.7 cm` higher, and a large right-leg posture mismatch:

```text
tick 0 seed5 - seed0:
  right_ankle    +0.5354 rad
  right_knee     +0.4809 rad
  left_ankle     -0.4302 rad
  actual L2      0.8789
  sent-target L2 0.0436
```

The sent targets are nearly the same even though the state/contact manifold is
different. Seed 5 then reverses at tick `10` and collapses by tick `65`, still
with zero corrected-envelope velocity excess. Adding `--reset-settle-ticks 25`
is worse: seed 5 falls at `18` samples with mean vx `-0.7045 m/s`.

This closes passive reset-settle and more scalar anti-reverse/base-height
pressure as useful fixes for this specific blocker. The next valid branch
should target seed-5-like initial support states directly: live-oracle relabels
from tick 0, reset/contact-state augmentation, or a recovery behavior
conditioned on early contact and posture. Do not change the gate silently to
hide this reset manifold issue, and do not run robot validation from this
branch.

### z=0.0026 Seed-5 Live-Oracle Reset-Repair Smoke Hold

Artifact:

```text
outputs/analysis/PHASE2_Z0026_SEED5_INITIAL_SUPPORT_LIVE_ORACLE_ITER0_DECISION_20260703.md
```

Status:

```text
HOLD_LIVE_ORACLE_RESET_REPAIR_SMOKE_FAILED
```

One local CPU live-oracle iteration relabeled the known bad seed-5 reset states:
`65` samples at `x=0.08` with the `source_vx_blend` oracle and `58` samples at
`x=0.0` with a zero-action oracle. The aggregate manifest contained `6123`
samples, dominated by the existing z=0.0024 positive source data. A small
phase-modulated BC student fit the labels cleanly (`MAE=0.007024`, ONNX p95
error about `1.2e-7`), but rollout behavior failed the smoke screens:

```text
x=0.08 seed 5: fall at 57 samples, vx=-0.2527 m/s, track_ratio=-3.1587, vel_excess=0
x=0.0  seed 5: fall at 43 samples, vx=-0.3436 m/s, p95_vel_excess=0.1776
```

Do not scale this student and do not spend A100 time on this exact relabel
recipe. The new labels were actions on bad reset/failure states, not successful
recovery traces, and the smoke student made the moving-command failure worse
while breaking x=0.0 command preservation. The next useful branch needs either
a support-recovery oracle that actually survives seed-5-like no-contact resets,
or an explicit reset-distribution audit against the real robot start protocol.
Do not silently change the gate to hide the reset manifold issue.

### z=0.0026 Reset Distribution Audit

Artifact:

```text
outputs/analysis/PHASE2_Z0026_RESET_DISTRIBUTION_AUDIT_20260703.md
```

Status:

```text
HOLD_RESET_DISTRIBUTION_CONTAINS_NO_CONTACT_STARTS
```

The active Playground reset distribution for `rough_terrain_backlash` at
z=`0.0026` was sampled over seeds `0-31`. The reset implementation randomizes
base xy by `[-0.05, 0.05] m`, yaw by `[-3.14, 3.14] rad`, actuator qpos by a
per-joint multiplier `[0.5, 1.5]`, and base qvel by `[-0.05, 0.05]`, then
initializes ctrl to the randomized actuator qpos.

Support at reset:

```text
double: 16/32
left:    8/32
right:   6/32
none:    2/32
```

Seed 5 is one of the no-contact starts. At reset both feet are above the ground
contact manifold (`left_z=0.0312 m`, `right_z=0.0682 m`) with actuator posture
`L2=1.0251 rad` from home. The largest home deltas are `right_knee=0.6692 rad`,
`left_knee=0.6258 rad`, `right_hip_pitch=-0.2838 rad`, and
`right_ankle=0.2553 rad`.

This confirms the current z=0.0026 seed-5 blocker is not just a policy
rollout failure; it is produced by a broad randomized reset distribution that
can start the robot outside the standing support manifold. The next branch must
decide whether that reset distribution is physically representative of the real
robot start protocol. If not, constrain the sim reset for evaluation/training
explicitly and document the contract change. If yes, build a recovery source
that survives unsupported starts before relabeling those states.

### z=0.0026 Home-Support Reset Diagnostic

Artifact:

```text
outputs/analysis/PHASE2_Z0026_HOME_SUPPORT_RESET_DIAGNOSTIC_DECISION_20260703.md
```

Status:

```text
HOLD_Z0026_HOME_SUPPORT_LOW_PROGRESS
```

An eval-only `--reset-mode home-support` was added to the closed-loop evaluator
and seed-sweep harness. The default remains `playground`. `home-support` starts
from sim home qpos, zero qvel, and home ctrl before the policy loop, which
tests the normal grounded-start contract separately from unsupported-start
recovery.

The preserved z=0.0026 teacher-continuity `81920` parent was screened for 2 s
over seeds `0-7` under home-support reset:

```text
x=0.08: 0/8 falls, 8/8 duration complete, but HOLD_CANDIDATE_TRACKING
        mean_vx=0.0248 m/s, track_ratio=0.3099, max_tracking_p95=0.2054,
        p95_vel_excess=0, double_support=92%

x=0.0:  0/8 falls, 8/8 duration complete, PASS_CANDIDATE_SIM_GATE
        mean_vx=0.0051 m/s, p95_vel_excess=0, double_support=100%
```

This confirms the old seed-5 fall was reset-distribution driven: under
grounded-home reset it disappears. The parent still is not promotable, because
the moving-command behavior is too slow and double-support dominant. Future
gates must explicitly separate the grounded walking reset contract from an
unsupported-start recovery contract.

### z=0.0026 z=0.0025-Candidate Home-Support Short Screen

Artifact:

```text
outputs/analysis/PHASE2_Z0026_Z0025CANDIDATE_HOME_SUPPORT_SHORT_DECISION_20260703.md
```

Status:

```text
PASS_Z0026_HOME_SUPPORT_SHORT_STABILITY_SLOW
```

The existing z=0.0025 candidate was screened for 2 s at z=`0.0026` with the
same grounded-home reset contract:

```text
x=0.08: 8/8 duration complete, 0/8 falls, PASS_CANDIDATE_SIM_GATE
        mean_vx=0.0223 m/s, track_ratio=0.2784, max_tracking_p95=0.1868,
        p95_vel_excess=0, double_support=96%

x=0.0:  8/8 duration complete, 0/8 falls, PASS_CANDIDATE_SIM_GATE
        mean_vx=0.0033 m/s, p95_vel_excess=0, double_support=100%
```

This reinforces that the prior seed-5 z=0.0026 collapse was a reset-contract
artifact. It does not make the candidate deployable: the moving-command gait is
still very slow and nearly all double support. The next Phase 2 recipe should
start from this explicit reset contract and improve single-support/forward
progress while keeping corrected-envelope excess at zero.

### Playground Reset Contract Patch

The local Playground branch now exposes the reset randomization as default-off
runner overrides while preserving the original defaults:

```text
repo:   RobVanProd/Open_Duck_Playground
branch: codex/forward-progress-reward
commit: 4af95c9 sim: expose reset randomization config

--reset_base_xy_jitter_m
--reset_yaw_jitter_rad
--reset_actuator_qpos_multiplier_min
--reset_actuator_qpos_multiplier_max
--reset_base_qvel_jitter
```

The RDK training wrapper forwards matching hyphenated flags to Playground:

```text
--reset-base-xy-jitter-m
--reset-yaw-jitter-rad
--reset-actuator-qpos-multiplier-min
--reset-actuator-qpos-multiplier-max
--reset-base-qvel-jitter
```

For the grounded-home walking contract, use:

```text
--reset-base-xy-jitter-m 0
--reset-yaw-jitter-rad 0
--reset-actuator-qpos-multiplier-min 1
--reset-actuator-qpos-multiplier-max 1
--reset-base-qvel-jitter 0
```

Unsupported-start recovery is now a separate robustness target, not the default
walking gate.
