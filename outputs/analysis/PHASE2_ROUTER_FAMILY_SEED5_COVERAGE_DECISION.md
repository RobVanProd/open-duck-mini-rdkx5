# Router-Family Seed-5 Coverage Decision

status: `PASS_ROUTER_FAMILY_SEED5_COVERAGE`

Existing router-family candidates cover the full-gate seed-5 lunge failure: iter25, iter26, and iter27 pass seed 5 under the z=0.0075 rough+push corrected-bridge screen while iter24 reproduces the lunge.

This is an offline analysis decision. It did not train, deploy, SSH, run robot tests, grounded replay, or change runtime behavior.

## Screen

- screen_md: `outputs/analysis/PHASE2_ROUTER_FAMILY_SEED5_Z0075_INTERMEDIATE_PUSH_SCREEN.md`
- screen_json: `outputs/analysis/phase2_router_family_seed5_z0075_intermediate_push_screen.json`
- task: `rough_terrain_backlash`
- command_x: `0.08`
- terrain_hfield_z_scale: `0.0075`
- bridge: corrected fitted actuator bridge
- reset: `home-support`, settle ticks `10`
- pushes: `0.075-0.125` every `1.0-1.5 s`

## Result

| policy | status | samples | vx | track_ratio | pitch_p95 | base_min | p95_excess | max_excess |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `iter24` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 162 | 0.1370 | 1.7128 | 0.9002 | -0.0048 | 0.0000 | 0.0000 |
| `iter25` | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0314 | 0.3924 | 0.1779 | 0.1589 | 0.0000 | 0.0000 |
| `iter26` | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0301 | 0.3765 | 0.1668 | 0.1586 | 0.0000 | 0.0000 |
| `iter27` | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0277 | 0.3461 | 0.1729 | 0.1577 | 0.0000 | 0.0000 |

## Interpretation

- `iter24` repeats the seed-5 lunge/pitchover failure.
- `iter25`, `iter26`, and `iter27` each complete seed 5 with zero corrected velocity-envelope excess.
- Seed 5 is therefore covered by the branch family; the current blocker is branch selection / behavior preservation, not missing seed-5 source behavior.

## Next Recommendation

Build the next source around branch preservation/routing. A minimal full-8 source route can keep the command-gated source for seeds it already passes and route seed 5 to iter25/iter26/iter27 behavior. Do not add more tiny seed-specific relabels until an eval-only router/wrapper has been tested on full-8 coverage.
