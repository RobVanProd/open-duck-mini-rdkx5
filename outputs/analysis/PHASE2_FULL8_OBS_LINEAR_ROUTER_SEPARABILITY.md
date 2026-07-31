# Full-8 Obs-Linear Router Separability

status: `HOLD_OBS_LINEAR_ROUTER_OVERLAP`

Offline diagnostic only. It did not train a policy, deploy, SSH, run robot tests, change runtime behavior, or run grounded replay.

## Inputs

- manifest: `outputs/analysis/phase2_full8_router_source_selected_manifest.json`
- positive_marker: `iter25/seed_005`
- positive_samples: `750`
- negative_samples: `5250`

## Linear Score

- direction: `ge`
- threshold: `-0.017247`
- positive selected: `62.00%`
- negative false selected: `56.59%`
- balanced accuracy: `52.70%`

| group | mean | p05 | p50 | p95 |
|---|---:|---:|---:|---:|
| positive | 0.006910 | -0.139205 | 0.013743 | 0.117061 |
| negative | -0.006910 | -0.153896 | -0.000582 | 0.104710 |

## Top Features

| obs_index | weight | center | positive_mean | negative_mean |
|---:|---:|---:|---:|---:|
| 92 | -0.678469 | 0.008611 | 0.007939 | 0.009283 |
| 13 | -0.376238 | 0.023513 | 0.022555 | 0.024471 |
| 18 | -0.305352 | 0.184107 | 0.183773 | 0.184441 |
| 91 | 0.212384 | -0.032097 | -0.030976 | -0.033219 |
| 50 | -0.168168 | 0.046434 | 0.043770 | 0.049098 |
| 64 | -0.167226 | 0.046448 | 0.043803 | 0.049094 |
| 78 | -0.166627 | 0.046485 | 0.043853 | 0.049116 |
| 22 | 0.157029 | 0.007732 | 0.008183 | 0.007281 |
| 83 | -0.149294 | 0.021501 | 0.021125 | 0.021877 |
| 21 | 0.146480 | -0.032817 | -0.031742 | -0.033892 |
| 90 | 0.104809 | -0.083661 | -0.082222 | -0.085101 |
| 20 | 0.092557 | -0.082913 | -0.081354 | -0.084471 |
| 89 | -0.091457 | -0.048991 | -0.049369 | -0.048612 |
| 93 | 0.090205 | -0.127564 | -0.127035 | -0.128093 |
| 85 | 0.082370 | -0.757598 | -0.756588 | -0.758608 |
| 15 | 0.080821 | -0.116331 | -0.115036 | -0.117626 |
| 19 | -0.078301 | -0.052835 | -0.053249 | -0.052421 |
| 86 | -0.075156 | 1.365087 | 1.364024 | 1.366150 |
| 16 | -0.067229 | 0.039110 | 0.037904 | 0.040316 |
| 23 | 0.064531 | -0.074276 | -0.073764 | -0.074788 |

## Decision

Do not build a two-policy obs-linear gate from this score. The positive seed-5 branch and negative command-gated branch overlap heavily in stateless observation space, so a linear gate would select the seed-5 branch on too many non-seed-5 samples.
