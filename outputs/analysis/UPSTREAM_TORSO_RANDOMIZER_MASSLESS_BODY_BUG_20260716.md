# Upstream Finding: Torso Randomizer Targets a Massless Body

Status: `ISSUE_READY_REPRODUCED`

## Summary

In Open Duck Playground commit `24b82508aa5fc95cd17b14def9edcf6cc627b588`,
`playground/common/randomize.py` defines `TORSO_BODY_ID = 1`. In the compiled
Open Duck Mini V2 model, body 1 is `base` with mass 0 kg; the inertial torso is
body 2 `trunk_assembly`, mass 0.698526 kg.

Both affected operations use the wrong constant:

- COM jitter writes `body_ipos[TORSO_BODY_ID]`;
- torso-mass delta writes `body_mass[TORSO_BODY_ID]`.

Consequently the advertised torso uncertainty does not perturb the massive
torso dynamics for this model. In the R2 reproduction, all 16 traces from the
wrong body-1 X-COM mutation were byte-identical to the default comparator.

## Minimal reproduction

1. Compile the Open Duck Mini V2 MJCF.
2. Print `body(1).name`, `body_mass[1]`, `body(2).name`, and `body_mass[2]`.
3. Apply the current COM/mass randomizer with nonzero values.
4. Read back the changed body index and compare a deterministic rollout with
   default dynamics.

Observed: body 1 is `base`/0 kg, body 2 is `trunk_assembly`/0.698526 kg, and the
wrong-body COM rollout is identical to default.

## Proposed fix

Resolve `trunk_assembly` by name from the compiled model during setup; reject a
missing or massless target; pass the resolved ID into the randomizer. Do not
freeze a cross-model numeric body ID.

Add tests that assert:

- resolved name, ID and positive mass;
- nonzero COM jitter changes only the intended `body_ipos[torso_id]` axes;
- torso-mass delta changes the resolved massive body;
- default-off model arrays are exact; and
- a paired deterministic transition changes under a nonzero torso perturbation.

The local corrected contract passes these checks with body 2. This artifact is
an issue report, not an upstream write or policy claim.

