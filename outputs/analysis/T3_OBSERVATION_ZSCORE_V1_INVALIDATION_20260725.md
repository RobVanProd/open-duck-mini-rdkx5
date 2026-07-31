# T3 observation z-score v1 invalidation

- Status: `INVALID_PROVENANCE_MOCK_TRACE_INCLUDED`
- The v1 preregistration incorrectly classified
  `duck-auto-config-2529a83096d04812b0d5491303b2e42a/trace.jsonl` as
  real-robot component evidence.
- Its adjacent `metadata.json` states `backend: mock`,
  `hardware_authorized: false`, and `informational_only: true`.
- The draft v1 result was deleted before commit and has no decision weight.
- A v2 preregistration must exclude this trace and verify the hardware backend
  of every remaining external capture before execution.
