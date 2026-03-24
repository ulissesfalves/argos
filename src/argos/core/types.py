"""Core enums and typed aliases."""

from __future__ import annotations

from enum import Enum


class CalendarFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class CarryRule(str, Enum):
    EXACT = "exact"
    FORWARD_FILL = "forward_fill"
