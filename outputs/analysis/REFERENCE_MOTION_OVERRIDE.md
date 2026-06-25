# Reference Motion Override

status: `PASS_REFERENCE_OVERRIDE_BUILT`
source_reference: `/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/data/polynomial_coefficients.pkl`
output_pickle: `outputs/analysis/reference_motion_x004_override.pkl`
output_sha256: `deb8553d72e162331e788ca2b7e3e055b765a2ae01642b15ae316f07afb55601`

## Override

- replaced_key: `0.074_-0.037_-0.074`
- command_for_lookup: `{'x': 0.04, 'y': 0.0, 'yaw': 0.0}`

## Source Mix

- `0.0_-0.037_-0.074` weight `0.2297`
- `0.0_0.037_-0.074` weight `0.2297`
- `0.074_-0.037_-0.074` weight `0.2703`
- `0.074_0.037_-0.074` weight `0.2703`

## Synthesized Base Velocity

| signal | min | max | mean | p95_abs |
|---|---:|---:|---:|---:|
| `linvel_x` | 0.0193 | 0.0649 | 0.0426 | 0.0641 |
| `linvel_y` | -0.2361 | 0.2362 | -0.0021 | 0.2350 |
| `linvel_z` | -0.0831 | 0.0514 | -0.0007 | 0.0598 |
| `angvel_x` | -0.0000 | 0.0000 | -0.0000 | 0.0000 |
| `angvel_y` | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `angvel_z` | -0.0001 | -0.0000 | -0.0000 | 0.0001 |

## Interpretation

- The override preserves the original reference-grid shape by replacing the nearest key that the current environment already selects for `x=0.04,y=0,yaw=0`.
- This avoids changing `PolyReferenceMotion` before we know whether a command-matched reference helps.
- Do not deploy this to the robot. It is a training-only artifact for a possible V20 experiment.
