"""Motor A - structural scarcity."""

from argos.motors.motor_a.engine import MotorAEngine
from argos.motors.motor_a.models import (
    FeatureNormalizationResult,
    MotorAConfig,
    MotorAFeatureSpec,
    RegimeState,
    ScarcityDirection,
    ScarcitySnapshot,
)

__all__ = [
    "FeatureNormalizationResult",
    "MotorAConfig",
    "MotorAEngine",
    "MotorAFeatureSpec",
    "RegimeState",
    "ScarcityDirection",
    "ScarcitySnapshot",
]
