# C3 Legacy Runtime Golden Vector

Status: `PASS_LEGACY_RUNTIME_GOLDEN_VECTOR`

The June 21 first-evidence file
`outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_thresholds.jsonl`
contains 747 contiguous ticks and has SHA-256
`4b668482058e5d43a46aa35dc84c84ea0615b05fe698766f3d03ddd10e094206`.
Its action filter is off (`cutoff_frequency_hz=null`), it records the 14-D
pre-head-overlay `motor_targets_post_rate_limit_rad`, and its tick sequence
proves telemetry-every-n=1.

The extractor selected adjacent ticks 0 and 1. Verification passes:

- the current 101-D observation is present;
- current obs[83:97] equals the prior sent target exactly;
- current obs[99:101] equals the prior row's recorded advanced phase exactly;
- the pre-head-overlay target is present; and
- the action filter is off.

Golden vector SHA-256:
`0ac018d25a8c3ccb7959670830acce510a98bfda5d614a7aa5be4c242ea0d2d6`.
Verification SHA-256:
`108dcfe7ef3bac46e0b7987199a3ec36d67f2f0f1024328dc57da9eb26927b3a`.

This closes C3 without a new hardware capture. It validates the legacy
sent-target/obs-then-advance runtime contract only; it does not repair the C1
applied-target mismatch or authorize robot use.

