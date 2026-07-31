# Phase 2 Command-Gated Recovery / Walking Candidate Decision

status: `PASS_COMMAND_GATED_Z0025_BOUNDARY_GATE`

This is an offline sim/eval result only. No robot test, SSH, deploy, grounded
replay, tuning, or runtime behavior change was performed.

## Candidate

- candidate: `outputs/analysis/phase2_z0025_command_gated_bestrec70_rate1p9_candidate/candidate.onnx`
- candidate_sha256: `41ec72e7d3ab2b2a351c36de57b38a3c78c273270b6ba10950979df73733fea7`
- contract: `obs[1,101] -> continuous_actions[1,14]`
- gate: `high_weight = clip(abs(obs[6]) / 0.08, 0, 1)`
- low-command recovery policy: `outputs/analysis/phase2_bestwalk_gain070_targetlimited0999_candidate/candidate.onnx`
- low-command recovery sha256: `941781d4d3178ccc1d99941dbeb1d867405fa92271c68197d2490e3c05976a8e`
- high-command walking policy: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0_contactphase_rate1p9_bc_candidate/candidate.onnx`
- high-command walking sha256: `f00ba8a89f4e24e7c393309acd434cbc95132473aa3df562dacf4fe527049822`
- composition tool: `tools/compose_command_gated_onnx_policy.py`

The low-command branch is a scaled, target-limited BEST_WALK recovery policy
used only near zero command. The high-command branch is the existing `rate1p9`
rough-terrain walking student used at x=0.08. The composed ONNX remains a single
feed-forward deployable policy with the standard 101-observation / 14-action
contract.

## Preflight Screens

### Low-Command Recovery Screen

Artifact:
`outputs/analysis/PHASE2_BESTWALK_GAIN070_TARGETLIMITED0999_SCREEN_X0_SEED5_Z0025.md`

- command_x: `0.0`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0025`
- seed: `5`
- status: `PASS_CANDIDATE_SIM_GATE`
- samples: `750`
- mean_local_vx: `0.0010 m/s`
- base_height_min: `0.1457 m`
- max_pitch_vel_p95: `2.7472 rad/s`
- p95/max velocity excess: `0.0000 / 0.0000 rad/s`
- max_tracking_p95: `0.1947 rad`

### Command-Gated x=0 Seed-5 Screen

Artifact:
`outputs/analysis/PHASE2_Z0025_COMMAND_GATED_BESTREC70_RATE1P9_SCREEN_X0_SEED5.md`

- command_x: `0.0`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0025`
- seed: `5`
- status: `PASS_CANDIDATE_SIM_GATE`
- samples: `750`
- mean_local_vx: `0.0010 m/s`
- max_pitch_vel_p95: `2.7472 rad/s`
- max_tracking_p95: `0.1947 rad`

### Command-Gated x=0.08 Preservation Screen

Artifact:
`outputs/analysis/PHASE2_Z0025_COMMAND_GATED_BESTREC70_RATE1P9_SCREEN_X008_SEEDS0_3.md`

- command_x: `0.08`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0025`
- seeds: `0, 3`
- status: `PASS_CANDIDATE_SIM_GATE` on both seeds

## Full Gate: x=0.0

Artifact:
`outputs/analysis/PHASE2_Z0025_COMMAND_GATED_BESTREC70_RATE1P9_FULLGATE_X0.md`

- command_x: `0.0`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0025`
- bridge_mode: `fitted`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- seeds: `0-7`
- duration: `15 s`
- status: `PASS_CANDIDATE_SIM_GATE` on `8/8`
- falls: `0/8`
- duration_complete: `8/8`
- mean_local_vx_mean: `-0.0004 m/s`
- body_pitch_p95_mean: `0.0294 rad`
- base_height_min_mean: `0.1526 m`
- max_pitch_vel_p95_mean: `2.7472 rad/s`
- p95 velocity excess mean: `0.0000 rad/s`
- max velocity excess mean: `0.0000 rad/s`
- max_tracking_p95_mean: `0.1929 rad`

This resolves the previous zero-command seed-5 hold for the `rate1p9` candidate.

## Full Gate: x=0.08

Artifact:
`outputs/analysis/PHASE2_Z0025_COMMAND_GATED_BESTREC70_RATE1P9_FULLGATE_X008.md`

- command_x: `0.08`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0025`
- bridge_mode: `fitted`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- seeds: `0-7`
- duration: `15 s`
- status: `PASS_CANDIDATE_SIM_GATE` on `8/8`
- falls: `0/8`
- duration_complete: `8/8`
- mean_local_vx_mean: `0.0299 m/s`
- track_ratio_mean: `0.3742`
- body_pitch_p95_mean: `0.1153 rad`
- base_height_min_mean: `0.1526 m`
- max_pitch_vel_p95_mean: `1.9160 rad/s`
- p95 velocity excess mean: `0.0000 rad/s`
- max velocity excess mean: `0.0000 rad/s`
- max_tracking_p95_mean: `0.1937 rad`
- single_support_mean: `21.3667 %`

The candidate preserves the rough-terrain walking behavior from the high-command
branch while keeping the corrected bridge velocity envelope clean.

## Interpretation

The composed command-gated ONNX passes the current z=0.0025 rough-terrain
boundary gate at both x=0.0 and x=0.08. It is still a slow walker, with x=0.08
track ratio around `0.3742`, but it preserves command semantics: it stands near
zero command and moves forward at nonzero command without corrected-envelope
excess.

This is not the final Phase 2 domain-randomized robustness goal. It is a
recovered boundary candidate that fixes the previous x=0 seed-5 blocker and can
serve as a stronger warm start or baseline for the next push/terrain robustness
stage.

## Next Step

Proceed offline to the next Phase 2 robustness gate:

1. Run push-recovery evaluation on this command-gated candidate.
2. If push recovery holds, train or fine-tune from this candidate with the
   staged Phase 2 domain-randomization curriculum.
3. Keep robot validation blocked until the offline corrected-bridge robustness
   gates are reviewed.
