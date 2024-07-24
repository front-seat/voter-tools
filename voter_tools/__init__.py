"""Tools for working with voter registration data."""

from .ga import GeorgiaVoterRegistrationTool
from .mi import MichiganVoterRegistrationTool
from .pa import PennsylvaniaVoterRegistrationTool
from .tool import VoterRegistrationTool
from .wi import WisconsinVoterRegistrationTool
from .zipcodes import get_state

_REGISTRATION_TOOLS: dict[str, type[VoterRegistrationTool]] = {
    "GA": GeorgiaVoterRegistrationTool,
    "MI": MichiganVoterRegistrationTool,
    "PA": PennsylvaniaVoterRegistrationTool,
    "WI": WisconsinVoterRegistrationTool,
}


def get_registration_tool(
    *, zipcode: str | None = None, state: str | None = None
) -> VoterRegistrationTool | None:
    """Return a voter registration tool for the given ZIP code or state."""
    if state is None:
        if zipcode is None:
            raise ValueError("Must provide either a ZIP code or state")
        state = get_state(zipcode)

    if state is None:
        return None

    tool_class = _REGISTRATION_TOOLS.get(state)
    return tool_class() if tool_class else None
