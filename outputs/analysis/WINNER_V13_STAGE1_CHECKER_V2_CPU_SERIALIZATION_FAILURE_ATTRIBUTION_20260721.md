# Winner-v13 Stage-1 checker-v2 serialization-failure attribution

- Status: `INVALID_ZERO_RESULT_SERIALIZATION_FAILURE`
- Decision: `CORRECT_SERIALIZATION_AND_LAUNCH_FRESH_ZERO_CELL_CONTRACT`
- GitHub run / attempt: `29822072300 / 1`
- Artifact ID / ZIP SHA-256: `8491779699` / `ac0b1bb863f65eee0c37b75528317f59009c8334c7f2663e5650350615b9a8a4`
- Result present: `false`
- Optimizer / simulation / locomotion / robot access: `0 / 0 / 0 / 0`

All checker calculations ran, but strict result serialization rejected NumPy
boolean scalars. The artifact therefore contains only the generated ONNX graph
and cannot support a scientific decision. A native-boolean correction and one
fresh zero-cell run are authorized; training remains forbidden.
