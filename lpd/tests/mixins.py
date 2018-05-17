"""
Mixins used by classes spread across different test modules
"""

from django.contrib.auth import get_user_model


# Classes

class UserSetupMixin(object):
    """
    Mixin for test classes that require a user.
    """
    def setUp(self):  # pylint: disable=missing-docstring
        self.password = 'some_password'
        self.user = get_user_model().objects.create(username='student_user')
        self.user.set_password(self.password)
        self.user.save()

    def login(self, username=None, password=None):
        """
        Perform login with `username` and `password` credentials,
        and assert that login was successful.
        """
        username = username if username else self.user.username
        password = password if password else self.password
        self.assertTrue(self.client.login(username=username, password=password))
