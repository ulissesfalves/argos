"""Join policies for point-in-time safe calendar alignment."""

from __future__ import annotations

from argos.core.exceptions import IncompatibleCalendarError
from argos.core.types import CalendarFrequency, CarryRule

_ALLOWED_FORWARD_FILL = {
    CalendarFrequency.DAILY: {CalendarFrequency.WEEKLY, CalendarFrequency.MONTHLY, CalendarFrequency.QUARTERLY},
    CalendarFrequency.WEEKLY: {CalendarFrequency.MONTHLY, CalendarFrequency.QUARTERLY},
    CalendarFrequency.MONTHLY: {CalendarFrequency.QUARTERLY},
    CalendarFrequency.QUARTERLY: set(),
}


def validate_join(left_frequency: CalendarFrequency, right_frequency: CalendarFrequency, carry_rule: CarryRule) -> None:
    """Validate whether a temporal join is allowed."""
    if carry_rule == CarryRule.EXACT and left_frequency != right_frequency:
        raise IncompatibleCalendarError("exact join requires identical calendar frequencies")
    if carry_rule == CarryRule.FORWARD_FILL:
        allowed = _ALLOWED_FORWARD_FILL.get(left_frequency, set())
        if right_frequency not in allowed and left_frequency != right_frequency:
            raise IncompatibleCalendarError("forward_fill is not allowed for the requested frequencies")
