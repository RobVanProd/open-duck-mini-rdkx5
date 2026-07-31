# Phase 2 z=0.0075 Iter3 Snippet-Augmented Rate150 Decision

status: `HOLD_RECOVERY_TRANSFERRED_BUT_RATE_SPIKED`

This is an offline-only behavior-cloning and sim-screen result. No robot tests,
SSH, deploy, grounded replay, runtime behavior changes, or PPO training were
performed.

## Candidate

- candidate: `policy/candidates/phase2_z0075_iter3_seed0_recovery_snippet_augmented_rate150_20260704/candidate.onnx`
- candidate_sha256: `c6e665b743468e796b070ba3bd405627fb42f3c611ddac257fbfbfb33e132c84`
- student_npz: `policy/candidates/phase2_z0075_iter3_seed0_recovery_snippet_augmented_rate150_20260704/student.npz`
- student_npz_sha256: `8c9cbc4b5737b4424ae2161b068afad13fd382dea2afe0fefa3382f6a635111d`
- training_manifest: `outputs/analysis/phase2_z0075_iter3_seed0_recovery_snippet_augmented_weighted_manifest.json`
- dataset_id: `9f4ba6b1c342d17b`
- source entries: `74`
- samples: `51294`
- weighted samples: `51889.0000`

## Fit

- status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`
- MAE: `0.009070`
- p95 abs error: `0.028178`
- max abs error: `0.670479`
- target-rate p95: `1.355027 rad/s`
- target-rate p99: `1.711225 rad/s`
- target-rate max: `5.560378 rad/s`
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

Result: `HOLD_CANDIDATE_TARGET_VELOCITY`

| seed | status | samples | mean vx | track ratio | body pitch p95 | base height min | max pitch vel p95 | p95 vel excess | max vel excess | max tracking p95 | push success |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.0342 | 0.4275 | 0.1934 | 0.1532 | 1.8031 | 0.0000 | 0.3722 | 0.1860 | 0.9167 |
| 7 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.0328 | 0.4098 | 0.1668 | 0.1532 | 1.7948 | 0.0000 | 0.2734 | 0.1891 | 0.9000 |

Aggregate:

- falls: `0/2`
- duration complete: `2/2`
- mean track ratio: `0.4187`
- mean vx: `0.0335 m/s`
- mean push success: `0.9083`
- p95 velocity excess: `0.0000`
- max velocity excess mean/max: `0.3228 / 0.3722 rad/s`

### x=0.0

Result: `PASS`

| seed | status | samples | mean vx | body pitch p95 | base height min | max pitch vel p95 | p95/max vel excess | max tracking p95 | push success |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0010 | 0.0678 | 0.1533 | 0.0204 | 0.0000 / 0.0000 | 0.0419 | 0.9167 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0007 | 0.0556 | 0.1533 | 0.0206 | 0.0000 / 0.0000 | 0.0398 | 0.9231 |

## Interpretation

The targeted push-window snippets transferred the intended recovery behavior:
seed 0 changed from early forward-lunge/pitchover at 126 samples to full
duration completion, while x=0.0 command semantics stayed intact.

The candidate is still not promotable because both x=0.08 seeds now hold on
max corrected-envelope target-velocity excess. This is a better failure mode
than falling, but it is still outside the Phase 2 gate.

The next branch should rate-clean this recovered behavior rather than add more
broad DAgger data. Useful bounded options:

- retrain the same snippet-augmented manifest with stronger target-rate
  regularization or lower target-rate limit;
- isolate the spike ticks from this candidate and relabel/rate-limit only those
  transitions;
- keep the snippet weighting because it demonstrably fixed seed-0 push
  recovery, but prevent the rare target-rate max from leaking into the export.

Do not promote this candidate to robot validation.
