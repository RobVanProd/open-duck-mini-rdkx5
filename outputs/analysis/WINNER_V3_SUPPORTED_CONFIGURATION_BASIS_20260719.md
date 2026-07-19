# Winner-v3 Supported-Configuration Domain Basis — 2026-07-19

Decision: `PASS_VARIABLE_CONFIGURATION_DOMAIN_BASIS_CURRENT_CANDIDATE_HELD`

The supported domain is derived from the already-frozen R2 dynamics endpoints
and the compiled `trunk_assembly` readback, not from a per-unit measurement or
an invented component ledger. Torso COM spans `±0.05 m` independently in X, Y
and Z. All-link mass scale remains `0.9–1.1`; torso added mass remains
`±0.1 kg`, producing a torso-mass range of
`0.528673400–0.868378600 kg`.

The compiled torso has mass `0.698526000 kg`, inertial position
`[-0.0483259, -9.97823e-05, 0.0384971]`, principal inertia `[0.0034448951258009347, 0.0029271882823563265, 0.001676066591842733] kg·m²`,
and geometry AABB `[-0.15400003603578855, -0.055000357109437646, -0.03510910453222782]–[0.04603293675628423, 0.05500015009962982, 0.10789103308747082] m`. Every frozen
COM corner stays inside that geometry. Inertia variation is coupled to the
frozen mass/placement ranges using the parallel-axis bound; only positive-
definite, triangle-valid inertia tensors may be sampled.

Optional non-locomotion combinations are represented by their aggregate
dynamics. No manual inventory, mass, COM or inertia entry is required. A build
is supportable only when both its aggregate configuration and later automatic
response profile remain inside the frozen envelopes.

The current `99d3afce…304de` graph cannot supply the runtime envelope: its
verified X-COM bracket fails well inside the required `±0.05 m` domain. It
remains held and no `supported_configuration_envelope.v1` is emitted. The 73
automatic-response bounds remain pending a passing replacement and may not be
widened from physical outcomes.

This result authorizes only prospective replacement-study preregistration. It
does not authorize training, hosted compute, GPU/iGPU, RDK-X5, robot, automatic
calibration, X5 preflight, Gate 5, deployment or robot clearance.
