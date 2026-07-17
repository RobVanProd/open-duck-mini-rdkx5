# Real-Build Torso-COM Measurement Packet

Status: `READY_FOR_BUILD_SPECIFIC_INPUTS`

This packet collects the only evidence still needed for the frozen real-build
COM comparison. It does not require powering the robot, running motors, using
the RDK-X5, or changing software.

## Coordinate record

Choose one physically reproducible torso-fixed datum and document it with a
photo, drawing, or build CAD. Record:

1. the datum's X coordinate in the simulator `trunk_assembly` frame;
2. the uncertainty of that datum mapping;
3. whether increasing physical ruler X maps to simulator `+X` (`+1`) or `-X`
   (`-1`); and
4. the evidence path supporting the mapping.

The model defines `trunk_assembly` at identity relative to `base`. It also
contains a `trunk` site at X = -0.024 m, but that site may be used as a
physical datum only if the selected build drawing or CAD locates the same
frame on the real torso. Do not infer a physical landmark from the XML alone.

## Component record

Populate every row in
`outputs/analysis/real_build_torso_com_measurement_template.json`.
For each installed group, record:

- measured installed mass and scale uncertainty;
- X coordinate of that group's own center of mass relative to the chosen
  datum and placement uncertainty; and
- an evidence path or measurement-note identifier.

The inventory must cover the printed torso/fasteners, RDK-X5 board,
thermal/mount stack, cables/adapters, actual battery pack, BMS/charger/wiring,
servo-bus/IMU/power hardware, and covers or ballast. If the last optional
group is absent, record zero mass and zero uncertainty plus evidence that it is
not installed; do not leave the row null.

Measure assemblies together when their internal mass distribution cannot be
reliably separated, but do not count a part in more than one row. A group COM
can be obtained from build CAD with assigned material masses or a documented
balance/fixture measurement. Nominal web weights cannot replace an as-built
measurement.

## Evidence quality

- Use kilograms and metres in the JSON, retaining the raw gram/mm record in
  the cited evidence.
- Mass uncertainty must include scale resolution/repeatability.
- X uncertainty must include landmark location, group-COM determination and
  placement repeatability.
- Datum uncertainty is common to the assembly and is entered once in
  `datum_origin_x_uncertainty_m`; do not duplicate it in every component.
- Keep photos, drawings, scale readings and calculations under an immutable
  repository evidence directory and cite each from `source` or
  `transform_evidence`.

## Deterministic evaluation

After the template contains measured values, run:

```bash
python3 tools/evaluate_real_build_torso_com.py \
  --input outputs/analysis/real_build_torso_com_measurement_template.json \
  --output outputs/analysis/real_build_torso_com_result.json
```

The calculator evaluates the exact mass/position uncertainty-box extrema and
the common datum uncertainty. It compares the full sim-to-real interval with
the frozen admissible interval:

- lower error must be at least -0.021875 m; and
- upper error must be at most +0.0046875 m.

Those limits are the certified asymmetric inner bounds after reserving the
frozen 0.00078125 m curve-resolution margin. Missing or invalid data produces
`HOLD_REAL_BUILD_COM_INPUTS_INCOMPLETE` and no numerical estimate. A measured
outside interval produces `HOLD_REAL_BUILD_COM_OUTSIDE_CERTIFIED_RADIUS`.
Neither result authorizes model correction, Gate 5, deployment, or robot use.

