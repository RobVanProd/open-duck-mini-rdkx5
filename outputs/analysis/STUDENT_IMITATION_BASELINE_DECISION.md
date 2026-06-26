# Student Imitation Baseline Decision

status: `HOLD_DAGGER2_ONNX_MULTI_SEED_LOW_FORWARD_PROGRESS`

This is an offline planning artifact. It does not run robot tests, SSH,
deployment, PPO training, or runtime behavior changes.

## Input Evidence

All rows use the same low-rate closed-loop teacher-window manifest:

```text
outputs/analysis/closed_loop_teacher_dataset_manifest.json
dataset_id: 407af2cbe0ad69e1
entries: 259
samples: 6475
source rollout dirs: 16
```

The gate was straight `x=0.08`, `5s`, seeds `0-7`, upstream-main
`flat_terrain_backlash`, CPU JAX/MJX.

| student | artifact | status | key result |
|---|---|---|---|
| kNN, k=5 | `CLOSED_LOOP_TEACHER_DATASET_BC_GATE_X008.md` | `HOLD_BC_REPLAY_TERMINATED` | 5/8 moving, 2/8 near-standstill, 1/8 fall/reverse |
| aggregate sequence | `CLOSED_LOOP_TEACHER_SEQUENCE_REPLAY_X008.md` | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | all seeds complete, near-standstill, sent-vel p95 `0.2660` |
| aggregate sequence, no seam | `CLOSED_LOOP_TEACHER_SEQUENCE_REPLAY_X008_NO_SEAM.md` | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | all seeds complete, near-standstill, sent-vel p95 `0.2853` |
| MLP 64x64 | `CLOSED_LOOP_TEACHER_DATASET_MLP_BC_GATE_X008.md` | `HOLD_BC_REPLAY_LOW_FORWARD_MOTION` | 1/8 moving, sent-vel p95 `5.2400` every seed |
| MLP + target-rate pair loss | `CLOSED_LOOP_TEACHER_DATASET_MLP_RATE_REG_BC_GATE_X008.md` | `HOLD_BC_REPLAY_TERMINATED` | 3/8 terminated, sent-vel p95 `5.2400` every seed |
| MLP + obs consistency | `CLOSED_LOOP_TEACHER_DATASET_MLP_CONSISTENCY_BC_GATE_X008.md` | `HOLD_BC_REPLAY_TERMINATED` | 3/8 terminated, sent-vel p95 `5.2400` every seed |
| linear ridge | `CLOSED_LOOP_TEACHER_DATASET_LINEAR_BC_GATE_X008.md` | `HOLD_BC_REPLAY_TERMINATED` | 0/8 moving, 1/8 fall/reverse, sent-vel p95 `0.7319-3.0866` |
| blend, kNN weight 0.75 | `CLOSED_LOOP_TEACHER_DATASET_BLEND075_BC_GATE_X008.md` | `HOLD_BC_REPLAY_LOW_FORWARD_MOTION` | 5/8 moving, 0/8 terminated, seeds 1/4/7 near-standstill |
| blend, kNN weight 0.80 | `CLOSED_LOOP_TEACHER_DATASET_BLEND080_BC_GATE_X008.md` | `HOLD_BC_REPLAY_LOW_FORWARD_MOTION` | best cheap baseline: 5/8 moving, 0/8 terminated, target-rate safe |
| blend, kNN weight 0.90 | `CLOSED_LOOP_TEACHER_DATASET_BLEND090_BC_GATE_X008.md` | `HOLD_BC_REPLAY_TERMINATED` | 4/8 moving, seed 3 falls/reverses |
| kNN, k=3 | `CLOSED_LOOP_TEACHER_DATASET_KNN3_BC_GATE_X008.md` | `HOLD_BC_REPLAY_TERMINATED` | worse than k=5: 4/8 moving, seed 3 falls/reverses |

## Decision

Do not promote any exported or learned student yet.

The curated low-rate teacher windows contain useful motion signal, but every
simple one-model student has a distinct failure:

```text
kNN:
  preserves local motion, but is seed-fragile

aggregate sequence / linear:
  smooth enough, but too weak to propel

MLP:
  state-conditioned, but high-rate and low-progress in closed loop

MLP local regularizers:
  do not keep the rollout on the low-rate teacher manifold

blend 0.75-0.80:
  combines kNN motion with enough linear smoothing to remove the seed-3 fall,
  but still freezes seeds 1, 4, and 7
```

The source-filtered velocity selector is the first offline replay pass. It is
not a deployable policy: it is a diagnostic selector over teacher windows and
two local models. The next branch should convert or distill this selector into
a reviewed portable student, then test that student against stricter offline
gates before any robot discussion.

The traced blend `0.80` replay classifies that freeze as
`HOLD_FREEZE_LOW_ACTION_DOUBLE_SUPPORT`:

```text
moving seeds 0/2/3/5/6:
  single support mean: 46.24%
  pitch-chain target velocity p95 mean: 3.19 rad/s

frozen seeds 1/4/7:
  single support mean: 2.67%
  double support mean: 97.20%
  pitch-chain target velocity p95 mean: 0.40 rad/s
```

This means the next student must add closed-loop pressure against quiet
double-support dwell, not merely smooth the kNN policy further.

The traced raw kNN `k=5` replay clarifies the tradeoff:

```text
raw kNN moving seeds: 0, 1, 2, 5, 6
raw kNN seed 3: fall/reverse after 79 samples
raw kNN seeds 4/7: double-support freeze

blend 0.80 moving seeds: 0, 2, 3, 5, 6
blend 0.80 seeds 1/4/7: low-action double-support freeze
```

A single global blend cannot solve all seeds. Seed `1` needs more kNN-local
motion than blend `0.80`, seed `3` needs less kNN aggression than raw kNN, and
seeds `4`/`7` need an additional anti-double-support mechanism.

A narrow blend-alpha sweep from `0.75` to `0.88` did not change the seed split:
every one of those coefficients moved seeds `0/2/3/5/6` and froze `1/4/7`.
At `0.90`, seed `3` terminates again. Further global alpha sweeps are not a
promising branch.

A simple double-support dwell selector was also tested:

```text
base blend: 0.80
dwell blend: 1.00 / raw kNN

trigger 5 ticks:
  seed 3 terminates again

trigger 10 or 20 ticks:
  same split as blend 0.80
```

This rules out the simplest state-conditioned blend switch. The next student
needs closed-loop training/selection that produces a better local action for
double-support freeze states, not just a later switch to raw kNN.

A velocity-gated blend is the first selector that beats blend `0.80`:

```text
base blend: 0.80
raw-kNN blend: 1.00
switch condition: local vx >= -0.02 m/s

moving seeds: 0, 1, 2, 3, 5, 6
frozen seeds: 4, 7
terminated seeds: none
```

It recovers seed `1` while keeping seed `3` alive. The remaining failure is
still low-action double-support dwell on seeds `4` and `7`.

A source-filtered velocity selector is the first offline selector to clear the
5-second and 10-second replay gates:

```text
primary model:
  full curated teacher dataset

alternate model:
  curated teacher dataset excluding source labels matching _seed4/

source switch:
  use alternate when local vx >= +0.02 m/s

internal blend switch:
  use raw-kNN blend when local vx >= -0.02 m/s

5s gate:
  PASS_BC_FIT_SMOKE_FORWARD_REPLAY
  moving seeds: 8 / 8
  terminated seeds: 0 / 8
  sent-target velocity p95 range: 2.4474-2.5315 rad/s

10s gate:
  PASS_BC_FIT_SMOKE_FORWARD_REPLAY
  moving seeds: 8 / 8
  terminated seeds: 0 / 8
  sent-target velocity p95 range: 2.4293-2.4851 rad/s

10s fitted actuator bridge gate:
  PASS_BC_FIT_SMOKE_FORWARD_REPLAY
  moving seeds: 8 / 8
  terminated seeds: 0 / 8
  track ratio range: 0.5491-0.6172
  sent-target velocity p95 range: 2.2569-2.3622 rad/s
  joint tracking p95 range: 0.1809-0.1863 rad

5s stress actuator bridge gate:
  HOLD_BC_REPLAY_TERMINATED
  failure: near-standstill on most seeds and seed 5 fall/progress failure
```

This should be treated as an offline selector proof, not as a deployable policy.
It shows that the low-rate teacher windows contain enough state-conditioned
signal to move all eight seeds when the source/velocity selector is chosen
closed-loop. It now also survives the fitted actuator bridge, but it is not
stress-bridge robust.

The selector was then replayed under the fitted actuator bridge with full
observations and converted into a compact distillation manifest:

```text
outputs/analysis/SOURCE_VX_SELECTOR_FITTED_BRIDGE_TRACE_MANIFEST.md
status: PASS_BC_TRACE_MANIFEST_READY
entries: 8
samples: 4000
```

A source-switch-free blend student trained from that manifest passes the same
10-second fitted-bridge gate:

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_BLEND080_FITTED_BRIDGE_BC_GATE_X008_10S.md
student: blend 0.80 over selector-trace manifest
status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
moving seeds: 8 / 8
terminated seeds: 0 / 8
track ratio range: 0.5170-0.6279
sent-target velocity p95 range: 2.0779-2.2134 rad/s
joint tracking p95 range: 0.1803-0.1843 rad
```

This is stronger than the source selector because it removes the local-vx/source
switch from the closed-loop policy path. It is still a kNN/linear blend student,
not an exported ONNX policy.

A small neural clone from the same manifest does not pass:

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_MLP128_FITTED_BRIDGE_BC_GATE_X008_10S.md
student: MLP 128x128, 3000 steps
status: HOLD_BC_REPLAY_TERMINATED
failure: all seeds fall/progress-fail with reverse velocity and high target rate

outputs/analysis/SOURCE_VX_SELECTOR_TRACE_MLP128_RATE_REG_FITTED_BRIDGE_BC_GATE_X008_10S.md
student: MLP 128x128 + target-rate regularizer
status: HOLD_BC_REPLAY_TERMINATED
failure: one seed completes near standstill, most seeds still reverse/fall
sent-target velocity p95 range: 3.6588-4.4620 rad/s
```

## DAgger Relabeling Result

The failed MLP rollouts were then used as DAgger-style state coverage. Student
visited states were relabeled with the safer blend teacher, preserving the
original student action as `original_action` in ignored raw traces:

```text
tools/relabel_bc_trace_actions.py
```

The first relabel pass produced:

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_MLP128_RELABEL_BLEND.md
status: PASS_BC_TRACE_RELABEL_READY
samples_out: 1166
```

The DAgger-1 MLP improved materially but still held on seed `5`:

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER1_MLP128_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: HOLD_BC_REPLAY_TERMINATED
result: 7 / 8 seeds completed; seed 5 fell/reversed
```

A second relabel pass added DAgger-1 visited states:

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER1_MLP128_RELABEL_BLEND.md
status: PASS_BC_TRACE_RELABEL_READY
samples_out: 3602

outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER2_MANIFEST.md
status: PASS_BC_TRACE_MANIFEST_READY
entries: 24
samples: 8768
dataset_id: 29210cfbb880ecb9
```

The DAgger-2 128x128 MLP is the first compact neural student to preserve the
fitted-bridge smoke result:

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER2_MLP128_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
moving seeds: 8 / 8
terminated seeds: 0 / 8
track ratio range: 0.5208-0.6182
sent-target velocity p95 range: 2.1174-2.1601 rad/s
joint tracking p95 range: 0.1770-0.1813 rad
```

The same model exports to a small ONNX policy with the runtime-compatible
contract:

```text
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_candidate/candidate.onnx
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_candidate/candidate_mlp.npz
policy sha256: a4e8575afc7a88fec336207fa6622e68387212c90596fbe6c0d038be4d5f4460
contract: obs[1,101] -> continuous_actions[1,14]
onnx verify max_abs_error: 4.172325e-07
```

The standard closed-loop ONNX evaluator completes on CPU with the fitted bridge:

```text
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_onnx_eval/CLOSED_LOOP_ACTUATOR_BRIDGE_EVAL.md
status: PASS_CLOSED_LOOP_REPRODUCTION
duration: 10s / 500 samples
mean local vx: 0.0197 m/s
track ratio: 0.2457
terminated: no
```

This is an exportability milestone, not a deployment decision. The ONNX
candidate moves slowly in the standard evaluator and still needs multi-seed
ONNX evaluation plus stress-bridge review before it can be promoted beyond an
offline candidate.

The multi-seed standard ONNX fitted-bridge review holds:

```text
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_onnx_multiseed_fitted/MULTISEED_FITTED_SUMMARY.md
status: HOLD_DAGGER2_ONNX_MULTI_SEED_LOW_FORWARD_PROGRESS
duration complete: 6 / 8
moving seeds with track ratio >= 0.5: 0 / 8
moving seeds with mean local vx >= 0.02 m/s: 4 / 8
early terminations: seeds 1 and 7
```

This means the ONNX export path works, but the exported DAgger-2 MLP is not a
promotion candidate. The source-switch-free blend student remains the stronger
behavior baseline.

The first standard review used default `flat_terrain`, while the DAgger smoke
gate used `flat_terrain_backlash`. A task-matched review on
`flat_terrain_backlash` is materially better but still holds:

```text
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_onnx_multiseed_fitted_backlash/MULTISEED_FITTED_BACKLASH_SUMMARY.md
status: HOLD_DAGGER2_ONNX_BACKLASH_LOW_FORWARD_PROGRESS
duration complete: 8 / 8
moving seeds with track ratio >= 0.5: 7 / 8
mean track ratio: 0.5409
max pitch-chain sent-target p95 range: 4.5943-4.8522 rad/s
```

That closes the task-mismatch confound but exposes the real portable-student
issue: the MLP can move on the backlash task, but it does so with max
pitch-chain target velocity above the fitted actuator envelope.

An eval-only scalar action-gain screen does not fix this:

```text
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_onnx_gain_screen_backlash/GAIN_SCREEN_SUMMARY.md
status: HOLD_GAIN_SCREEN_NO_ENVELOPE_SAFE_MOTION
```

Gain `0.90` still exceeds the envelope and already loses forward tracking on
the screened seeds; lower gains reduce target rate but collapse motion. Do not
turn this into a runtime gain hack.

## Required Next Design

- Use the DAgger-2 ONNX candidate as proof that compact neural export is wired,
  not as the behavior target.
- Keep the source-switch-free blend student as the stronger offline behavior
  baseline.
- The next portable student must preserve task-matched backlash forward
  progress while bringing max pitch-chain target velocity and tracking down.
- Do not pursue scalar action-gain wrapping as the next branch; it failed the
  two-seed envelope/motion screen.
- Do not treat the failed 128x128 MLP clones as proof that neural distillation
  is impossible; they show naive one-step MLP and simple target-rate
  regularization still overdrive.
- Treat the stress bridge hold as a margin limit to improve, not as a regression
  of the fitted-bridge pass.
- Do not rely on one global kNN/linear blend coefficient; the traced kNN/blend
  comparison shows the seed failures need state-conditioned selection.
- Penalize or reject candidates whose closed-loop sent-target p95 reaches
  `5.24 rad/s`.
- Grade on all eight seeds, with both 5s and longer-duration gates.
- Gate on forward motion, fall/reverse count, near-standstill count, and
  max-joint pitch-chain p95 target velocity.
- Keep all behavior default-off and offline.

## Stop Rules

- Do not deploy or run robot validation.
- Do not call the DAgger-2 ONNX candidate robot-ready; it is only the first
  exportable fitted-bridge smoke pass and it fails multi-seed standard ONNX
  review.
- Do not treat action-gain damping as a fix; the offline gain screen trades
  target-rate safety for lost forward motion.
- Do not treat the 2-seed kNN smoke as a pass.
- Do not use aggregate sequence replay as the student.
- Do not use plain one-step MLP BC as the student.
- Do not assume pairwise target-rate or observation-consistency regularization
  solves closed-loop rate saturation.
- Do not optimize supervised action error alone.
- Do not call the source-filtered selector robot-ready; it is only an offline
  selector smoke pass.
- Do not keep sweeping one global blend alpha; `0.75-0.88` have the same
  moving/freeze split and `0.90` reintroduces the seed-3 fall.
- Do not use the simple dwell-to-raw-kNN selector as the solution; early dwell
  switching terminates seed 3 and later switching preserves the freeze.

## Current Next Step

Turn the source-filtered velocity selector into a reviewed student/distillation
or training target and test it against stricter offline gates, especially the
fitted actuator bridge. Do not move to robot validation from this selector
artifact.
