# Phase 2 z=0.0075 Post-Push Stability A100 Result

status: `HOLD_NO_PROMOTABLE_CHECKPOINT`
generated_at: `2026-07-04T05:05:31.095293+00:00`

## Scope

- Offline sim/training analysis only.
- No robot tests, SSH, deploy, grounded replay, or runtime behavior changes were performed.
- This report summarizes the A100 `phase2-b0g` run and the local compact corrected-bridge checkpoint sweep.

## Training

- run_dir: `outputs/analysis/phase2_z0075_post_push_stability_a100_20260704`
- colab_exit_status: `exit_status=0`
- training_status: `INFO_NON_DEPLOYABLE_TRAINING_RUN`
- returncode: `0`
- elapsed_s: `750.0473559039999`
- latest_onnx: `/content/open_duck_training_phase2_b0g_cli/smoke_20260704T042912Z_gpu/2026_07_04_044055_122880.onnx`
- latest_onnx_sha256: `c45569a28f1af792ca193dab5405711362fc08e5bc2899b6634bf924270b63f3`
- downloaded_bundle_sha256: `95a51e6ded5b6ad3d5596f3512e1120f469c13b5e99474f7a1504dab891efd8b`

### Exported Checkpoints

| checkpoint | sha256 | size_bytes |
|---|---|---:|
| `outputs/analysis/phase2_z0075_post_push_stability_a100_20260704/checkpoints/2026_07_04_043749_40960.onnx` | `7186ca3f08984275847ed3cd86fa55d630da821475c47f057fd7c3f50072051f` | 883946 |
| `outputs/analysis/phase2_z0075_post_push_stability_a100_20260704/checkpoints/2026_07_04_044034_81920.onnx` | `5a852ae5638235d387722af5c39b7a422ad416b624bfcf0aa907610a207410bf` | 884094 |
| `outputs/analysis/phase2_z0075_post_push_stability_a100_20260704/checkpoints/2026_07_04_044055_122880.onnx` | `c45569a28f1af792ca193dab5405711362fc08e5bc2899b6634bf924270b63f3` | 884094 |

## Compact Corrected-Bridge Sweep

- sweep_json: `outputs/analysis/phase2_z0075_post_push_stability_a100_20260704/checkpoint_sweep/candidate_checkpoint_sweep.json`
- commands: `[0.0, 0.08]`
- duration_s: `1.0`
- bridge_mode: `fitted`
- corrected_bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`

| policy | decision | pass_count | max_vel_p95 | max_tracking_p95 | x=0.08 ratio |
|---|---|---:|---:|---:|---:|
| `phase2_b0g_40960` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/2 | 1.3241 | 0.3120 | 0.1001 |
| `phase2_b0g_81920` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/2 | 1.5179 | 0.3120 | 0.0898 |
| `phase2_b0g_122880` | `HOLD_REJECT_CANDIDATE_CHECKPOINT` | 0/2 | 1.4520 | 0.3065 | 0.0636 |

## Decision

- promote_to_full_gates: `False`
- full_gates_run: `False`
- full_gates_skipped_reason: `compact sweep found no checkpoint with meaningful in-envelope forward progress`
- best_compact_screen_policy: `phase2_b0g_40960`
- best_compact_screen_x008_ratio: `0.10008687788649695`

The A100 training run completed and exported valid ONNX checkpoints, but all
three checkpoints failed the compact corrected-bridge screen. The failure is
not over-envelope velocity or action saturation; it is insufficient forward
progress while tracking remains around the prior plateau. No checkpoint from
this run is promoted to full gates or robot work.

next_recommendation: `do not promote this b0g PPO result; return to teacher-action or trust-region continuity rather than another scalar reward tweak`
