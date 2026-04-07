from __future__ import annotations

from scripts.mutation_smoke_target import is_even_non_negative


def test_even_non_negative_accepts_even_positive() -> None:
    assert is_even_non_negative(2)


def test_even_non_negative_rejects_odd_positive() -> None:
    assert not is_even_non_negative(3)


def test_even_non_negative_rejects_negative_even() -> None:
    assert not is_even_non_negative(-2)


def test_even_non_negative_accepts_zero() -> None:
    assert is_even_non_negative(0)


def test_even_non_negative_rejects_negative_odd() -> None:
    assert not is_even_non_negative(-1)
