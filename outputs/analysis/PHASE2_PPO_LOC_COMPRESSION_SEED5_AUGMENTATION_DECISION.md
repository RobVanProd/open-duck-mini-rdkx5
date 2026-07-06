# Phase 2 PPO-Loc Compression Seed-5 Augmentation Decision

status: `HOLD_PPO_LOC_COMPRESSION_SEED_TRADEOFF`

This is an offline compression and gate decision. It did not SSH, deploy, run
robot tests, touch the robot, run grounded replay, or change robot runtime
behavior.

## Context

The current deployable-shape phase-modulated parent still passes the corrected
bridge rough+push gates:

- parent ONNX: `policy/candidates/phase2_health_routed_parent_phase_mod_rate150_20260706/candidate.onnx`
- parent ONNX sha256: `5cadefcb3582043eb989a0e7c65ea9e2702a0815ba46c9ffe1c70b1f68f1db8f`
- x=0.08 rough+push corrected bridge: `8 / 8` duration complete
- x=0.0 rough+push corrected bridge: `8 / 8` duration complete

The blocker is converting that passing parent into a restorable PPO-compatible
step-0 checkpoint for Stage A domain-randomized training.

## Seed-5 Augmentation

The initial PPO-loc step-0 checkpoint reproduced the supervised PPO-loc prior
with high fidelity, but failed seed 5 after a late push:

- status: `HOLD_PPO_STEP0_SEED5_FAILURE`
- x=0.08 full8: `7 / 8`
- failing seed: `5`
- failure: post-push stability margin loss, not velocity-envelope excess

To test whether this was a localized compression gap, a passing parent seed-5
trace was added to the manifest:

- trace manifest: `outputs/analysis/phase2_health_routed_parent_seed5_trace_manifest.json`
- trace manifest status: `PASS_BC_TRACE_MANIFEST_READY`
- seed-5 trace samples: `750`
- augmented manifest: `outputs/analysis/phase2_health_routed_parent_seed5_augmented_manifest.json`
- augmented manifest status: `PASS_FILTERED_BC_MANIFEST_READY`
- augmented manifest entries: `8`
- augmented manifest samples: `6000`

## Variants Tested

All variants used:

- PPO-loc actor contract
- hidden sizes: `[512, 256, 128]`
- activation: `swish`
- target-rate scale: `0.08`
- target-rate limit: `1.5 rad/s`
- step-0 export scale logit: `-2.0`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- terrain z scale: `0.0075`
- pushes: enabled, `0.075-0.125`, interval `1.0-1.5 s`
- reset: `home-support`, settle ticks `10`

| variant | step-0 ONNX sha256 | gate result | failing seed |
|---|---|---|---|
| original PPO-loc step0, no seed-5 trace | `10499450f92307a49de9faf8de557cb6348977b9ec4f0ecb798758b57cfc5aa8` | `7 / 8` x=0.08 full8 | `5` |
| seed-5 trace weighted `5.0x` | `58eb6e0b4ce1af2e920105ff7cbd07d67b9864aed329745e6726cdcb349460f4` | `7 / 8` x=0.08 full8 | `0` |
| seed-5 trace weighted `2.5x` | `cd87074bebf106e28eea0e13d1f0d8b0ac559986836d18b0ce76f661e9dc22e8` | `1 / 2` seed-0/5 screen | `0` |
| seed-5 trace equal weight, fit seed `31` | `ab159c60ee2bc42299b5e960495bc5a182c15a1881929ae3a190ee3db1cffe40` | `7 / 8` x=0.08 full8 | `2` |
| seed-5 trace equal weight, fit seed `33` | `d431b8b30f3ac51d8e6715938d9d09e981daf341f8af16e00fb3aa63b5dbab0f` | `2 / 3` seed-0/2/5 screen | `5` |

## Key Gate Evidence

### Seed-5 weighted 5.0x

- report: `outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_SEED5_WEIGHTED_PPO_LOC_RATE150_STEP0_X008_FULL8_GATE.md`
- JSON sha256: `12035a88bcbd08931dd6c288338c3fc192ec464a9a563f46e62d55d0c88fb26b`
- duration complete: `7 / 8`
- failing seed: `0`
- seed 0 termination: `fall_or_nan` at `644` samples
- seed 5: `PASS_CANDIDATE_SIM_GATE`
- velocity-envelope excess p95/max: `0.0000 / 0.0000`

### Seed-5 weighted 2.5x

- report: `outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_SEED5_W2P5_PPO_LOC_RATE150_STEP0_X008_SEED0_5_SCREEN.md`
- JSON sha256: `6d89edc80a89bf79858d470be0a351327b1da358641a883b498770e93c402a98`
- duration complete: `1 / 2`
- failing seed: `0`
- seed 0 termination: `fall_or_nan` at `658` samples
- seed 0 mean vx: `-0.0004 m/s`
- seed 0 max velocity excess: `0.4312 rad/s`
- seed 5: `PASS_CANDIDATE_SIM_GATE`

### Seed-5 equal weight, fit seed 31

- report: `outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_SEED5_EQUAL_PPO_LOC_RATE150_STEP0_X008_FULL8_GATE.md`
- JSON sha256: `17eb9119a4017b84e4f1cd3ee7765c72cff2d48529547cb0e60cd867a06ded0e`
- duration complete: `7 / 8`
- failing seed: `2`
- seed 2 termination: `fall_or_nan` at `293` samples
- seed 2 mean vx: `-0.0398 m/s`
- seed 2 track ratio: `-0.4979`
- seed 5: `PASS_CANDIDATE_SIM_GATE`
- velocity-envelope excess p95/max: `0.0000 / 0.0000`

### Seed-5 equal weight, fit seed 33

- report: `outputs/analysis/PHASE2_HEALTH_ROUTED_PARENT_SEED5_EQUAL_SEED33_PPO_LOC_RATE150_STEP0_X008_SEED0_2_5_SCREEN.md`
- JSON sha256: `7d898648e332674479d18efb4153f1aa546445f2936b7dc7c872b4cd22bcc1a9`
- duration complete: `2 / 3`
- failing seed: `5`
- seed 5 termination: `fall_or_nan` at `156` samples
- seed 5 mean vx: `0.1332 m/s`
- seed 5 track ratio: `1.6645`
- seed 0 and seed 2: `PASS_CANDIDATE_SIM_GATE`
- velocity-envelope excess p95/max: `0.0000 / 0.0000`

## Decision

Scalar seed-5 manifest weighting and random re-fitting are not sufficient to
produce a valid Phase 2 PPO step-0 warm-start. The failures move between seeds:

- no seed-5 trace: seed 5 fails
- seed-5 trace overweighted: seed 0 fails
- seed-5 trace equal weight, fit seed 31: seed 2 fails
- seed-5 trace equal weight, fit seed 33: seed 5 fails

The passing phase-modulated parent remains valid, but the standard PPO-loc
compression is not robust enough to preserve it across the rough+push full8
gate. Do not launch Stage A domain-randomized training from any PPO-loc step-0
variant in this report.

## Next Work

The next aligned Phase 2 work is to preserve the parent mechanism in the
trainable artifact instead of continuing scalar PPO-loc compression sweeps:

1. Add or adapt a restorable PPO actor path that preserves the phase/context
   conditioning used by the passing phase-modulated parent.
2. Build a step-0 checkpoint from that policy class with action-level fidelity
   to the parent.
3. Re-run the same x=0.08 rough+push full8 gate and the x=0.0 command-semantics
   full8 gate before launching Stage A DR.

Robot validation remains blocked.
