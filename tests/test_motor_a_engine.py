from __future__ import annotations

from datetime import date, timedelta

from argos.contracts.series import CanonicalPoint
from argos.contracts.temporal import TemporalMetadata
from argos.core.types import CalendarFrequency
from argos.motors.motor_a.engine import MotorAEngine
from argos.motors.motor_a.models import MotorAConfig, MotorAFeatureSpec, RegimeState, ScarcityDirection


def make_weekly_series(metric: str, values: list[float], start_date: date) -> list[CanonicalPoint]:
    return [
        CanonicalPoint(
            entity_id="copper",
            metric=metric,
            value=value,
            unit=None,
            currency=None,
            frequency=CalendarFrequency.WEEKLY,
            temporal=TemporalMetadata(
                observation_date=start_date + timedelta(days=7 * idx),
                publication_date=start_date + timedelta(days=7 * idx),
                availability_date=start_date + timedelta(days=7 * idx),
                effective_date=start_date + timedelta(days=7 * idx),
            ),
        )
        for idx, value in enumerate(values)
    ]


def build_specs() -> dict[str, MotorAFeatureSpec]:
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


def test_motor_a_detects_structural_tightness_from_multisignal_confirmation() -> None:
    start = date(2025, 1, 3)
    engine = MotorAEngine(MotorAConfig(short_window=4, persistence_observations=2))
    specs = build_specs()
    series = {
        "inventory": make_weekly_series("inventory", [100, 98, 95, 92, 88, 80, 70, 60], start),
        "term": make_weekly_series("spread_0_3m", [1, 1, 2, 3, 4, 6, 8, 10], start),
        "supply": make_weekly_series("supply_risk", [30, 35, 40, 45, 50, 55, 60, 68], start),
        "refining": make_weekly_series("refining_concentration", [50, 52, 54, 55, 56, 57, 58, 60], start),
        "relief": make_weekly_series("relief_supply", [30, 30, 28, 25, 24, 20, 18, 15], start),
    }
    prev = None
    snapshot = None
    for idx in range(5, 8):
        decision_date = start + timedelta(days=7 * idx)
        snapshot = engine.compute_snapshot(
            commodity="copper",
            decision_date=decision_date,
            feature_specs=specs,
            feature_series=series,
            previous_regime=prev,
        )
        prev = snapshot.regime
    assert snapshot is not None
    assert snapshot.score >= 0.70
    assert snapshot.regime in {RegimeState.STRUCTURAL_TIGHTNESS, RegimeState.SQUEEZE}
    assert snapshot.evidence_count >= 3
    assert "inventory" in snapshot.active_evidence_groups
    assert "term" in snapshot.active_evidence_groups


def test_motor_a_hysteresis_does_not_liquidate_on_one_week_relief() -> None:
    start = date(2025, 1, 3)
    engine = MotorAEngine(MotorAConfig(short_window=4, persistence_observations=2))
    specs = build_specs()
    tight_series = {
        "inventory": make_weekly_series("inventory", [100, 98, 95, 92, 88, 80, 70, 60], start),
        "term": make_weekly_series("spread_0_3m", [1, 1, 2, 3, 4, 6, 8, 10], start),
        "supply": make_weekly_series("supply_risk", [30, 35, 40, 45, 50, 55, 60, 68], start),
        "refining": make_weekly_series("refining_concentration", [50, 52, 54, 55, 56, 57, 58, 60], start),
        "relief": make_weekly_series("relief_supply", [30, 30, 28, 25, 24, 20, 18, 15], start),
    }
    prev = None
    for idx in range(5, 8):
        snapshot = engine.compute_snapshot(
            commodity="copper",
            decision_date=start + timedelta(days=7 * idx),
            feature_specs=specs,
            feature_series=tight_series,
            previous_regime=prev,
        )
        prev = snapshot.regime

    relieved_series = dict(tight_series)
    relieved_series["inventory"] = make_weekly_series("inventory", [100, 98, 95, 92, 88, 80, 70, 75], start)
    relieved_series["term"] = make_weekly_series("spread_0_3m", [1, 1, 2, 3, 4, 6, 8, 6], start)
    relieved_snapshot = engine.compute_snapshot(
        commodity="copper",
        decision_date=start + timedelta(days=7 * 7),
        feature_specs=specs,
        feature_series=relieved_series,
        previous_regime=prev,
    )
    assert relieved_snapshot.regime != RegimeState.LOOSE


def test_relief_feature_reduces_overall_score() -> None:
    start = date(2025, 1, 3)
    engine = MotorAEngine(MotorAConfig(short_window=4, persistence_observations=2))
    specs = build_specs()
    stressed = {
        "inventory": make_weekly_series("inventory", [100, 98, 95, 92, 88, 80], start),
        "term": make_weekly_series("spread_0_3m", [1, 1, 2, 3, 4, 6], start),
        "supply": make_weekly_series("supply_risk", [30, 35, 40, 45, 50, 55], start),
        "refining": make_weekly_series("refining_concentration", [50, 52, 54, 55, 56, 57], start),
        "relief": make_weekly_series("relief_supply", [10, 10, 10, 10, 10, 10], start),
    }
    with_relief = dict(stressed)
    with_relief["relief"] = make_weekly_series("relief_supply", [10, 15, 20, 30, 40, 50], start)
    decision_date = start + timedelta(days=7 * 5)
    score_without_relief = engine.compute_snapshot(
        commodity="copper",
        decision_date=decision_date,
        feature_specs=specs,
        feature_series=stressed,
    ).score
    score_with_relief = engine.compute_snapshot(
        commodity="copper",
        decision_date=decision_date,
        feature_specs=specs,
        feature_series=with_relief,
    ).score
    assert score_with_relief < score_without_relief
