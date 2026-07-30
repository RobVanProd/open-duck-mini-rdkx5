# T221 T220 command-route audit result

- Status: `HOLD_T221_T220_COMMAND_ROUTE_AUDIT`
- Result JSON was written with canonical SHA-256
  `ec3992c8d7f5d0dcfe6082a72556386eee5d478e66968df9f79f18924a494980`
  before the Markdown reporter raised on an empty selected-cell list.
- The runner compared JSON decimal `0.077` against the exact float32 endpoint
  with strict equality, so the nominal and targeted endpoint lists were empty.
- Its random-state sensitivity sample also produced saturated/rate-clipped
  outputs and did not exercise the command dependency seen in the frozen T220
  trajectories.
- The route attribution itself remained green: both Y-negative contexts select
  the nominal expert; the preserved T149 `.074` cap is present and inactive.
- Simulator / optimizer / behavior / hosted / robot: `0/0/0/0/0`.
- This hold does not authorize a transform or behavior. A preregistered
  read-only verifier recovery is required.
