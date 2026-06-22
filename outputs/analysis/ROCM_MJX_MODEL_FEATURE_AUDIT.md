# ROCm MJX Model Feature Audit

xml: `/home/lsd/robots/open-duck-mini-rdkx5/../Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_flat_terrain.xml`
playground_path: `/home/lsd/robots/open-duck-mini-rdkx5/../Open_Duck_Playground`

## Executive Summary

- compile_status: `PASS_MUJOCO_COMPILE`
- compiled nq/nv/nu: `21/20/14`
- compiled bodies/joints/geoms/sites/sensors: `18/15/47/5/15`
- static mesh assets/geoms: `28/47`
- static contact-relevant items: `3`
- contact items missing explicit solref/solimp: `3/3`

This audit does not step physics. It is safe for offline ROCm/MJX
debugging and does not involve robot hardware, SSH, deployment, or
training.

## Compiled Counts

| field | value |
|---|---:|
| `nq` | 21 |
| `nv` | 20 |
| `nu` | 14 |
| `nbody` | 18 |
| `njnt` | 15 |
| `ngeom` | 47 |
| `nsite` | 5 |
| `nsensor` | 15 |
| `nmesh` | 28 |
| `npair` | 0 |
| `neq` | 0 |
| `nkey` | 1 |

## MuJoCo Options

| option | value |
|---|---:|
| `timestep` | 0.002 |
| `iterations` | 1 |
| `ls_iterations` | 5 |
| `integrator` | 0 |
| `cone` | 0 |
| `jacobian` | 2 |
| `solver` | 2 |

## Contact-Relevant Geoms

| name | type | body | contype | conaffinity | condim | friction | solref | solimp |
|---|---|---|---:|---:|---:|---|---|---|
| `left_foot_bottom_tpu` | `mesh` | `foot_assembly` | 1 | 1 | 3 | `[1.0, 0.005, 0.0001]` | `[0.02, 1.0]` | `[0.9, 0.95, 0.001, 0.5, 2.0]` |
| `right_foot_bottom_tpu` | `mesh` | `foot_assembly_2` | 1 | 1 | 3 | `[1.0, 0.005, 0.0001]` | `[0.02, 1.0]` | `[0.9, 0.95, 0.001, 0.5, 2.0]` |
| `floor` | `plane` | `floor` | 1 | 0 | 3 | `[0.6, 0.005, 0.0001]` | `[0.02, 1.0]` | `[0.9, 0.95, 0.001, 0.5, 2.0]` |

## Static Contact Items

| file | name | tag | type | class | contype | conaffinity | condim | friction | solref | solimp |
|---|---|---|---|---|---|---|---|---|---|---|
| `scene_flat_terrain.xml` | `floor` | `geom` | `plane` | `None` | `1` | `0` | `3` | `0.6` | `None` | `None` |
| `open_duck_mini_v2.xml` | `left_foot_bottom_tpu` | `geom` | `mesh` | `collision` | `None` | `None` | `None` | `None` | `None` | `None` |
| `open_duck_mini_v2.xml` | `right_foot_bottom_tpu` | `geom` | `mesh` | `collision` | `None` | `None` | `None` | `None` | `None` | `None` |

## Actuator Order

| id | name | ctrlrange | forcerange |
|---:|---|---|---|
| 0 | `left_hip_yaw` | `[-0.5235987755982979, 0.5235987755982997]` | `[-3.23, 3.23]` |
| 1 | `left_hip_roll` | `[-0.4363323129985815, 0.43633231299858327]` | `[-3.23, 3.23]` |
| 2 | `left_hip_pitch` | `[-1.2217304763960306, 0.5235987755982987]` | `[-3.23, 3.23]` |
| 3 | `left_knee` | `[-1.5707963267948966, 1.5707963267948966]` | `[-3.23, 3.23]` |
| 4 | `left_ankle` | `[-1.5707963267948957, 1.5707963267948974]` | `[-3.23, 3.23]` |
| 5 | `neck_pitch` | `[-0.34906585039884375, 1.1344640137963364]` | `[-3.23, 3.23]` |
| 6 | `head_pitch` | `[-0.7853981633974483, 0.7853981633974483]` | `[-3.23, 3.23]` |
| 7 | `head_yaw` | `[-2.792526803190927, 2.792526803190927]` | `[-3.23, 3.23]` |
| 8 | `head_roll` | `[-0.523598775598218, 0.5235987755983796]` | `[-3.23, 3.23]` |
| 9 | `right_hip_yaw` | `[-0.523598775598297, 0.5235987755983006]` | `[-3.23, 3.23]` |
| 10 | `right_hip_roll` | `[-0.4363323129985797, 0.43633231299858505]` | `[-3.23, 3.23]` |
| 11 | `right_hip_pitch` | `[-0.5235987755982987, 1.2217304763960306]` | `[-3.23, 3.23]` |
| 12 | `right_knee` | `[-1.5707963267948966, 1.5707963267948966]` | `[-3.23, 3.23]` |
| 13 | `right_ankle` | `[-1.5707963267948957, 1.5707963267948974]` | `[-3.23, 3.23]` |

## Sensors

| id | name | dim | adr | type |
|---:|---|---:|---:|---:|
| 0 | `gyro` | 3 | 0 | 3 |
| 1 | `local_linvel` | 3 | 3 | 2 |
| 2 | `accelerometer` | 3 | 6 | 1 |
| 3 | `upvector` | 3 | 9 | 30 |
| 4 | `forwardvector` | 3 | 12 | 28 |
| 5 | `global_linvel` | 3 | 15 | 31 |
| 6 | `global_angvel` | 3 | 18 | 32 |
| 7 | `position` | 3 | 21 | 26 |
| 8 | `orientation` | 4 | 24 | 27 |
| 9 | `right_foot_global_linvel` | 3 | 28 | 31 |
| 10 | `left_foot_global_linvel` | 3 | 31 | 31 |
| 11 | `left_foot_upvector` | 3 | 34 | 28 |
| 12 | `right_foot_upvector` | 3 | 37 | 28 |
| 13 | `left_foot_pos` | 3 | 40 | 26 |
| 14 | `right_foot_pos` | 3 | 43 | 26 |

## ROCm Debugging Interpretation

- The model compiles and can be reset in compatible local envs, while the
  local 7900 XTX hold appears at `mjx_env.step(...)`.
- The audit highlights the candidate feature area for future minimization:
  mesh foot collision against the floor plane plus reset-time collision
  checks.
- CPU and CUDA remain valid correctness paths; this audit is only for the
  local ROCm backend-debug workstream.
