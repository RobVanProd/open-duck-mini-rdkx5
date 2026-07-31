# Direct Torso-COM Reaction Measurement Packet

Status: `READY_FOR_POWERED_OFF_OPERATOR_MEASUREMENTS`

Robot clearance: `NO`

This packet is the short operator path for obtaining the remaining policy-side
COM evidence. It uses no software, serial link, RDK-X5 execution, torque, or
motor command. Do not perform it while the battery is electrically connected.

## Equipment

- two tared scales or load cells that can simultaneously carry the torso;
- two narrow transverse support rails/knife edges;
- a ruler or caliper for support X positions;
- an independent scale reading for the complete same specimen; and
- a camera for the evidence records.

## Specimen boundary

Measure the complete torso-fixed deployment assembly with the RDK-X5, exact
battery arrangement, heatsink/fan/mounts, torso wiring, covers, fasteners,
bus/IMU/power hardware and ballast installed. Disconnect electrical power.

Exclude the articulated children at the modeled boundaries:

- left leg at `left_hip_yaw`;
- right leg at `right_hip_yaw`; and
- head/neck child at `neck_pitch`.

The torso-side servo portions remain with the torso. If the measured boundary
is uncertain, stop and record it as incomplete; do not guess. No stand, cable,
hand, head or leg may carry load during a reading.

## Coordinate and readings

Use the midpoint of the two hip-yaw rotation axes as X = `0` for the physical
measurements. Physical +X is the robot's forward/toe direction at home. The
calculator maps that datum to simulator `trunk_assembly` X = `-0.019 m`.

1. Photograph the complete deployment configuration and the isolated specimen.
2. Locate both support rails relative to the hip-axis datum. Call the rearward
   coordinate `x_a` and forward coordinate `x_b`; their complete uncertainty
   intervals must be separated by at least `0.060 m`.
3. Record conservative position uncertainties and each scale's calibrated
   load uncertainty.
4. Tare the supports, place the torso, and record reaction A and B.
5. Remove and replace the torso, repeating until exactly three formal trials
   are recorded.
6. Independently weigh the same complete specimen and record its uncertainty.

Use metres and kilograms in the JSON; evidence notes may retain raw millimetres
and grams. Populate
`outputs/analysis/real_build_torso_com_direct_reaction_template.json`. The 15
numeric entries are one datum uncertainty, four support values/uncertainties,
two scale uncertainties, two total-mass values/uncertainties, and six reaction
readings. Complete the four specimen predicates and cite immutable evidence for
the configuration, isolation, inventory, datum, supports, calibration, total
mass and each trial.

## Evaluation

After the measurements are committed, run:

```bash
python3 tools/evaluate_real_build_torso_com_direct_reaction.py \
  --input outputs/analysis/real_build_torso_com_direct_reaction_template.json \
  --output outputs/analysis/real_build_torso_com_direct_reaction_result.json
```

The calculator rejects a wrong specimen boundary, inconsistent total mass,
support span below 60 mm, nonpositive reaction interval, or nonoverlapping
trial COM intervals. It reports the conservative union of all trial intervals
and applies the unchanged asymmetric policy allowance. A pass closes only the
COM measurement blocker; it does not authorize Gate 5, deployment or motion.
