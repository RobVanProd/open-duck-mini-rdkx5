# Winner-v2 Observer Cross-Fit Result

Status: `PASS_P30_OBSERVER_MEASURED_CROSS_FIT_BRACKET`

Decision: `PASS_P30_OBSERVER_MEASURED_CROSS_FIT_BRACKET`

| observer | plant | step | x=0 | moving | worst tracking | min vx | matrix pass |
|---|---|---:|---|---|---:|---:|---|
| `p30` | `p30` | 512000 | `True` | `True` | 0.180855995 | 0.086461715 | `True` |
| `p30` | `p30` | 1024000 | `True` | `True` | 0.183170038 | 0.097619724 | `True` |
| `p30` | `p31_34` | 512000 | `True` | `True` | 0.179331797 | 0.084084972 | `True` |
| `p30` | `p31_34` | 1024000 | `True` | `True` | 0.180274206 | 0.098407268 | `True` |
| `p31_34` | `p30` | 512000 | `True` | `True` | 0.182713115 | 0.084404321 | `True` |
| `p31_34` | `p30` | 1024000 | `True` | `True` | 0.182229316 | 0.095423178 | `True` |
| `p31_34` | `p31_34` | 512000 | `True` | `True` | 0.178732973 | 0.084911748 | `True` |
| `p31_34` | `p31_34` | 1024000 | `True` | `True` | 0.181057256 | 0.096040766 | `True` |

- Formal cells: 32/32
- Trace rows: 19200
- Maximum plant/observer separation: 0.004135804 rad
- P30-observer worst tracking p95: 0.183170038 rad
- P30-observer minimum vx: 0.084084972 m/s

A pass pins only the P30 observer artifact for the offline winner-v2 configuration. It does not claim current hardware health or authorize Gate 5, deployment, RDK-X5 or robot use.
