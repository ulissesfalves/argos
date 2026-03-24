from __future__ import annotations

from datetime import date

import pytest

from argos.canonical.join_policy import validate_join
from argos.contracts.series import CanonicalPoint
from argos.contracts.temporal import TemporalMetadata
from argos.core.exceptions import IncompatibleCalendarError, TemporalValidationError
from argos.core.types import CalendarFrequency, CarryRule
from argos.feature_store.materializer import FeatureMaterializer


def make_point(value: float, availability_date: date) -> CanonicalPoint:
    return CanonicalPoint(
        entity_id="copper_lme",
        metric="inventory",
        value=value,
        unit="tons",
        currency=None,
        frequency=CalendarFrequency.WEEKLY,
        temporal=TemporalMetadata(
            observation_date=availability_date,
            publication_date=availability_date,
            availability_date=availability_date,
            effective_date=availability_date,
        ),
    )


def test_temporal_metadata_rejects_invalid_order() -> None:
    with pytest.raises(TemporalValidationError):
        TemporalMetadata(
            observation_date=date(2026, 1, 10),
            publication_date=date(2026, 1, 9),
            availability_date=date(2026, 1, 10),
            effective_date=date(2026, 1, 10),
        )


def test_exact_join_rejects_incompatible_calendars() -> None:
    with pytest.raises(IncompatibleCalendarError):
        validate_join(
            left_frequency=CalendarFrequency.WEEKLY,
            right_frequency=CalendarFrequency.MONTHLY,
            carry_rule=CarryRule.EXACT,
        )


def test_forward_fill_join_accepts_lower_frequency_source() -> None:
    validate_join(
        left_frequency=CalendarFrequency.WEEKLY,
        right_frequency=CalendarFrequency.MONTHLY,
        carry_rule=CarryRule.FORWARD_FILL,
    )


def test_materialization_is_deterministic() -> None:
    materializer = FeatureMaterializer()
    points = (
        make_point(100.0, date(2026, 1, 3)),
        make_point(90.0, date(2026, 1, 10)),
    )

    run_1 = materializer.materialize_mean_feature(
        feature_name="inventory_pressure",
        source_metric="inventory",
        inputs=points,
        output_frequency=CalendarFrequency.WEEKLY,
    )
    run_2 = materializer.materialize_mean_feature(
        feature_name="inventory_pressure",
        source_metric="inventory",
        inputs=points,
        output_frequency=CalendarFrequency.WEEKLY,
    )

    assert run_1.signature == run_2.signature
    assert run_1.lineage["algorithm"] == "identity_mean_baseline_v1"
    assert run_1.record_count == 2


def test_materialization_rejects_empty_input() -> None:
    with pytest.raises(TemporalValidationError):
        FeatureMaterializer().materialize_mean_feature(
            feature_name="inventory_pressure",
            source_metric="inventory",
            inputs=[],
            output_frequency=CalendarFrequency.WEEKLY,
        )
