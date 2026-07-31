# V126 all-tick contract recovery amendment

Status: `PREREGISTERED_WINNER_V126_ALL_TICK_CONTRACT_RECOVERY`

The first runner lost the simulator HOLD by reading a missing trace before serializing a result. One unchanged-input recovery execution is frozen; it must persist the simulator status before trace parsing.
