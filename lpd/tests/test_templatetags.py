"""
Tests for custom template tags and filters
"""

from mock import patch

import ddt
from django.test import TestCase
from freezegun import freeze_time
from pytz import utc

from lpd.models import AnswerOption
from lpd.templatetags.lpd_filters import likert_range, ranking_range, render_custom_formatting
from lpd.templatetags.lpd_tags import get_answer, get_data, get_last_update
from lpd.tests.factories import QualitativeQuestionFactory, SectionFactory, SubmissionFactory, UserFactory
from lpd.tests.test_models import QUANTITATIVE_QUESTION_FACTORIES


# Classes

class TemplateTagsTests(TestCase):
    """Tests for custom template tags."""

    def setUp(self):
        self.learner = UserFactory()

    def test_get_last_update(self):
        """
        Test that `get_last_update` behaves correctly for existing and non-existing submissions.

        - If submission does not exist, `get_last_update` should return `None` (and not error out).
        - If submission exists, `get_last_update` should return information
          derived from current value of `updated` field of submission.
        """
        # Submission does not exist
        section = SectionFactory()
        last_update = get_last_update(section, self.learner)
        self.assertIsNone(last_update)

        # Submission exists
        with freeze_time('2017-01-17 11:25:00') as freezed_time:
            updated = utc.localize(freezed_time())
            SubmissionFactory(section=section, learner=self.learner, updated=updated)
            last_update = get_last_update(section, self.learner)
            expected_last_update = 'Submitted on 01/17/2017 at 11:25 AM'
            self.assertEqual(last_update, expected_last_update)

    def test_get_answer(self):
        """
        Test that `get_answer` tag makes appropriate calls to obtain answer provided by learner.
        """
        question = QualitativeQuestionFactory()
        with patch('lpd.models.QualitativeQuestion.get_answer') as patched_get_answer:
            expected_answer = 'Expected answer.'
            patched_get_answer.return_value = expected_answer
            answer = get_answer(question, self.learner)
            patched_get_answer.assert_called_once_with(self.learner)
            self.assertEqual(answer, expected_answer)

    def test_get_data(self):
        """
        Test that `get_data` tag makes appropriate calls to obtain answer provided by learner.
        """
        question = QualitativeQuestionFactory()
        for question_factory in QUANTITATIVE_QUESTION_FACTORIES:
            with patch('lpd.models.AnswerOption.get_data') as patched_get_data:
                expected_data = {'expected': 'data'}
                patched_get_data.return_value = expected_data
                question = question_factory()
                answer_option = AnswerOption.objects.create(content_object=question)
                data = get_data(answer_option, self.learner)
                patched_get_data.assert_called_once_with(self.learner)
                self.assertEqual(data, expected_data)


@ddt.ddt
class TemplateFilterTests(TestCase):
    """Tests for custom template filters."""

    @ddt.data(
        (1, [1]),
        (2, [1, 2]),
        (3, [1, 2, 3]),
        (4, [1, 2, 3, 4]),
        (5, [1, 2, 3, 4, 5]),
    )
    @ddt.unpack
    def test_ranking_range(self, count, expected_range):
        """
        Test that `ranking_range` filter returns appropriate range.
        """
        range = ranking_range(count)  # pylint: disable=redefined-builtin
        self.assertEqual(range, expected_range)

    @ddt.data(
        (
            'value',
            [
                (1, 'Not Very Valuable'),
                (2, 'Slightly Valuable'),
                (3, 'Valuable'),
                (4, 'Very Valuable'),
                (5, 'Extremely Valuable'),
            ]
        ),
        (
            'agreement',
            [
                (1, 'Strongly Disagree'),
                (2, 'Disagree'),
                (3, 'Undecided'),
                (4, 'Agree'),
                (5, 'Strongly Agree'),
            ]
        ),
    )
    @ddt.unpack
    def test_likert_range(self, answer_option_range, expected_range):
        """
        Test that `likert_range` filter returns appropriate range.
        """
        range = likert_range(answer_option_range)  # pylint: disable=redefined-builtin
        self.assertEqual(list(range), expected_range)

    @ddt.data(
        ('This is not a test.', 'This is not a test.'),
        ('*This* is **not** a test.', '<em>This</em> is <strong>not</strong> a test.'),
        ('<em>This</em> is **not** a test.', '<em>This</em> is <strong>not</strong> a test.'),
        ('<strong>This</strong> is *not* a test.', '<strong>This</strong> is <em>not</em> a test.'),
    )
    @ddt.unpack
    def test_render_custom_formatting(self, string, expected_output):
        """
        Test that `render_custom_formatting` filter converts Markdown to HTML
        and preserves custom HTML.
        """
        output = render_custom_formatting(string)
        self.assertEqual(output, expected_output)
