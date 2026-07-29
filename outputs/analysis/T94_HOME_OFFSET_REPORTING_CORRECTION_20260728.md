# T94 home-offset reporting correction

Status: `CORRECTED_T94_HOME_OFFSET_REPORTING`

The four apparent home-offset calibration failures were reporting-only. The evaluator correctly expanded the preregistered scalar `±0.03 rad` shorthand to all 14 joints, and every readback and home-initialization delta is exact.

- Corrected safe calibration cells: **40/40**
- Fit classifications: **23/40**
- Negative-COM false positives: **2**
- Decision remains: `CLOSE_CALIBRATION_ROUTED_EXPERT_MECHANISM`

No simulation block was rerun and no hosted compute or hardware was used. Discrete calibration-routed experts remain closed because calibration safety was not the routing failure.

Correction SHA-256: `5bfb90b0287f62de7e0eeff5a3ccbbaeadc54f8903d11789c70e980dee099b75`
