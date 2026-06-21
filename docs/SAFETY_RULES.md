# Safety Rules

These rules apply to every person, script, agent, and PR touching this robot project.

## Hardware Movement

- Do not run moving hardware tests unless Rob is physically present and has explicitly approved that test.
- Robot must be physically supported unless the test explicitly says grounded.
- Grounded tests require side-view observation and immediate access to power cutoff.
- Start paused wherever possible.
- Keep fingers clear of joints, belts, linkages, feet, and support points.
- Be ready to cut power before unpausing policy replay.
- Default movement amplitudes must be small.

## Runtime Changes

- Do not change joint offsets without evidence and review.
- Do not change gains without evidence and review.
- Do not change IMU axis remaps or offsets without evidence and review.
- Do not change action scale without evidence and review.
- Do not change gait phase timing without evidence and review.
- Do not train or deploy a new policy until the diagnostic gates pass.
- Keep default runtime behavior unchanged unless a branch is explicitly for a reviewed fix.

## Remote Access

- Read-only SSH checks are allowed.
- Do not run servo, IMU, calibration, walking, or power commands remotely unless Rob has confirmed the robot is safe for that exact command.
- Do not assume the robot is supported just because it is reachable.

## Repository Hygiene

- Do not commit private SSH keys.
- Do not commit `known_hosts`.
- Do not commit tokens or secrets.
- Do not commit huge raw JSONL logs by default.
- Do not commit videos by default.
- Commit small analyzer summaries, manifests, and selected evidence snapshots.
- Prefer small PRs with one purpose each.

## Stop Conditions

Stop the test sequence if any of these occur:

- Upright accelerometer is not roughly `[small, small, +9.5]`.
- Gyro is not stable while stationary.
- Joint tracking error is large while holding home.
- Foot contact polarity is swapped or inverted.
- A hip pitch, knee, or ankle moves the wrong joint, wrong side, or unexpected sign.
- Bus errors appear repeatedly while stationary.
- Policy replay shows immediate saturation or an obvious forward-biased posture in suspension.
