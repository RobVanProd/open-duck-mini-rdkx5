# Real-Build Torso-COM Measurement Schema Correction

Status: `PASS_INPUT_SCHEMA_MADE_NUMERIC_BEFORE_MEASUREMENT`

The frozen 2026-07-16 method requires every measured component coordinate to
be transformed from a documented build datum into the simulator
`trunk_assembly` X frame. The v1 JSON template contained only a free-text
`transform_to_trunk_assembly_body_frame` field. That field could document a
transform but could not execute or audit it numerically.

Before any build measurement was entered, the template was advanced to v2 by
replacing that ambiguous field with:

- `datum_origin_x_in_trunk_assembly_m`;
- `datum_origin_x_uncertainty_m`;
- `axis_sign_to_trunk_assembly_x`, restricted to `-1` or `+1`; and
- `transform_evidence`.

Component `x_m` and `x_uncertainty_m` remain coordinates relative to the
documented physical datum. The calculator maps their complete intervals into
the body frame, then adds the common datum-origin uncertainty once. This is an
input-schema correction only. It does not change the preregistered weighted-COM
formula, independent component boxes, simulator comparator, certified inner
bounds, 0.00078125 m margin, or decision tokens. No outcome data existed when
the correction was made.

