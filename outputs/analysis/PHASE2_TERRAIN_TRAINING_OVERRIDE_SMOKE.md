# Phase 2 Terrain Training Override Smoke

status: `PASS_TERRAIN_TRAINING_OVERRIDE_SMOKE`

## Summary

`tools/run_actuator_bridge_training_smoke.py` now supports a training-only
terrain hfield z-scale override:

```text
--terrain-hfield-z-scale <float>
```

The wrapper backs up the selected task XML, patches the `<hfield size="...">`
z-scale for the training subprocess, and restores the original XML in
`finally`.

## Smoke Command

```text
../envs/open-duck-playground/bin/python tools/run_actuator_bridge_training_smoke.py \
  --task rough_terrain_backlash \
  --terrain-hfield-z-scale 0.002 \
  --num-timesteps 256 \
  --output-root outputs/analysis/terrain_training_override_smoke \
  --platform cpu \
  --timeout-s 900 \
  --run
```

## Result

```text
status: PASS_SMOKE_RUN
returncode: 0
elapsed_s: 134.0419
checkpoint steps: 0, 320
```

## Restore Proof

```text
destination:
  /home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_rough_terrain_backlash.xml

destination_sha256_before:
  879768817f5ae5d2c01b5494f855686bb10d1ec444a404efeced8f5766574ffc

destination_sha256_after_patch:
  cfdefc46f41e0b7d1160ab6ebb6433b95248af3a7fb442e833b6bc64e82d3290

destination_sha256_restored:
  879768817f5ae5d2c01b5494f855686bb10d1ec444a404efeced8f5766574ffc
```

Post-run file check:

```text
<hfield name="hfield" file="assets/hfield.png" size="10 10 .01 0.1"/>
```

No robot motion, SSH, deployment, grounded replay, or runtime behavior change
was performed.
