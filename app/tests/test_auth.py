import ddt
import mock
from django.conf import settings
from django.contrib.auth.models import User
from django.test import SimpleTestCase

from .. import ApplicationHookManager


@ddt.ddt
@mock.patch('app.User.objects')
class ApplicationHookManagerTests(SimpleTestCase):
    def setUp(self):
        self.manager = ApplicationHookManager()

    def _get_uname_and_password(self, user_id):
        uname = self.manager._compress_user_name(user_id)
        password = self.manager._generate_password(user_id, settings.PASSWORD_GENERATOR_NONCE)
        return uname, password

    @staticmethod
    def user_does_not_exist_side_effect(username="irrelevant"):
        raise User.DoesNotExist()

    @ddt.unpack
    @ddt.data(
        ('FN-2187', 'fn-2187@first_order.com', True),
        ('Kylo Ren', None, False),
        ('abcdef1234567890', None, False),
    )
    def test_authentication_hook_user_exists(self, user_id, email, auth_result, user_objects_manager):
        user_objects_manager.get.return_value = User()
        request = mock.Mock()
        expected_uname, expected_password = self._get_uname_and_password(user_id)

        with mock.patch('app.authenticate') as authenticate_mock, mock.patch('app.login') as login_mock:
            auth_result = mock.Mock() if auth_result else None
            authenticate_mock.return_value = auth_result
            self.manager.authentication_hook(request, user_id, 'irrelevant', email)

            authenticate_mock.assert_called_once_with(username=expected_uname, password=expected_password)
            login_mock.assert_called_once_with(request, auth_result)

    @ddt.unpack
    @ddt.data(
        ('Luke Skywalker', 'luke27@tatooine.com', True),
        ('Ben Solo', None, False),
    )
    def test_authentication_hook_user_missing(self, user_id, email, auth_result, user_objects_manager):
        user_objects_manager.get.side_effect = self.user_does_not_exist_side_effect
        request = mock.Mock()
        expected_uname, expected_password = self._get_uname_and_password(user_id)
        expected_email = email = email if email else user_id+'@localhost'

        with mock.patch('app.authenticate') as authenticate_mock, mock.patch('app.login') as login_mock:
            auth_result = mock.Mock() if auth_result else None
            authenticate_mock.return_value = auth_result
            self.manager.authentication_hook(request, user_id, 'irrelevant', email)

            user_objects_manager.create_user.assert_called_once_with(
                username=expected_uname, email=expected_email, password=expected_password
            )
            authenticate_mock.assert_called_once_with(username=expected_uname, password=expected_password)
            login_mock.assert_called_once_with(request, auth_result)
