# Winner-v55b native reset-quantization result

- Status: `PASS_WINNER_V55B_NATIVE_RESET_QUANTIZATION_ATTRIBUTION`
- Classification: `NATIVE_RESET_LABELS_REMAIN_SEPARABLE`
- Decision: `AUTHORIZE_FIRST_TICK_TEACHER_MAPPING_CPU_CONTRACT_PREREGISTRATION_ONLY`
- Result SHA-256:
  `303fee53c378a11e54e7bd99edebb78f88747f0ca05d6f56c84570a72ad78e99`.
- Raw / quantized inputs: `15 / 15`
- Teacher labels / quantized graph actions: `4 / 15`
- Conflict groups: `0`
- Simulator steps / optimizer / robot: `0 / 0 / 0`

All 30 raw observation hashes reproduce Winner-v55 exactly. Native BNO055 and
servo quantization changes 16 observation fields per row, with a maximum
absolute change of `0.004612922668457031`, but preserves all 15
configuration-specific reset inputs and all 15 graph actions. No exact
quantized input maps to more than one of the four bounded teacher labels.

Together, Winner-v55 and Winner-v55b establish that deployable reset
information exists and survives the frozen physical-resolution model. The
causal failure is therefore not an impossible reset label or missing
long-range information transport. Winner-v55's handoff result shows that the
mapping is time-critical: one wrong graph action causes eight failures even
when the sufficient teacher controls every later tick.

The evidence selects only a prospective first-tick teacher-mapping CPU
contract over training configurations, with held-out labels still forbidden.
It does not yet select an objective scale, run an update, choose a checkpoint,
or grant deployment or robot clearance.
