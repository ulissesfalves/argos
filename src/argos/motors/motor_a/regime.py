"""Regime classification with hysteresis and evidence gates."""

from __future__ import annotations

from collections import deque

from argos.motors.motor_a.models import MotorAConfig, RegimeState


class RegimeClassifier:
    """State machine for Motor A regimes."""

    def __init__(self, config: MotorAConfig) -> None:
        self.config = config
        self._structural_buffer = deque(maxlen=config.persistence_observations)
        self._squeeze_buffer = deque(maxlen=config.persistence_observations)

    def classify(self, score: float, evidence_count: int, squeeze_evidence_count: int, previous_regime: RegimeState | None) -> RegimeState:
        structural_candidate = score >= self.config.regime_entry_structural and evidence_count >= self.config.min_positive_evidence
        squeeze_candidate = score >= self.config.regime_entry_squeeze and evidence_count >= self.config.min_positive_evidence and squeeze_evidence_count >= self.config.min_squeeze_evidence
        self._structural_buffer.append(structural_candidate)
        self._squeeze_buffer.append(squeeze_candidate)

        regime = previous_regime or RegimeState.LOOSE

        if regime == RegimeState.SQUEEZE:
            if score >= self.config.regime_exit_squeeze and evidence_count >= self.config.min_positive_evidence and squeeze_evidence_count >= 1:
                return RegimeState.SQUEEZE
            regime = RegimeState.STRUCTURAL_TIGHTNESS

        if regime == RegimeState.STRUCTURAL_TIGHTNESS:
            if all(self._squeeze_buffer):
                return RegimeState.SQUEEZE
            if score >= self.config.regime_exit_structural and evidence_count >= 2:
                return RegimeState.STRUCTURAL_TIGHTNESS
            regime = RegimeState.CYCLICAL_TIGHTNESS

        if regime == RegimeState.CYCLICAL_TIGHTNESS:
            if all(self._squeeze_buffer):
                return RegimeState.SQUEEZE
            if all(self._structural_buffer):
                return RegimeState.STRUCTURAL_TIGHTNESS
            if score >= self.config.regime_exit_cyclical and evidence_count >= 1:
                return RegimeState.CYCLICAL_TIGHTNESS
            return RegimeState.LOOSE

        if all(self._squeeze_buffer):
            return RegimeState.SQUEEZE
        if all(self._structural_buffer):
            return RegimeState.STRUCTURAL_TIGHTNESS
        if score >= self.config.regime_entry_cyclical and evidence_count >= 1:
            return RegimeState.CYCLICAL_TIGHTNESS
        return RegimeState.LOOSE
