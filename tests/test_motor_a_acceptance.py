from __future__ import annotations

from datetime import date, timedelta

import pytest

from argos.contracts.series import CanonicalPoint
from argos.contracts.temporal import TemporalMetadata
from argos.core.types import CalendarFrequency
from argos.motors.motor_a.engine import MotorAEngine
from argos.motors.motor_a.models import MotorAConfig, MotorAFeatureSpec, RegimeState, ScarcityDirection


def make_series(metric: str, values: list[float], start: date) -> list[CanonicalPoint]:
    return [
        CanonicalPoint(
            entity_id="copper",
            metric=metric,
            value=value,
            unit=None,
            currency=None,
            frequency=CalendarFrequency.WEEKLY,
            temporal=TemporalMetadata(
                observation_date=start + timedelta(days=7 * idx),
                publication_date=start + timedelta(days=7 * idx),
                availability_date=start + timedelta(days=7 * idx),
                effective_date=start + timedelta(days=7 * idx),
            ),
        )
        for idx, value in enumerate(values)
    ]


def make_specs() -> dict[str, MotorAFeatureSpec]:
    return {
        "inventory": MotorAFeatureSpec(
            name="inventory",
            source_metric="inventory",
            weight=0.30,
            direction=ScarcityDirection.LOWER_IS_SCARCER,
            frequency=CalendarFrequency.WEEKLY,
            group="inventory",
        ),
        "term": MotorAFeatureSpec(
            name="term",
            source_metric="spread_0_3m",
            weight=0.25,
            direction=ScarcityDirection.HIGHER_IS_SCARCER,
            frequency=CalendarFrequency.WEEKLY,
            group="term",
        ),
        "supply": MotorAFeatureSpec(
            name="supply",
            source_metric="supply_risk",
            weight=0.20,
            direction=ScarcityDirection.HIGHER_IS_SCARCER,
            frequency=CalendarFrequency.WEEKLY,
            group="supply",
        ),
        "refining": MotorAFeatureSpec(
            name="refining",
            source_metric="refining_concentration",
            weight=0.15,
            direction=ScarcityDirection.HIGHER_IS_SCARCER,
            frequency=CalendarFrequency.WEEKLY,
            group="refining",
        ),
        "relief": MotorAFeatureSpec(
            name="relief",
            source_metric="relief_supply",
            weight=0.10,
            direction=ScarcityDirection.HIGHER_IS_SCARCER,
            frequency=CalendarFrequency.WEEKLY,
            group="relief",
            is_relief=True,
            evidence_threshold=0.90,
        ),
    }


def test_acceptance_multisignal_can_reach_squeeze() -> None:
    start = date(2025, 1, 3)
    specs = make_specs()
    engine = MotorAEngine(MotorAConfig(short_window=4, persistence_observations=2))
    series = {
        "inventory": make_series("inventory", [100, 97, 94, 90, 84, 76, 64, 52, 40], start),
        "term": make_series("spread_0_3m", [1, 2, 3, 4, 6, 8, 11, 14, 18], start),
        "supply": make_series("supply_risk", [30, 32, 35, 40, 48, 55, 62, 72, 82], start),
        "refining": make_series("refining_concentration", [50, 52, 54, 56, 58, 60, 62, 64, 66], start),
        "relief": make_series("relief_supply", [20, 19, 18, 16, 14, 13, 12, 11, 10], start),
    }
    prev = None
    last = None
    for idx in range(5, 9):
        last = engine.compute_snapshot(
            commodity="copper",
            decision_date=start + timedelta(days=7 * idx),
            feature_specs=specs,
            feature_series=series,
            previous_regime=prev,
        )
        prev = last.regime
    assert last is not None
    assert last.regime in {RegimeState.STRUCTURAL_TIGHTNESS, RegimeState.SQUEEZE}
    assert last.evidence_count >= 3
    assert len(last.contributing_features) >= 4


def test_acceptance_snapshot_is_auditable() -> None:
    start = date(2025, 1, 3)
    specs = make_specs()
    engine = MotorAEngine()
    series = {
        "inventory": make_series("inventory", [100, 95, 90, 85, 80], start),
        "term": make_series("spread_0_3m", [1, 2, 3, 4, 5], start),
        "supply": make_series("supply_risk", [30, 35, 40, 45, 50], start),
        "refining": make_series("refining_concentration", [50, 51, 52, 53, 54], start),
        "relief": make_series("relief_supply", [20, 20, 20, 20, 20], start),
    }
    snapshot = engine.compute_snapshot(
        commodity="copper",
        decision_date=start + timedelta(days=7 * 4),
        feature_specs=specs,
        feature_series=series,
    )
    assert 0.0 <= snapshot.score <= 1.0
    assert isinstance(snapshot.active_evidence_groups, tuple)
    assert snapshot.contributing_features
    for feature in snapshot.contributing_features:
        assert 0.0 <= feature.long_score <= 1.0
        assert 0.0 <= feature.short_score <= 1.0
        assert 0.0 <= feature.blended_score <= 1.0


def test_acceptance_requires_available_history() -> None:
    start = date(2025, 1, 3)
    specs = {
        "inventory": MotorAFeatureSpec(
            name="inventory",
            source_metric="inventory",
            weight=0.30,
            direction=ScarcityDirection.LOWER_IS_SCARCER,
            frequency=CalendarFrequency.WEEKLY,
            group="inventory",
            min_history=10,
        )
    }
    engine = MotorAEngine()
    series = {"inventory": make_series("inventory", [100, 90, 80, 70, 60], start)}
    with pytest.raises(ValueError):
        engine.compute_snapshot(
            commodity="copper",
            decision_date=start + timedelta(days=7 * 4),
            feature_specs=specs,
            feature_series=series,
        )
