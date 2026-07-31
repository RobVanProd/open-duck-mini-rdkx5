# Ground-Up Robustness R2 Reporting Contract

status: `PASS_ROBUSTNESS_R2_REPORTING_CONTRACT`

The first condition-1 outputs were not aggregated: they included the requested
override but the campaign wrapper discarded the simulator's per-run model
readback, violating the preregistered evidence contract.

The correction is serialization-only. Each run now copies
`insertion_point.dynamics_override` into its result. A CPU smoke records floor
friction `1.0 -> 0.5`, key `floor_friction`, value `.5`, and changed index
`[0,0]` exactly.

The unaggregated first outputs are invalidated and must be overwritten by an
identical 16-cell rerun. No behavior parameter changed and no condition-2 or
later work is authorized.
