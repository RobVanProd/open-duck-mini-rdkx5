#!/usr/bin/env python3
"""Restore the normal runtime RAM gains, then disable torque."""

from mini_bdx_runtime.duck_config import DuckConfig
from mini_bdx_runtime.rustypot_position_hwi import HWI


def main():
    hwi = HWI(DuckConfig())
    kps = [30.0] * len(hwi.joints)
    kds = [0.0] * len(hwi.joints)
    kps[5:9] = [8.0, 8.0, 8.0, 8.0]
    try:
        hwi.set_kps(kps)
        hwi.set_kds(kds)
    finally:
        hwi.turn_off()
    print("DEFAULT_RUNTIME_GAINS_RESTORED_AND_TORQUE_DISABLED", flush=True)


if __name__ == "__main__":
    main()
