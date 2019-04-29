"""
Model tests for Learner Profile Dashboard
"""

# pylint: disable=too-many-lines

import logging
import random

import ddt
from django.test import TestCase
from freezegun import freeze_time
from mock import call, patch
from pytz import utc

from lpd.constants import QuestionTypes, UnknownQuestionTypeError
from lpd.models import (
    AnswerOption,
    KnowledgeComponent,
    LearnerProfileDashboard,
    LikertScaleQuestion,
    MultipleChoiceQuestion,
    QualitativeQuestion,
    QuantitativeAnswer,
    QuantitativeQuestion,
    RankingQuestion,
    Score,
    Submission,
)
from lpd.tests.factories import (
    KnowledgeComponentFactory,
    LearnerProfileDashboardFactory,
    LikertScaleQuestionFactory,
    MultipleChoiceQuestionFactory,
    QualitativeAnswerFactory,
    QualitativeQuestionFactory,
    RankingQuestionFactory,
    SectionFactory,
    SubmissionFactory,
    UserFactory,
)
from lpd.tests.mixins import UserSetupMixin


# Globals

log = logging.getLogger(__name__)

QUALITATIVE_QUESTION_FACTORIES = [
    QualitativeQuestionFactory,
]
QUANTITATIVE_QUESTION_FACTORIES = [
    MultipleChoiceQuestionFactory,
    RankingQuestionFactory,
    LikertScaleQuestionFactory
]
QUESTION_FACTORIES = QUALITATIVE_QUESTION_FACTORIES + QUANTITATIVE_QUESTION_FACTORIES

QUESTION_BATCH_SIZE = 5  # Number of questions to create per question type


# Classes

@ddt.ddt
class LearnerProfileDashboardTests(TestCase):
    """LearnerProfileDashboard model tests."""

    def test_str(self):
        """
        Test string representation of `LearnerProfileDashboard` model.
        """
        lpd = LearnerProfileDashboardFactory(name='Empty LPD')
        self.assertEqual(str(lpd), 'LPD 1: Empty LPD')

    @ddt.data(
        (
            [],  # No sections
            0.
        ),
        (
            [  # Learner didn't complete any sections (0 out of 1)
                0.,
            ],
            0.,
        ),
        (
            [  # Learner didn't complete any sections (0 out of 3)
                0.,
                0.,
                0.,
            ],
            0.,
        ),
        (
            [  # Learner completed some sections (1 out of 3)
                100.,
                0.,
                0.,
            ],
            33.,
        ),
        (
            [  # Learner completed some sections (2 out of 3)
                100.,
                100.,
                0.,
            ],
            67.,
        ),
        (
            [  # Learner partially completed some sections (1 out of 3)
                40.,
                0.,
                0.,
            ],
            13.,
        ),
        (
            [  # Learner partially completed some sections (2 out of 3)
                25.,
                82.,
                0.,
            ],
            36.,
        ),
        (
            [  # Learner completed a section and partially completed another one
                0.,
                100.,
                53.,
            ],
            51.,
        ),
        (
            [  # Learner partially completed all sections
                14.,
                98.,
                61.,
            ],
            58.,
        ),
        (
            [  # Learner completed all sections (1 out of 1)
                100.,
            ],
            100.,
        ),
        (
            [  # Learner completed all sections (3 out of 3)
                100.,
                100.,
                100.,
            ],
            100.,
        ),
    )
    @ddt.unpack
    def test_get_percent_complete(self, section_percent_complete, expected_percent_complete):
        """
        Test that `get_percent_complete` method returns appropriate value
        based on number of sections that learner completed.
        """
        learner = UserFactory()
        lpd = LearnerProfileDashboardFactory(name='Test LPD')

        num_sections = len(section_percent_complete)
        for n in range(num_sections):
            SectionFactory(lpd=lpd, title='Test section {n}'.format(n=n))

        with patch('lpd.models.Section.get_percent_complete') as patched_get_percent_complete:
            patched_get_percent_complete.side_effect = section_percent_complete
            expected_calls = num_sections * [call(learner)]

            percent_complete = lpd.get_percent_complete(learner)

            patched_get_percent_complete.assert_has_calls(expected_calls)
            self.assertEqual(round(percent_complete), expected_percent_complete)


@ddt.ddt
class SectionTests(TestCase):
    """Section model tests."""

    def setUp(self):
        self.lpd = LearnerProfileDashboardFactory(name='Test LPD')

    @classmethod
    def _create_questions(cls, section):
        """
        Create a list of questions associated with `section` and return it.

        For each type of question (as specified by `QUESTION_FACTORIES`),
        create `QUESTION_BATCH_SIZE` questions and add them to the result list,
        then return result list.
        """
        questions = []
        question_numbers = sorted(random.sample(range(1, 100), QUESTION_BATCH_SIZE*len(QUESTION_FACTORIES)))
        for unused in range(QUESTION_BATCH_SIZE):
            for question_factory in QUESTION_FACTORIES:
                question_number = question_numbers.pop(0)
                log.info('Creating question #%d using %s.', question_number, question_factory)
                question = question_factory(section=section, number=question_number)
                questions.append(question)
        return questions

    def test_str(self):
        """
        Test string representation of `Section` model.
        """
        section = SectionFactory(lpd=self.lpd, title='Basic information')
        self.assertEqual(str(section), 'LPD 1: Test LPD > Section 1: Basic information')

    def test_questions(self):
        """
        Test that `questions` property returns questions belonging to `Section` in appropriate order.
        """
        log.info('Testing `questions` property of `Section` model.')
        section = SectionFactory(lpd=self.lpd, title='Details, Details, Details')
        questions = self._create_questions(section)
        self.assertEqual(section.questions, questions)

    def test_get_percent_complete_no_questions(self):
        """
        Test that `get_percent_complete` method returns appropriate value
        based on number of questions that learner answered.
        """
        learner = UserFactory()
        section = SectionFactory(lpd=self.lpd, title='Test section')

        with patch('lpd.models.QualitativeQuestion.has_answer_from') as patched_qualitative_has_answer_from, \
                patch('lpd.models.MultipleChoiceQuestion.has_answer_from') as patched_multiple_has_answer_from, \
                patch('lpd.models.RankingQuestion.has_answer_from') as patched_ranking_has_answer_from, \
                patch('lpd.models.LikertScaleQuestion.has_answer_from') as patched_likert_has_answer_from:

            percent_complete = section.get_percent_complete(learner)
            patched_qualitative_has_answer_from.assert_not_called()
            patched_multiple_has_answer_from.assert_not_called()
            patched_ranking_has_answer_from.assert_not_called()
            patched_likert_has_answer_from.assert_not_called()
            self.assertEqual(percent_complete, 0.)

    # pylint: disable=too-many-locals
    @ddt.data(
        (
            {  # Learner didn't answer any questions
                'qualitative': 0,
                'multiple_choice': 0,
                'ranking': 0,
                'likert': 0,
            },
            0.,
        ),
        (
            {  # Learner answered some questions (9 out of 20)
                'qualitative': 1,
                'multiple_choice': 0,
                'ranking': 5,
                'likert': 3,
            },
            45.,
        ),
        (
            {  # Learner answered all questions
                'qualitative': QUESTION_BATCH_SIZE,
                'multiple_choice': QUESTION_BATCH_SIZE,
                'ranking': QUESTION_BATCH_SIZE,
                'likert': QUESTION_BATCH_SIZE,
            },
            100.,
        ),
    )
    @ddt.unpack
    def test_get_percent_complete(self, num_questions_answered, expected_percent_complete):
        """
        Test that `get_percent_complete` method returns appropriate value
        based on number of questions that learner answered.
        """
        learner = UserFactory()
        section = SectionFactory(lpd=self.lpd, title='Test section')
        questions = self._create_questions(section)

        # Verify assumption that this test makes about total number of questions belonging to `section`
        self.assertEqual(len(questions), QUESTION_BATCH_SIZE * len(QUESTION_FACTORIES))

        with patch('lpd.models.QualitativeQuestion.has_answer_from') as patched_qualitative_has_answer_from, \
                patch('lpd.models.MultipleChoiceQuestion.has_answer_from') as patched_multiple_has_answer_from, \
                patch('lpd.models.RankingQuestion.has_answer_from') as patched_ranking_has_answer_from, \
                patch('lpd.models.LikertScaleQuestion.has_answer_from') as patched_likert_has_answer_from:
            num_qualitative_questions_answered = num_questions_answered['qualitative']
            num_qualitative_questions_unanswered = QUESTION_BATCH_SIZE - num_qualitative_questions_answered
            patched_qualitative_has_answer_from.side_effect = (
                num_qualitative_questions_answered * [True] + num_qualitative_questions_unanswered * [False]
            )
            num_multiple_choice_questions_answered = num_questions_answered['multiple_choice']
            num_multiple_choice_questions_unanswered = QUESTION_BATCH_SIZE - num_multiple_choice_questions_answered
            patched_multiple_has_answer_from.side_effect = (
                num_multiple_choice_questions_answered * [True] + num_multiple_choice_questions_unanswered * [False]
            )
            num_ranking_questions_answered = num_questions_answered['ranking']
            num_ranking_questions_unanswered = QUESTION_BATCH_SIZE - num_ranking_questions_answered
            patched_ranking_has_answer_from.side_effect = (
                num_ranking_questions_answered * [True] + num_ranking_questions_unanswered * [False]
            )
            num_likert_questions_answered = num_questions_answered['likert']
            num_likert_questions_unanswered = QUESTION_BATCH_SIZE - num_likert_questions_answered
            patched_likert_has_answer_from.side_effect = (
                num_likert_questions_answered * [True] + num_likert_questions_unanswered * [False]
            )
            expected_calls = QUESTION_BATCH_SIZE * [call(learner)]

            percent_complete = section.get_percent_complete(learner)
            patched_qualitative_has_answer_from.assert_has_calls(expected_calls)
            patched_multiple_has_answer_from.assert_has_calls(expected_calls)
            patched_ranking_has_answer_from.assert_has_calls(expected_calls)
            patched_likert_has_answer_from.assert_has_calls(expected_calls)
            self.assertEqual(percent_complete, expected_percent_complete)


class QuestionTests(TestCase):
    """Question model tests."""

    def setUp(self):
        self.lpd = LearnerProfileDashboard.objects.create(name='Test LPD')

    def test_section_number(self):
        """
        Test that `section_number` property returns appropriate value.
        """
        log.info('Testing `section_number` property of `Question` model.')
        sections = SectionFactory.build_batch(3, lpd=self.lpd)

        for section in sections:
            for question_factory in QUESTION_FACTORIES:
                log.info('Creating %d questions using %s.', QUESTION_BATCH_SIZE, question_factory)
                questions = question_factory.build_batch(QUESTION_BATCH_SIZE, section=section)
                for question in questions:
                    self.assertEqual(question.section_number, '{}.{}'.format(section.order+1, question.number))


@ddt.ddt  # pylint: disable=too-many-instance-attributes
class QualitativeQuestionTests(TestCase):
    """QualitativeQuestion model tests."""

    def setUp(self):
        lpd = LearnerProfileDashboardFactory(name='Test LPD')
        section = SectionFactory(lpd=lpd, title='Test section')

        self.qualitative_question_1 = QualitativeQuestionFactory(
            section=section,
            question_text='Is this a qualitative question?',
            influences_group_membership=True,
        )
        self.qualitative_question_2 = QualitativeQuestionFactory(
            section=section,
            question_text='Is this another qualitative question?',
            influences_group_membership=True,
        )
        self.qualitative_question_3 = QualitativeQuestionFactory(
            section=section,
            question_text='Is this yet another qualitative question?',
            influences_group_membership=False,
        )

        self.learner_1 = UserFactory()
        self.learner_2 = UserFactory()

        self.learner_1_answer_to_question_1 = "Learner 1's answer to question_1"
        self.learner_1_answer_to_question_2 = "Learner 1's answer to question_2"
        # This answer should be ignored when updating scores
        # because the question that it belongs to is set up to *not* influence group membership
        learner_1_answer_to_question_3 = "Learner 1's answer to question_3"

        self.learner_2_answer_to_question_1 = "Learner 2's answer to question_1"
        # This answer should be ignored when updating scores
        # because the question that it belongs to is set up to *not* influence group membership
        learner_2_answer_to_question_3 = "Learner 2's answer to question_3"

        self.kc_1 = KnowledgeComponentFactory(
            kc_id='kc_id_1', kc_name='knowledge_component_1'
        )
        self.kc_2 = KnowledgeComponentFactory(
            kc_id='kc_id_2', kc_name='knowledge_component_2'
        )

        QualitativeAnswerFactory(
            learner=self.learner_1,
            question=self.qualitative_question_1,
            text=self.learner_1_answer_to_question_1,
        )
        QualitativeAnswerFactory(
            learner=self.learner_1,
            question=self.qualitative_question_2,
            text=self.learner_1_answer_to_question_2,
        )
        QualitativeAnswerFactory(
            learner=self.learner_1,
            question=self.qualitative_question_3,
            text=learner_1_answer_to_question_3,
        )
        QualitativeAnswerFactory(
            learner=self.learner_2,
            question=self.qualitative_question_1,
            text=self.learner_2_answer_to_question_1,
        )
        QualitativeAnswerFactory(
            learner=self.learner_2,
            question=self.qualitative_question_3,
            text=learner_2_answer_to_question_3,
        )

    def test_str(self):
        """
        Test string representation of `QualitativeQuestion` model.
        """
        self.assertEqual(
            str(self.qualitative_question_1),
            'LPD 1: Test LPD > Section 1: Test section > '
            'QualitativeQuestion 1: Is this a qualitative question?'
        )
        self.assertEqual(
            str(self.qualitative_question_2),
            'LPD 1: Test LPD > Section 1: Test section > '
            'QualitativeQuestion 2: Is this another qualitative question?'
        )
        self.assertEqual(
            str(self.qualitative_question_3),
            'LPD 1: Test LPD > Section 1: Test section > '
            'QualitativeQuestion 3: Is this yet another qualitative question?'
        )

    def test_type(self):
        """
        Test that `type` property returns appropriate value.
        """
        essay_question = QualitativeQuestionFactory(question_type=QuestionTypes.ESSAY)
        short_answer_question = QualitativeQuestionFactory(question_type=QuestionTypes.SHORT_ANSWER)
        self.assertEqual(essay_question.type, QuestionTypes.ESSAY)
        self.assertEqual(short_answer_question.type, QuestionTypes.SHORT_ANSWER)

    @ddt.data(False, True)
    def test_get_answer(self, split_answer):
        """
        Test that `get_answer` method returns appropriate value.
        """
        question = QualitativeQuestionFactory(split_answer=split_answer)
        learner = UserFactory()

        # Learner has yet to answer question
        self.assertEqual(question.get_answer(learner), '')

        answer_text = 'This, is, not, an, answer'
        if split_answer:
            for answer_component in answer_text.split(', '):
                QualitativeAnswerFactory(learner=learner, question=question, text=answer_component)
        else:
            QualitativeAnswerFactory(learner=learner, question=question, text=answer_text)

        # Learner answered question
        self.assertEqual(question.get_answer(learner), answer_text)

    @ddt.data(
        (False, ['This,is, not ,an , answer (and commas are all weird)']),
        (True, ['This', 'is', 'not', 'an', 'answer (and commas are all weird)']),
    )
    @ddt.unpack
    def test_get_answer_components(self, split_answer, expected_answer_components):
        """
        Test that `get_answer_components` method returns appropriate value.
        """
        question = QualitativeQuestionFactory(split_answer=split_answer)
        answer_text = 'This,is, not ,an , answer (and commas are all weird)'

        answer_components = question.get_answer_components(answer_text)
        self.assertEqual(answer_components, expected_answer_components)

    @patch('lpd.models.calculate_probabilities')
    def test_update_scores(self, patched_calculate_probabilities):
        """
        Test the behaviour of `update_scores` class method.
        """
        patched_calculate_probabilities.return_value = {
            'kc_id_1': 0.2, 'kc_id_2': 0.8
        }

        # Update scores of learner_1 and assert that the results are correct
        QualitativeQuestion.update_scores(self.learner_1)

        self.assertItemsEqual(
            patched_calculate_probabilities.call_args[0][0],
            [self.learner_1_answer_to_question_1, self.learner_1_answer_to_question_2]
        )
        self.assertEqual(Score.objects.all().count(), 2)
        self.assertEqual(Score.objects.filter(learner=self.learner_1).count(), 2)
        self.assertEqual(Score.objects.filter(learner=self.learner_2).count(), 0)

        # Scores have to be equal to (1 - probability)
        # to have the desired effect
        # on recommendations generated by the adaptive engine.
        self.assertAlmostEqual(
            Score.objects.get(
                learner=self.learner_1, knowledge_component=self.kc_1
            ).value,
            0.8,
            places=2
        )
        self.assertAlmostEqual(
            Score.objects.get(
                learner=self.learner_1, knowledge_component=self.kc_2
            ).value,
            0.2,
            places=2
        )

        patched_calculate_probabilities.return_value = {
            'kc_id_1': 0.3, 'kc_id_2': 0.7
        }

        # Update scores of learner_2 and assert that the results are correct
        QualitativeQuestion.update_scores(self.learner_2)

        self.assertItemsEqual(
            patched_calculate_probabilities.call_args[0][0],
            [self.learner_2_answer_to_question_1]
        )
        self.assertEqual(Score.objects.all().count(), 4)
        self.assertEqual(Score.objects.filter(learner=self.learner_1).count(), 2)
        self.assertEqual(Score.objects.filter(learner=self.learner_2).count(), 2)
        self.assertAlmostEqual(
            Score.objects.get(
                learner=self.learner_1, knowledge_component=self.kc_1
            ).value,
            0.8,
            places=2
        )
        self.assertAlmostEqual(
            Score.objects.get(
                learner=self.learner_1, knowledge_component=self.kc_2
            ).value,
            0.2,
            places=2
        )
        self.assertAlmostEqual(
            Score.objects.get(
                learner=self.learner_2, knowledge_component=self.kc_1
            ).value,
            0.7,
            places=2
        )
        self.assertAlmostEqual(
            Score.objects.get(
                learner=self.learner_2, knowledge_component=self.kc_2
            ).value,
            0.3,
            places=2
        )

    @ddt.data(
        ('', False),
        ('Yes!', True),
        ('This is not an answer.', True),
        ('12345', True),
        ('a, comma-separated, list, of, items', True)
    )
    @ddt.unpack
    def test_has_answer_from(self, answer, expected_answer_status):
        """
        Test that `has_answer_from` method returns appropriate value
        based on answer that learner provided for qualitative question.

        For qualitative questions, any text submitted by the learner counts as an answer.
        """
        learner = UserFactory()
        question = QualitativeQuestionFactory()
        with patch('lpd.models.QualitativeQuestion.get_answer') as patched_get_answer:
            patched_get_answer.return_value = answer

            has_answer_from_learner = question.has_answer_from(learner)

            patched_get_answer.assert_called_once_with(learner)
            self.assertEqual(has_answer_from_learner, expected_answer_status)


@ddt.ddt
class QuantitativeQuestionTests(TestCase):
    """QuantitativeQuestion model tests."""

    def setUp(self):
        self.unranked_option_value = 9
        for number_of_options_to_rank in range(2, self.unranked_option_value, 2):
            RankingQuestionFactory(number_of_options_to_rank=number_of_options_to_rank)

    @patch('lpd.models.MultipleChoiceQuestion._get_score')
    @patch('lpd.models.RankingQuestion._get_score')
    @patch('lpd.models.LikertScaleQuestion._get_score')
    def test_get_score(self, patched_likert_get_score, patched_ranking_get_score, patched_mc_get_score):
        """
        Verify that `get_score` dispatches to subclass methods appropriately,
        and raises exception for unknown question type.
        """
        with self.assertRaises(UnknownQuestionTypeError):
            QuantitativeQuestion.get_score('invalid_question_type', 42)

        patched_mc_get_score.return_value = 0
        patched_ranking_get_score.return_value = 23
        patched_likert_get_score.return_value = 42

        # MCQs
        score = QuantitativeQuestion.get_score(QuestionTypes.MCQ, 1)
        patched_mc_get_score.assert_has_calls([call(1)])
        self.assertEqual(score, 0)
        # MRQs
        score = QuantitativeQuestion.get_score(QuestionTypes.MRQ, 1)
        patched_mc_get_score.assert_has_calls([call(1), call(1)])
        self.assertEqual(score, 0)
        # Ranking questions
        score = QuantitativeQuestion.get_score(QuestionTypes.RANKING, 2)
        patched_ranking_get_score.assert_called_once_with(2)
        self.assertEqual(score, 23)
        # Likert scale questions
        score = QuantitativeQuestion.get_score(QuestionTypes.LIKERT, 3)
        patched_likert_get_score.assert_called_once_with(3)
        self.assertEqual(score, 42)

    @ddt.data(
        (QuestionTypes.MCQ, 1, 1),
        (QuestionTypes.MCQ, 0, 0),
        (QuestionTypes.MRQ, 1, 1),
        (QuestionTypes.MRQ, 0, 0),
        (QuestionTypes.RANKING, 3, 3),
        (QuestionTypes.RANKING, None, 9),
        (QuestionTypes.LIKERT, 2, 2),
        (QuestionTypes.LIKERT, None, None),
    )
    @ddt.unpack
    def test_get_answer_value(self, question_type, raw_value, expected_value):
        """
        Test that `get_answer_value` returns appropriate values for different question types.
        """
        answer_value = QuantitativeQuestion.get_answer_value(question_type, raw_value)
        self.assertEqual(answer_value, expected_value)


class QuantitativeQuestionTestMixin(object):
    """Mixin for tests targeting QuantitativeQuestion models."""

    def setUp(self):  # pylint: disable=missing-docstring
        lpd = LearnerProfileDashboardFactory(name='Test LPD')
        self.section = SectionFactory(lpd=lpd, title='Test section')

    @classmethod
    def _create_answer_options(cls, question, option_texts, fallback_options=(False, False, False)):
        """
        Create answer options for `question` based on options listed in `option_texts`,
        and make them fallback options based on value of `fallback_options`.
        """
        return [
            AnswerOption.objects.create(
                content_object=question, option_text=option_text, fallback_option=fallback_option
            ) for option_text, fallback_option in zip(option_texts, fallback_options)
        ]

    def test_get_answer_options(self):
        """
        Test that `get_answer_options` returns answer options in appropriate order.
        """
        question = self.question_factory(randomize_options=True)

        # Create fallback options first, to make sure order of answer options in DB
        # doesn't match order that we want to test for.
        expected_fallback_options = self._create_answer_options(
            question, ("Don't know", 'Other:'), fallback_options=(True, True)
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


@ddt.ddt
class MultipleChoiceQuestionTests(QuantitativeQuestionTestMixin, TestCase):
    """MultipleChoiceQuestion model tests."""

    def setUp(self):
        super(MultipleChoiceQuestionTests, self).setUp()
        self.question_factory = MultipleChoiceQuestionFactory
        self.mcq = self.question_factory(
            section=self.section,
            question_text='Is this a multiple choice question?',
            max_options_to_select=1
        )
        self.mrq = self.question_factory(
            section=self.section,
            question_text='Is this a multiple response question?',
            max_options_to_select=5
        )

    def test_str(self):
        """
        Test string representation of `MultipleChoiceQuestion` model.
        """
        self.assertEqual(
            str(self.mcq),
            'LPD 1: Test LPD > Section 1: Test section > '
            'MultipleChoiceQuestion 1: Is this a multiple choice question?'
        )
        self.assertEqual(
            str(self.mrq),
            'LPD 1: Test LPD > Section 1: Test section > '
            'MultipleChoiceQuestion 2: Is this a multiple response question?'
        )

    def test_type(self):
        """
        Test that `type` property returns appropriate value.
        """
        self.assertEqual(self.mcq.type, QuestionTypes.MCQ)
        self.assertEqual(self.mrq.type, QuestionTypes.MRQ)

    @ddt.data(
        (0, 1),
        (1, 0),
    )
    @ddt.unpack
    def test__get_score(self, answer_value, expected_score):
        """
        Test that `_get_score` returns appropriate score
        and raises exception for invalid answer values.
        """
        with self.assertRaises(AssertionError):
            MultipleChoiceQuestion._get_score(answer_value+23)

        score = MultipleChoiceQuestion._get_score(answer_value)
        self.assertEqual(score, expected_score)

    @ddt.data(
        # MCQ
        (1, (False, False, False), 3, False),  # No answers (learner did not select any option)
        (1, (False, False, True), 3, True),    # Learner selected 1 fallback option
        (1, (False, True, False), 2, True),    # Learner selected 1 regular option
        (1, (True, False, False), 1, True),    # Learner selected 1 regular option
        # MRQ
        (3, (False, False, False), 3, False),  # No answers (learner did not select any option)
        (3, (False, False, True), 3, True),    # Learner selected 1 fallback option
        (3, (False, True, False), 2, True),    # Learner selected 1 regular option
        (3, (False, True, True), 2, True),     # Learner selected 1 regular option, 1 fallback option
        (3, (True, False, False), 1, True),    # Learner selected 1 regular option
        (3, (True, False, True), 1, True),     # Learner selected 1 regular option, 1 fallback option
        (3, (True, True, False), 1, True),     # Learner selected 2 regular options
        (3, (True, True, True), 1, True),      # learner selected 2 regular options, 1 fallback option
    )
    @ddt.unpack
    def test_has_answer_from(
            self, max_options_to_select, answer_option_selection_status, expected_checks, expected_answer_status
    ):
        """
        Test that `has_answer_from` method returns appropriate value
        based on number of answer options that learner selected for multiple choice question.

        For multiple choice questions, learner must select at least one answer option
        for the LPD to consider the question answered.
        """
        learner = UserFactory()
        question = self.question_factory(
            question_text='Will you answer this or not?',
            max_options_to_select=max_options_to_select
        )
        self._create_answer_options(question, ('A', 'B', 'C'), fallback_options=(False, False, True))
        with patch('lpd.models.AnswerOption.is_selected_by') as patched_is_selected_by:
            patched_is_selected_by.side_effect = answer_option_selection_status
            expected_calls = expected_checks * [call(learner)]

            has_answer_from_learner = question.has_answer_from(learner)

            patched_is_selected_by.assert_has_calls(expected_calls)
            self.assertEqual(has_answer_from_learner, expected_answer_status)


@ddt.ddt
class RankingQuestionTests(QuantitativeQuestionTestMixin, TestCase):
    """RankingQuestion model tests."""

    def setUp(self):
        super(RankingQuestionTests, self).setUp()
        self.question_factory = RankingQuestionFactory
        self.question = self.question_factory(
            section=self.section,
            question_text='Is this a ranking question?',
            number_of_options_to_rank=3
        )

    def test_str(self):
        """
        Test string representation of `RankingQuestion` model.
        """
        self.assertEqual(
            str(self.question),
            'LPD 1: Test LPD > Section 1: Test section > '
            'RankingQuestion 1: Is this a ranking question?'
        )

    def test_type(self):
        """
        Test that `type` property returns appropriate value.
        """
        self.assertEqual(self.question.type, QuestionTypes.RANKING)

    def test_unranked_option_value(self):
        """
        Test that `unranked_option_value` returns appropriate value.
        """
        for rank in [3, 5, 10]:
            self.question_factory(number_of_options_to_rank=rank)
        self.assertEqual(RankingQuestion.unranked_option_value(), 11)

    @ddt.data(
        (1, 0.0),
        (2, 1.0/3),
        (3, 2.0/3),
        (4, 1.0),
    )
    @ddt.unpack
    def test__get_score(self, answer_value, expected_score):
        """
        Test that `_get_score` returns appropriate score.
        """
        score = RankingQuestion._get_score(answer_value)
        self.assertEqual(score, expected_score)

    @ddt.data(
        ((False, False, False, False), False),  # No answers (learner did not rank any options)
        ((False, False, False, True), False),   # Learner ranked 1 out of 2 options to rank
                                                # (0 regular options, 1 fallback option)
        ((False, False, True, False), False),   # Learner ranked 1 out of 2 options to rank
                                                # (0 regular options, 1 fallback option)
        ((False, False, True, True), True),     # Learner ranked 2 out of 2 options to rank
                                                # (0 regular options, 2 fallback options)
        ((False, True, False, False), False),   # Learner ranked 1 out of 2 options to rank
                                                # (1 regular option, 0 fallback options)
        ((False, True, False, True), True),     # Learner ranked 2 out of 2 options to rank
                                                # (1 regular option, 1 fallback option)
        ((False, True, True, False), True),     # Learner ranked 2 out of 2 options to rank
                                                # (1 regular option, 1 fallback option)
        ((True, False, False, False), False),   # Learner ranked 1 out of 2 options to rank
                                                # (1 regular option, 0 fallback options)
        ((True, False, False, True), True),     # Learner ranked 2 out of 2 options to rank
                                                # (1 regular option, 1 fallback option)
        ((True, False, True, False), True),     # Learner ranked 2 out of 2 options to rank
                                                # (1 regular option, 1 fallback option)
        ((True, True, False, False), True),     # Learner ranked 2 out of 2 options to rank
                                                # (2 regular options, 0 fallback options)
    )
    @ddt.unpack
    def test_has_answer_from(self, answer_option_selection_status, expected_answer_status):
        """
        Test that `has_answer_from` method returns appropriate value
        based on number of answer options that learner selected for multiple choice question.

        For ranking questions, learner must rank required number of answer options
        (as specified by `number_of_options_to_rank`) for the LPD to consider the question answered.
        """
        learner = UserFactory()
        question = self.question_factory(
            question_text='How many options will you select?',
            number_of_options_to_rank=2
        )
        self._create_answer_options(
            question, ('A', 'B', 'C', 'D'), fallback_options=(False, False, True, True)
        )
        with patch('lpd.models.AnswerOption.is_selected_by') as patched_is_selected_by:
            patched_is_selected_by.side_effect = answer_option_selection_status
            expected_calls = len(answer_option_selection_status) * [call(learner)]

            has_answer_from_learner = question.has_answer_from(learner)

            patched_is_selected_by.assert_has_calls(expected_calls)
            self.assertEqual(has_answer_from_learner, expected_answer_status)


@ddt.ddt
class LikertScaleQuestionTests(QuantitativeQuestionTestMixin, TestCase):
    """LikertScaleQuestion model tests."""

    def setUp(self):
        super(LikertScaleQuestionTests, self).setUp()
        self.question_factory = LikertScaleQuestionFactory
        self.question = self.question_factory(
            section=self.section,
            question_text='Is this a Likert scale question?',
        )

    def test_str(self):
        """
        Test string representation of `LikertScaleQuestion` model.
        """
        self.assertEqual(
            str(self.question),
            'LPD 1: Test LPD > Section 1: Test section > '
            'LikertScaleQuestion 1: Is this a Likert scale question?'
        )

    def test_type(self):
        """
        Test that `type` property returns appropriate value.
        """
        self.assertEqual(self.question.type, QuestionTypes.LIKERT)

    def test__get_score(self):
        """
        Verify that `_get_score` is stubbed out.
        """
        with self.assertRaises(NotImplementedError):
            LikertScaleQuestion._get_score(42)

    @ddt.data(
        ((False, False, False), 1, False),  # No answers
        ((False, False, True), 1, False),   # No answers for regular options
        ((False, True, False), 1, False),   # Learner provided answer for 1 out of 2 regular options
        ((False, True, True), 1, False),    # Learner provided answer for 1 out of 2 regular options
                                            # and 1 fallback option
        ((True, False, False), 2, False),   # Learner provided answer for 1 out of 2 regular options
        ((True, False, True), 2, False),    # Learner provided answer for 1 out of 2 regular options
                                            # and 1 fallback option
        ((True, True, False), 2, True),     # Learner provided answer for 2 out of 2 regular options
        ((True, True, True), 2, True),      # Learner provided answer for 2 out of 2 regular options
                                            # and 1 fallback option
    )
    @ddt.unpack
    def test_has_answer_from(self, answer_option_selection_status, expected_checks, expected_answer_status):
        """
        Test that `has_answer_from` method returns appropriate value
        based on number of answer options that learner selected for multiple choice question.

        For Likert scale questions, learner must select value for each answer option
        (except for fallback options) for the LPD to consider the question answered.
        """
        learner = UserFactory()
        self._create_answer_options(self.question, ('A', 'B', 'C'), fallback_options=(False, False, True))
        with patch('lpd.models.AnswerOption.is_selected_by') as patched_is_selected_by:
            patched_is_selected_by.side_effect = answer_option_selection_status
            expected_calls = expected_checks * [call(learner)]

            has_answer_from_learner = self.question.has_answer_from(learner)

            patched_is_selected_by.assert_has_calls(expected_calls)
            self.assertEqual(has_answer_from_learner, expected_answer_status)


@ddt.ddt
class AnswerOptionTests(TestCase):
    """AnswerOption model tests."""

    def setUp(self):
        lpd = LearnerProfileDashboardFactory(name='Test LPD')
        section = SectionFactory(lpd=lpd, title='Test section')
        question = MultipleChoiceQuestionFactory(
            section=section,
            question_text='Is this a multiple choice question?',
        )
        self.answer_option = AnswerOption.objects.create(
            content_object=question, option_text='This is not an option.'
        )

    def test_str(self):
        """
        Test string representation of `LikertScaleQuestion` model.
        """
        self.assertEqual(
            str(self.answer_option),
            'LPD 1: Test LPD > Section 1: Test section > '
            'MultipleChoiceQuestion 1: Is this a multiple choice question? > '
            'AnswerOption 1: This is not an option.'
        )

    def test_get_data(self):
        """
        Test that `get_data` returns appropriate data.
        """
        learner = UserFactory()
        self.assertIsNone(self.answer_option.get_data(learner))
        answer = QuantitativeAnswer.objects.create(
            learner=learner,
            answer_option=self.answer_option,
            value=1,
            custom_input="I'm still providing custom input",
        )
        expected_data = {
            'value': answer.value,
            'custom_input': answer.custom_input
        }
        self.assertEqual(self.answer_option.get_data(learner), expected_data)

    @ddt.data(
        (MultipleChoiceQuestionFactory, None, False),
        (RankingQuestionFactory, None, False),
        (LikertScaleQuestionFactory, None, False),
        (MultipleChoiceQuestionFactory, {'value': 0, 'custom_input': ''}, False),
        (MultipleChoiceQuestionFactory, {'value': 0, 'custom_input': 'Yellow'}, False),
        (MultipleChoiceQuestionFactory, {'value': 1, 'custom_input': ''}, True),
        (MultipleChoiceQuestionFactory, {'value': 1, 'custom_input': 'Purple'}, True),
        (RankingQuestionFactory, {'value': 2, 'custom_input': ''}, True),
        (RankingQuestionFactory, {'value': 2, 'custom_input': 'Green'}, True),
        (RankingQuestionFactory, {'value': 5, 'custom_input': ''}, False),  # Mock default for unranked options
        (RankingQuestionFactory, {'value': 5, 'custom_input': 'Blue'}, False),  # Mock default for unranked options
        (LikertScaleQuestionFactory, {'value': 1, 'custom_input': ''}, True),
        (LikertScaleQuestionFactory, {'value': 1, 'custom_input': 'Red'}, True),
    )
    @ddt.unpack
    def test_is_selected_by(self, question_factory, answer_data, expected_selection_status):
        """
        Test that `is_selected_by` method returns appropriate value
        based on `answer_data` for answer option.
        """
        learner = UserFactory()
        question = question_factory()
        answer_option = AnswerOption.objects.create(content_object=question)

        with patch('lpd.models.AnswerOption.get_data') as patched_get_data, \
                patch('lpd.models.RankingQuestion.unranked_option_value') as patched_unranked_option_value:
            patched_get_data.return_value = answer_data
            patched_unranked_option_value.return_value = 5

            selected_by_learner = answer_option.is_selected_by(learner)

            patched_get_data.assert_called_once_with(learner)
            if question_factory == RankingQuestionFactory and answer_data is not None:
                patched_unranked_option_value.assert_called_once_with()

            self.assertEqual(selected_by_learner, expected_selection_status)


class QualitativeAnswerTests(TestCase):
    """QualitativeAnswer model tests."""

    def test_str(self):
        """
        Test string representation of `QualitativeAnswer` model.
        """
        learner = UserFactory()
        for index, qualitative_question_factory in enumerate(QUALITATIVE_QUESTION_FACTORIES, start=1):
            question = qualitative_question_factory()
            qualitative_answer = QualitativeAnswerFactory(
                learner=learner, question=question, text='This is not a qualitative answer.'
            )
            self.assertEqual(
                str(qualitative_answer), 'QualitativeAnswer {id}: This is not a qualitative answer.'.format(id=index)
            )


class QuantitativeAnswerTests(TestCase):
    """QuantitativeAnswer model tests."""

    def test_str(self):
        """
        Test string representation of `QuantitativeAnswer` model.
        """
        learner = UserFactory()
        for index, quantitative_question_factory in enumerate(QUANTITATIVE_QUESTION_FACTORIES, start=1):
            answer_option = AnswerOption.objects.create(content_object=quantitative_question_factory())
            quantitative_answer = QuantitativeAnswer.objects.create(
                learner=learner, answer_option=answer_option, value=42
            )
            self.assertEqual(
                str(quantitative_answer), 'QuantitativeAnswer {id}: 42'.format(id=index)
            )


class KnowledgeComponentTests(TestCase):
    """KnowledgeComponent model tests."""

    def test_str(self):
        """
        Test string representation of `KnowledgeComponent` model.
        """
        # Test string representation of knowledge component that is not associated with an answer option
        knowledge_component = KnowledgeComponent.objects.create(kc_id='test_id', kc_name='test_name')
        self.assertEqual(str(knowledge_component), 'KnowledgeComponent 1: test_id, test_name')

        # Test string representation of knowledge component that is associated with an answer option
        lpd = LearnerProfileDashboardFactory(name='Test LPD')
        section = SectionFactory(lpd=lpd, title='Test section')
        question = MultipleChoiceQuestionFactory(
            section=section,
            question_text='Is this a multiple choice question?',
        )
        AnswerOption.objects.create(
            content_object=question, option_text='This is not an option.',
            knowledge_component=knowledge_component
        )
        self.assertEqual(
            str(knowledge_component),
            'KnowledgeComponent 1: test_id, test_name '
            '(associated with LPD 1: Test LPD > Section 1: Test section > '
            'MultipleChoiceQuestion 1: Is this a multiple choice question? > '
            'AnswerOption 1: This is not an option.)'
        )


class ScoreTests(TestCase):
    """Score model tests."""

    def test_str(self):
        """
        Test string representation of `LikertScaleQuestion` model.
        """
        knowledge_component = KnowledgeComponent.objects.create(kc_id='test_id', kc_name='test_name')
        learner = UserFactory()
        score = Score.objects.create(knowledge_component=knowledge_component, learner=learner, value=23)
        self.assertEqual(str(score), 'Score 1: 23')


class SubmissionTests(UserSetupMixin, TestCase):
    """Submission model tests."""

    def setUp(self):
        self.section = SectionFactory(title='Test section')
        super(SubmissionTests, self).setUp()

    def test_str(self):
        """
        Test string representation of `Submission` model.
        """
        submission = SubmissionFactory(section=self.section, learner=self.student_user)
        self.assertEqual(str(submission), 'Submission 1: Test section, student_user')

    def test_get_last_update(self):
        """
        Test that `get_last_update` behaves correctly for existing and non-existing submissions.

        - If submission does not exist, `get_last_update` should return `None` (and not error out).
        - If submission exists, `get_last_update` should return value of `updated` field.
        """
        # Submission does not exist
        try:
            last_update = Submission.get_last_update(self.section, self.student_user)
        except Submission.DoesNotExist:
            self.fail('`Submission.get_last_update` should not error out if submission does not exist.')
        else:
            self.assertIsNone(last_update)

        # Submission exists
        with freeze_time('2017-01-17 11:25:00') as freezed_time:
            updated = utc.localize(freezed_time())
            SubmissionFactory(section=self.section, learner=self.student_user, updated=updated)
            last_update = Submission.get_last_update(self.section, self.student_user)
            self.assertEqual(last_update, updated)
