# SPDX-License-Identifier: Apache-2.0
"""Deterministic mutation-smoke target for merge-surface CI."""

from __future__ import annotations


def is_even_non_negative(value: int) -> bool:
    """Return True only for non-negative even integers."""
    return value >= 0 and value % 2 == 0
