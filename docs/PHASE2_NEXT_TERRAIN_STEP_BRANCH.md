# Phase 2 Next Terrain Step Branch

status: `PRE_REGISTERED_NOT_STARTED`

## Objective

Recover terrain/carpet robustness by making alternating per-foot swing and
forward touchdown advance structurally unavoidable before another PPO/BC stage.

This branch is offline-only. It does not authorize robot tests, SSH, deploy,
grounded replay, runtime changes, or training from scratch.

## Current Evidence

Phase 2 already has a corrected-bridge flat / low-friction walker, but medium
carpet and rough-terrain sim expose a planted-foot shuffle:

```text
Phase 1 / Stage A: corrected-bridge walker exists and transfers on easy surfaces
rough z=0.002: low-clearance / double-support shuffle
C8 swing balance: HOLD, reduced motion
C9 swing advance: HOLD, reduced motion; seed 4 stayed planted
action gain 1.05/1.10: HOLD, worsened progress; not an amplitude fix
MPC rough preflight: HOLD, actuator-safe but too slow and double-support dominated
C7 z=0.001 threshold: seed 2 passes, seed 4 still planted
existing flat-trace hard-step rescore: PASS source windows exist
live-oracle iter0 z=0.001 transfer: HOLD, velocity/tracking over gate
live-oracle iter0 z=0.001/z=0.002 window rescore: PASS source windows exist
```

Hard-step diagnostics now show:

```text
seed 2 can produce a small swing segment
seed 4 can remain at 0 swing segments and 0.0000 m rel-x range
```

So the blocker is not actuator envelope or terrain height alone. The blocker is
a seed-dependent planted-foot mode.

The existing-trace hard-step rescore found valid 100-tick flat fitted-bridge
windows for seeds `2,4`, especially from live-oracle DAgger iteration 1:

```text
seed 2: mean vx 0.0571 m/s, sent vel p95 2.2257 rad/s,
        tracking p95 0.1818 rad, min swing segments 3
seed 4: mean vx 0.0544 m/s, sent vel p95 2.2291 rad/s,
        tracking p95 0.1809 rad, min swing segments 4
```

That source proves the corrected flat manifold contains hard per-foot stepping
windows. It does not yet prove terrain robustness. A transfer check of the
live-oracle iteration 0 candidate on `rough_terrain_backlash` at
`terrain_hfield_z_scale=0.001` completed both seeds and stepped, but held on the
corrected envelope/tracking gate:

```text
seed 2: mean vx 0.0488 m/s, max pitch vel p95 3.5739 rad/s,
        velocity excess 0.8239 rad/s, tracking p95 0.2545 rad
seed 4: mean vx 0.0423 m/s, max pitch vel p95 3.5845 rad/s,
        velocity excess 0.8345 rad/s, tracking p95 0.2590 rad
```

So the next source branch should use those flat hard-step windows as evidence
and mining material, but it still needs an explicit rough-terrain source or
candidate that stays inside the corrected per-joint envelope.

Window-level rescoring of the same rough-terrain rollouts found that explicit
source:

```text
z=0.001 seed 2: mean vx 0.0560, sent vel p95 2.1892,
                tracking p95 0.1764, min swing segments 3
z=0.001 seed 4: mean vx 0.0493, sent vel p95 1.9976,
                tracking p95 0.1714, min swing segments 3
z=0.002 seed 2: mean vx 0.0558, sent vel p95 2.0902,
                tracking p95 0.1788, min swing segments 3
z=0.002 seed 4: mean vx 0.0532, sent vel p95 2.2194,
                tracking p95 0.1704, min swing segments 3
```

This is a source-window pass, not a policy pass: the full candidate still
exceeds corrected velocity/tracking limits on rough terrain. The next action is
to turn the terrain-safe windows into a curated source manifest or live-oracle
relabel pass, then train/fine-tune against that source.

Canonical curated source manifest:

```text
outputs/analysis/PHASE2_TERRAIN_SAFE_HARD_STEP_SOURCE_MANIFEST.md
outputs/analysis/phase2_terrain_safe_hard_step_source_manifest.json
status: PASS_TERRAIN_SAFE_HARD_STEP_SOURCE_MANIFEST
source_policy_sha256: f3492159a775b0e0f73a25cf528b84ae202c16d5b2ba2f1344f7b7256e4e7261
windows: z=0.001 and z=0.002, seeds 2 and 4, 100 samples each
```

First plain BC compression test:

```text
manifest: outputs/analysis/PHASE2_TERRAIN_SAFE_HARD_STEP_BC_MANIFEST.md
fit: outputs/analysis/PHASE2_TERRAIN_SAFE_HARD_STEP_BC_STUDENT.md
gate: outputs/analysis/PHASE2_TERRAIN_SAFE_HARD_STEP_BC_STUDENT_TERRAIN_Z002_GATE_CPU.md
result: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
```

The 400-sample memoryless BC student fits the slices but fails closed-loop with
near-standstill and velocity spikes. This is not a promotable candidate. Use the
manifest for live relabel/DAgger or memory/phase student work, not for another
plain BC retry.

First small recurrent BC test:

```text
fit: outputs/analysis/PHASE2_TERRAIN_SAFE_HARD_STEP_RECURRENT_BC_STUDENT.md
gate: outputs/analysis/PHASE2_TERRAIN_SAFE_HARD_STEP_RECURRENT_BC_STUDENT_TERRAIN_Z002_GATE_CPU.md
result: HOLD_CANDIDATE_FALL_OR_TERMINATION
```

This recurrent fit was also trained only on the four curated snippets. It falls
backward on seeds `2,4`, so recurrence alone does not rescue a tiny static
dataset. The next branch still needs live/on-policy relabel coverage or a
larger terrain-window dataset.

Live/on-policy relabel coverage has now been tested:

```text
decision: outputs/analysis/PHASE2_TERRAIN_LIVE_ORACLE_DAGGER_DECISION.md
status: HOLD_TERRAIN_LIVE_ORACLE_DAGGER_TRACKING_PLATEAU
iterations: 0, 1, 2
```

Result:

```text
iter 0: low-progress / partial freeze
iter 1: progress recovered, but tracking/envelope held
iter 2: vx 0.0459-0.0526 m/s, track ratio 0.5736-0.6570,
        velocity excess 0.8704-0.8938 rad/s,
        tracking p95 0.2527-0.2533 rad
```

The live loop moved the student out of standstill but did not satisfy the
corrected bridge terrain gate. Do not repeat the same DAgger recipe as the next
step. The next terrain branch should make the oracle labels themselves
tracking-aware, for example by rate-limiting/filtering relabel actions or using
PPO fine-tuning with explicit corrected-envelope penalties.

A first tracking-aware label filter was tested:

```text
decision: outputs/analysis/PHASE2_TERRAIN_TRACKING_AWARE_LABEL_DECISION.md
status: HOLD_TRACKING_AWARE_LABEL_FILTER_FREEZES
```

It clipped pitch-chain oracle labels to a conservative `2.25 rad/s` target-rate
cap, fit a smooth PPO-compatible BC student, and then gated it on
`rough_terrain_backlash` at `z=0.002`. The filter reduced velocity excess and
tracking pressure, but collapsed the gait back into double-support low
progress:

```text
seed 2: vx 0.0107 m/s, track ratio 0.1335, double support 90%
seed 4: vx 0.0105 m/s, track ratio 0.1314, double support 96%
```

So a simple global label smoothing pass is now closed. The next terrain branch
must preserve the swing/advance transition while staying inside the corrected
per-joint envelope; do not repeat this filter with only minor threshold tweaks.

Trace comparison confirmed the mechanism:

```text
artifact: outputs/analysis/PHASE2_TERRAIN_TRACKING_AWARE_TRACE_COMPARISON.md
iter2 single support: about 30-35%
tracking-aware single support: about 4-10%
```

The next pre-registered branch is:

```text
docs/PHASE2_TRANSITION_PRESERVING_TERRAIN_BRANCH.md
```

It should preserve double-support preparation into single-support transition
while enforcing the corrected per-joint envelope in closed-loop training/eval.

## Closed Paths

Do not spend the next run on:

- global action gain
- stronger scalar swing-balance pressure
- stronger scalar swing-advance pressure
- stronger scalar clearance pressure
- another PPO stage that is only scored after training
- a target source that can pass without both feet producing swing segments
- a simple global pitch-chain label-rate filter that damps the transition into
  double support
- another transition-blind BC fit from the same tiny terrain snippet set

Those have already been tested or are directly implied by the new hard-step
diagnostics.

## Required Pre-Training Gate

Before any PPO/BC run, a target source or candidate seed must pass a hard
step-transition screen on `rough_terrain_backlash`:

```text
seeds: 2,4 at minimum; expand to 0-7 before promotion
terrain_hfield_z_scale: 0.001 first, then 0.002
command_x: 0.08
duration: 5 s for policy candidates, 100/150 ticks for target windows
bridge: corrected fitted bridge
max velocity excess: 0
max tracking p95: <= 0.20 rad
min per-foot swing segments: >= 1
min per-foot rel-x range p95: >= 0.003 m
min per-foot swing peak lift: >= 0.005 m
single support: meaningful and balanced
double support: not dominant
```

If seed 4 remains at `0` swing segments, the branch holds. Do not train around
that result.

## Candidate Approaches

### A. Higher-clearance Source Mining

Re-mine from the corrected-bridge walker and C7 trace library using the hard
step-transition scorer:

- require both left and right swing segments in the selected window
- require forward relative-foot excursion
- require swing lift over stance
- reject one-sided seed/source hacks
- reject target windows that are in-envelope only because they barely step

Proceed only if at least one source clears seed `2,4` at `z=0.001`.

### B. Hard Anti-Planted Teacher

Modify the offline teacher, not the reward function, so phase transitions cannot
advance unless the swing foot actually leaves stance and advances:

- state machine must hold / recover until the intended swing foot creates a
  measurable swing segment
- support side must alternate
- touchdown must occur with forward relative-foot advance
- teacher-side velocity cap stays at or below the corrected envelope

Proceed only if the teacher clears the same hard-step target-source gate.

### C. PPO Re-Entry

Only after A or B clears the hard-step gate:

- warm-start from the corrected-bridge candidate or selected C7 checkpoint
- keep corrected actuator envelope authoritative
- start at `z=0.001`
- keep terrain rewards weak and audited
- evaluate every checkpoint with the hard swing gate before promotion

## Decision Rule

`PASS_TERRAIN_STEP_SOURCE`:
  A source/candidate clears the hard-step gate at `z=0.001` for seeds `2,4`
  without velocity excess or tracking regression. Then expand to `z=0.002` and
  eight seeds.

Current status: `PASS_TERRAIN_STEP_SOURCE` at the source-window level for
`z=0.001` and `z=0.002`; not yet a candidate-policy pass.

`HOLD_PLANTED_SEED_MODE`:
  Seed 4 remains at `0` swing segments or `0.0000 m` rel-x range. Do not start
  another scalar reward run.

`HOLD_ACTUATOR_ENVELOPE`:
  Any apparent step source needs target velocities over the corrected envelope.

`HOLD_TERRAIN_TRANSFER`:
  A flat hard-step source exists, but the corresponding policy/candidate exceeds
  corrected velocity or tracking limits on `z=0.001` terrain. Do not promote it;
  mine a terrain-safe source or build the hard anti-planted teacher.

## Current Recommended Next Command

Run source mining or teacher search against the hard-step scorer, not PPO:

```bash
python3 tools/score_target_candidates_objective.py \
  --trace-glob '<candidate-traces>/*/seed_*.jsonl' \
  --seeds 2,4 \
  --window-samples 100 \
  --command-x 0.08 \
  --min-mean-vx 0.04 \
  --max-double-support-pct 75 \
  --min-single-support-pct 20 \
  --min-each-single-support-pct 5 \
  --min-contact-transitions 2 \
  --min-swing-segments-per-foot 1 \
  --min-swing-rel-x-range-p95-m 0.003 \
  --min-swing-peak-lift-m 0.005 \
  --max-sent-velocity-p95 2.5 \
  --max-tracking-p95 0.20
```
