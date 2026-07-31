# T5 actuator-protection gate reanalysis

- Status: `PASS_T5_MIS_SPECIFIED_INSTANTANEOUS_CONSTRAINT`
- Decision: `REOPEN_V121_V175_CAMPAIGN_CLOSURES`
- Corrected full-matrix passes: `3/3` (`V121, V123, V128`)
- V10 moving force-limit hits: `1729`
- Float32 values between V10 clamp and old decimal gate: `0`

| Candidate | Original | Corrected | Current run | Overload run | Status |
| --- | ---: | ---: | ---: | ---: | --- |
| V121 | 11/16 | 16/16 | 10 | 11 | PASS |
| V123 | 4/16 | 16/16 | 10 | 11 | PASS |
| V128 | 10/16 | 16/16 | 8 | 11 | PASS |
| V157 | 0/1 | 1/1 | 9 | 9 | REOPEN_INCOMPLETE |
| V162 | 3/4 | 4/4 | 9 | 10 | REOPEN_INCOMPLETE |
| V174 | 6/6 | 6/6 | 10 | 10 | PASS |
| V177 | 8/16 | 16/16 | 10 | 11 | PASS |

The official [STS3215 A/0 specification](https://www.feetechrc.com/Data/feetechrc/upload/file/20200611/6372749961523760249976542.pdf) documents duration-triggered protection, not a one-tick trip at stall torque/current. This result reopens the affected offline closures but does not select a policy, authorize training, or open Gate 5.
