# Winner-v15 pitch-margin objective attribution

- Status: `PASS_WINNER_V15_PITCH_MARGIN_OBJECTIVE_ATTRIBUTION`
- Decision: `PREREGISTER_ONE_SIDED_NEGATIVE_PITCH_MARGIN_CPU_CONTRACT`
- Persistent failures: `COM_CORNER_01, COM_CORNER_03, COM_X_NEG, DISCOVERY_03, HELDOUT_09`
- Failure ticks / pitch: `28-71` / `-0.383697--0.350161 rad`
- Training / locomotion / robot access: `0 / 0 / 0`

All five fixed action scales fail. Every nonzero scale retains distinct
response context, corrected prediction, exact repeats, and graph bounds.
The common failure is early negative pitch, including four configurations
already in the training population. This selects one bounded training-only
reward change: replace the flat valid-transition reward with normalized
one-sided negative-pitch margin. No coefficient search is authorized.
