# Real-Build Torso-COM Input Re-audit

Status: `HOLD_REAL_BUILD_COM_INPUTS_INCOMPLETE`

Decision: `MEASURE_BUILD_SPECIFIC_MASS_AND_X_PLACEMENT`

The 2026-07-16 input audit was repeated after the winner-v2 observer cross-fit
closed. Repository filenames were checked for STEP/IGES/FreeCAD/SolidWorks/3MF
assembly sources, and repository text was searched for build-specific RDK-X5
or battery mass, X-location, datum, center-of-mass and uncertainty evidence.

No new as-built evidence was found. The workspace still has stock Open Duck
Mini geometry and the compiled simulator torso values, but it has no
RDK-X5-specific torso assembly CAD, complete installed-component mass ledger,
common trunk datum, installed component X locations, or uncertainty bounds.
Stock geometry, nominal product specifications, and inference are not valid
substitutes for the missing measurements.

Therefore no numerical real-build COM estimate or comparison with the
certified asymmetric break-radius interval is made. The committed measurement
template remains the next evidence input. The observer cross-fit pass removes
the separate fit-selection measurement from the current offline blocker list;
it does not change this COM hold or authorize Gate 5, deployment, RDK-X5, or
robot use.

