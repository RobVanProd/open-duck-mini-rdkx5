# Winner-v5 Automatic Support-Recovery Result

status: `HOLD_WINNER_V5_AUTOMATIC_SUPPORT_RECOVERY`

raw result SHA-256: `f36855923f91f683ebe691b0726e1231c04c5036ab7dff27836534ade7b0d17a`

attributed repository result SHA-256: `641b164d451cca6d83f94dc6f4b1f9961b5c774c28a3e738d04c480d5e798653`

The frozen 960-cell gate failed: 784 cells passed and 176 failed across 28 configurations. All 176 failures were triggered recoveries; the rule did not fail because it overlooked an unstable case. Fifty-eight cells collapsed, while 118 remained upright but violated uninterrupted two-foot support. The fixed recovery target is therefore non-universal.

Under nominal quantized input, 73 configurations pass both actuator fits, 11 fail both, 8 pass only P30, and 4 pass only P31/34. The nearest P30 pass/fail trigger pair is only `0.001090830782` rad/s apart—one BNO055 gyro count in this contract.

Decision: close the one-shot IMU threshold plus fixed recovery target. Do not retune it. A later prospective study may test dynamic state feedback that continues adapting after the first sample; no training, runtime, or robot action is authorized by this result.
