# Phase 2 Push-Trained Checkpoint Screen Decision

status: `HOLD_PUSH_TRAINED_CHECKPOINTS_NOT_PROMOTABLE`

This screen tested whether already-generated Phase 2 push-training checkpoints could
supersede the command-gated terrain candidate for rough-terrain gentle-push robustness.

All tests were offline sim only:

- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- terrain: `hfield_z_scale=0.002`
- command: `x=0.08`
- bridge mode: `fitted`
- duration: `5s`
- push: enabled, interval `1.0-1.5s`, magnitude `0.05-0.10`
- swing gates enabled

## Results

| checkpoint | seeds | status | key result |
|---|---|---|---|
| Stage B0 mild-push latest `491520` | `6,7` screen | `PASS_CANDIDATE_SIM_GATE` | fixed the previously weak push seeds with max tracking p95 `0.1997 rad` |
| Stage B0 mild-push latest `491520` | `0-7` full | `HOLD_CANDIDATE_TRACKING` | 4/8 seeds held on tracking; max tracking p95 `0.2050 rad`; no falls; no envelope excess |
| Stage B0 mild-push `163840` | `0,2,4,5` screen | `HOLD_CANDIDATE_TRACKING` | seeds 0 and 5 held; max tracking p95 `0.2038 rad` |
| Stage B0 mild-push `327680` | `0,2,4,5` screen | `HOLD_CANDIDATE_TRACKING` | all screened seeds held; max tracking p95 `0.2057 rad` |
| Stage B1 full-flat/gentle-push latest `491520` | `0,2,4,5,6,7` screen | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | mean track ratio `0.1247`; rough-terrain gait collapses toward standstill |

## Interpretation

Stage B0 is the useful direction: it reduces pitch-chain target velocity to about
`1.7-1.8 rad/s`, preserves forward movement, and fixes the original seed-6 push envelope
failure. Its blocker is strict tracking p95 on several seeds, not actuator envelope or
falling.

Stage B1 is not useful for promotion: stronger push/physics robustness pressure makes the
policy too conservative on rough terrain, with low single-support percentage and low
forward progress.

## Next Recommendation

Do not promote any screened push-trained checkpoint. The next training run should start
from the B0/motion-preserving direction and add tracking-margin pressure without further
reducing forward progress. Concretely, prefer a short B0-continuation recipe with:

- lower or no extra push magnitude increase,
- explicit command-progress preservation,
- stronger actuator tracking margin only around the `0.20 rad` strict gate,
- no global target filtering.

No robot test, SSH, deploy, grounded replay, or runtime behavior change was performed.
