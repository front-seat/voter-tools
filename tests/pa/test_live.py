import datetime
import os
import pathlib
import unittest

from PIL import Image

from . import client as c

PA_OVR_LIVE_TESTS = os.getenv("PA_OVR_LIVE_TESTS") == "True"
"""If True, we will actually submit real data to the PA staging server."""


def _api_key() -> str:
    API_KEY = os.environ.get("PA_OVR_API_KEY")
    if not API_KEY:
        raise ValueError("PA_OVR_API_KEY environment variable must be set.")
    return API_KEY


@unittest.skipUnless(PA_OVR_LIVE_TESTS, "PA_OVR_LIVE_TESTS not enabled")
class LiveApplicationTestCase(unittest.TestCase):
    def test_simple(self):
        """Test submitting the simplest possible application."""
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
            drivers_license="12345678",
        )
        application = c.VoterApplication(record=record)

        client = c.PAClient.staging(_api_key())
        response = client.set_application(application)
        self.assertIsNone(response.error_code)

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

        client = c.PAClient.staging(_api_key())
        response = client.set_application(application)
        self.assertIsNone(response.error_code)

    TEST_SIGNATURE_PATH = pathlib.Path(__file__).parent / "test_signature.png"

    @unittest.skip("""
        XXX I can see that the image data included in our POST request
        exactly matches the API spec, but the staging endpoint
        times out and never responds when I send it. A bug on PA's part?
    """)
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

        client = c.PAClient.staging(_api_key())
        response = client.set_application(application)
        self.assertIsNone(response.error_code)
