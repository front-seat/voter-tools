import typing as t

import pydantic as p

from ..errors import APIError


class ProgrammingError(APIError):
    """Raised when a something is broken with this library's code."""

    pass


class InvalidAccessKeyError(APIError):
    """
    Raised when an invalid access key is provided.

    The key may be invalid, or it may not have the necessary permissions.

    For instance, a read-only key may not be used to submit registrations.
    """

    _default_message: t.ClassVar[str] = """

    Invalid API access key. It may be *entirely* invalid, or it may simply not
    have the permissions necessary to fulfill the request. For instance, the
    PA SOS hands out read-only keys that can't be used to submit registrations,
    and also hands out keys that cannot be used for mail-in applications.
"""

    def __init__(self, message: str | None = None) -> None:
        """Initialize the error with the given message."""
        super().__init__(message or self._default_message)


class TimeoutError(APIError):
    """Raised when a request to the server times out."""

    pass


class ServiceUnavailableError(APIError):
    """Raised when the service is currently unavailable."""

    pass


class APIErrorDetails(p.BaseModel, frozen=True):
    """Details meant to mimic pydantic's internal ErrorDetails."""

    type: str
    msg: str
    loc: tuple[str, ...]


class APIValidationError(APIError):
    """Raised when the pennsylvania API returns one or more validation errors."""

    # This is intended to look similar to pydantic's ValidationError,
    # but building Pydantic ValidationErrors directly is somewhat annoying
    # (see

    _errors: tuple[APIErrorDetails, ...]

    def __init__(self, errors: t.Iterable[APIErrorDetails]) -> None:
        """Initialize the error with the given errors."""
        self._errors = tuple(errors)
        locs = ", ".join(str(error.loc) for error in errors)
        super().__init__(f"Validation error on {locs}")

    def errors(self) -> list[APIErrorDetails]:
        """Return the validation errors."""
        return list(self._errors)

    def json(self) -> list:
        """Return the validation errors as a JSON-serializable dictionary."""
        return [error.model_dump() for error in self._errors]

    def append(self, other: "APIValidationError") -> "APIValidationError":
        """Merge this error with another."""
        return APIValidationError(self._errors + other._errors)

    def extend(self, others: t.Iterable["APIValidationError"]) -> "APIValidationError":
        """Merge this error with others."""
        return APIValidationError(
            self._errors + tuple(error for other in others for error in other._errors)
        )
