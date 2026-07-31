# T3 observation z-score preregistration

- Status: `PREREGISTERED_T3_OBSERVATION_ZSCORE_AUDIT`
- Contract SHA-256: `525dcf6629fa999843a786c6390628279ff58119fa0f4dd50868a3e2d7b3ca4a`
- Scope: offline analysis only; no policy, simulator, RDK, or robot mutation.
- Rule: flag a channel/source after 50 consecutive valid samples with `abs(z) > 0.5`.
- Coverage rule: missing real fields remain unavailable; they are never synthesized.
- Known hold: the raw corrected 747-tick replay is absent, so T2 is not executable from the current archive.
