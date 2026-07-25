# Winner V166c module-invocation correction

- Status: `PASS_WINNER_V166C_MODULE_INVOCATION_CORRECTION`
- The V166b wrapper failed during import, before argument parsing, run-root creation, or simulation.
- Correction changes only invocation from a file path to Python's module form so the repository root is importable.
- Runner and wrapper hashes are unchanged.
- Policy, factor, interpolation, matrix, gates, and stop rule are unchanged.
- Authorizes one CPU-only rerun in a fresh root; no training or production change.
