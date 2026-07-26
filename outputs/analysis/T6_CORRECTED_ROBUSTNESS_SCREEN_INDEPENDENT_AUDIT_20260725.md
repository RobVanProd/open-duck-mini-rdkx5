# T6 corrected robustness screen — independent audit

- Status: `PASS_T6_INDEPENDENT_AUDIT`
- Audit SHA-256: `70a9b3ca045522ceda1df86f4712878e81aaba07d97283441f8a2ea82bb4d9c3`
- Result file SHA-256: `31317e52fe4dae94567b7ce633fd8542507973c7e7168a0887f7a5267970f932`
- Result canonical SHA-256: `0a1000dc370ab04b830ad6c06301e558f88983d4aa382786618be35f8f33252c`
- Evidence: `16` manifests, `16` evaluations, `64` traces, `64` cells, `64` exact override readbacks
- Survivors: `0`

| candidate | green cells | full pair | worst tracking | min vx | current run | overload run |
|---|---:|---|---:|---:|---:|---:|
| `V121` | 0/16 | `False` | 0.14862397313117984 | -0.3518881556681461 | 3 | 3 |
| `V123` | 0/16 | `False` | 0.15696418285369873 | -0.41399077645037324 | 4 | 5 |
| `V128` | 0/16 | `False` | 0.1524039030075073 | -0.3837141164214067 | 4 | 4 |
| `V177` | 1/16 | `False` | 0.14925726652145385 | -0.32158057741297963 | 5 | 5 |

This auditor does not import the T6 runner. It independently recomputes the preregistration and result canonical hashes, every manifest/evaluation/trace hash, exact COM mutation readback, trace duration-protection metrics, behavior classifications, candidate aggregates, and the final decision.

This CPU-only audit authorizes no hosted training, robot access, Gate 5, torque, or motion.
