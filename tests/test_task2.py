import sys
import pathlib
import pytest

# --- make git-pycore-hw-03 importable without packaging ---
ROOT = pathlib.Path(__file__).resolve().parents[2]  # .../MyPath
HW03 = ROOT / "git-pycore-hw-03"
if str(HW03) not in sys.path:
    sys.path.insert(0, str(HW03))

from task2 import get_numbers_ticket


def is_sorted_non_decreasing(seq):
    return all(a <= b for a, b in zip(seq, seq[1:]))


def test_basic_properties_1_49_q6():
    nums = get_numbers_ticket(1, 49, 6)
    assert isinstance(nums, list)
    assert len(nums) == 6
    assert len(set(nums)) == 6  # unique
    assert is_sorted_non_decreasing(nums)
    assert all(1 <= x <= 49 for x in nums)


def test_full_range_quantity_equals_range_size():
    # when quantity == available numbers, should return the whole range
    nums = get_numbers_ticket(10, 15, 6)  # 10..15 inclusive -> 6 numbers
    assert nums == list(range(10, 16))


@pytest.mark.parametrize(
    "min_v,max_v,qty",
    [
        (0, 10, 5),        # min < 1
        (1, 1001, 5),      # max > 1000
        (10, 10, 1),       # min >= max
        (20, 10, 1),       # min > max
        (1, 10, 0),        # qty <= 0
        (1, 5, 10),        # qty > range size
        ("1", 10, 5),      # wrong type
        (1, "10", 5),      # wrong type
        (1, 10, "5"),      # wrong type
        (1.0, 10, 5),      # float
        (1, 10.0, 5),      # float
        (1, 10, 5.0),      # float
    ],
)
def test_invalid_params_return_empty(min_v, max_v, qty):
    assert get_numbers_ticket(min_v, max_v, qty) == []


def test_min_boundary_1_max_boundary_1000_small_q():
    nums = get_numbers_ticket(1, 1000, 3)
    assert len(nums) == 3
    assert len(set(nums)) == 3
    assert is_sorted_non_decreasing(nums)
    assert all(1 <= x <= 1000 for x in nums)


def test_randomness_uniqueness_across_calls():
    # Not asserting specific numbers (to avoid version-dependent RNG sequences),
    # just ensure each call respects uniqueness and range.
    for _ in range(10):
        nums = get_numbers_ticket(5, 25, 8)
        assert len(nums) == 8
        assert len(set(nums)) == 8
        assert is_sorted_non_decreasing(nums)
        assert all(5 <= x <= 25 for x in nums)
