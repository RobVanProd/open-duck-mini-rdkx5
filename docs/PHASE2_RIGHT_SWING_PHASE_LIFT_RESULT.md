# Phase 2 Right-Swing Phase-Lift Result

status: `HOLD_RIGHT_SWING_PHASE_LIFT_RECIPE`

## Summary

The phase-primary right-swing lift recipe trained and exported cleanly on a
fresh A100 Colab session. It did not produce a promotable candidate against the
corrected-bridge x=0.08 gate.

This was an offline-only run. No robot test, SSH, deploy, grounded replay, or
runtime behavior change was performed.

## Inputs

- Playground commit: `06d95c5` (`rewards: add phase-primary swing lift cost`)
- RDK commit: `e414601` (`tools: add phase-primary right swing lift workflow`)
- Colab session: `open-duck-a100-phase-lift`
- Artifact bundle:
  `outputs/analysis/colab_cli/open-duck-a100-phase-lift-phase2-right-swing-phase-lift-20260630T185346Z/open_duck_colab_cli_phase2-right-swing-phase-lift_20260630T185443Z_artifacts.tar.gz`
- Artifact sha256:
  `5ff096d39169c4e1bbf24314dbf1032779105b4f29c4d2820086772fd76ab2e4`
- Corrected bridge:
  `outputs/analysis/actuator_response_fit_corrected_knee.json`
- Eval:
  `rough_terrain_backlash`, `x=0.08`, fitted bridge, z-scale `0.0024`,
  seeds `0-7`, CPU evaluator.

## Recipe

The recipe added a default-off phase-primary lift cost to the Playground:

```text
forward_phase_swing_lift_scale: -0.0006
forward_phase_swing_lift_target_m: 0.012
forward_phase_swing_lift_huber_delta: 0.003
```

This was intended to shape lift during the commanded swing phase even when the
foot stays planted, rather than relying only on contact-primary swing
clearance. The corrected per-joint bridge gate was unchanged.

## Exported Checkpoints

| checkpoint | sha256 |
|---|---|
| `2026_06_30_190655_40960.onnx` | `f7e8567977a2313565e2ef377a6088dc53ce98ac97a9d337120a6993a057484a` |
| `2026_06_30_190949_81920.onnx` | `10f6b35d697cc21646376544ecd5df799117bae531071f4e64f72b060bce8c1a` |
| `2026_06_30_191010_122880.onnx` | `7ed05371667c1b1a96fb73c2b970fb1a3377393d2ae445da9fa6fc11da680d7f` |

## Gate Result

Artifact:
`outputs/analysis/phase2_right_swing_phase_lift_a100_20260630/PHASE2_RIGHT_SWING_PHASE_LIFT_A100_X008_GATE.md`

| checkpoint | pass count | falls | duration complete | mean track ratio | mean vx | mean max-velocity excess |
|---|---:|---:|---:|---:|---:|---:|
| `40960` | 1/8 | 0/8 | 8/8 | 0.2514 | 0.0201 m/s | 0.1007 rad/s |
| `81920` | 3/8 | 0/8 | 8/8 | 0.2496 | 0.0200 m/s | 0.0879 rad/s |
| `122880` | 2/8 | 0/8 | 8/8 | 0.2590 | 0.0207 m/s | 0.1852 rad/s |

The terrain swing subchecks were not the binding failure. The policies stayed
upright and usually produced enough local swing lift/advance to pass the local
terrain swing checks, but failed the full candidate gate by low forward
progress and occasional corrected-envelope max target-velocity excess.

## Interpretation

The phase-primary lift signal helped some individual seeds compared with the
right-swing structural run, but it did not move the distribution enough to
promote a candidate. Mean track ratio stayed near `0.25`, far below the Phase 1
slow-walk baseline and below the Phase 2 objective.

This closes another scalar reward hook around the existing swing pattern. The
next branch should change the swing strategy itself, not add another scalar
penalty. Candidate directions:

- longer swing timing to trade rate for time;
- phase-advance only where latency is the binding issue;
- knee-bend-first right swing to improve vertical manipulability within the
  corrected right knee/ankle limits;
- a phase-aware/recurrent student if the stance-transition behavior cannot be
  represented by the current feed-forward policy.

## Follow-Up Swing Diagnostic

The best phase-lift checkpoint by pass count, `81920`, was rerun through the
phase-primary swing-clearance diagnostic:

```text
artifact: outputs/analysis/phase2_right_swing_phase_lift_a100_20260630/PHASE2_RIGHT_SWING_PHASE_LIFT_81920_SWING_DIAGNOSTIC.md
aggregate_verdict: LATENCY_LIMITED
side_verdicts: left LATENCY_LIMITED, right LATENCY_LIMITED
left classifications: 8/8 LATENCY_LIMITED
right classifications: 5/8 LATENCY_LIMITED, 3/8 STRUCTURAL
rate drivers: left_hip_pitch 8, right_ankle 7, right_knee 1
```

Compared with the pre-phase-lift diagnostic, the old blanket right-leg
`R > 1` command-rate problem was mostly removed. The remaining issue is that
the swing windows stay planted for most of the commanded phase even when the
commanded rates are usually affordable. This makes phase timing the next
branch to test: advance the swing-side lift/rate signal by the corrected
3-tick actuator delay and verify that planted swing percentage drops without
reintroducing corrected-envelope excess.
