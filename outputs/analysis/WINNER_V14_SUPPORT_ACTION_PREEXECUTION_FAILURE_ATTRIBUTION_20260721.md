# Winner-v14 support-action pre-execution failure attribution

- Status: `INVALID_WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC_PREEXECUTION`
- Decision: `CORRECT_ONLY_FORMAL_RESULT_HASH_MODE_AND_FRESHLY_PREREGISTER`
- GitHub run / attempt: `29833400247 / 1`
- Optimizer / main / repeat / locomotion / robot: `0 / 0 / 0 / 0 / 0`

The runner stopped at the formal-result hash check before constructing
an episode or executing a diagnostic cell. Git checkout normalized the
tracked JSON from CRLF to LF, while the runner compared the Windows raw
hash. The only permitted correction is an LF-normalized hash comparison
followed by a fresh preregistration and new run.
