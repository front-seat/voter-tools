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


class UnparsableResponseError(APIError):
    """The PA API returned a response that could not be parsed."""

    pass


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
        message = f"Validation errors on {locs}"
        if len(self._errors) == 1:
            message += f": {self._errors[0].msg}"
        super().__init__(message)

    def errors(self) -> tuple[APIErrorDetails, ...]:
        """Return the validation errors."""
        return self._errors

    def json(self) -> list:
        """Return the validation errors as a JSON-serializable dictionary."""
        return [error.model_dump(mode="json") for error in self._errors]

    def merge(self, other: "APIValidationError") -> "APIValidationError":
        """Merge this error with another and return the result."""
        # NOTE: This is different than python's list.append() method since
        # it returns a new object rather than modifying the existing one.
        return APIValidationError(self._errors + other._errors)

    @classmethod
    def simple(cls, field: str, type: str, msg: str) -> "APIValidationError":
        """Create a simple validation error with a single error."""
        return cls([APIErrorDetails(type=type, msg=msg, loc=(field,))])

    @classmethod
    def unexpected(cls, code: str | None = None) -> "APIValidationError":
        """Create a generic validation error for unexpected error codes."""
        code_f = f" ({code})" if code is not None else "(empty response)"
        details = APIErrorDetails(
            type="unexpected",
            msg=f"Unexpected error. Please correct your form and try again. {code_f}",
            loc=(),
        )
        return cls([details])


# -----------------------------------------------------------------------------
# Mapping of well-known API error codes to error behaviors
# -----------------------------------------------------------------------------

# The intent of all this code is to make it easy to map the weird error codes
# that the PA API returns into either:
#
# 1. A handful of special purpose exceptions (like InvalidAccessKeyError)
# 2. A validation error that looks very similar to a pydantic ValidationError


def merge_errors(errors: t.Iterable[APIError]) -> APIError | None:
    """
    Merge multiple errors into a single error.

    If no errors are provided, None is returned.

    If all errors derive from APIValidationError, they are merged into a single
    APIValidationError, which is returned. Otherwise, the first
    non-APIValidationError is returned.
    """
    accumulated: APIValidationError | None = None
    for error in errors:
        if not isinstance(error, APIValidationError):
            return error
        if accumulated is None:
            accumulated = error
        else:
            accumulated = accumulated.merge(error)
    return accumulated


def build_error_for_codes(codes: tuple[str, ...]) -> APIError | None:
    """
    Return the single most appropriate error for a collection of PA API codes.

    If no codes are provided, None is returned.
    """
    errors: list[APIError] = []
    for code in codes:
        error = ERROR_MAP.get(code.lower())
        if error is None:
            error = APIValidationError.unexpected(code)
        errors.append(error)
    return merge_errors(errors)


# A collection of mappings from known API error codes to error behaviors.
#
# We have two kinds of "behaviors": APIError classes and validation errors.
#
# APIErrors generally get directly raised when they are encountered.
#
# Validation errors mean that the API request succeeded, but the voter
# registration data was invalid in some way.
#
# Note that *most* of these, particularly the validation errors, should
# never happen in practice. That's because our own validation code should catch
# them *before* we ever make a request to the PA API. But we include them here
# just in case.
#
# A handful of validations *are* genuinely possible. For instance, only
# the API back-end knows how to validate a driver's license number, so we
# expect this *may* be returned by the API.
#
# It's worth noting that a handful of these errors are repeated. For instance,
# there are several different errors that all amount to "you didn't select
# a valid `political_party`.". Some errors are ambiguous or may be re-used
# for multiple fields. It's a mess, folks! So be it.
ERROR_MAP: dict[str, APIError] = {
    "vr_wapi_invalidaccesskey": InvalidAccessKeyError(),
    "vr_wapi_invalidaction": ProgrammingError("Action not found."),
    "vr_wapi_invalidapibatch": ProgrammingError("Batch value is invalid."),
    "vr_wapi_invalidovrcounty": ProgrammingError(
        "Computed `county` field was invalid."
    ),
    "vr_wapi_invalidovrdl": APIValidationError.simple(
        "drivers_license", "invalid", "Invalid driver's license."
    ),
    "vr_wapi_invalidovrdlformat": APIValidationError.simple(
        "drivers_license", "invalid", "Invalid driver's license format."
    ),
    "vr_wapi_invalidovrdob": APIValidationError.simple(
        "birth_date", "invalid", "Invalid date of birth."
    ),
    "vr_wapi_invalidovremail": APIValidationError.simple(
        "email", "invalid", "Invalid email address."
    ),
    "vr_wapi_invalidovrmailingzipcode": APIValidationError.simple(
        "mailing_zipcode", "invalid", "Please enter a valid 5 or 9-digit ZIP code."
    ),
    "vr_wapi_invalidovrphone": APIValidationError.simple(
        "phone_number", "invalid", "Invalid phone number."
    ),
    "vr_wapi_invalidovrpreviouscounty": APIValidationError.simple(
        "previous_county", "invalid", "Unknown county."
    ),
    "vr_wapi_invalidovrpreviouszipcode": APIValidationError.simple(
        "previous_zip5", "invalid", "Please enter a valid 5-digit ZIP code."
    ),
    "vr_wapi_invalidovrssnformat": APIValidationError.simple(
        "ssn4", "invalid", "Please enter the last four digits of your SSN."
    ),
    "vr_wapi_invalidovrzipcode": APIValidationError.simple(
        "zip5", "invalid", "Please enter a valid 5-digit ZIP code."
    ),
    "vr_wapi_invalidpreviousregyear": APIValidationError.simple(
        "previous_year", "invalid", "Please enter a valid year."
    ),
    "vr_wapi_invalidreason": ProgrammingError("Invalid registration_kind provided."),
    "vr_wapi_missingaccesskey": ProgrammingError(
        "The PA client did not supply an API key."
    ),
    # TODO DAVE:
    # ASK PA API TEAM: this error appears to apply to both `address`
    # *and* to `mailing_address`. Is there a way to distinguish?
    "vr_wapi_missingaddress": APIValidationError.simple(
        "mailing_address", "missing", "A complete address is required."
    ),
    "vr_wapi_missingapiaction": ProgrammingError(
        "The PA client did not supply an `action` value."
    ),
    "vr_wapi_missingcounty": ProgrammingError(
        "The PA client did not supply a `county` value in a `get_municipalities` call.",
    ),
    "vr_wapi_missinglanguage": ProgrammingError(
        "The PA client did not supply a `language` value."
    ),
    "vr_wapi_missingovrassistancedeclaration": APIValidationError.simple(
        "assistant_declaration",
        "missing",
        "Please indicate assistance was provided with the completion of this form.",
    ),
    "vr_wapi_missingovrcity": APIValidationError.simple(
        "city", "missing", "Please enter a valid city."
    ),
    "vr_wapi_missingovrcounty": ProgrammingError(
        "Computed `county` field was missing."
    ),
    "vr_wapi_missingovrdeclaration1": APIValidationError.simple(
        "confirm_declaration",
        "missing",
        "Please confirm you have read and agree to the terms.",
    ),
    "vr_wapi_missingovrdl": APIValidationError.simple(
        "drivers_license",
        "missing",
        "Please supply a valid PA driver's license or PennDOT ID card number.",
    ),
    "vr_wapi_missingovrfirstname": APIValidationError.simple(
        "first_name", "missing", "Your first name is required."
    ),
    "vr_wapi_missingovrinterpreterlang": APIValidationError.simple(
        "interpreter_language", "missing", "Required if interpreter is checked."
    ),
    "vr_wapi_missingovrisageover18": APIValidationError.simple(
        "will_be_18", "missing", "You must provide a response."
    ),
    "vr_wapi_missingovrisuscitizen": APIValidationError.simple(
        "is_us_citizen", "missing", "You must provide a response."
    ),
    "vr_wapi_missingovrlastname": APIValidationError.simple(
        "last_name", "missing", "Your last name is required."
    ),
    "vr_wapi_missingovrotherparty": APIValidationError.simple(
        "other_party", "missing", "You must write-in a party of 'other' is selected."
    ),
    "vr_wapi_missingovrpoliticalparty": APIValidationError.simple(
        "political_party", "missing", "Please select a political party."
    ),
    "vr_wapi_missingovrpreviousaddress": APIValidationError.simple(
        "previous_address", "missing", "Required for an address change application."
    ),
    "vr_wapi_missingovrpreviouscity": APIValidationError.simple(
        "previous_city", "missing", "Required for an address change application."
    ),
    "vr_wapi_missingovrpreviousfirstname": APIValidationError.simple(
        "previous_first_name", "missing", "Required for a name change application."
    ),
    "vr_wapi_missingovrpreviouslastname": APIValidationError.simple(
        "previous_last_name", "missing", "Required for a name change application."
    ),
    "vr_wapi_missingovrpreviouszipcode": APIValidationError.simple(
        "previous_zip5", "missing", "Required for an address change application."
    ),
    "vr_wapi_missingovrssndl": APIValidationError.simple(
        "ssn4", "missing", "Please supply the last four digits of your SSN."
    ),
    "vr_wapi_missingovrstreetaddress": APIValidationError.simple(
        "address", "missing", "Please enter your street address."
    ),
    "vr_wapi_missingovrtypeofassistance": APIValidationError.simple(
        "assistance_type", "missing", "Please select the type of assistance required."
    ),
    "vr_wapi_missingovrzipcode": APIValidationError.simple(
        "zip5", "missing", "Please enter your 5-digit ZIP code."
    ),
    # CONSIDER DAVE: maybe this is a ProgrammingError?
    "vr_wapi_missingreason": APIValidationError.simple(
        "registration_kind",
        "missing",
        "Please select at least one reason for change applications.",
    ),
    "vr_wapi_penndotservicedown": ServiceUnavailableError(
        "The PennDOT service is currently down. Please try again later.",
    ),
    "vr_wapi_requesterror": ProgrammingError(
        "The API request was invalid for unknown reasons."
    ),
    "vr_wapi_serviceerror": ServiceUnavailableError(
        "The PA signature service is currently down. PLease try again later.",
    ),
    "vr_wapi_systemerror": ServiceUnavailableError(
        "The PA voter registration service is currently down. Please try again later.",
    ),
    "vr_wapi_invalidovrassistedpersonphone": APIValidationError.simple(
        "assistant_phone", "invalid", "Please enter a valid phone number."
    ),
    "vr_wapi_invalidovrsecondemail": APIValidationError.simple(
        "alternate_email", "invalid", "Please enter a valid email address."
    ),
    "vr_wapi_invalidsignaturestring": ServiceUnavailableError(
        "The signature upload was not successful. Please try again.",
    ),
    "vr_wapi_invalidsignaturetype": ProgrammingError(
        "Invalid signature file type was sent to the API endpoint."
    ),
    "vr_wapi_invalidsignaturesize": ProgrammingError(
        "Invalid signature file size of >= 5MB was sent to the API endpoint.",
    ),
    "vr_wapi_invalidsignaturedimension": ProgrammingError(
        "A signature image of other than 180 x 60 pixels was sent to the API endpoint.",
    ),
    "vr_wapi_invalidsignaturecontrast": ProgrammingError(
        "The signature has invalid contrast."
    ),
    "vr_wapi_missingovrparty": APIValidationError.simple(
        "political_party", "missing", "Please select a political party."
    ),
    "vr_wapi_invalidovrpoliticalparty": APIValidationError.simple(
        "political_party", "missing", "Please select a political party."
    ),
    "vr_wapi_invalidsignatureresolution": ProgrammingError(
        "Invalid signature resolution of other than 96dpi was sent to the endpoint.",
    ),
    "vr_wapi_missingovrmailinballotaddr": APIValidationError.simple(
        "mail_in_address", "missing", "Please enter an address."
    ),
    "vr_wapi_missingovrmailincity": APIValidationError.simple(
        "mail_in_city", "missing", "Please enter a city."
    ),
    "vr_wapi_missingovrmailinstate": APIValidationError.simple(
        "mail_in_state", "missing", "Please enter a state."
    ),
    "vr_wapi_invalidovrmailinzipcode": APIValidationError.simple(
        "mail_in_zipcode", "missing", "Please enter a 5 or 9-digit ZIP code."
    ),
    "vr_wapi_missingovrmailinlivedsince": APIValidationError.simple(
        "mail_in_lived_since", "missing", "Please choose a date."
    ),
    "vr_wapi_missingovrmailindeclaration": APIValidationError.simple(
        "mail_in_declaration",
        "missing",
        "Please indicate you have read and agreed to the terms.",
    ),
    "vr_wapi_mailinnoteligible": APIValidationError.simple(
        "is_mail_in", "invalid", "This application is not mail-in eligible."
    ),
    "vr_wapi_invalidistransferpermanent": APIValidationError.simple(
        "transfer_permanent_status", "invalid", "This is not a valid value."
    ),
}
