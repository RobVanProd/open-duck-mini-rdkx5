# Physical Pose Reference Renders

source_xml: `/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_flat_terrain.xml`

These images are generated from the repo MJCF, not from a photo or video.

## Poses

- `zero`: all 14 actuator joints at `0.0 rad`; this is the reference used by `find_soft_offsets.py`.
- `home`: runtime `HWI.init_pos`; this matches the sim `scene_flat_terrain.xml` `home` keyframe.

## Joint Order

| index | joint | zero rad | home rad | home deg |
|---:|---|---:|---:|---:|
| 0 | `left_hip_yaw` | 0.000 | 0.002 | 0.1 |
| 1 | `left_hip_roll` | 0.000 | 0.053 | 3.0 |
| 2 | `left_hip_pitch` | 0.000 | -0.630 | -36.1 |
| 3 | `left_knee` | 0.000 | 1.368 | 78.4 |
| 4 | `left_ankle` | 0.000 | -0.784 | -44.9 |
| 5 | `neck_pitch` | 0.000 | 0.000 | 0.0 |
| 6 | `head_pitch` | 0.000 | 0.000 | 0.0 |
| 7 | `head_yaw` | 0.000 | 0.000 | 0.0 |
| 8 | `head_roll` | 0.000 | 0.000 | 0.0 |
| 9 | `right_hip_yaw` | 0.000 | -0.003 | -0.2 |
| 10 | `right_hip_roll` | 0.000 | -0.065 | -3.7 |
| 11 | `right_hip_pitch` | 0.000 | 0.635 | 36.4 |
| 12 | `right_knee` | 0.000 | 1.379 | 79.0 |
| 13 | `right_ankle` | 0.000 | -0.796 | -45.6 |

## Images

| pose | contact sheet |
|---|---|
| zero | `zero_contact_sheet.png` |
| home | `home_contact_sheet.png` |

Use these references to decide whether the robot's current home pose and
the operator-selected zero pose match the repo coordinate system before
editing `duck_config.json` offsets.
