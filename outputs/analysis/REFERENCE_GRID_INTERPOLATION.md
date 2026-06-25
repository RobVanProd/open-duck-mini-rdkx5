# Reference Grid Interpolation

status: `PASS_INTERPOLATED_REFERENCE_PROPOSAL`
reference_path: `/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/data/polynomial_coefficients.pkl`
target_command: `{'x': 0.04, 'y': 0.0, 'yaw': 0.0}`

## Source Keys

- `0.0_-0.037_-0.074` command `{'x': 0.0, 'y': -0.037, 'yaw': -0.074}` weight `0.2297`
- `0.0_0.037_-0.074` command `{'x': 0.0, 'y': 0.037, 'yaw': -0.074}` weight `0.2297`
- `0.074_-0.037_-0.074` command `{'x': 0.074, 'y': -0.037, 'yaw': -0.074}` weight `0.2703`
- `0.074_0.037_-0.074` command `{'x': 0.074, 'y': 0.037, 'yaw': -0.074}` weight `0.2703`

## Composite Base Velocity

| signal | min | max | mean | p95_abs |
|---|---:|---:|---:|---:|
| `linvel_x` | 0.0193 | 0.0649 | 0.0426 | 0.0641 |
| `linvel_y` | -0.2361 | 0.2362 | -0.0021 | 0.2350 |
| `linvel_z` | -0.0831 | 0.0514 | -0.0007 | 0.0598 |
| `angvel_x` | -0.0000 | 0.0000 | -0.0000 | 0.0000 |
| `angvel_y` | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `angvel_z` | -0.0001 | -0.0000 | -0.0000 | 0.0001 |

## Interpretation

- The reference grid has no exact `y=0` entry, but it has symmetric positive/negative lateral entries.
- Averaging the two nearest lateral references cancels most mean lateral velocity.
- Interpolating between the nearest lower/upper `dx` rows can synthesize a lower-speed reference closer to the `x=0.04` gate than the raw nearest key.
- This is an offline analysis only; training would need explicit support for using a synthesized reference artifact before launching V20.
