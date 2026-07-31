# Winner-v98 response-conditioned training preregistration

- Source actor: exact selected T2 512K graph `99d3afce...304de`
- Calibration: 250 response ticks + 250 home-return ticks, outside PPO
- Trainable policy family: recurrent response adapter only
- Protected: actor weights and source observation normalization
- CPU smoke: one 1,024-step run; full hosted curriculum is not yet authorized
- Flat transport: disabled
- Robot / RDK / motion access: `0 / 0 / 0`
