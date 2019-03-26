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
        # Create student user
        self.student_password = 'student_password'
        self.student_user = get_user_model().objects.create(username='student_user')
        self.student_user.set_password(self.student_password)
        self.student_user.save()

        # Create admin user
        self.admin_password = 'admin_password'
        self.admin_user = get_user_model().objects.create(
            username='admin_user',
            is_staff=True,
            is_superuser=True,
        )
        self.admin_user.set_password(self.admin_password)
        self.admin_user.save()

    def _login(self, username, password):
        """
        Perform login with `username` and `password` credentials,
        and assert that login was successful.
        """
        self.assertTrue(self.client.login(username=username, password=password))

    def student_login(self):
        """
        Log in as a student.
        """
        self._login(self.student_user.username, self.student_password)

    def admin_login(self, username=None, password=None):
        """
        Log in as an admin.
        """
        self._login(self.admin_user.username, self.admin_password)
