"""Robust normalization for Motor A using ECDF with decay and short window percentiles."""

from __future__ import annotations

import math
from typing import Iterable

from argos.motors.motor_a.models import ScarcityDirection


def _scarcity_value(raw_value: float, direction: ScarcityDirection) -> float:
    if direction == ScarcityDirection.HIGHER_IS_SCARCER:
        return raw_value
    return -raw_value


def _weighted_percentile_rank(values: list[float], value: float, weights: list[float]) -> float:
    total_weight = sum(weights)
    if total_weight <= 0:
        raise ValueError("weights must sum to a positive value")

    lower = sum(weight for observed, weight in zip(values, weights) if observed < value)
    equal = sum(weight for observed, weight in zip(values, weights) if observed == value)
    return (lower + 0.5 * equal) / total_weight


def expanding_ecdf_decay(
    values: Iterable[float],
    *,
    half_life: int,
) -> list[float]:
    observed = list(values)
    if half_life <= 0:
        raise ValueError("half_life must be positive")

    scores: list[float] = []
    for idx in range(len(observed)):
        history = observed[: idx + 1]
        ages = [idx - j for j in range(idx + 1)]
        weights = [math.exp(-math.log(2) * age / half_life) for age in ages]
        scores.append(_weighted_percentile_rank(history, observed[idx], weights))
    return scores


def rolling_window_ecdf(values: Iterable[float], *, window: int) -> list[float]:
    observed = list(values)
    if window <= 0:
        raise ValueError("window must be positive")

    scores: list[float] = []
    for idx in range(len(observed)):
        start = max(0, idx - window + 1)
        history = observed[start : idx + 1]
        weights = [1.0] * len(history)
        scores.append(_weighted_percentile_rank(history, observed[idx], weights))
    return scores


def blended_ecdf_score(
    raw_values: Iterable[float],
    *,
    direction: ScarcityDirection,
    long_alpha: float,
    short_window: int,
    decay_half_life: int,
) -> tuple[list[float], list[float], list[float]]:
    if not 0.0 <= long_alpha <= 1.0:
        raise ValueError("long_alpha must be within [0, 1]")

    scarcity_values = [_scarcity_value(value, direction) for value in raw_values]
    long_scores = expanding_ecdf_decay(scarcity_values, half_life=decay_half_life)
    short_scores = rolling_window_ecdf(scarcity_values, window=short_window)
    blended_scores = [
        long_alpha * long_score + (1.0 - long_alpha) * short_score
        for long_score, short_score in zip(long_scores, short_scores)
    ]
    return long_scores, short_scores, blended_scores
