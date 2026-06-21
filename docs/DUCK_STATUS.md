# Open Duck Mini Local Status

Updated: 2026-06-16 16:00 EDT

## Current Priority

Validate the current sim-qualified Open Duck Mini policy on hardware in ordered stages.
Do not call the policy hardware-validated until the required hardware trial records pass in order.

Next required stage:

```bash
cd /home/lsd/robots/open_duck_peer/bundle/open_duck_mini_candidate
OPEN_DUCK_MINI_RUNTIME=/home/lsd/robots/Open_Duck_Mini_Runtime STAGE_ARMED=imu_static ./run_hardware_stage.sh imu_static
```

`imu_static` is the first safe stage. It samples the IMU while the robot is fixed upright. It is not a walking test.

## Active Candidate

- Candidate ONNX: `/home/lsd/robots/open_duck_peer/bundle/open_duck_mini_candidate/candidate.onnx`
- Candidate SHA256: `6c90e252c023f405ae8ffe9c81e1c6771c2aee0dcfdd9f9f5081d36224f068ce`
- Bundle archive: `/home/lsd/robots/open_duck_peer/open_duck_mini_candidate_bundle.tar.gz`
- Bundle SHA256: `fa1a8946be523dcc2345d126599665ff262ec452bbd4baadf77530b1592db23d`
- Status: `sim_qualified_not_hardware_validated`
- ONNX contract: obs dim `101`, action dim `14`

Dry preflight on this workstation passes:

- Result: `/home/lsd/robots/open_duck_peer/preflight/preflight_2026-06-16T195743Z.json`
- ONNX smoke shape: `[1, 101] -> [1, 14]`
- Smoke max abs action: `0.7081195712089539`
- Sanity sweep max abs action: `0.7456612586975098`

ONNX Runtime currently prints many schema warnings to stderr, but inference succeeds and preflight exits `0`.

## Sim Analysis

The current candidate beats the old baseline in the Mac-side durability gate:

- Candidate durable score: `174.51887604448532`
- Baseline `BEST_WALK_ONNX_2` durable score: `99.87989546827899`
- Score delta: `+74.63898057620633`
- Candidate hard failures: `0`
- Baseline hard failures: `4`
- Candidate mean fall rate: `0.0`
- Candidate mean forward velocity: `0.1372611974008192`

Durability cases all passed:

| Case | Score | Fall Rate | Mean Velocity |
| --- | ---: | ---: | ---: |
| `flat_backlash_015_random` | `174.517` | `0.0` | `0.140` |
| `flat_backlash_015_home` | `179.778` | `0.0` | `0.150` |
| `flat_backlash_012_random` | `178.977` | `0.0` | `0.118` |
| `flat_backlash_018_random` | `167.991` | `0.0` | `0.153` |
| `rough_backlash_light_seed11` | `173.129` | `0.0` | `0.130` |
| `rough_backlash_light_seed17` | `171.659` | `0.0` | `0.133` |

Quality-search note from the Mac bundle: later quality branches did not improve the retained candidate. They repeatedly failed the rough-light backlash cases, so the recommendation is to prioritize ordered hardware validation before wider search.

## Hardware Validation Order

Required ordered records:

1. `imu_static`, fixed upright, 10 seconds, max falls `0`
2. `blocks_static`, on blocks, 10 seconds, max falls `0`
3. `flat_tether_0.08`, tethered flat floor, 10 seconds, command x `0.08`, max falls `0`
4. `flat_tether_0.12`, tethered flat floor, 10 seconds, command x `0.12`, max falls `0`
5. `flat_stop`, flat floor stop, 5 seconds, command x `0.0`, max falls `0`

Use `./hardware_status.py` inside the bundle to print the exact next command.

## Local Runtime State

Runtime repo:

```text
/home/lsd/robots/Open_Duck_Mini_Runtime
```

Local patch applied to:

```text
/home/lsd/robots/Open_Duck_Mini_Runtime/scripts/v2_rl_walk_mujoco.py
```

Patch purpose:

- Adds `--fixed_command_x`
- Adds `--max_runtime_seconds`
- Adds `--force_unpaused`
- Enables motor target velocity clamping
- Adds `finally` cleanup with `self.hwi.turn_off()`

This repo is intentionally dirty because the deploy bundle preflight requires these safety hooks.

Robot config:

```text
/home/lsd/duck_config.json
```

It is conservative and starts paused. Joint offsets are zero placeholders. This is acceptable for the local Ubuntu preflight path, but it is not a substitute for the RDK-X5 robot's real calibrated `~/duck_config.json`.

Known board-side history from `/home/lsd/robots/outputs/duck_rdkx5_status.md` says servo zero calibration was completed on the RDK-X5 on 2026-06-14, including mechanical correction of two mis-clocked left-leg parts. Treat the board's config as the physical truth; treat this workstation's config as a safe local guard file.

## Prior Hardware Work

Detailed index:

```text
/home/lsd/robots/outputs/DUCK_OUTPUTS_INDEX.md
```

Key points from existing logs:

- RDK-X5 board access: primary Wi-Fi `192.168.1.50`, SSH user `sunrise`; key material is in `/home/lsd/robots/.duck_access/`. Direct Ethernet `192.168.127.10` is fallback only when a cable is connected.
- Board-only/no-motor Ethernet stability test passed for 359 samples from 2026-06-15 02:01 to 08:02 EDT with `0` ping failures, `0` SSH failures, `0` boot ID changes, and `0` uptime resets.
- Earlier Wi-Fi disappearance was determined to be network reachability, not a board power loss.
- Battery/UBEC/Dupont power path remained suspect for real resets under the battery harness.
- Board logs showed a dirty FAT unmount warning; do not run fsck against mounted live filesystems.
- Some previous walking experiments reached unpaused motion, but logs include tilt spikes up to `88.5 deg` in one responsive run and repeated blocked unpause events when controller commands were not neutral.
- Current disciplined path should use the staged deploy bundle, not the older ad hoc walk scripts.

## Main Local Folders

| Path | Purpose |
| --- | --- |
| `/home/lsd/robots/open_duck_peer` | Current Mac bridge handoff and deploy bundle |
| `/home/lsd/robots/Open_Duck_Mini_Runtime` | Physical robot runtime |
| `/home/lsd/robots/Open_Duck_Mini` | Open Duck Mini repo and older ONNX baselines |
| `/home/lsd/robots/Open_Duck_Playground` | Simulation/playground repo |
| `/home/lsd/robots/Open_Duck_reference_motion_generator` | Reference motion generator |
| `/home/lsd/robots/outputs` | Prior hardware logs, prints, runbooks, and generated outputs |
| `/home/lsd/robots/verify_scratch` | Older verification scratch data and ONNX checkpoints |
| `/home/lsd/robots/housekeeping_archive/2026-06-16-duck-tidy` | Files moved during cleanup, preserved not deleted |

## Housekeeping Done

- Archived empty accidental `=version` files from `Open_Duck_Playground`.
- Archived reference-motion generator `placo_presets/tmp`.
- Archived generated `__pycache__` from the extracted peer bundle.
- Copied the successful preflight JSON and stderr log out of `/tmp` into `open_duck_peer/preflight`.
- Added this status file and a focused peer-bundle README.
