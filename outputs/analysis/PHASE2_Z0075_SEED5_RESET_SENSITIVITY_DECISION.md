# Phase 2 z=0.0075 Seed 5 Reset Sensitivity Decision

status: `PASS_SEED5_RESET_SENSITIVITY_DIAGNOSTIC`
verdict: `PLAYGROUND_RESET_SENSITIVITY`

This diagnostic is offline sim analysis only. It did not SSH, deploy, train, run robot tests, or change robot runtime behavior.

## Executive Summary

Iter10 seed 5 failure is reset-mode sensitive. With `reset_mode=playground`, the candidate fails immediately on flat and rough terrain, with and without push perturbations. With `reset_mode=home-support`, the same candidate completes the 5 second diagnostic on flat and rough terrain, including rough terrain with intermediate pushes.

The failure happens before any push event fires, and it also appears on flat terrain. Terrain roughness and push perturbations are therefore not the initial trigger. Adding 25 settle ticks to the Playground reset does not rescue the rollout; it makes the failure faster.

## Candidate

- policy: `policy/candidates/phase2_z0075_spike_local_rate150_20260704/candidate.onnx`
- candidate hash: `3874e11e4a132ac90e14a0600071e41b5f147ef1a1486e06934a69368ecca70f`
- command_x: `0.08`
- bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- bridge_mode: `fitted`
- platform: `cpu`
- duration: `5.0s`
- seed: `5`

## Case Matrix

| case | task | reset | settle | push | z scale | status | samples | vx | track | pitch p95 | base min | p95 excess | max excess | tracking p95 | push events | push success |
|---|---|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| rough_z0075_push_playground | rough_terrain_backlash | playground | 0 | yes | 0.0075 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 45 | -0.2996 | -3.7453 | 0.0581 | 0.0888 | 0.0000 | 0.0000 | 0.2203 | 0 | NA |
| rough_z0075_nopush_playground | rough_terrain_backlash | playground | 0 | no | 0.0075 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 45 | -0.2996 | -3.7453 | 0.0581 | 0.0888 | 0.0000 | 0.0000 | 0.2203 | 0 | NA |
| rough_z0075_push_home_support | rough_terrain_backlash | home-support | 0 | yes | 0.0075 | `PASS_CANDIDATE_SIM_GATE` | 250 | 0.0288 | 0.3606 | 0.1847 | 0.1532 | 0.0000 | 0.0000 | 0.1831 | 4 | 0.75 |
| rough_z0075_nopush_home_support | rough_terrain_backlash | home-support | 0 | no | 0.0075 | `PASS_CANDIDATE_SIM_GATE` | 250 | 0.0264 | 0.3303 | 0.1863 | 0.1532 | 0.0000 | 0.0000 | 0.1839 | 0 | NA |
| flat_nopush_playground | flat_terrain_backlash | playground | 0 | no | NA | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 59 | -0.2400 | -2.9998 | 0.0783 | 0.0763 | 0.0000 | 0.0000 | 0.1889 | 0 | NA |
| flat_nopush_home_support | flat_terrain_backlash | home-support | 0 | no | NA | `PASS_CANDIDATE_SIM_GATE` | 250 | 0.0291 | 0.3638 | 0.1082 | 0.1515 | 0.0000 | 0.0000 | 0.1721 | 0 | NA |
| rough_z0075_nopush_playground_settle25 | rough_terrain_backlash | playground | 25 | no | 0.0075 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 16 | -0.7435 | -9.2940 | 0.4258 | 0.0850 | 0.0000 | 0.0000 | 0.1552 | 0 | NA |
| rough_z0075_push_playground_settle25 | rough_terrain_backlash | playground | 25 | yes | 0.0075 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 16 | -0.7435 | -9.2940 | 0.4258 | 0.0850 | 0.0000 | 0.0000 | 0.1552 | 0 | NA |

## Decision

`PLAYGROUND_RESET_SENSITIVITY`

Seed 5 is not primarily failing because of intermediate pushes or rough terrain. It fails from the Playground reset distribution even before push events occur. The same policy survives from `home-support` reset on flat and rough terrain and handles 4 push events with 75% recovery in the 5 second rough diagnostic.

`reset_settle_ticks=25` is not a fix. Both settle variants fail at 16 samples with stronger reverse motion than the no-settle Playground cases.

## Recommended Next Step

Do not add more feed-forward label weights for this failure. Run a broader diagnostic gate with `reset_mode=home-support` across all 8 seeds to determine whether the current policy is actually rough/push-limited once the reset-state mismatch is removed. In parallel, inspect the Playground reset distribution against `home-support` reset so training and evaluation use a consistent initial-state contract.

This diagnostic is not a promotion gate. A deployable Phase 2 candidate still needs the canonical full-duration corrected-bridge gates reviewed before any robot-side validation.
