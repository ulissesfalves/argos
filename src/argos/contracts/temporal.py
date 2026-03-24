"""Temporal contracts used across ARGOS."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator

from argos.core.exceptions import TemporalValidationError


class TemporalMetadata(BaseModel):
    """Point-in-time metadata required for every series and feature."""

    model_config = ConfigDict(frozen=True)

    observation_date: date
    publication_date: Optional[date] = None
    availability_date: date
    effective_date: Optional[date] = None

    @model_validator(mode="after")
    def validate_temporal_order(self) -> "TemporalMetadata":
        if self.publication_date and self.publication_date < self.observation_date:
            raise TemporalValidationError(
                "publication_date cannot be earlier than observation_date"
            )
        if self.availability_date < self.observation_date:
            raise TemporalValidationError(
                "availability_date cannot be earlier than observation_date"
            )
        if self.publication_date and self.availability_date < self.publication_date:
            raise TemporalValidationError(
                "availability_date cannot be earlier than publication_date"
            )
        if self.effective_date and self.effective_date < self.availability_date:
            raise TemporalValidationError(
                "effective_date cannot be earlier than availability_date"
            )
        return self
