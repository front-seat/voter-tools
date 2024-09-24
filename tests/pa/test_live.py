import datetime
import os
import pathlib
import unittest

from PIL import Image

from voter_tools.pa import client as c
from voter_tools.pa import errors as pa_errors

PA_API_LIVE_TESTS = os.getenv("PA_API_LIVE_TESTS") == "True"
"""If True, we will actually submit real data to the PA staging server."""


def _pa_api_key() -> str:
    API_KEY = os.environ.get("PA_API_KEY")
    if not API_KEY:
        raise ValueError("PA_API_KEY environment variable must be set.")
    return API_KEY


@unittest.skipUnless(PA_API_LIVE_TESTS, "PA_API_LIVE_TESTS not enabled")
class LiveApplicationTestCase(unittest.TestCase):
    def test_simple(self):
        """Test submitting the simplest possible application."""
        record = c.VoterApplicationRecord(
            first_name="Twelve",
            last_name="Penndot",
            is_us_citizen=True,
            will_be_18=True,
            political_party=c.PoliticalPartyChoice.DEMOCRATIC,
            gender=c.GenderChoice.MALE,
            email="test.applicant1@example.com",
            birth_date=datetime.date(1994, 2, 20),
            registration_kind=c.RegistrationKind.NEW,
            confirm_declaration=True,
            address="123 Main St",
            city="Philadelphia",
            zip5="19127",
            drivers_license="99001586",
        )
        application = c.VoterApplication(record=record)

        client = c.PennsylvaniaAPIClient.staging(_pa_api_key(), timeout=100.0)
        response = client.set_application(application)
        self.assertFalse(response.has_error())

    def test_invalid_dl(self):
        """Test submitting an application with an invalid DL format."""
        record = c.VoterApplicationRecord(
            first_name="Test",
            last_name="Applicant1",
            is_us_citizen=True,
            will_be_18=True,
            political_party=c.PoliticalPartyChoice.DEMOCRATIC,
            gender=c.GenderChoice.MALE,
            email="test.applicant1@example.com",
            birth_date=datetime.date(1980, 1, 1),
            registration_kind=c.RegistrationKind.NEW,
            confirm_declaration=True,
            address="123 Main St",
            city="Philadelphia",
            zip5="19127",
            drivers_license="DEADBEEF",
        )
        application = c.VoterApplication(record=record)

        # from voter_tools.pa.debug import CurlDebugTransport
        # transport = CurlDebugTransport(sys.stdout)

        client = c.PennsylvaniaAPIClient.staging(
            _pa_api_key(),
            timeout=100.0,  # _transport=transport
        )
        with self.assertRaises(pa_errors.APIValidationError) as ctx:
            _ = client.set_application(application)
        errors = ctx.exception.errors()
        # print("ERRORS ARE: ", errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].loc, ("drivers_license",))

    def test_ssn4(self):
        """Test submitting an application with SSN4, not a driver's license."""
        record = c.VoterApplicationRecord(
            first_name="Test",
            last_name="Applicant1",
            is_us_citizen=True,
            will_be_18=True,
            political_party=c.PoliticalPartyChoice.DEMOCRATIC,
            gender=c.GenderChoice.MALE,
            email="test.applicant1@example.com",
            birth_date=datetime.date(1980, 1, 1),
            registration_kind=c.RegistrationKind.NEW,
            confirm_declaration=True,
            address="123 Main St",
            city="Philadelphia",
            zip5="19127",
            ssn4="1234",
        )
        application = c.VoterApplication(record=record)

        client = c.PennsylvaniaAPIClient.staging(_pa_api_key(), timeout=100.0)
        response = client.set_application(application)
        self.assertFalse(response.has_error())

    TEST_SIGNATURE_PATH = pathlib.Path(__file__).parent / "test_signature.png"

    def test_signature_image(self):
        """Test submitting an application with a signature image."""
        signature_img = Image.open(self.TEST_SIGNATURE_PATH)
        record = c.VoterApplicationRecord(
            first_name="Test",
            last_name="Applicant1",
            is_us_citizen=True,
            will_be_18=True,
            political_party=c.PoliticalPartyChoice.DEMOCRATIC,
            gender=c.GenderChoice.MALE,
            email="test.applicant1@example.com",
            birth_date=datetime.date(1980, 1, 1),
            registration_kind=c.RegistrationKind.NEW,
            confirm_declaration=True,
            address="123 Main St",
            city="Philadelphia",
            zip5="19127",
            signature=c.validate_signature_image(signature_img),
        )
        application = c.VoterApplication(record=record)

        # According to folks @ PA SOS, it can take up to 80 seconds for the
        # staging endpoint to respond when a signature is uploaded.
        client = c.PennsylvaniaAPIClient.staging(_pa_api_key(), timeout=100.0)
        response = client.set_application(application)
        self.assertFalse(response.has_error())
