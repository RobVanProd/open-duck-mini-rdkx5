# Phase 2 z=0.0075 Iter3 Snippet-Augmented Rateclean15 Decision

status: `HOLD_RATE_CLEAN_REINTRODUCED_SEED0_FALL`

This is an offline-only behavior-cloning and sim-screen result. No robot tests,
SSH, deploy, grounded replay, runtime behavior changes, or PPO training were
performed.

## Candidate

- candidate: `policy/candidates/phase2_z0075_iter3_seed0_recovery_snippet_augmented_rateclean15_20260704/candidate.onnx`
- candidate_sha256: `924699fc7b4c580181b715f37dd2d22fd506352399ec0d25de34377a993ed265`
- student_npz: `policy/candidates/phase2_z0075_iter3_seed0_recovery_snippet_augmented_rateclean15_20260704/student.npz`
- student_npz_sha256: `acd2fcc6e34ff823a65b2073a554efa45462b771dd8f47178236ec69868885a5`
- training_manifest: `outputs/analysis/phase2_z0075_iter3_seed0_recovery_snippet_augmented_weighted_manifest.json`
- dataset_id: `9f4ba6b1c342d17b`
- target-rate regularization: limit `1.5 rad/s`, scale `1.0`

## Fit

- status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`
- samples: `51294`
- MAE: `0.010091`
- p95 abs error: `0.034079`
- max abs error: `0.671804`
- target-rate p95: `1.332225 rad/s`
- target-rate p99: `1.491268 rad/s`
- target-rate max: `1.669861 rad/s`
- ONNX p95 error: `0.00000012`
- ONNX max error: `0.00000024`

## Compact Screen

Configuration:

- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0075`
- bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- bridge_mode: `fitted`
- reset_mode: `home-support`
- push interval: `1.0-1.5 s`
- push magnitude: `0.075-0.125`
- duration: `15.0 s`
- platform: `cpu`

### x=0.08

Result: `HOLD_CANDIDATE_FALL_OR_TERMINATION`

| seed | status | samples | mean vx | track ratio | body pitch p95 | base height min | max pitch vel p95 | p95 vel excess | max vel excess | max tracking p95 | push success |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 116 | 0.1733 | 2.1662 | 0.9415 | 0.0105 | 1.5513 | 0.0000 | 0.0000 | 0.1986 | 0.0000 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0322 | 0.4022 | 0.2037 | 0.1532 | 1.5255 | 0.0000 | 0.0000 | 0.1862 | 0.9000 |

Aggregate:

- falls: `1/2`
- duration complete: `1/2`
- mean track ratio: `1.2842`
- mean vx: `0.1027 m/s`
- p95/max velocity excess: `0.0000 / 0.0000`

### x=0.0

Result: `PASS`

| seed | status | samples | mean vx | body pitch p95 | base height min | max pitch vel p95 | p95/max vel excess | max tracking p95 | push success |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0010 | 0.0695 | 0.1533 | 0.0216 | 0.0000 / 0.0000 | 0.0422 | 0.9167 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0007 | 0.0564 | 0.1533 | 0.0217 | 0.0000 / 0.0000 | 0.0397 | 0.9231 |

## Interpretation

The stronger target-rate regularization cleaned up the velocity excess but
reintroduced the seed-0 push/pitchover failure. Compared with the non-rateclean
snippet-augmented student:

- non-rateclean: seed 0 and seed 7 both completed, but both held on max
  corrected-envelope excess;
- rateclean15: seed 7 passes cleanly and x=0.0 still passes, but seed 0 falls
  again.

This shows the current feed-forward student has a local tradeoff between
push-window recovery and rare rate spikes. A global target-rate penalty is too
blunt: it removes the spike by weakening/timing-shifting the recovery behavior.

Do not promote this candidate. The next branch should localize the rate cleanup
to the spike ticks/transitions of the non-rateclean recovered candidate, or add
explicit push/recovery context so the model does not need to encode recovery
with globally sharper action transitions.
