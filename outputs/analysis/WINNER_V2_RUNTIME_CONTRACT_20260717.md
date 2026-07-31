# Winner v2 Runtime Offline Contract

Status: `PASS_WINNER_V2_RUNTIME_OFFLINE_CONTRACT_HOLD_HARDWARE_FIT_SELECTION`

Decision: `PASS_WINNER_V2_RUNTIME_OFFLINE_CONTRACT_HOLD_HARDWARE_FIT_SELECTION`

- Frozen full-observation rows checked: 40520
- Frozen bridge rows checked: 9600
- Runtime-to-recorded bridge maximum error: 0 rad
- Stateful policies checked: 2
- Failed checks: []

The default legacy 101-D path remains selected unless winner-v2 is explicitly requested. Winner-v2 now has a strict 115-D observation composer, fitted bridge observer, projected-reference lookup, and stateful CPU ONNX runner. It requires an explicit contracted fit and does not choose a hardware fit.

This is an offline implementation result only. Hardware fit selection, deployment, Gate 5, robot/RDK-X5 access, and robot clearance remain unauthorized.
