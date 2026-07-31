# PPO-Loc Iter24 Live-Oracle Seed2-Active Rate150 Step0 Decision

status: `HOLD_PPO_LOC_STEP0_GATE_REGRESSION`

## Context

Iter24 remains the latest useful deployable live-oracle baseline: it passes
compact rough+push seeds 0, 1, 2, and 7, but fails seed6. Iter27 showed that
continuing the current BC-only live-oracle rung makes the distribution worse.

This experiment changed the representation into a PPO-compatible actor shape
so future Phase 2 training can warm-start from a real Brax PPO checkpoint
rather than from a deployable-only ONNX.

No PPO updates, robot tests, SSH, deploy, grounded replay, or runtime behavior
changes were performed.

## Artifacts

- source manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_024_history_context_resetsettle10_seed2_active/live_oracle_dagger_aggregate_manifest.json`
- PPO-loc BC NPZ: `outputs/analysis/ppo_loc_iter24_live_oracle_seed2_active_rate150_candidate/candidate_mlp.npz`
- PPO-loc BC NPZ sha256: `886ec5b7153f430cc4dcbf593d277bd66bdff9f29ec5121b15ab5e3e6de824b3`
- PPO-loc BC ONNX: `outputs/analysis/ppo_loc_iter24_live_oracle_seed2_active_rate150_candidate/candidate.onnx`
- PPO-loc BC ONNX sha256: `cbd608e11a3f9290fe747fafc1b2c676103d2269db2dd64de958f3128cdefae0`
- PPO step0 checkpoint: `outputs/analysis/ppo_loc_iter24_live_oracle_seed2_active_rate150_step0_checkpoint`
- PPO step0 ONNX: `outputs/analysis/ppo_loc_iter24_live_oracle_seed2_active_rate150_step0.onnx`
- PPO step0 ONNX sha256: `de669ede7342797e07f0acd21f7b8a5be975af62bde0f07d9a1730918a454ee7`
- step0 fidelity JSON sha256: `4284c0685f64ab0bda4fa092fb29c55a8720589e8cf3757e7c3d44b31734f13f`
- x=0.08 screen JSON sha256: `e922d34ab4c8ebb3932f219383ba1e0659814ba767c29b01d23a5363732fa104`

## Step0 Export Fidelity

The PPO checkpoint was exported through the normal Playground/Brax ONNX path and
compared with the PPO-loc BC ONNX over 2048 manifest observations.

status: `PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY`

- MAE: `0.0000000495`
- p95 abs error: `0.0000001416`
- max abs error: `0.0000002980`

This proves the checkpoint/export path is faithful to the PPO-loc BC model.

## Compact x=0.08 Screen

Task-matched corrected-bridge screen:

- task: `rough_terrain_backlash`
- command: `x=0.08`
- terrain hfield z scale: `0.0075`
- reset mode: `home-support`
- reset settle ticks: `10`
- push perturbations: enabled, `0.075-0.125`, interval `1.0-1.5 s`

| seed | status | samples | termination | track_ratio | mean_local_vx | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 | max_vel_excess |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 638 | `fall_or_nan` | 0.0190 | 0.0015 | 0.1650 | 0.0788 | 1.5193 | 0.1782 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3428 | 0.0274 | 0.1928 | 0.1583 | 1.5284 | 0.1817 | 0.0000 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3323 | 0.0266 | 0.1821 | 0.1584 | 1.5248 | 0.1839 | 0.0000 |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 212 | `fall_or_nan` | -0.7918 | -0.0633 | 0.2343 | 0.0724 | 1.5167 | 0.1764 | 0.0000 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 577 | `fall_or_nan` | 0.6774 | 0.0542 | 0.3193 | 0.0033 | 1.5336 | 0.1783 | 0.0000 |

Distribution:

- pass count: `2 / 5`
- fall count: `3 / 5`
- mean track ratio: `0.1160`
- mean local vx: `0.0093 m/s`
- max corrected velocity-envelope excess: `0.0000 rad/s`

## Interpretation

The PPO-loc step0 path is now technically available and export-faithful, but
the PPO-shaped compression does not preserve the iter24 live-oracle behavior
well enough to promote as a training start by itself. It regresses seeds 0, 6,
and 7 under the compact rough+push corrected-bridge screen.

The regression is not from actuator-rate excess or ONNX export mismatch. It is
from model/optimization compression into the PPO-loc actor shape.

## Decision

Do not promote this step0 checkpoint as the next Phase 2 training restore point
without an additional behavior-preservation mechanism.

Recommended next step:

- use this artifact as the verified PPO checkpoint-construction path;
- do not run long PPO from it directly;
- build the next PPO run around stronger behavior preservation, such as a
  behavior-prior loss from the deployable iter24/selector oracle, or a step0
  candidate selected by task-matched gate rather than action fidelity alone.
