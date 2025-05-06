import datetime
import io
import pathlib
from unittest import TestCase

import httpx
from PIL import Image

from voter_tools.pa import client as c
from voter_tools.pa.errors import (
    APIValidationError,
    InvalidAccessKeyError,
    UnparsableResponseError,
)


class PAResponseDateTestCase(TestCase):
    def test_parse_str_valid(self):
        date_str = "01/02/2023"
        expected = datetime.date(year=2023, month=1, day=2)
        parsed = c.parse_response_date(date_str)
        self.assertEqual(parsed, expected)

    def test_parse_date_valid(self):
        expected = datetime.date(year=2023, month=1, day=2)
        parsed = c.parse_response_date(expected)
        self.assertEqual(parsed, expected)

    def test_parse_str_invalid(self):
        with self.assertRaises(ValueError):
            _ = c.parse_response_date("burrito")

    def test_serialize(self):
        date = datetime.date(year=2023, month=1, day=2)
        expected = "01/02/2023"
        serialized = c.serialize_response_date(date)
        self.assertEqual(serialized, expected)


class PAResponseDateTimeTestCase(TestCase):
    def test_parse_str_valid(self):
        dt_str = "Jan 2 2024  1:23AM"
        expected = datetime.datetime(year=2024, month=1, day=2, hour=1, minute=23)
        parsed = c.parse_response_dt(dt_str)
        self.assertEqual(parsed, expected)

    def test_parse_str_also_valid(self):
        dt_str = "Jan 02 2024  01:23AM"
        expected = datetime.datetime(year=2024, month=1, day=2, hour=1, minute=23)
        parsed = c.parse_response_dt(dt_str)
        self.assertEqual(parsed, expected)

    def test_parse_dt_valid(self):
        expected = datetime.datetime(year=2024, month=1, day=2, hour=1, minute=23)
        parsed = c.parse_response_dt(expected)
        self.assertEqual(parsed, expected)

    def test_parse_str_invalid(self):
        with self.assertRaises(ValueError):
            _ = c.parse_response_dt("burrito")

    def test_serialize(self):
        dt = datetime.datetime(year=2024, month=1, day=2, hour=1, minute=23)
        expected = "Jan 02 2024  01:23AM"
        serialized = c.serialize_response_dt(dt)
        self.assertEqual(serialized, expected)


class PARequestDateFormatTestCase(TestCase):
    def test_parse_str_valid(self):
        date_str = "2023-01-02"
        expected = datetime.date(year=2023, month=1, day=2)
        parsed = c.parse_request_date(date_str)
        self.assertEqual(parsed, expected)

    def test_parse_str_also_valid(self):
        date_str = "2023-1-2"
        expected = datetime.date(year=2023, month=1, day=2)
        parsed = c.parse_request_date(date_str)
        self.assertEqual(parsed, expected)

    def test_parse_date_valid(self):
        expected = datetime.date(year=2023, month=1, day=2)
        parsed = c.parse_request_date(expected)
        self.assertEqual(parsed, expected)

    def test_parse_str_invalid(self):
        with self.assertRaises(ValueError):
            _ = c.parse_request_date("burrito")

    def test_serialize(self):
        date = datetime.date(year=2023, month=1, day=2)
        expected = "2023-01-02"
        serialized = c.serialize_request_date(date)
        self.assertEqual(serialized, expected)


class PATimeFormatTestCase(TestCase):
    def test_parse_str_valid(self):
        time_str = "01:23 PM"
        expected = datetime.time(hour=13, minute=23)
        parsed = c.parse_time(time_str)
        self.assertEqual(parsed, expected)

    def test_parse_str_also_valid(self):
        time_str = "1:23 PM"
        expected = datetime.time(hour=13, minute=23)
        parsed = c.parse_time(time_str)
        self.assertEqual(parsed, expected)

    def test_parse_time_valid(self):
        expected = datetime.time(hour=13, minute=23)
        parsed = c.parse_time(expected)
        self.assertEqual(parsed, expected)

    def test_parse_str_invalid(self):
        with self.assertRaises(ValueError):
            _ = c.parse_time("burrito")

    def test_serialize(self):
        time = datetime.time(hour=13, minute=23)
        expected = "01:23 PM"
        serialized = c.serialize_time(time)
        self.assertEqual(serialized, expected)


class PhoneNumberTestCase(TestCase):
    def test_valid_1(self):
        number = "123-456-7890"
        expected = "123-456-7890"
        parsed = c.parse_phone_number(number)
        self.assertEqual(parsed, expected)

    def test_valid_2(self):
        number = "(206) 555-1212"
        expected = "206-555-1212"
        parsed = c.parse_phone_number(number)
        self.assertEqual(parsed, expected)

    def test_valid_3(self):
        number = "2065551212"
        expected = "206-555-1212"
        parsed = c.parse_phone_number(number)
        self.assertEqual(parsed, expected)

    def test_valid_4(self):
        number = "206.555.1212"
        expected = "206-555-1212"
        parsed = c.parse_phone_number(number)
        self.assertEqual(parsed, expected)

    def test_valid_5(self):
        number = "hello (206) good friend 555 how are 1212 you"
        expected = "206-555-1212"
        parsed = c.parse_phone_number(number)
        self.assertEqual(parsed, expected)

    def test_invalid_wrong_length(self):
        with self.assertRaises(ValueError):
            _ = c.parse_phone_number("206-555-121")

    def test_invalid_start_with_2(self):
        with self.assertRaises(ValueError):
            _ = c.parse_phone_number("2-206-555-1212")

    def test_valid_6(self):
        number = "1-206-555-1212"
        expected = "206-555-1212"
        parsed = c.parse_phone_number(number)
        self.assertEqual(parsed, expected)


class BitTestCase(TestCase):
    def test_valid_int_false(self):
        expected = False
        parsed = c.validate_bit(0)
        self.assertEqual(parsed, expected)

    def test_valid_int_true(self):
        expected = True
        parsed = c.validate_bit(1)
        self.assertEqual(parsed, expected)

    def test_valid_str_false(self):
        expected = False
        parsed = c.validate_bit("0")
        self.assertEqual(parsed, expected)

    def test_valid_str_true(self):
        expected = True
        parsed = c.validate_bit("1")
        self.assertEqual(parsed, expected)

    def test_valid_bool_false(self):
        expected = False
        parsed = c.validate_bit(False)
        self.assertEqual(parsed, expected)

    def test_valid_bool_true(self):
        expected = True
        parsed = c.validate_bit(True)
        self.assertEqual(parsed, expected)

    def test_invalid_int(self):
        with self.assertRaises(ValueError):
            _ = c.validate_bit(2)

    def test_invalid_str(self):
        with self.assertRaises(ValueError):
            _ = c.validate_bit("2")

    def test_invalid_bool(self):
        with self.assertRaises(ValueError):
            _ = c.validate_bit(None)  # type: ignore

    def test_serialize_false(self):
        expected = 0
        serialized = c.bit_serializer(False)
        self.assertEqual(serialized, expected)

    def test_serialize_true(self):
        expected = 1
        serialized = c.bit_serializer(True)
        self.assertEqual(serialized, expected)


class TrueBitTestCase(TestCase):
    def test_invalid_int_false(self):
        with self.assertRaises(ValueError):
            _ = c.validate_true_bit(0)

    def test_valid_int_true(self):
        expected = True
        parsed = c.validate_true_bit(1)
        self.assertEqual(parsed, expected)

    def test_invalid_str_false(self):
        with self.assertRaises(ValueError):
            _ = c.validate_true_bit("0")

    def test_valid_str_true(self):
        expected = True
        parsed = c.validate_true_bit("1")
        self.assertEqual(parsed, expected)

    def test_invalid_bool_false(self):
        with self.assertRaises(ValueError):
            _ = c.validate_true_bit(False)

    def test_valid_bool_true(self):
        expected = True
        parsed = c.validate_true_bit(True)
        self.assertEqual(parsed, expected)


class ImageTestCaseMixin:
    # Empty 1x1 transparent GIF
    EMPTY_GIF = (
        "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
    )
    TEST_IMG_PATH = pathlib.Path(__file__).parent / "test_img.png"
    TEST_IMG_URL_PATH = pathlib.Path(__file__).parent / "test_img_url.txt"


class ImageDataRoundtripTestCase(TestCase, ImageTestCaseMixin):
    def test_image_to_data_url_and_back(self):
        pil_image = Image.open(self.TEST_IMG_PATH)
        data_url = c.image_to_data_url(pil_image)
        re_image = c.data_url_to_image(data_url)
        self.assertEqual(pil_image.size, re_image.size)
        self.assertEqual(pil_image.mode, re_image.mode)
        self.assertEqual(pil_image.tobytes(), re_image.tobytes())


class DataURLToImageTestCase(TestCase, ImageTestCaseMixin):
    def test_invalid_1(self):
        with self.assertRaises(ValueError):
            _ = c.data_url_to_image("data:text/plain;base64,SGVsbG8sIFdvcmxkIQ==")

    def test_invalid_2(self):
        with self.assertRaises(ValueError):
            _ = c.data_url_to_image("nope")

    def test_invalid_3(self):
        with self.assertRaises(ValueError):
            _ = c.data_url_to_image("data:image/png;base917,SGVsbG8sIFdvcmxkIQ==")

    def test_invalid_4(self):
        with self.assertRaises(ValueError):
            _ = c.data_url_to_image("data:image/png;base64,whee==")


class ValidateSignatureImageTestCase(TestCase, ImageTestCaseMixin):
    def test_valid_str(self):
        with open(self.TEST_IMG_URL_PATH, "r") as f:
            data_url = f.read().strip()
        result = c.validate_signature_image(data_url)
        pil_image = c.data_url_to_image(result)
        self.assertEqual(pil_image.size, c.SIGNATURE_IMAGE_SIZE)

    def test_invalid_str(self):
        with self.assertRaises(ValueError):
            _ = c.validate_signature_image("nope")

    def test_valid_bytes(self):
        with open(self.TEST_IMG_PATH, "rb") as f:
            image_data = f.read()
        result = c.validate_signature_image(image_data)
        pil_image = c.data_url_to_image(result)
        self.assertEqual(pil_image.size, c.SIGNATURE_IMAGE_SIZE)

    def test_invalid_bytes(self):
        with self.assertRaises(ValueError):
            _ = c.validate_signature_image(b"nope")

    def test_valid_io(self):
        with open(self.TEST_IMG_PATH, "rb") as f:
            data = f.read()
        binary_io = io.BytesIO(data)
        result = c.validate_signature_image(binary_io)
        pil_image = c.data_url_to_image(result)
        self.assertEqual(pil_image.size, c.SIGNATURE_IMAGE_SIZE)

    def test_invalid_io(self):
        with self.assertRaises(ValueError):
            _ = c.validate_signature_image(io.BytesIO(b"nope"))

    def test_valid_pil_image(self):
        initial_image = Image.open(self.TEST_IMG_PATH)
        result = c.validate_signature_image(initial_image)
        pil_image = c.data_url_to_image(result)
        self.assertEqual(pil_image.size, c.SIGNATURE_IMAGE_SIZE)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            _ = c.validate_signature_image(None)  # type: ignore


class VoterEligibilityTestCase(TestCase):
    def test_age_validation(self):
        with self.assertRaises(ValueError):
            _ = c.VoterEligibility(is_us_citizen=True, will_be_18=False)  # type: ignore

    def test_citizenship_validation(self):
        with self.assertRaises(ValueError):
            _ = c.VoterEligibility(is_us_citizen=False, will_be_18=True)  # type: ignore

    def test_valid(self):
        try:
            _ = c.VoterEligibility(is_us_citizen=True, will_be_18=True)
        except ValueError:
            self.fail()


class VoterReasonTestCase(TestCase):
    def test_reason_validation_new_valid(self):
        try:
            _ = c.VoterReason(registration_kind=c.RegistrationKind.NEW)
        except ValueError:
            self.fail()

    def test_reason_validation_new_invalid(self):
        with self.assertRaises(ValueError):
            _ = c.VoterReason(
                registration_kind=c.RegistrationKind.NEW, is_name_change=True
            )
        with self.assertRaises(ValueError):
            _ = c.VoterReason(
                registration_kind=c.RegistrationKind.NEW, is_address_change=True
            )
        with self.assertRaises(ValueError):
            _ = c.VoterReason(
                registration_kind=c.RegistrationKind.NEW, is_party_change=True
            )

    def test_reason_validation_change_invalid(self):
        with self.assertRaises(ValueError):
            _ = c.VoterReason(registration_kind=c.RegistrationKind.CHANGE)

    def test_reason_validation_change_name_invalid(self):
        with self.assertRaises(ValueError):
            _ = c.VoterReason(
                registration_kind=c.RegistrationKind.CHANGE, is_name_change=True
            )
        with self.assertRaises(ValueError):
            _ = c.VoterReason(
                registration_kind=c.RegistrationKind.CHANGE,
                is_name_change=True,
                previous_last_name="Last",
                # missing first name
            )
        with self.assertRaises(ValueError):
            _ = c.VoterReason(
                registration_kind=c.RegistrationKind.CHANGE,
                is_name_change=True,
                # missing last name
                previous_first_name="First",
            )

    def test_reason_validation_change_name_valid(self):
        try:
            _ = c.VoterReason(
                registration_kind=c.RegistrationKind.CHANGE,
                is_name_change=True,
                previous_last_name="Doe",
                previous_first_name="John",
            )
        except ValueError:
            self.fail()

    def test_reason_validation_change_address_invalid(self):
        with self.assertRaises(ValueError):
            _ = c.VoterReason(
                registration_kind=c.RegistrationKind.CHANGE, is_address_change=True
            )
        with self.assertRaises(ValueError):
            _ = c.VoterReason(
                registration_kind=c.RegistrationKind.CHANGE,
                is_address_change=True,
                previous_address="123 Main St",
                previous_city="Springfield",
                previous_zip5="12345",
                # missing county
            )
        with self.assertRaises(ValueError):
            _ = c.VoterReason(
                registration_kind=c.RegistrationKind.CHANGE,
                is_address_change=True,
                previous_address="123 Main St",
                previous_city="Springfield",
                previous_county=c.CountyChoice.ADAMS,
                # missing zip5
            )
        with self.assertRaises(ValueError):
            _ = c.VoterReason(
                registration_kind=c.RegistrationKind.CHANGE,
                is_address_change=True,
                previous_address="123 Main St",
                previous_zip5="12345",
                previous_county=c.CountyChoice.ADAMS,
                # missing city
            )
        with self.assertRaises(ValueError):
            _ = c.VoterReason(
                registration_kind=c.RegistrationKind.CHANGE,
                is_address_change=True,
                previous_city="Springfield",
                previous_zip5="12345",
                previous_county=c.CountyChoice.ADAMS,
                # missing address
            )

    def test_reason_validation_change_address_valid(self):
        try:
            _ = c.VoterReason(
                registration_kind=c.RegistrationKind.CHANGE,
                is_address_change=True,
                previous_address="123 Main St",
                previous_city="Springfield",
                previous_zip5="12345",
                previous_county=c.CountyChoice.ADAMS,
            )
        except ValueError:
            self.fail()


class VoterAddressTestCase(TestCase):
    def test_valid_zip5(self):
        try:
            _ = c.VoterAddress(
                address="123 Main St",
                city="Springfield",
                zip5="17337",  # Adams County, PA
            )
        except ValueError:
            self.fail()

    def test_invalid_zip5(self):
        with self.assertRaises(ValueError):
            _ = c.VoterAddress(
                address="123 Main St",
                city="Springfield",
                zip5="98105",  # somewhere in Seattle!
            )

    def test_county(self):
        va = c.VoterAddress(
            address="123 Main St",
            city="Springfield",
            zip5="17337",  # Adams County, PA
        )
        self.assertEqual(va.county, c.CountyChoice.ADAMS)


class VoterMailingAddressTestCase(TestCase):
    def test_valid_not_required(self):
        try:
            _ = c.VoterMailingAddress(no_street_permanent=False)
        except ValueError:
            self.fail()

    def test_invalid_required(self):
        with self.assertRaises(ValueError):
            _ = c.VoterMailingAddress(no_street_permanent=True)

    def test_invalid_missing(self):
        with self.assertRaises(ValueError):
            _ = c.VoterMailingAddress(
                no_street_permanent=True,
                mailing_address="123 Main St",
                mailing_city="Springfield",
                mailing_state="IL",
                # missing mailing zipcode
            )
        with self.assertRaises(ValueError):
            _ = c.VoterMailingAddress(
                no_street_permanent=True,
                mailing_address="123 Main St",
                mailing_city="Springfield",
                mailing_zipcode="12345",
                # missing mailing state
            )
        with self.assertRaises(ValueError):
            _ = c.VoterMailingAddress(
                no_street_permanent=True,
                mailing_address="123 Main St",
                mailing_state="IL",
                mailing_zipcode="12345",
                # missing mailing city
            )
        with self.assertRaises(ValueError):
            _ = c.VoterMailingAddress(
                no_street_permanent=True,
                mailing_city="Springfield",
                mailing_state="IL",
                mailing_zipcode="12345",
                # missing mailing address
            )

    def test_valid_required(self):
        try:
            _ = c.VoterMailingAddress(
                no_street_permanent=True,
                mailing_address="123 Main St",
                mailing_city="Springfield",
                mailing_state="IL",
                mailing_zipcode="12345",
            )
        except ValueError:
            self.fail()


class VoterIdentificationTestCase(TestCase, ImageTestCaseMixin):
    def test_invalid_no_identification(self):
        with self.assertRaises(ValueError):
            _ = c.VoterIdentification()

    def test_valid_dl(self):
        try:
            _ = c.VoterIdentification(drivers_license="abcd1234")
        except ValueError:
            self.fail()

    def test_invalid_dl_with_more(self):
        with self.assertRaises(ValueError):
            _ = c.VoterIdentification(drivers_license="abcd1234", ssn4="9876")
        with self.assertRaises(ValueError):
            _ = c.VoterIdentification(
                drivers_license="abcd1234", signature=self.EMPTY_GIF
            )

    def test_valid_ssn4(self):
        try:
            _ = c.VoterIdentification(ssn4="9876")
        except ValueError:
            self.fail()

    def test_invalid_ssn4_with_more(self):
        with self.assertRaises(ValueError):
            _ = c.VoterIdentification(ssn4="9876", signature=self.EMPTY_GIF)

    def test_valid_signature(self):
        try:
            _ = c.VoterIdentification(signature=self.EMPTY_GIF)
        except ValueError:
            self.fail()


class VoterPoliticalPartyTestCase(TestCase):
    def test_valid(self):
        try:
            _ = c.VoterPoliticalParty(political_party=c.PoliticalPartyChoice.DEMOCRATIC)
        except ValueError:
            self.fail()

    def test_invalid_normal_other_detail(self):
        with self.assertRaises(ValueError):
            _ = c.VoterPoliticalParty(
                political_party=c.PoliticalPartyChoice.DEMOCRATIC,
                other_party="Space Ghost",
            )

    def test_invalid_other_no_detail(self):
        with self.assertRaises(ValueError):
            _ = c.VoterPoliticalParty(political_party=c.PoliticalPartyChoice.OTHER)

    def test_valid_other_with_detail(self):
        try:
            _ = c.VoterPoliticalParty(
                political_party=c.PoliticalPartyChoice.OTHER, other_party="Space Ghost"
            )
        except ValueError:
            self.fail()


class VoterAssistanceTestCase(TestCase):
    def test_valid(self):
        try:
            _ = c.VoterAssistance()
        except ValueError:
            self.fail()

    def test_invalid_no_details(self):
        with self.assertRaises(ValueError):
            _ = c.VoterAssistance(require_help_to_vote=True)
        with self.assertRaises(ValueError):
            _ = c.VoterAssistance(
                require_help_to_vote=True,
                assistance_type=c.AssistanceTypeChoice.HARD_OF_HEARING,
            )
        with self.assertRaises(ValueError):
            _ = c.VoterAssistance(
                require_help_to_vote=True, preferred_language="whatever"
            )

    def test_valid_assistance(self):
        try:
            _ = c.VoterAssistance(
                require_help_to_vote=True,
                assistance_type=c.AssistanceTypeChoice.LANGUAGE,
                preferred_language="Spanish",
            )
        except ValueError:
            self.fail()


class VoterHelpWithFormTestCase(TestCase):
    def test_valid(self):
        try:
            _ = c.VoterHelpWithForm()
        except ValueError:
            self.fail()

    def test_invalid_incomplete(self):
        with self.assertRaises(ValueError):
            _ = c.VoterHelpWithForm(
                # assistant_name="JR Bob Dobbs",
                assistant_address="123 Subgenius St",
                assistant_phone="206-555-1212",
                assistant_declaration=True,
            )
        with self.assertRaises(ValueError):
            _ = c.VoterHelpWithForm(
                assistant_name="JR Bob Dobbs",
                # assistant_address="123 Subgenius St",
                assistant_phone="206-555-1212",
                assistant_declaration=True,
            )
        with self.assertRaises(ValueError):
            _ = c.VoterHelpWithForm(
                assistant_name="JR Bob Dobbs",
                assistant_address="123 Subgenius St",
                # assistant_phone="206-555-1212",
                assistant_declaration=True,
            )
        with self.assertRaises(ValueError):
            _ = c.VoterHelpWithForm(
                assistant_name="JR Bob Dobbs",
                assistant_address="123 Subgenius St",
                assistant_phone="206-555-1212",
                # assistant_declaration=True
            )

    def test_valid_complete(self):
        try:
            _ = c.VoterHelpWithForm(
                assistant_name="JR Bob Dobbs",
                assistant_address="123 Subgenius St",
                assistant_phone="206-555-1212",
                assistant_declaration=True,
            )
        except ValueError:
            self.fail()


class VoterPollWorkerTestCase(TestCase):
    def test_valid(self):
        try:
            _ = c.VoterPollWorker()
        except ValueError:
            self.fail()

    def test_invalid_interpreter(self):
        with self.assertRaises(ValueError):
            _ = c.VoterPollWorker(be_interpreter=True)

    def test_valid_interpreter(self):
        try:
            _ = c.VoterPollWorker(be_interpreter=True, interpreter_language="Spanish")
        except ValueError:
            self.fail()


class VoterMailInBallotTestCase(TestCase):
    def test_valid(self):
        try:
            _ = c.VoterMailInBallot()
        except ValueError:
            self.fail()

    def test_invalid_incomplete(self):
        kwargs = {
            "mail_in_address_type": c.MailInAddressTypeChoice.RESIDENTIAL,
            "mail_in_address": "123 Main St",
            "mail_in_city": "Springfield",
            "mail_in_state": "IL",
            "mail_in_zipcode": "12345",
            "mail_in_lived_since": c.parse_request_date("2023-01-02"),
            "mail_in_declaration": True,
        }
        for key in kwargs:
            with self.assertRaises(ValueError):
                _ = c.VoterMailInBallot(
                    is_mail_in=True, **{k: v for k, v in kwargs.items() if k != key}
                )

    def test_valid_mailin(self):
        try:
            _ = c.VoterMailInBallot(
                is_mail_in=True,
                mail_in_address_type=c.MailInAddressTypeChoice.RESIDENTIAL,
                mail_in_address="123 Main St",
                mail_in_city="Springfield",
                mail_in_state="IL",
                mail_in_zipcode="12345",
                mail_in_lived_since=c.parse_request_date("2023-01-02"),
                mail_in_declaration=True,
            )
        except ValueError:
            self.fail()


class ClientTestCase(TestCase):
    def _valid_application(self) -> c.VoterApplication:
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
        return c.VoterApplication(record=record)

    def _client(self, handler):
        return c.PennsylvaniaAPIClient(
            api_url="http://test",
            api_key="test",
            _transport=httpx.MockTransport(handler),
        )

    def test_mock_success(self):
        """Test submitting the simplest possible application."""

        def handler(request: httpx.Request):
            xml_response = (
                """<RESPONSE><APPLICATIONID>good</APPLICATIONID></RESPONSE>"""
            )
            # Yes, it's super weird to set json=xml_response (a string!)
            # but, uh, that's what the PA API endpoint actually does.
            return httpx.Response(200, json=xml_response)

        application = self._valid_application()
        client = self._client(handler)
        response = client.set_application(application)
        self.assertFalse(response.has_error())

    def test_empty_failure(self):
        """Test behavior when API returns an empty response."""

        # Unfortunately, this *does* happen. Inexplicably, at least in
        # the sandbox.
        def handler(request: httpx.Request):
            xml_response = """<RESPONSE></RESPONSE>"""
            return httpx.Response(200, json=xml_response)

        application = self._valid_application()
        client = self._client(handler)
        with self.assertRaises(APIValidationError) as ctx:
            _ = client.set_application(application)
        self.assertEqual(ctx.exception.errors()[0].type, "unexpected")

    def test_empty_failure_do_not_raise(self):
        """Test behavior when API returns an empty response."""

        # Unfortunately, this *does* happen. Inexplicably, at least in
        # the sandbox.
        def handler(request: httpx.Request):
            xml_response = """<RESPONSE></RESPONSE>"""
            return httpx.Response(200, json=xml_response)

        application = self._valid_application()
        client = self._client(handler)
        response = client.set_application(application, raise_validation_error=False)
        self.assertTrue(response.has_error())

    def test_validation_error(self):
        """Test behavior when API returns a validation error response."""

        def handler(request: httpx.Request):
            xml_response = """
                <RESPONSE>
                    <APPLICATIONID>123</APPLICATIONID>
                    <ERROR>VR_WAPI_InvalidOVRDL</ERROR>
                </RESPONSE>
            """
            return httpx.Response(200, json=xml_response)

        application = self._valid_application()
        client = self._client(handler)
        with self.assertRaises(APIValidationError) as ctx:
            _ = client.set_application(application)
        self.assertEqual(ctx.exception.errors()[0].loc[0], "drivers_license")

    def test_validation_errors(self):
        """Test behavior when API returns multiple validation errors."""

        def handler(request: httpx.Request):
            xml_response = """
                <RESPONSE>
                    <ERROR>VR_WAPI_InvalidOVRDL</ERROR>
                    <ERROR>VR_WAPI_InvalidOVRDOB</ERROR>
                </RESPONSE>
            """
            return httpx.Response(200, json=xml_response)

        application = self._valid_application()
        client = self._client(handler)
        with self.assertRaises(APIValidationError) as ctx:
            _ = client.set_application(application)
        self.assertEqual(ctx.exception.errors()[0].loc[0], "drivers_license")
        self.assertEqual(ctx.exception.errors()[1].loc[0], "birth_date")

    def test_invalid_access_key_error(self):
        """Test behavior when API returns an invalid API key error."""

        def handler(request: httpx.Request):
            xml_response = """
                <RESPONSE>
                    <ERROR>VR_WAPI_InvalidAccessKey</ERROR>
                </RESPONSE>
            """
            return httpx.Response(200, json=xml_response)

        application = self._valid_application()
        client = self._client(handler)
        with self.assertRaises(InvalidAccessKeyError):
            # Set raise_exception INTENTIONALLY to false
            _ = client.set_application(application)

    def test_unparsable_response_json(self):
        """Test behavior when API returns an unparsable response."""

        def handler(request: httpx.Request):
            return httpx.Response(200, content=b"not even json")

        application = self._valid_application()
        client = self._client(handler)
        with self.assertRaises(UnparsableResponseError):
            _ = client.set_application(application)

    def test_unparsable_response_not_xml(self):
        """Test behavior when API returns an unparsable response."""

        def handler(request: httpx.Request):
            return httpx.Response(200, json="not xml")

        application = self._valid_application()
        client = self._client(handler)
        with self.assertRaises(UnparsableResponseError):
            _ = client.set_application(application)

    def test_unparsable_response_xml_root(self):
        """Test behavior when API returns an unparsable response."""

        def handler(request: httpx.Request):
            return httpx.Response(200, json="<BINGO />")

        application = self._valid_application()
        client = self._client(handler)
        with self.assertRaises(UnparsableResponseError):
            _ = client.set_application(application)
