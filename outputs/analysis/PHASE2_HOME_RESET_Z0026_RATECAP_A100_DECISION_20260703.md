# Phase 2 Home-Reset z0.0026 Rate-Cap A100 Decision

status: `HOLD_RATECAP_A100_NOT_PROMOTABLE`

## Setup

- source candidate: `policy/candidates/corrected_bridge_cmd_conditioned_rate175_20260627/candidate.onnx`
- source candidate sha256: `63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e`
- warm-start checkpoint: `outputs/analysis/phase2_restore_checkpoints/ppo_bc_command_conditioned_rate175_step0_checkpoint`
- Colab session: `open-duck-a100-phase2-ratecap2`
- Colab hardware: `A100`
- JAX/JAXLIB pin: `0.7.2`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.0026`
- reset contract: zero reset randomization during training; local gate uses `home-support`
- robot/SSH/deploy/grounded replay: `not run`

## Recipe Delta

This run repeated the previous home-reset z0.0026 continuation but made target-rate
pressure active:

- `target_rate_scale=-0.02`
- `actuator_tracking_scale=-0.01`
- `restore_policy_kl_scale=8`
- `forward_swing_target_rate_limit_scale=-0.04`
- `forward_swing_target_rate_limit_joint_indices=2,3,4,11,12,13`
- `forward_swing_target_rate_limit_values=2.5,3.25,2.75,2.25,2.75,2.0`

The detached Colab path completed after the initial `colab exec` transport hold.
The first rate-cap attempt remains recorded as
`HOLD_COLAB_TRANSPORT_ARTIFACT_EMPTY`; this artifact is the actual completed
rate-cap training result.

## Startup Smoke

A concurrent 4096-step startup smoke with the same rate-cap flags completed and
exported:

- ONNX: `outputs/analysis/colab_cli/open-duck-a100-phase2-ratecap2-phase2-z0025-boundary-20260703T054312Z/manual_download/ratecap_startup_smoke_files_final/2026_07_03_055652_5120.onnx`
- sha256: `06aa19c4dcf80f7891dfe7f808175e5fa8eb236d6bd8cd0cf725268ecc504add`
- status: `PASS_SMOKE_RUN`
- reward at step 5120: `86.8771`

This confirms the rate-cap flags and restore checkpoint can compile/train on the
A100 stack. The hold below is a policy-quality result, not a startup failure.

## Produced Checkpoints

| checkpoint | sha256 |
|---:|---|
| 40960 | `01d8ca25ecb5f3eaef02f5025eca0e03d1b482929a2a3efce4fb7215d62bc611` |
| 81920 | `a1fadcbacf281ac923d02b6c68b0d3a03d78434401415170bd951823ac259f9c` |
| 122880 | `4f6b5b1103bd52bdb44d7b352ba4fb33a4c51bea042720dbf7f1841c750a36fe` |

Training summary:

- step 0 reward: `67.1196`
- step 40960 reward: `76.3850`
- step 81920 reward: `62.6652`
- step 122880 reward: `70.6092`

## Checkpoint Screen

Artifact:

- `outputs/analysis/PHASE2_HOME_RESET_Z0026_RATECAP_A100_CHECKPOINT_SCREEN_X008_5S.md`
- `outputs/analysis/phase2_home_reset_z0026_ratecap_a100_checkpoint_screen_x008_5s.json`

5s, seed 0, `x=0.08`, `rough_terrain_backlash`, z=`0.0026`,
`reset-mode=home-support`, corrected fitted bridge:

| candidate | result | mean vx | track ratio | max pitch vel p95 | p95 vel excess | tracking p95 | contact mode |
|---|---|---:|---:|---:|---:|---:|---|
| `ratecap_40960` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0078 | 0.0974 | 1.9902 | 0.0000 | 0.1807 | 100% double support |
| `ratecap_81920` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 0.2271 | 2.8384 | 5.2400 | 2.7283 | 0.2768 | fall / over-envelope |
| `ratecap_122880` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0107 | 0.1343 | 5.0381 | 2.7881 | 0.2131 | slow and over-envelope |

## Decision

Do not promote any rate-cap checkpoint from this A100 run.

The added rate-cap pressure did not produce the desired middle behavior. The
early checkpoint is in-envelope but freezes in double support. The middle
checkpoint moves by falling and leaving the corrected envelope. The late
checkpoint returns to low progress while still over the corrected envelope.

Next recipe should not repeat scalar rate-cap continuation. The remaining
problem is still swing/advance and single-support behavior under the corrected
per-joint limits.
