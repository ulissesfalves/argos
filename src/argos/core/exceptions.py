"""Domain exceptions for ARGOS."""


class ArgosError(Exception):
    """Base exception for the project."""


class TemporalValidationError(ArgosError):
    """Raised when temporal metadata is invalid or incomplete."""


class IncompatibleCalendarError(ArgosError):
    """Raised when datasets cannot be joined without an explicit carry rule."""
