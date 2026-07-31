# Contract C4 Round-Robin Servo Health Telemetry

Status: `PASS_C4_CPU_MOCK_CONTRACT`

The existing opt-in `--telemetry-read-voltage` hardware guard now enables an
extended health sample for one servo per logged tick. The cursor covers all 14
servo IDs, preserves the established ID-13-last read order, and wraps after 14
samples. For the selected servo it calls the Rustypot current, voltage and
temperature accessors through the existing retry/reopen boundary.

Telemetry retains raw current, voltage and temperature values. Voltage is also
reported in volts using the already-established 0.1-V register scale. No unit
is invented for current or temperature. The per-tick sample records joint
name, ID, index, coverage cursor and errors; rolling 14-element arrays retain
the latest sample for each servo.

Default-off remains exact at the bus boundary: when the existing guard is
false, the health helper returns before calling HWI and all extended arrays are
reported as null. Mock tests prove 14-ID coverage, wraparound, values and the
existing transport/order behavior. The schema and static runtime contract pass.

Across 5,000 CPU/mock samples, the three-register round-robin helper's p95 was
0.000002054 s and its incremental p95 over a no-op was 0.000001994 s, below
the frozen 0.005 s mock budget. This is mock dispatch timing, not a claim about
serial-bus or RDK timing.

This is not an on-device API or timing validation. In particular,
`get_present_temperature` is contracted against the mock but remains to be
verified against the RDK-installed Rustypot build in a separately authorized
read-only hardware phase. No hardware was accessed here.

Robot clearance remains `NO`.
