from __future__ import annotations

from tools.run_t184_bilateral_single_support_anatomy import (
    contact_mode,
    contiguous_run_ending_at,
)


def test_contact_mode_maps_all_binary_vectors() -> None:
    assert contact_mode([0, 0]) == "none"
    assert contact_mode([1, 0]) == "left_only"
    assert contact_mode([0, 1]) == "right_only"
    assert contact_mode([1, 1]) == "both"


def test_contiguous_run_ending_at_stops_on_mode_change() -> None:
    modes = ["both", "left_only", "left_only", "none"]
    assert contiguous_run_ending_at(modes, 2) == 2
    assert contiguous_run_ending_at(modes, 3) == 1
