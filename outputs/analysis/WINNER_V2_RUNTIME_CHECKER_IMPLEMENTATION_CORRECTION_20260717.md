# Winner v2 Runtime Checker Implementation Correction

Status: `INVALID_INITIAL_INVOCATION_CORPUS_ROUTING_FIXED_BEFORE_VALID_RERUN`

The first invocation of `tools/check_winner_v2_runtime_contract.py` returned
`HOLD_WINNER_V2_RUNTIME_INTEGRATION` for two corpus checks. That invocation is
invalid as a formal runtime result because the checker routed the
full-observation check to
`ground_up_torso_com_eager_mjx_accelerometer_replay/traces`: an unrelated
36-trace, 21,600-row accelerometer implementation audit containing only
commands 0.074, 0.077 and 0.080.

The frozen 40,520-row corpus named by the preregistration and prior artifact
record is instead enumerated, with per-file paths and SHA-256 hashes, by
`ground_up_torso_com_full_obs_replay_manifest.json`. It contains 144 traces and
includes the required x=0 rows. The initial invocation itself measured exact
projected-reference reproduction (`0.0` maximum error) and prior-applied-target
timing error of `5.960322746467739e-8` rad on the wrongly routed subset.

The correction changes only corpus discovery: read all 144 paths from the
frozen manifest and verify every file hash before checking its rows. It does
not change the runtime implementation, ABI, data values, tolerance, expected
40,520-row count, zero-command requirement, pass rule, or authority boundary.
This correction and the checker are committed before the valid rerun.
