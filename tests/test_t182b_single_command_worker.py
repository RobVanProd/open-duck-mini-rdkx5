from __future__ import annotations

import tools.evaluate_t182_shared_failure_single_cell as worker


def test_formal_command_tuple_is_exact_single_cell() -> None:
    assert worker.FORMAL_COMMANDS == (0.077,)


def test_wrapper_reuses_t27_worker_implementation() -> None:
    assert worker.base.CALIBRATION_TICKS == 250
    assert worker.base.HOME_RETURN_TICKS == 0
    assert callable(worker.base.main)
