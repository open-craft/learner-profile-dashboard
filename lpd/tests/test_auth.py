"""
Tests for custom LTI integration logic
"""

import ddt
import mock
from django.conf import settings
from django.contrib.auth.models import User
from django.test import SimpleTestCase

from lpd.auth import ApplicationHookManager


@ddt.ddt
@mock.patch('lpd.auth.User.objects')
class ApplicationHookManagerTests(SimpleTestCase):
    """Tests for ApplicationHookManager."""
    def setUp(self):
        self.manager = ApplicationHookManager()

    def _get_uname_and_password(self, user_id):
        """
        Generate username and password for `user_id` and return them.
        """
        uname = self.manager._compress_username(user_id)
        password = self.manager._generate_password(user_id, settings.PASSWORD_GENERATOR_NONCE)
        return uname, password

    @staticmethod
    def user_does_not_exist_side_effect(username="irrelevant"):
        """
        Raise `DoesNotExist` error.
        """
        raise User.DoesNotExist()

    @ddt.unpack
    @ddt.data(
        ('FN-2187', 'fn-2187@first_order.com', True),
        ('Kylo Ren', None, False),
        ('abcdef1234567890', None, False),
    )
    def test_authentication_hook_user_exists(self, user_id, email, can_authenticate, user_objects_manager):
        """
        Test behavior of `authentication_hook` for existing user.
        """
        user_objects_manager.get.return_value = User()
        request_mock = mock.Mock()
        expected_uname, expected_password = self._get_uname_and_password(user_id)

        with mock.patch('lpd.auth.authenticate') as authenticate_mock, mock.patch('lpd.auth.login') as login_mock:
            auth_result = mock.Mock() if can_authenticate else None
            authenticate_mock.return_value = auth_result
            self.manager.authentication_hook(request_mock, user_id, 'irrelevant', email)

            authenticate_mock.assert_called_once_with(
                request_mock, username=expected_uname, password=expected_password
            )
            login_mock.assert_called_once_with(request_mock, auth_result)

    @ddt.unpack
    @ddt.data(
        ('Luke Skywalker', 'luke27@tatooine.com', True),
        ('Ben Solo', None, False),
    )
    def test_authentication_hook_user_missing(self, user_id, email, can_authenticate, user_objects_manager):
        """
        Test behavior of `authentication_hook` for missing user.
        """
        user_objects_manager.get.side_effect = self.user_does_not_exist_side_effect
        request_mock = mock.Mock()
        expected_uname, expected_password = self._get_uname_and_password(user_id)
        expected_email = email = email if email else user_id+'@localhost'

        with mock.patch('lpd.auth.authenticate') as authenticate_mock, mock.patch('lpd.auth.login') as login_mock:
            auth_result = mock.Mock() if can_authenticate else None
            authenticate_mock.return_value = auth_result
            self.manager.authentication_hook(request_mock, user_id, 'irrelevant', email)

            user_objects_manager.create_user.assert_called_once_with(
                username=expected_uname, email=expected_email, password=expected_password
            )
            authenticate_mock.assert_called_once_with(
                request_mock, username=expected_uname, password=expected_password
            )
            login_mock.assert_called_once_with(request_mock, auth_result)

    @ddt.data('1', '2', '123')
    def test_authenticated_redirect(self, lpd_id, user_objects_manager):
        """
        Test that `authenticated_redirect_to` takes custom parameters into account when building URL to redirect to.
        """
        request = mock.Mock()
        lti_data = {
            'custom_lpd_id': lpd_id,
        }
        expected_redirect = "/lpd/{lpd_id}".format(lpd_id=lpd_id)
        actual_redirect = self.manager.authenticated_redirect_to(request, lti_data)

        self.assertEqual(actual_redirect, expected_redirect)
