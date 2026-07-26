# T7 universal response-support result

- Status: `PASS_T7_UNIVERSAL_RESPONSE_SUPPORT`
- Decision: `EARN_STATE_COHERENT_SUPPORT_TO_LOCOMOTION_CPU_SCREEN`
- Cells: `12/12`
- Result SHA-256: `8c77bdbd2f35c31b076c3453847cf1e2f109c91e4417c73ee9879b185989469d`

| configuration | fit | repeat | pass | min z | mean vx | pitch p95 | current run | overload run | context |
|---|---|---:|---|---:|---:|---:|---:|---:|---|
| `NOMINAL` | `p30` | 0 | `True` | 0.151530802 | 0.000888658 | 0.035242210 | 0 | 0 | `d6b9412a676b…` |
| `NOMINAL` | `p30` | 1 | `True` | 0.151530802 | 0.000888658 | 0.035242210 | 0 | 0 | `d6b9412a676b…` |
| `NOMINAL` | `p31_34` | 0 | `True` | 0.151530802 | 0.000887207 | 0.035497989 | 0 | 0 | `788d29fce97e…` |
| `NOMINAL` | `p31_34` | 1 | `True` | 0.151530802 | 0.000887207 | 0.035497989 | 0 | 0 | `788d29fce97e…` |
| `TORSO_COM_X_NEG` | `p30` | 0 | `True` | 0.151730672 | -0.000045392 | 0.053704482 | 0 | 0 | `22d441601e68…` |
| `TORSO_COM_X_NEG` | `p30` | 1 | `True` | 0.151730672 | -0.000045392 | 0.053704482 | 0 | 0 | `22d441601e68…` |
| `TORSO_COM_X_NEG` | `p31_34` | 0 | `True` | 0.151730672 | -0.000048972 | 0.053703718 | 0 | 0 | `03daa33488bd…` |
| `TORSO_COM_X_NEG` | `p31_34` | 1 | `True` | 0.151730672 | -0.000048972 | 0.053703718 | 0 | 0 | `03daa33488bd…` |
| `TORSO_COM_X_POS` | `p30` | 0 | `True` | 0.151467219 | 0.001311907 | 0.077217959 | 0 | 0 | `49b496bd664a…` |
| `TORSO_COM_X_POS` | `p30` | 1 | `True` | 0.151467219 | 0.001311907 | 0.077217959 | 0 | 0 | `49b496bd664a…` |
| `TORSO_COM_X_POS` | `p31_34` | 0 | `True` | 0.151467219 | 0.001307136 | 0.077342734 | 0 | 0 | `0a6505abd5a4…` |
| `TORSO_COM_X_POS` | `p31_34` | 1 | `True` | 0.151467219 | 0.001307136 | 0.077342734 | 0 | 0 | `0a6505abd5a4…` |

## Response separation

- `p30`: signed `0.156809302`, nominal→negative `0.105660278`, nominal→positive `0.052315593`.
- `p31_34`: signed `0.156853781`, nominal→negative `0.105694227`, nominal→positive `0.052315861`.

This result has zero training steps and no robot/RDK-X5 access. A pass authorizes only the separately preregistered, zero-training state-coherent handoff screen; it does not authorize hosted training, Gate 5, torque, motion, or deployment.
