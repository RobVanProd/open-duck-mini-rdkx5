# RDK X5 servo-bus digital audit — 2026-07-12

## Scope and safety

- Read-only host, USB, process, package, and upstream-source inspection.
- No servo-port transaction was issued.
- No motor command was issued.
- No GPU was used.

## Live RDK observations

- Host: `ubuntu`, Linux `6.1.83`, aarch64.
- Servo adapter: QinHeng `1a86:55d3`, serial `5B61034312`.
- Device: `/dev/ttyACM0`, driver `cdc_acm`.
- Topology: adapter enumerated at USB full speed (12 Mbit/s) through the onboard USB 2 hub.
- No process owned `/dev/ttyACM0`.
- No walking/runtime process was active.
- Current-boot kernel journal contained no matching USB reset, disconnect, descriptor, over-current, `cdc_acm`, or `ttyACM` error event.
- CPU governors were `schedutil` on CPUs 0–7.
- Installed packages matched Frank Fu's RDK X5 recipe: Rustypot 0.1.0, ONNX Runtime 1.18.1, NumPy 1.26.4, SciPy 1.15.1, Pygame 2.6.0, and Adafruit BNO055 5.4.13.

The closed-port `stty` display showed 9600 baud. This is not evidence that the runtime uses 9600 baud: Rustypot configures the device when it opens the port, and the runtime uses 1,000,000 baud.

## Clock correction

The board booted at `2000-01-01` in `Asia/Shanghai`. The timezone was changed to `America/New_York`. This image reports `NTP not supported`, so the system and RTC were set from the workstation epoch. Verified board time: `2026-07-12T01:49:20-04:00`.

## Rustypot source finding

The installed and Frank-Fu-pinned Rustypot is 0.1.0. In upstream commit `c97d871` (2026-01-05, included in v1.4.1, v1.4.2, and v1.5.0), Rustypot changed the pre-instruction receive-buffer handling:

- Old behavior: if nonempty, flush once, then `assert!` that the buffer is empty.
- New behavior: bounded flush-and-retry (three attempts, 5 ms delay), returning a communication timeout instead of asserting.

This is directly relevant to the OpenDuck checksum/input-buffer failure family. It establishes that the installed 0.1.0 transport handling is obsolete and that upstream subsequently hardened the exact buffer boundary implicated by reported failures. It does **not** establish that ID 13 is mechanically or electrically defective, nor does it prove that an upgrade alone eliminates physical packet corruption.

## Evidence-based conclusion

The current evidence does not support RDK CPU overload, USB enumeration failure, port contention, or a demonstrated right-knee mechanical fault. The leading boundary is the shared half-duplex transport/parser path. A controlled Rustypot compatibility test is justified before servo replacement or mechanical intervention.

## Next safe gate

1. Build/test the newer Rustypot API against the runtime offline on CPU, without the robot port.
2. Diff bindings and STS3215 semantics before considering deployment.
3. If compatible, stage a reversible board-side environment copy; do not replace the working environment.
4. Any live bus read or motor test requires explicit approval and a defined abort/cleanup contract.

## Implemented offline candidate

The runtime candidate now preserves Rustypot 0.1.0's API and all servo semantics,
but changes error recovery in `rustypot_position_hwi.HWI._retry`: after a bus
exception it releases the old PyO3 IO object, reopens the same serial path at
1,000,000 baud, and retries on the fresh handle. This prevents repeated retries
against a partially consumed receive buffer and avoids the old core's next-send
empty-buffer assertion. The clean path does not reopen or add a transaction.

`transport_reset_count` is exposed in telemetry. CPU-only mock tests prove that
an injected checksum error produces one reopen with the unchanged port/baud
contract and that a clean operation produces zero reopens. This is a repository
candidate only; it has not been copied to the RDK or exercised against the bus.

Candidate 1 was subsequently exercised at suspended `x=0.00` and rejected: an
exception traceback retained the exclusive serial handle, so reopen failed as
busy. Candidate 2 isolates the call in a short-lived frame and the regression
test now explicitly models exclusive-open behavior. See
`RUSTYPOT_TRANSPORT_RECOVERY_X0_ATTEMPT1_20260712.md`.

Sources:

- Frank Fu RDK X5 guide: https://frankfu.blog/openai/understanding-reinforcement-learning-through-openduck/
- Rustypot: https://github.com/pollen-robotics/rustypot
- Buffer fix: https://github.com/pollen-robotics/rustypot/commit/c97d871
