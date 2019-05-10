"""
Tests for custom template tags and filters
"""

from mock import patch

import ddt
from django.test import TestCase
from freezegun import freeze_time
from pytz import utc

from lpd.models import AnswerOption
from lpd.templatetags import lpd_filters
from lpd.templatetags import lpd_tags
from lpd.tests.factories import (
    LearnerProfileDashboardFactory,
    QualitativeQuestionFactory,
    SectionFactory,
    SubmissionFactory,
    UserFactory
)
from lpd.tests.test_models import QUANTITATIVE_QUESTION_FACTORIES


# Classes

@ddt.ddt
class TemplateTagsTests(TestCase):
    """Tests for custom template tags."""

    def setUp(self):
        self.learner = UserFactory()

    @ddt.data(
        (0, '0%'),
        (0., '0%'),
        (0.123, '0%'),
        (0.987, '1%'),
        (14, '14%'),
        (14., '14%'),
        (14.3456, '14%'),
        (14.8765, '15%'),
        (70, '70%'),
        (70., '70%'),
        (70.23456, '70%'),
        (70.76543, '71%'),
        (100, '100%'),
        (100., '100%'),
    )
    @ddt.unpack
    def test_get_percent_complete(self, component_percent_complete, expected_percent_complete):
        """
        Test that `get_percent_complete` correctly formats LPD and section-level completeness.
        """
        lpd = LearnerProfileDashboardFactory()
        section = SectionFactory(lpd=lpd)
        with patch('lpd.models.LearnerProfileDashboard.get_percent_complete') as patched_lpd_get_percent_complete, \
                patch('lpd.models.Section.get_percent_complete') as patched_section_get_percent_complete:
            patched_lpd_get_percent_complete.return_value = component_percent_complete
            patched_section_get_percent_complete.return_value = component_percent_complete
            lpd_percent_complete = lpd_tags.get_percent_complete(lpd, self.learner)
            section_percent_complete = lpd_tags.get_percent_complete(section, self.learner)
            patched_lpd_get_percent_complete.assert_called_once_with(self.learner)
            patched_section_get_percent_complete.assert_called_once_with(self.learner)
            self.assertEqual(lpd_percent_complete, expected_percent_complete)
            self.assertEqual(section_percent_complete, expected_percent_complete)

    def test_get_last_update(self):
        """
        Test that `get_last_update` behaves correctly for existing and non-existing submissions.

        - If submission does not exist, `get_last_update` should return `None` (and not error out).
        - If submission exists, `get_last_update` should return timestamp corresponding to
          current value of `updated` field of submission.
        """
        # Submission does not exist
        section = SectionFactory()
        last_update = lpd_tags.get_last_update(section, self.learner)
        self.assertIsNone(last_update)

        # Submission exists
        with freeze_time('2017-01-17 11:25:00') as freezed_time:
            updated = utc.localize(freezed_time())
            SubmissionFactory(section=section, learner=self.learner, updated=updated)
            last_update = lpd_tags.get_last_update(section, self.learner)
            expected_last_update = 1484652300
            self.assertEqual(last_update, expected_last_update)

    def test_get_answer(self):
        """
        Test that `get_answer` tag makes appropriate calls to obtain answer provided by learner.
        """
        question = QualitativeQuestionFactory()
        with patch('lpd.models.QualitativeQuestion.get_answer') as patched_get_answer:
            expected_answer = 'Expected answer.'
            patched_get_answer.return_value = expected_answer
            answer = lpd_tags.get_answer(question, self.learner)
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
                data = lpd_tags.get_data(answer_option, self.learner)
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
        range = lpd_filters.ranking_range(count)  # pylint: disable=redefined-builtin
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
        range = lpd_filters.likert_range(answer_option_range)  # pylint: disable=redefined-builtin
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
        output = lpd_filters.render_custom_formatting(string)
        self.assertEqual(output, expected_output)

    # pylint: disable=line-too-long
    @ddt.data(
        (
            'This section should take approximately 2 minutes.<br /><br />'
            'Second paragraph.',
            'Second paragraph.',
        ),
        (
            'This section should take approximately 2 minutes, though you are welcome to take as much time as you like.<br /><br />'
            'Second paragraph.',
            'Second paragraph.',
        ),
        (
            'This section should take approximately 20 minutes.<br /><br />'
            'Second paragraph.',
            'Second paragraph.',
        ),
        (
            'This section should take approximately 20 minutes, though you are welcome to take as much time as you like.<br /><br />'
            'Second paragraph.',
            'Second paragraph.',
        ),
        (
            'First paragraph.<br /><br />'
            'This section should take approximately 2 minutes.<br /><br />'
            'Third paragraph.',
            'First paragraph.<br /><br />'
            'Third paragraph.',
        ),
        (
            'First paragraph.<br /><br />'
            'This section should take approximately 2 minutes, though you are welcome to take as much time as you like.<br /><br />'
            'Third paragraph.',
            'First paragraph.<br /><br />'
            'Third paragraph.',
        ),
        (
            'First paragraph.<br /><br />'
            'This section should take approximately 20 minutes.<br /><br />'
            'Third paragraph.',
            'First paragraph.<br /><br />'
            'Third paragraph.',
        ),
        (
            'First paragraph.<br /><br />'
            'This section should take approximately 20 minutes, though you are welcome to take as much time as you like.<br /><br />'
            'Third paragraph.',
            'First paragraph.<br /><br />'
            'Third paragraph.',
        ),
        (
            'First paragraph.<br /><br />'
            'This section should take approximately 2 minutes.',
            'First paragraph.<br /><br />'
        ),
        (
            'First paragraph.<br /><br />'
            'This section should take approximately 2 minutes, though you are welcome to take as much time as you like.',
            'First paragraph.<br /><br />'
        ),
        (
            'First paragraph.<br /><br />'
            'This section should take approximately 20 minutes.',
            'First paragraph.<br /><br />'
        ),
        (
            'First paragraph.<br /><br />'
            'This section should take approximately 20 minutes, though you are welcome to take as much time as you like.',
            'First paragraph.<br /><br />'
        ),
    )
    @ddt.unpack
    def test_remove_estimates(self, string, expected_output):
        """
        Test that `remove_estimates` correctly strips paragraph(s) providing effort estimates from `string`.
        """
        output = lpd_filters.remove_estimates(string)
        self.assertEqual(output, expected_output)

    @ddt.data(
        (
            '(A note to keep.) The remainder of this string.',
            '(A note to keep.) The remainder of this string.'
        ),
        (
            'The start of this string. (A note to remove.)',
            'The start of this string.'
        ),
    )
    @ddt.unpack
    def test_remove_notes(self, string, expected_output):
        """
        Test that `remove_notes` correctly strips notes from `string`.

        A note is any portion of the string that is wrapped in parentheses
        and follows the main, non-parenthesized portion of the string.
        """
        output = lpd_filters.remove_notes(string)
        self.assertEqual(output, expected_output)
