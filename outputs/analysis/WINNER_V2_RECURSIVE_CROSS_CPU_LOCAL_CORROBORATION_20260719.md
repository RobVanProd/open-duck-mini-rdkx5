# Winner-v2 Recursive Cross-CPU Local Corroboration

Status: `PASS_LOCAL_CORROBORATION_NOT_FORMAL_RUNTIME_DECISION`

Frozen-rule decision on this CPU: `PASS_RECURSIVE_BIT_EXACT_WIRE_CLOSURE`.

This is an independent post-preregistration Linux CPU replay of the
committed runtime implementation. It is corroborating evidence, not
the requested formal result from the runtime agent's CPU.

## Selected 512000 result

- selected logical-target maximum: `0 rad`;
- selected P30 maximum: `5.9576471311828527e-08 rad`;
- selected raw goal mismatches: `0`;
- x=0 action/state/target/P30: bit-exact;
- same-input `1e-6` and native half-count gates: pass.

All four 600-tick cells were run. The 1024000 cells remain audit-only.
No robot, RDK-X5, hardware, GPU or iGPU access occurred. Runtime
acceptance, physical COM, Gate 5 and robot clearance remain pending.
