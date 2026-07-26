# T8 state-coherent handoff failure analysis

- Status: `T8_FAILURE_LOCALIZED_X0_PREFIX_TRANSITION`
- Analysis SHA-256: `fb6e6f3b1a5f4217e346188967da70348625fecb00307a0d68d1ba87a86571c7`
- Moving cells: `12/12 green`
- x=0 cells: `0/4 green`
- Training: `0 steps`

All four x=0 cells complete 600 ticks, remain stationary and upright, clear tracking and servo-duration protection, preserve the response/recurrent/applied-target handoff, and command exact-zero policy action on every scored tick. Their only failed quantity is one rate event at tick 0: the previous action is the universal support vector, while the x=0 deadband output is exact zero.

The same six pitch joints exceed their measured envelopes in all four cells; the worst excess is `3.989999294281006 rad/s`. From tick 1 through tick 599, excess is exactly zero. Physical x=0 traces are checkpoint-independent within each actuator fit.

The next earned falsifier is therefore a command-aware startup branch: while paused/x=0, remain at home and bypass response excitation; for moving commands, retain the already-green direct T8 handoff. It needs four new x=0 CPU cells and reuses the twelve immutable audited moving cells. It earns no training by itself.
