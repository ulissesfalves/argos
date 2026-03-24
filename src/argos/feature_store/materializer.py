"""Deterministic feature materialization with temporal validation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Iterable

from argos.contracts.series import CanonicalPoint, FeaturePoint
from argos.core.exceptions import TemporalValidationError
from argos.core.types import CalendarFrequency


@dataclass(frozen=True)
class MaterializedFeatureSet:
    feature_name: str
    frequency: CalendarFrequency
    signature: str
    record_count: int
    lineage: dict[str, str]
    records: tuple[FeaturePoint, ...]


class FeatureMaterializer:
    """Materialize features deterministically from canonical inputs."""

    def materialize_mean_feature(
        self,
        feature_name: str,
        source_metric: str,
        inputs: Iterable[CanonicalPoint],
        output_frequency: CalendarFrequency,
    ) -> MaterializedFeatureSet:
        points = tuple(sorted(inputs, key=self._sort_key))
        if not points:
            raise TemporalValidationError("cannot materialize a feature from an empty input")

        feature_points = tuple(
            FeaturePoint(
                entity_id=point.entity_id,
                feature_name=feature_name,
                feature_value=point.value,
                frequency=output_frequency,
                temporal=point.temporal,
                source_metric=source_metric,
            )
            for point in points
        )

        signature = self._build_signature(feature_points)
        lineage = {
            "source_metric": source_metric,
            "feature_name": feature_name,
            "algorithm": "identity_mean_baseline_v1",
            "signature": signature,
        }
        return MaterializedFeatureSet(
            feature_name=feature_name,
            frequency=output_frequency,
            signature=signature,
            record_count=len(feature_points),
            lineage=lineage,
            records=feature_points,
        )

    @staticmethod
    def _sort_key(point: CanonicalPoint) -> tuple[str, str, str]:
        return (
            point.entity_id,
            point.metric,
            point.temporal.availability_date.isoformat(),
        )

    @staticmethod
    def _build_signature(points: tuple[FeaturePoint, ...]) -> str:
        payload = [
            {
                "entity_id": point.entity_id,
                "feature_name": point.feature_name,
                "feature_value": point.feature_value,
                "frequency": point.frequency.value,
                "source_metric": point.source_metric,
                "observation_date": point.temporal.observation_date.isoformat(),
                "publication_date": point.temporal.publication_date.isoformat() if point.temporal.publication_date else None,
                "availability_date": point.temporal.availability_date.isoformat(),
                "effective_date": point.temporal.effective_date.isoformat() if point.temporal.effective_date else None,
            }
            for point in points
        ]
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
