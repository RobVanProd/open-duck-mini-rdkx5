# Ground-Up Measured-Bridge Continuation CPU Smoke Result

status: `PASS_CPU_MEASURED_BRIDGE_CONTINUATION_SMOKE`

failed checks: `none`

source-to-step-zero max error: `0.0`
changed policy leaves: `10` / `10`
step-zero ONNX SHA-256: `f583377fef75e90f93380b9f4bf971f664f484629193a0e58ae6f466c3bad2be`
final ONNX SHA-256: `4fde5754cb71f396c3ea2275666094273f96b01022b126fcafdafd86b6900be0`
final ONNX max chained bound excess: `2.9802322387695312e-08`

This proves CPU restore/update/export compatibility with the bridge-only transition. Training reward and this short rollout are not policy-selection evidence, and no robot clearance follows.
