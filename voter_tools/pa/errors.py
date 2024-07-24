import typing as t


class APIError(Exception):
    """Base class for all API errors."""

    pass


class InvalidAccessKeyError(APIError):
    """
    Raised when an invalid access key is provided.

    The key may be invalid, or it may not have the necessary permissions.

    For instance, a read-only key may not be used to submit registrations.
    """

    _message: t.ClassVar[str] = """

    Invalid API access key. It may be *entirely* invalid, or it may simply not
    have the permissions necessary to fulfill the request. For instance, the
    PA SOS hands out read-only keys that can't be used to submit registrations,
    and also hands out keys that cannot be used for mail-in applications.
"""

    def __init__(self, message: str = _message) -> None:
        """Initialize the error with the given message."""
        super().__init__(message)


class UnexpectedResponseError(APIError):
    """Raised when an unexpected response is received from the server."""

    pass


class InvalidRegistrationError(APIError):
    """Raised when an invalid voter registration is provided."""

    pass


class InvalidDLError(APIError):
    """Raised when an invalid driver's license is provided."""

    pass


class InvalidSignatureError(APIError):
    """Raised when an invalid signature is provided."""

    pass


_CODE_TO_ERROR: t.Mapping[str, t.Type[APIError]] = {
    "VR_WAPI_InvalidAccessKey": InvalidAccessKeyError,
    "VR_WAPI_InvalidOVRDL": InvalidDLError,
    "VR_WAPI_Invalidsignaturestring": InvalidSignatureError,
    "VR_WAPI_Invalidsignaturetype": InvalidSignatureError,
    "VR_WAPI_Invalidsignaturesize": InvalidSignatureError,
    "VR_WAPI_Invalidsignaturedimension": InvalidSignatureError,
    "VR_WAPI_Invalidsignaturecontrast": InvalidSignatureError,
    "VR_WAPI_Invalidsignatureresolution": InvalidSignatureError,
}


def get_error_class(
    code: str, default: t.Type[APIError] = APIError
) -> t.Type[APIError]:
    """Return the error class for the given error code."""
    return _CODE_TO_ERROR.get(code, default)
