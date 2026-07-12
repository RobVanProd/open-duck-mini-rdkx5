# Rate165 Zero-Hold Timing Audit

status: `LOCAL_PASS_REMOTE_STAGE_WAITING_FOR_RDK`

An opt-in `--log-stage-timing` mode now adds these durations to each telemetry
record:

- observation acquisition, including serial position/velocity reads
- ONNX policy inference
- target preparation
- serial motor write
- pre-telemetry work total
- previous telemetry serialization/write time

The flag fails closed unless telemetry logging is also enabled. With the flag
absent, timing collection does not run.

Offline CPU benchmark, 2,000 iterations using an actual 5,384-byte telemetry
record and the zero-hold ONNX:

| component | p95 | maximum |
|---|---:|---:|
| policy inference | 0.0206 ms | 3.0402 ms |
| JSON serialization | 0.0440 ms | 0.1465 ms |
| buffered write + flush | 0.0022 ms | 0.0547 ms |

These measured components cannot explain the observed 60.87/62.12 ms control
gaps. Serial I/O and scheduler delay remain unmeasured candidates; do not
assign causality without the staged timing trace.

Validation:

- walker and benchmark tool compile successfully
- motor velocity parser tests: 3 passed, 3 subtests passed
- `git diff --check`: pass
- local GPU and onboard GPU: unused
- robot motion/serial access: none

The first read-only RDK snapshot attempt at 20:14 UTC timed out. After the
operator reset power, a fresh snapshot at 20:15 UTC passed, with no runtime and
no `/dev/ttyACM0` owner. Files were copied to the isolated directory
`/home/sunrise/rate165_zero_hold_timing_stage_20260712`; no live path was
targeted. The RDK then became unreachable again before remote hashes and idle
state could be verified. Therefore staging is `INCOMPLETE_UNVERIFIED`, not a
pass. Resolve power stability, then verify or replace that isolated directory.
No installation or motor action occurred.
