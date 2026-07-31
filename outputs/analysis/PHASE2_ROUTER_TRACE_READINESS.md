# Phase 2 Router Trace Readiness

status: `PASS_ROUTER_TRACE_DATA_READY`

## Executive Summary

Full-observation traces are present for Iter24, Iter25, Iter26, and Iter27 across the compact z=0.0075 seed set. The observation-based router diagnostic can be built from current local data.

This is offline/read-only. It did not train, SSH, deploy, run robot tests, change runtime behavior, or run grounded replay.

## Sources

| source | exists | trace count | seeds | total size | full obs |
|---|---|---:|---|---:|---|
| `iter24_iter27` | `True` | `10` | `[0, 1, 2, 6, 7]` | `46591524` | `True` |
| `iter25_iter26` | `True` | `10` | `[0, 1, 2, 6, 7]` | `44801849` | `True` |

## Trace Files

| policy | seed | rows | obs rows scanned | size | sha256 |
|---|---:|---:|---:|---:|---|
| `iter24` | `0` | `750` | `25` | `5768889` | `7c02728128959f39f573ae6a878b9956fbb699b50a7d9f38b4c40274113c9871` |
| `iter24` | `1` | `750` | `25` | `5767707` | `8d72d5e67f682e1adf882e427efd7e52a3552b68e72b5919d295273ca224aa5d` |
| `iter24` | `2` | `750` | `25` | `5767431` | `1eb9831201fbd409ff5398a576a8a6ed9c27ba0c880323cea7cb603f8d3097b7` |
| `iter24` | `6` | `250` | `25` | `1922620` | `315749855486d7f4c14a7e0a2425812f64b13b928434128d711758b529488001` |
| `iter24` | `7` | `750` | `25` | `5768862` | `a239b41886ddd6f99af2d7dcf89cc4d9fac78ed7d8d7efb21c5466400a5f75fd` |
| `iter27` | `0` | `750` | `25` | `5768443` | `4291a916501f749cf052793830b376f5c5117a1ce3adae44f16c51daf11ed5c6` |
| `iter27` | `1` | `750` | `25` | `5769024` | `d4e74d860bd81bc3c8b4c364a0546b7b6ad8cd0a81c0ef59c68a136498889679` |
| `iter27` | `2` | `307` | `25` | `2361669` | `4f6f43a927a8da3ddc3a781021d836e884a2e2975e54ed4b07605d4ccd364dfa` |
| `iter27` | `6` | `390` | `25` | `2998226` | `c2b458cb8ce13425532fee1f731dd06934fe03e139524343a475e0df9886c9b8` |
| `iter27` | `7` | `611` | `25` | `4698653` | `aa88f0cfd442a14ca78674769507b1b2e0d8fea7fe6f7dc92fcf7e6d5f13f1d9` |
| `iter25` | `0` | `525` | `25` | `4038323` | `e1ea07fe99f2c1d692dc591b05a9f3202e1df2b777afab41d120e9dc52417165` |
| `iter25` | `1` | `750` | `25` | `5768016` | `e3dba615bbfe7a62bee5d76e929f0d2e3477e85294c18c8c978b26484cecdf30` |
| `iter25` | `2` | `750` | `25` | `5768814` | `e4d1001304621f361db244315c98b03f4b27cf6210f6f26199462e234d29fe93` |
| `iter25` | `6` | `750` | `25` | `5768130` | `677dcdd20a8b47ed3b96f227123df80f91620cbf8c8ec5471ae3aaf7a2c36aa9` |
| `iter25` | `7` | `470` | `25` | `3614996` | `8f9890579425905f4e6cde50f73fd39dce82b8a242bac07dd7a2f4936b27c71c` |
| `iter26` | `0` | `554` | `25` | `4260770` | `8da729a9eb6434a3000dd71c07619dad05c9a50405e17f591a737160f30c77d9` |
| `iter26` | `1` | `593` | `25` | `4560135` | `992e7917c7a5c93f95d0e430f997c648cf697d39f502edd232ef94b2ec020c90` |
| `iter26` | `2` | `286` | `25` | `2200605` | `76462d2db041a44ea53f867e9235947a4e2b3c84fa24d52c743a29437c08e2b6` |
| `iter26` | `6` | `750` | `25` | `5768514` | `e5b1ec742cf8a9a9a3b97b410c00dadbed371c25565a350aceb87f761a42245e` |
| `iter26` | `7` | `397` | `25` | `3053546` | `0daae595cfc2bf795732705f5f9b9bfbfb1b4aaa992385bf7ec48bbaa618efd1` |

## Next

- Train/test only offline router diagnostics from these traces.
- Do not use seed id as a deployable routing feature.
- Gate any router on the canonical z=0.0075 rough+push compact screen before generating trainable behavior-preservation data.
