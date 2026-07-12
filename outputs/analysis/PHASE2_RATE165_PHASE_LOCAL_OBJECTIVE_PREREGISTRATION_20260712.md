# Rate165 Phase-Local Motion-Preserving Objective Preregistration

status: `PREREGISTERED_OFFLINE_ONLY`

## Evidence and scope

The clean ID13-last suspended `x=0.08` trace has zero CRC/reset events but
misses the unchanged `0.05 rad` tracking-p95 gate at left hip pitch and left
knee. The fixed-target gain A/B and local target-tail cap screens were rejected.

An eight-bin phase audit of ticks 5 onward gives:

| joint | highest-error phase bins | bin p95 errors (rad) | low-error bins |
|---|---|---|---|
| left hip pitch | 1, 2 | 0.05944, 0.06237 | 0, 3, 4, 7 |
| left knee | 0, 1 | 0.06181, 0.07343 | 5, 6, 7 |

Absolute tracking error versus same-tick absolute target rate has Pearson
correlation `0.4145` for left hip pitch and `0.2945` for left knee. This is
evidence of phase localization and association, not proof of causation.

The current rate165 student already penalizes temporal target-rate excess over
`1.65 rad/s` for every action. A global smoothing or hard-cap experiment would
therefore duplicate an existing mechanism and is out of scope.

## Frozen hypothesis

A phase-local, pitch-chain temporal penalty applied during student fitting can
reduce demand in the empirically weak tracking windows while an explicit
rate165 behavior-anchor loss preserves the walking trajectory. The
corresponding half-cycle-shifted windows must be applied to the right leg to
preserve bilateral structure; this is a training objective, not a runtime
filter or target rewrite.

## Frozen screen order

1. Implement contract-tested phase/joint weighting in the existing BC trainer.
2. Run one CPU-only compact fit/screen, with no robot, iGPU, onboard GPU, Colab,
   deployment, or runtime changes.
3. Compare against the exact rate165 parent on the existing corrected bridge.
4. Allocate Colab only if the compact screen passes every rule below.

## Frozen pass rules

The compact candidate must satisfy all of the following:

- `x=0.08`: duration complete, no fall, zero corrected p95/max velocity excess.
- `x=0.08`: track ratio at least `0.3230` (95% of parent `0.3400`).
- `x=0.08`: mean local vx at least `0.02584 m/s` (95% of parent `0.0272`).
- `x=0.08`: single support at least `21.4066%` (95% of parent `22.5333%`).
- `x=0.0`: duration complete, no fall, mean local vx magnitude no greater than
  `0.002 m/s`, and max pitch-chain p95 velocity no greater than `0.07 rad/s`.
- Predicted pitch-chain demand must improve broadly, not only at the maximum:
  left hip-pitch and left-knee target-rate p95 must each improve by at least
  `10%` on the rate165 trace corpus.
- No other joint target-rate p95 or maximum may regress by more than `10%`.

Any failure closes this objective without parameter sweeping. Passing the
compact screen authorizes a separately logged Colab training proposal only; it
does not authorize hardware movement or grounded replay.

