import uuid

import mock
import requests
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from morango.certificates import Certificate

from kolibri.core.auth.test.test_api import FacilityFactory


class RegisterFacilityTestCase(TestCase):
    """
    Tests for management command of claiming a facility on a data portal server.
    """

    def setUp(self):
        self.token = "token"
        FacilityFactory()

    @mock.patch("requests.post")
    def test_no_owned_certificates(self, post_mock):
        post_mock.json.return_value = {"id": uuid.uuid4().hex}
        cert = Certificate.objects.first()
        cert.private_key = None
        cert.save()
        with self.assertRaisesRegexp(CommandError, "not own a certificate"):
            call_command("register", "token")

    @mock.patch("requests.post")
    def test_no_community(self, post_mock):
        post_mock.side_effect = requests.exceptions.HTTPError(
            response=mock.Mock(status_code=404, text="Community")
        )
        post_mock.json.return_value = {"status_code": 404, "text": "Community"}
        with self.assertRaisesRegexp(CommandError, "does not exist"):
            call_command("register", "token")