"""Baseline Motor A engine for the initial copper sleeve."""

from __future__ import annotations

from datetime import date

from argos.contracts.series import CanonicalPoint
from argos.motors.motor_a.models import (
    FeatureNormalizationResult,
    MotorAConfig,
    MotorAFeatureSpec,
    RegimeState,
    ScarcitySnapshot,
)
from argos.motors.motor_a.normalization import blended_ecdf_score
from argos.motors.motor_a.regime import RegimeClassifier


class MotorAEngine:
    """Compute the scarcity score and operational regime for one commodity."""

    def __init__(self, config: MotorAConfig | None = None) -> None:
        self.config = config or MotorAConfig()
        self._classifier = RegimeClassifier(self.config)

    def compute_snapshot(
        self,
        *,
        commodity: str,
        decision_date: date,
        feature_specs: dict[str, MotorAFeatureSpec],
        feature_series: dict[str, list[CanonicalPoint]],
        previous_regime: RegimeState | None = None,
    ) -> ScarcitySnapshot:
        normalized_features: list[FeatureNormalizationResult] = []
        for feature_name, spec in feature_specs.items():
            points = [
                point for point in feature_series.get(feature_name, [])
                if point.temporal.availability_date <= decision_date
            ]
            if len(points) < spec.min_history:
                continue
            points.sort(key=lambda point: point.temporal.availability_date)
            raw_values = [point.value for point in points]
            long_scores, short_scores, blended_scores = blended_ecdf_score(
                raw_values,
                direction=spec.direction,
                long_alpha=self.config.long_alpha,
                short_window=self.config.short_window,
                decay_half_life=self.config.decay_half_life,
            )
            latest = points[-1]
            normalized = blended_scores[-1]
            signed_weight = -spec.weight if spec.is_relief else spec.weight
            evidence_active = normalized >= spec.evidence_threshold and signed_weight > 0
            normalized_features.append(
                FeatureNormalizationResult(
                    name=feature_name,
                    group=spec.group,
                    decision_date=latest.temporal.availability_date,
                    raw_value=latest.value,
                    long_score=long_scores[-1],
                    short_score=short_scores[-1],
                    blended_score=normalized,
                    reliability_weight=spec.reliability_weight,
                    signed_weight=signed_weight,
                    evidence_active=evidence_active,
                    history_count=len(points),
                )
            )

        if not normalized_features:
            raise ValueError("no Motor A features are available at the requested decision_date")

        numerator = sum(
            item.blended_score * item.signed_weight * item.reliability_weight
            for item in normalized_features
        )
        denominator = sum(abs(item.signed_weight) * item.reliability_weight for item in normalized_features)
        score = max(0.0, min(1.0, numerator / denominator))

        evidence_groups = tuple(sorted({item.group for item in normalized_features if item.evidence_active}))
        evidence_count = len(evidence_groups)
        squeeze_evidence_count = sum(
            1 for group in self.config.squeeze_required_groups if group in evidence_groups
        )
        regime = self._classifier.classify(score, evidence_count, squeeze_evidence_count, previous_regime)
        return ScarcitySnapshot(
            commodity=commodity,
            decision_date=decision_date,
            score=score,
            regime=regime,
            evidence_count=evidence_count,
            active_evidence_groups=evidence_groups,
            contributing_features=tuple(sorted(normalized_features, key=lambda item: item.name)),
        )
