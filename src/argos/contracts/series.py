"""Canonical series contracts."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from argos.contracts.temporal import TemporalMetadata
from argos.core.types import CalendarFrequency


class CanonicalPoint(BaseModel):
    """Standardized observation in the canonical data layer."""

    model_config = ConfigDict(frozen=True)

    entity_id: str = Field(min_length=1)
    metric: str = Field(min_length=1)
    value: float
    unit: Optional[str] = None
    currency: Optional[str] = None
    frequency: CalendarFrequency
    temporal: TemporalMetadata


class FeaturePoint(BaseModel):
    """Materialized feature aligned to the decision calendar."""

    model_config = ConfigDict(frozen=True)

    entity_id: str = Field(min_length=1)
    feature_name: str = Field(min_length=1)
    feature_value: float
    frequency: CalendarFrequency
    temporal: TemporalMetadata
    source_metric: str = Field(min_length=1)
