# Upstream Sim / Morphology Audit

status: `PASS_MORPHOLOGY_MATCHES_UPSTREAM_CODE_DRIFT_ONLY`

This is an offline audit. It does not train, deploy, SSH, or touch the robot.

## Git State

- playground_path: `/home/lsd/robots/Open_Duck_Playground`
- branch: `codex/forward-progress-reward`
- head: `16a804a43cbe0881cf424376e6ab4f2f024492d0`
- upstream_ref: `origin/main`
- upstream_commit: `b9be205ac64488c23504ca42e5ec790337adeec3`
- morphology_mismatch_count: `0`
- code_mismatch_count: `2`

## Drift From Upstream

- `M	playground/open_duck_mini_v2/joystick.py`
- `M	playground/open_duck_mini_v2/runner.py`

## Key File Hashes

| category | path | matches_upstream |
|---|---|---:|
| morphology_or_reference | `playground/open_duck_mini_v2/data/polynomial_coefficients.pkl` | `True` |
| morphology_or_reference | `playground/open_duck_mini_v2/xmls/joints_properties.xml` | `True` |
| morphology_or_reference | `playground/open_duck_mini_v2/xmls/open_duck_mini_v2.xml` | `True` |
| morphology_or_reference | `playground/open_duck_mini_v2/xmls/open_duck_mini_v2_backlash.xml` | `True` |
| morphology_or_reference | `playground/open_duck_mini_v2/xmls/scene_flat_terrain.xml` | `True` |
| morphology_or_reference | `playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml` | `True` |
| morphology_or_reference | `playground/open_duck_mini_v2/xmls/scene_rough_terrain_backlash.xml` | `True` |
| morphology_or_reference | `playground/open_duck_mini_v2/xmls/sensors.xml` | `True` |
| code | `playground/open_duck_mini_v2/base.py` | `True` |
| code | `playground/open_duck_mini_v2/constants.py` | `True` |
| code | `playground/open_duck_mini_v2/joystick.py` | `False` |
| code | `playground/open_duck_mini_v2/runner.py` | `False` |

## Physics Summary

### open_duck_mini_v2.xml

```json
{
  "options": [
    {
      "iterations": "1",
      "ls_iterations": "5"
    }
  ],
  "defaults": [
    {
      "class": null
    },
    {
      "class": "open_duck_mini_v2",
      "joint": {
        "frictionloss": "0.1",
        "armature": "0.005"
      },
      "position": {
        "kp": "50",
        "dampratio": "1"
      }
    },
    {
      "class": "visual",
      "geom": {
        "type": "mesh",
        "contype": "0",
        "conaffinity": "0",
        "group": "2"
      }
    },
    {
      "class": "collision",
      "geom": {
        "group": "3"
      }
    },
    {
      "class": null
    },
    {
      "class": "sts3215",
      "joint": {
        "damping": "0.56",
        "frictionloss": "0.068",
        "armature": "0.027"
      },
      "position": {
        "kp": "13.37",
        "kv": "0.0",
        "forcerange": "-3.23 3.23"
      },
      "geom": {
        "contype": "0",
        "conaffinity": "0"
      }
    },
    {
      "class": "backlash",
      "joint": {
        "damping": "0.01",
        "frictionloss": "0",
        "armature": "0.01",
        "limited": "true",
        "range": "-0.008726646259971648 0.008726646259971648"
      }
    }
  ],
  "actuator_count": 16,
  "actuator_names": [
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle"
  ],
  "floor_geoms": []
}
```

### scene_flat_terrain.xml

```json
{
  "options": [],
  "defaults": [],
  "actuator_count": 0,
  "actuator_names": [],
  "floor_geoms": [
    {
      "name": "floor",
      "size": "0 0 0.01",
      "type": "plane",
      "material": "groundplane",
      "contype": "1",
      "conaffinity": "0",
      "priority": "1",
      "friction": "0.6",
      "condim": "3"
    }
  ]
}
```

## Interpretation

- The local morphology XML and polynomial reference file match upstream byte-for-byte.
- The local branch drift is in training/eval code, primarily `joystick.py` and `runner.py`.
- The upstream-reference push-effectiveness failure therefore is not explained by local XML/reference-file drift.
- Next audit target: runtime environment/config behavior inside `joystick.py`, termination/reward overrides, and whether the known upstream walking demo used a different checkpoint/export path or older commit.
