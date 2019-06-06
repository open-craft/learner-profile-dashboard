"""
Mixins used by classes spread across different test modules
"""

from django.contrib.auth import get_user_model

from lpd import models
from lpd.tests import factories


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


class QuantitativeQuestionTestMixin(object):
    """Mixin for tests targeting QuantitativeQuestion models."""

    def setUp(self):  # pylint: disable=missing-docstring
        lpd = factories.LearnerProfileDashboardFactory(name='Test LPD')
        self.section = factories.SectionFactory(lpd=lpd, title='Test section')

    @classmethod
    def _create_answer_options(
            cls,
            question,
            option_texts,
            fallback_options=(False, False, False),
            allow_custom_input=(False, False, False)
    ):
        """
        Create answer options for `question` based on options listed in `option_texts`,
        make them fallback options based on value of `fallback_options`,
        and configure them to allow custom input based on value of `allow_custom_input`.
        """
        return [
            models.AnswerOption.objects.create(
                content_object=question,
                option_text=option_text,
                fallback_option=fallback_option,
                allows_custom_input=allows_custom_input
            ) for option_text, fallback_option, allows_custom_input in zip(
                option_texts, fallback_options, allow_custom_input
            )
        ]

    def test_get_answer_options(self):
        """
        Test that `get_answer_options` returns answer options in appropriate order.
        """
        question = self.question_factory(randomize_options=True)

        # Create fallback options first, to make sure order of answer options in DB
        # doesn't match order that we want to test for.
        expected_fallback_options = self._create_answer_options(
            question,
            ("Don't know", 'Other:'),
            fallback_options=(True, True),
            allow_custom_input=(False, True),
        )

        # Create regular answer options
        expected_answer_options = self._create_answer_options(question, ('Yellow', 'Blue', 'Red'))
        answer_options = list(question.get_answer_options())

        # Question is configured to display answer options in random order,
        # so we only need to check if `get_answer_options` returns all answer options (and no more).
        self.assertEqual(len(answer_options), 5)
        for answer_option in expected_answer_options:
            self.assertIn(answer_option, answer_options)

        # However, fallback options need to be listed last, in reverse alphabetical order:
        self.assertEqual(answer_options[3:], list(reversed(expected_fallback_options)))

        # Disable randomization option
        question.randomize_options = False
        question.save()

        answer_options = list(question.get_answer_options())
        # Question is configured *not* to display answer options in random order,
        # so we need to check if `get_answer_options` returns answer options in alphabetical order,
        # and whether it lists fallback options last, in reverse alphabetical order.
        self.assertEqual(len(answer_options), 5)
        self.assertEqual(
            answer_options,
            sorted(expected_answer_options, key=lambda o: o.option_text) + list(reversed(expected_fallback_options))
        )
