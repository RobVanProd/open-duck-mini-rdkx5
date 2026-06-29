# Phase 2 Target-Smoothing Diagnostic Decision

status: `HOLD_GLOBAL_TARGET_FILTERS_NOT_PROMOTABLE`

This diagnostic tested whether simple target-stage wrappers could recover the
rough-terrain gentle-push margin for the promoted corrected-bridge candidate without
damaging the existing no-push rough-terrain gate.

Base candidate:

- `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_20260628/candidate.onnx`

Wrapper:

- `target = obs[83:97] + alpha * (desired_target - obs[83:97])`
- command scale unchanged: `low_scale=1.0`, `high_scale=1.0`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- terrain: `hfield_z_scale=0.002`
- duration: `5s`

## Results

| wrapper | x=0.08 gentle push | x=0.08 no push | decision |
|---|---|---|---|
| unsmoothed promoted candidate | `HOLD_CANDIDATE_TARGET_VELOCITY` on seed 6, max excess `0.0212 rad/s` | `PASS_CANDIDATE_SIM_GATE` | baseline |
| target smooth `alpha=0.995` | `PASS_CANDIDATE_SIM_GATE`, max tracking p95 `0.1981 rad` | `HOLD_CANDIDATE_TRACKING` on seed 7, max tracking p95 `0.2005 rad` | not promotable |
| target smooth `alpha=0.997` | `PASS_CANDIDATE_SIM_GATE`, max tracking p95 `0.1986 rad` | `HOLD_CANDIDATE_TRACKING` on seed 7, max tracking p95 `0.2013 rad` | not promotable |
| target smooth `alpha=0.999` | targeted seed 6/7 push screen passed, max tracking p95 `0.1967 rad` | targeted seed 5/7 no-push screen held on seed 7, max tracking p95 `0.2002 rad` | not promotable |
| corrected per-joint target-delta clamp | targeted seed 6/7 push screen held on seed 7, max tracking p95 `0.2007 rad` | not run after push hold | not promotable |

## Interpretation

Target-stage smoothing directly addresses the push-induced rate margin: every tested
smoothing value removed the known seed-6 gentle-push envelope failure.

However, the same smoothing consistently pushes the no-push seed-7 tracking metric just
over the strict `0.20 rad` gate. This is a narrow miss, but it is still a gate miss. The
wrapper is therefore useful evidence for the mechanism, not a deployable/promotable Phase
2 candidate.

The corrected per-joint target-delta clamp also removed the seed-6 envelope excess, but it
still missed seed-7 tracking under the targeted gentle-push screen. That makes the result
stronger: the remaining issue is not just raw target velocity. The push recovery needs a
more local policy correction that changes the perturbation response itself.

## Next Recommendation

Stop global target-filter sweeps. The remaining push robustness problem needs a more local
policy correction that affects perturbation recovery itself, without changing nominal
no-push gait timing.

No robot test, SSH, deploy, grounded replay, training, or runtime behavior change was
performed.
