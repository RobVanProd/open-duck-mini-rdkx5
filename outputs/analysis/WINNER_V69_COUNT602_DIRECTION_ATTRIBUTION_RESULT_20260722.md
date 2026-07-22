# Winner-v69 count-602 direction attribution result

- Status: `PASS_WINNER_V69_COUNT602_DIRECTION_ATTRIBUTION`
- Classification: `INHERITED_ADAM_MOMENT_DIRECTION_OPPOSES_TEACHER`
- Teacher loss before: `0.0031728835311`
- Teacher-gradient dot inherited-Adam delta: `+4.8861402e-8` (opposed direction)
- Original Adam fractions through `1/16`: all non-descending, reproduced exactly.
- A `1/1024` Adam fraction changes loss by only one float32 quantum (`-2.3283e-10`).
- Norm-matched negative-gradient full step changes loss by `-8.0769e-7` and all five tested fractions descend.
- Committed updates / snapshots / ONNX / support / robot: `0 / 0 / 0 / 0 / 0`
- Result SHA-256: `cd1c25f0adf89597297a8fa5a52cd1a03a9da5e4743ad92a32fbaa23caf85b75`
- Decision: preregister one fresh-moment teacher-step proof only.
