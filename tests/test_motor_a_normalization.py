from __future__ import annotations

from argos.motors.motor_a.normalization import blended_ecdf_score
from argos.motors.motor_a.models import ScarcityDirection


def test_lower_values_can_mean_higher_scarcity() -> None:
    long_scores, short_scores, blended = blended_ecdf_score(
        [100.0, 90.0, 80.0, 70.0],
        direction=ScarcityDirection.LOWER_IS_SCARCER,
        long_alpha=0.8,
        short_window=3,
        decay_half_life=5,
    )
    assert blended[-1] > blended[0]
    assert long_scores[-1] > long_scores[0]
    assert short_scores[-1] > short_scores[0]


def test_future_outlier_does_not_change_past_normalization() -> None:
    base = blended_ecdf_score(
        [10.0, 11.0, 12.0],
        direction=ScarcityDirection.HIGHER_IS_SCARCER,
        long_alpha=0.8,
        short_window=2,
        decay_half_life=5,
    )[2]
    with_future = blended_ecdf_score(
        [10.0, 11.0, 12.0, 100.0],
        direction=ScarcityDirection.HIGHER_IS_SCARCER,
        long_alpha=0.8,
        short_window=2,
        decay_half_life=5,
    )[2]
    assert with_future[:3] == base
