# T182 worker-command contract recovery

- Status: `INVALID_T182_WORKER_COMMAND_CONTRACT_NO_BEHAVIOR`
- Traces / manifests / behavior cells: `0/0/0`
- Policy outcome measured: `false`
- Next authority: corrected single-command worker preregistration only

The inherited T27 formal worker accepts the complete four-command tuple. T182
correctly preregistered only x=`.077`, so the worker rejected the invocation
before starting simulation.

T182B may introduce only a thin formal worker whose allowed command tuple is
`(.077,)`. Policy, fit, positive-Z override, seed, duration, calibration,
handoff, observation/action contracts, classification, and protection gates
must remain unchanged.
