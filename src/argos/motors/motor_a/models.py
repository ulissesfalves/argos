"""Contracts and enums for Motor A."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum

from argos.core.types import CalendarFrequency


class ScarcityDirection(str, Enum):
    HIGHER_IS_SCARCER = "higher_is_scarcer"
    LOWER_IS_SCARCER = "lower_is_scarcer"


class RegimeState(str, Enum):
    LOOSE = "folga"
    CYCLICAL_TIGHTNESS = "aperto_ciclico"
    STRUCTURAL_TIGHTNESS = "aperto_estrutural"
    SQUEEZE = "squeeze"


@dataclass(frozen=True)
class MotorAFeatureSpec:
    name: str
    source_metric: str
    weight: float
    direction: ScarcityDirection
    frequency: CalendarFrequency
    group: str
    reliability_weight: float = 1.0
    is_relief: bool = False
    evidence_threshold: float = 0.65
    min_history: int = 5


@dataclass(frozen=True)
class MotorAConfig:
    long_alpha: float = 0.80
    short_window: int = 8
    decay_half_life: int = 12
    regime_entry_cyclical: float = 0.55
    regime_exit_cyclical: float = 0.45
    regime_entry_structural: float = 0.70
    regime_exit_structural: float = 0.60
    regime_entry_squeeze: float = 0.88
    regime_exit_squeeze: float = 0.80
    min_positive_evidence: int = 3
    min_squeeze_evidence: int = 2
    persistence_observations: int = 2
    squeeze_required_groups: tuple[str, ...] = ("inventory", "term")


@dataclass(frozen=True)
class FeatureNormalizationResult:
    name: str
    group: str
    decision_date: date
    raw_value: float
    long_score: float
    short_score: float
    blended_score: float
    reliability_weight: float
    signed_weight: float
    evidence_active: bool
    history_count: int


@dataclass(frozen=True)
class ScarcitySnapshot:
    commodity: str
    decision_date: date
    score: float
    regime: RegimeState
    evidence_count: int
    active_evidence_groups: tuple[str, ...]
    contributing_features: tuple[FeatureNormalizationResult, ...] = field(default_factory=tuple)
