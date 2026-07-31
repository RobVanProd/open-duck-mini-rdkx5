# Real-Build Torso-COM Estimate Preregistration

Status: `PREREGISTERED_OFFLINE_MEASUREMENT_REQUIRED`

## Question

What is the X-axis torso COM of Rob's assembled Frank Fu Open Duck Mini with
the installed RDK-X5, heatsink/cabling and actual battery arrangement, expressed
in the simulator `trunk_assembly` body frame?

## Frozen method

Use only build-specific measured or CAD-backed inputs. For every torso-fixed
component record mass `m_i`, X coordinate `x_i` relative to the documented
trunk datum, and independent bounds `dm_i`, `dx_i`. The estimate is
`sum(m_i*x_i)/sum(m_i)`. Its interval is computed by evaluating the extrema of
the recorded mass/position boxes; no nominal web weight may replace a missing
measurement.

The simulator comparator is the compiled body-2 `trunk_assembly` inertial:
mass 0.6985260248184204 kg and X inertial position -0.04832589998841286 m.
The comparison quantity is `real_x - sim_x`.

The required inventory includes at minimum:

- printed torso shells, brackets and fasteners actually installed;
- RDK-X5 board, heatsink/fan, mounting plate, cables and adapters;
- actual battery cells/pack, BMS, charger and wiring;
- servo/bus board, IMU and power hardware fixed to the torso; and
- any build-specific cover or ballast.

Stock Pi Zero geometry or stock-battery placement is not accepted as a proxy
for this build.

## Comparison rule

After the signed break-radius curve completes, the build is inside the measured
model envelope only if the complete sim-to-real error interval lies inside both
signed certified inner bounds with one full curve-resolution margin (0.00078125
m) remaining on each side.

- `PASS_REAL_BUILD_COM_INSIDE_CERTIFIED_RADIUS`: interval and margin fit.
- `HOLD_REAL_BUILD_COM_OUTSIDE_CERTIFIED_RADIUS`: interval is measured but does
  not fit; only a separately preregistered simulator torso-model correction and
  frozen re-gate may follow.
- `HOLD_REAL_BUILD_COM_INPUTS_INCOMPLETE`: any required mass, placement, datum
  transform or uncertainty is absent. No numerical COM estimate is reported.

This study is read-only and offline. It authorizes no robot actuation, RDK-X5
access, training, deployment, model correction or Gate 5.

