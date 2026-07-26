# T5 actuator-protection gate reanalysis preregistration

- Status: `PREREGISTERED_T5_ACTUATOR_PROTECTION_REANALYSIS`
- Contract SHA-256: `d42f76b40260a12eb2fc04a6dcde1b55a52a23fc3c199c15f847956958c8b381`
- Decision population: complete V121, V123, and V128 matrices.
- Frozen reopen trigger: all three pass after replacing only the instantaneous stall gates with the documented 2-second protection rules.
- Protection proxies: `>2 A` for `100` ticks and `>80%` stall torque for `100` ticks, evaluated per joint.
- Manufacturer evidence: the official [STS3215 A/0 detailed specification](https://www.feetechrc.com/Data/feetechrc/upload/file/20200611/6372749961523760249976542.pdf) and [2023 selection guide](https://www.feetechrc.com/Data/feetechrc/upload/file/20230218/%E4%BA%A7%E5%93%81%E6%89%8B%E5%86%8C20230217.pdf).
- V157/V162 partial cells, V174, and post-handoff V177 are reported without changing the trigger.
- No simulation, training, policy selection, robot access, or Gate 5 action is authorized.
