# Phase 2 z=0.0025 Reset-Settle Diagnostic

status: `HOLD_RESET_SETTLE_REGRESSES`

## Summary

This diagnostic tested whether the z=0.0025 rough-terrain seed-5 x=0 collapse is a reset-contact artifact that can be repaired by settling MJX physics under the reset motor target before the policy loop starts.

Result: reset-settle is not the repair. It worsened the failing x=0 seed and also broke the same seed at x=0.08, where the parent candidate had previously recovered for the 2 s support diagnostic.

## Candidate

- policy: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0_contactphase_rate1p9_bc_candidate/candidate.onnx`
- fit_json: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0025`
- bridge_mode: `fitted`
- seed: `5`
- duration: `2.0 s`
- jax_platform: `cpu`

## Eval Tool Change

Added default-off `--reset-settle-ticks` to the closed-loop evaluator and seed-sweep wrapper.

When nonzero, reset physics is stepped under the reset motor target before the policy loop starts. Policy hidden state, action history, reward counters, and sample counts are not advanced. Default `0` preserves canonical gates.

## Results

| condition | settle ticks | status | samples | vx m/s | track ratio | base min m | pitch vel p95 | max vel excess | tracking p95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| x=0.0 | 10 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | -0.4640 | NA | 0.0602 | 0.1574 | 0.0000 | 0.0437 |
| x=0.0 | 25 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 19 | -0.7824 | NA | 0.0377 | 0.6837 | 0.0000 | 0.0217 |
| x=0.08 | 10 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 35 | -0.4425 | -5.5308 | 0.0640 | 1.0728 | 0.0000 | 0.1161 |

Prior support diagnostic baseline for the same parent candidate:

- x=0 seed 5 without settle: failed at 43 samples with reverse-height collapse.
- x=0.08 seed 5 without settle: recovered for the 2 s support diagnostic with mean vx about `0.0401 m/s`.

## Interpretation

Reset-settle does not isolate a benign reset-contact artifact. Longer settle made the zero-command failure earlier and more severe, and settle also caused the moving command to reverse and fall.

The seed-5 issue remains a support/control-state fragility under partial or unsupported reset conditions, not a simple reset physics settling issue and not an actuator-envelope issue.

## Decision

- Do not canonicalize reset-settle for candidate promotion gates.
- Keep `--reset-settle-ticks` only as a default-off diagnostic knob.
- Do not use the zero-action or active-recovery relabel candidates as parents.
- Next useful branch should target unsupported/partial-contact reset recovery directly, or broaden reset-state training data, rather than settling before evaluation.

## Artifact Hashes

- settle10 x=0 report: `7dbfd039570973db16105d23d12cffcee8350f70208df4d03176ee0d546ff85f`
- settle25 x=0 report: `2088d4ce1c5440972dc537edd78dedb9660982e9e3a65229d1c8520b6fadf853`
- settle10 x=0.08 report: `01a41c0f91a3cee932071fd58c58a16c7a020cb93a3df72c691b2889a1a3695b`

No robot tests, SSH, deploy, grounded replay, or training were performed.
