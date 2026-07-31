# T180 input-mapping recovery

- Status: `INVALID_T180_INPUT_MAPPING_NO_RESULT`
- Result artifacts created: `0`
- Replay rows completed: `0`
- New behavior / optimizer / robot: `0/0/0`
- Next authority: corrected T180B preregistration only

The T180 builder selected T177 comparator blocks by checkpoint and actuator
fit but omitted the condition ID. Positive-Z cases therefore pointed at
condition-1 floor-friction traces. The frozen calibration-context SHA check
rejected the first mismatched row before ONNX attribution.

T180B must bind every block by condition, checkpoint, and fit. All six cases,
162-tick prefixes, thresholds, analysis equations, and decision rules remain
unchanged.
