# T34 T32 nominal matrix result

status: `HOLD_T34_T32_NOMINAL_MATRIX`

- green cells: `15/16`
- worst tracking p95: `0.169115901 rad`
- worst strict >2 A run: `15 ticks`
- worst strict overload run: `15 ticks`

The only failed cell was the final checkpoint under `p31_34` at
`x=0.077 m/s`. It fell after 494/600 ticks despite passing the replacement
quality checks (`tracking p95 0.156651783 rad`, zero saturation, and zero
rate excess). The half checkpoint passed all eight cells; the final
checkpoint passed seven of eight.

The frozen both-checkpoint persistence rule closes the T32 action-margin
train-through formulation. It does not earn robustness-matrix
preregistration. Gate 5 and robot access remain closed.
