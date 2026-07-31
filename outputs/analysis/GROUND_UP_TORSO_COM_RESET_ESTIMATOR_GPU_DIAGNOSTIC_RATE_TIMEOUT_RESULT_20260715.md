# Ground-Up Torso-COM Reset-Estimator GPU Diagnostic Rate Timeout — 2026-07-15

Decision: `STOP_NO_RETRY_DIAGNOSTIC_RATE_ATTESTATION_TIMEOUT`.

The approved short diagnostic allocated the exact named idle T4 and waited the
frozen 60 seconds. The Resources UI still reported the idle value 0/hour, so no
positive attestation was written. The launcher timed out before every upload
and diagnostic command, stopped the named session successfully after
74.175680 seconds, and independent inventory confirmed no active sessions.

This is a rate-acquisition failure, not an expansion result. Compute-unit
consumption is unknown. The raw plan SHA-256 is
`3e69d25005dd9f801254e90105ab07cf527b441f738a746f3aa35a47949e1330`;
the raw launch-record SHA-256 is
`e8653d96a87c7ae45d74711102aee69a65d968f78b193ec974c159533dfd48d0`.

The operator explicitly withdrew the requirement to provide further billing
numbers and authorized completing the goal without them. This does not permit
inventing usage; a successor must report compute units as unmeasured.
