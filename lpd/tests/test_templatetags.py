from mock import patch

import ddt
from django.test import TestCase

from lpd.models import AnswerOption
from lpd.templatetags.lpd_filters import option_range
from lpd.templatetags.lpd_tags import get_answer, get_data
from lpd.tests.factories import QualitativeQuestionFactory, UserFactory
from lpd.tests.test_models import QUANTITATIVE_QUESTION_FACTORIES


# Classes

class TemplateTagsTest(TestCase):
    """Tests for custom template tags."""

    def setUp(self):
        self.learner = UserFactory()

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
class TemplateFilterTest(TestCase):
    """Tests for custom template filters."""

    @ddt.data(
        (1, [1]),
        (2, [1, 2]),
        (3, [1, 2, 3]),
        (4, [1, 2, 3, 4]),
        (5, [1, 2, 3, 4, 5]),
    )
    @ddt.unpack
    def test_option_range(self, count, expected_range):
        """
        Test that `option` range filter returns appropriate range.
        """
        range = option_range(count)  # pylint: disable=redefined-builtin
        self.assertEqual(range, expected_range)
