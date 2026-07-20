# Winner-v4 Response Support Reset Causal Audit

status: `PASS_RESPONSE_SUPPORT_RESET_CAUSAL_AUDIT`

result SHA-256: `619ed2f3d4927e53a8d9f3e51e6ee0aa781cafe7eb13eebbd0672bb8695dc682`

completed formal result SHA-256: `b7eb0a5d8ccdfa4034fec85fdd98cd21e6888f7d4bd5b106c6e2052a07966730`

The completed result is not retried or reclassified. The audit isolates a `mj_setConst` ordering bug: nominal home support fails under the legacy order and remains upright under the corrected order. The corrected negative-X endpoint still falls, so response73 stays closed and only a new prospective support procedure may advance.
