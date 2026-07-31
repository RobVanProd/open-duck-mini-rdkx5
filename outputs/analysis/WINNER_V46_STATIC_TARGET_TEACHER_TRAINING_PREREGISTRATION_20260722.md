# Winner-v46 static-target teacher training preregistration

- Status: `PREREGISTERED_WINNER_V46_STATIC_TARGET_TEACHER_TRAINING`
- Decision: `AUTHORIZE_ONE_100_UPDATE_STATIC_TARGET_TEACHER_ARM_ONLY`
- Source / half / final optimizer count: `252 / 302 / 352`
- Continuation: `100 updates`, `80 x 250` scheduled ticks per update
- Predictor / prefix / teacher scales: `380.9135437011719 / 197.3112030029297 / 58.436370849609375`
- Formal support / robot: `0 / 0`

Winner-v42 proved a shared two-plant static support target for every failure configuration; V43/V44 isolated a training-only six-pitch gradient and its sole scale; V45 proved one exact update reduces same-batch teacher error while preserving the deployable graph. One inherited-length continuation now tests persistence.

No checkpoint is selected from training metrics. A passing artifact authorizes
only a separately frozen half/final support and context gate.
