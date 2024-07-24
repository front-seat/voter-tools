class VoterRegistrationError(Exception):
    """An error occurred while checking voter registration."""

    pass


class MultipleRecordsFoundError(VoterRegistrationError):
    """Multiple voters were found matching the given information."""

    pass
