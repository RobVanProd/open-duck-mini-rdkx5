# Grounded Rate165 Gate-2 Staging Result

Date: 2026-07-12

Status: `PASS_FILE_STAGING; PAUSED_RUNTIME_START_NOT_RUN`

Scope: copy and verify the candidate under a new filename without importing
motor hardware or starting the runtime.

## Candidate Identity

Local source:

```text
policy/candidates/phase2_corrected_live_oracle_iter1_rate165_20260703/candidate.onnx
size: 886302 bytes
SHA256: e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33
```

Remote destination:

```text
/home/sunrise/phase2_grounded_rate165_20260712_e06643e5.onnx
size: 886302 bytes
mode: 664
SHA256: e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33
```

The destination was proven absent before upload. The file was uploaded under a
hidden `.partial` name, verified, and atomically renamed. The first verification
command had an `awk` escaping error and stopped before rename; the partial file
was then verified successfully with a corrected command. No policy file was
overwritten, and no partial file remains.

## Preservation Checks

```text
duck_config SHA256:
  131a7b8fce1107b14f4727562f44f9e17324caf7fc22512ad7115911f050991b
baseline BEST_WALK_ONNX_2 SHA256:
  3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067
start_paused: true
runtime process: absent
```

The config and baseline policy are unchanged.

## Post-Staging Snapshot

```text
outputs/first_evidence/20260712T051548Z_grounded_rate165_gate2/
  20260712T051549Z_rdkx5_config_snapshot.json
snapshot SHA256:
  8abc45b060885ddedd1db7bfe2b2bbfec6f84bf4ee1ca3783a784fd77c74408b
remote_clock_plausible: true
```

The policy inventory contains the baseline, the prior June 27 candidate, and
the newly staged rate165 candidate with their expected hashes.

## Motor Boundary

No runtime was launched. Although `start_paused=true`, launching the runtime
can initialize motor hardware. The stated Gate-2 scope was no motor engagement,
so the paused-start/no-target-motion portion of the original approval packet
was not inferred from file-staging permission.

## Decision

File staging passes. The next hardware action is a paused runtime start followed
by suspended `x=0`, which can engage motors and requires a new explicit approval.
No `x=0.08` command or grounded replay is authorized.
