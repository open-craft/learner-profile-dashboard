import logging
import random

from django.test import TestCase

from lpd.constants import QuestionTypes
from lpd.models import (
    AnswerOption,
    KnowledgeComponent,
    LearnerProfileDashboard,
    QuantitativeAnswer,
    RankingQuestion,
    Score
)
from lpd.tests.factories import (
    LearnerProfileDashboardFactory,
    LikertScaleQuestionFactory,
    MultipleChoiceQuestionFactory,
    QualitativeAnswerFactory,
    QualitativeQuestionFactory,
    RankingQuestionFactory,
    SectionFactory,
    UserFactory
)


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

class LearnerProfileDashboardTests(TestCase):
    """LearnerProfileDashboard model tests."""

    def test_str(self):
        """
        Test string representation of `LearnerProfileDashboard` model.
        """
        lpd = LearnerProfileDashboard(name='Empty LPD')
        self.assertEquals(str(lpd), 'Empty LPD')


class SectionTests(TestCase):
    """Section model tests."""

    def setUp(self):
        self.lpd = LearnerProfileDashboardFactory(name='Test LPD')

    def test_str(self):
        """
        Test string representation of `Section` model.
        """
        section = SectionFactory(lpd=self.lpd, title='Basic information')
        self.assertEquals(str(section), 'Section 1: Basic information')

    def test_questions(self):
        """
        Test that `questions` property returns questions belonging to `Section` in appropriate order.
        """
        log.info('Testing `questions` property of `Section` model.')
        section = SectionFactory(lpd=self.lpd, title='Details, Details, Details')
        questions = []
        question_numbers = sorted(random.sample(range(1, 100), QUESTION_BATCH_SIZE*len(QUESTION_FACTORIES)))
        for unused in range(QUESTION_BATCH_SIZE):
            for question_factory in QUESTION_FACTORIES:
                question_number = question_numbers.pop(0)
                log.info('Creating question #%d using %s.', question_number, question_factory)
                question = question_factory(section=section, number=question_number)
                questions.append(question)
        self.assertEqual(section.questions, questions)


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
            question_factory = random.choice(QUESTION_FACTORIES)
            log.info('Creating %d questions using %s.', QUESTION_BATCH_SIZE, question_factory)
            questions = question_factory.build_batch(QUESTION_BATCH_SIZE, section=section)
            for question in questions:
                self.assertEqual(question.section_number, '{}.{}'.format(section.order, question.number))


class QualitativeQuestionTests(TestCase):
    """QualitativeQuestion model tests."""

    def test_str(self):
        """
        Test string representation of `QualitativeQuestion` model.
        """
        question = QualitativeQuestionFactory(question_text='Is this a qualitative question?')
        self.assertEqual(str(question), 'QualitativeQuestion 1: Is this a qualitative question?')

    def test_type(self):
        """
        Test that `type` property returns appropriate value.
        """
        essay_question = QualitativeQuestionFactory(question_type=QuestionTypes.ESSAY)
        short_answer_question = QualitativeQuestionFactory(question_type=QuestionTypes.SHORT_ANSWER)
        self.assertEqual(essay_question.type, QuestionTypes.ESSAY)
        self.assertEqual(short_answer_question.type, QuestionTypes.SHORT_ANSWER)

    def test_get_answer(self):
        """
        Test that `get_answer` method returns appropriate value.
        """
        question = QualitativeQuestionFactory()
        learner = UserFactory()
        self.assertEqual(question.get_answer(learner), '')
        answer = QualitativeAnswerFactory(learner=learner, question=question, text='This is not an answer.')
        self.assertEqual(question.get_answer(learner), answer.text)


class QuantitativeQuestionTestMixin(object):
    """Mixin for tests targeting QuantitativeQuestion models."""

    def test_get_answer_options(self):
        """
        Test that `get_answer_options` returns answer options in appropriate order.
        """
        question = self.question_factory(randomize_options=True)
        answer_option0 = AnswerOption.objects.create(content_object=question, option_text='Yellow')
        answer_option1 = AnswerOption.objects.create(content_object=question, option_text='Blue')
        answer_option2 = AnswerOption.objects.create(content_object=question, option_text='Red')
        answer_options = list(question.get_answer_options())
        # Question is configured to display answer options in random order,
        # so we only need to check if `get_answer_options` returns all answer options (and no more)
        self.assertEqual(len(answer_options), 3)
        for answer_option in [answer_option0, answer_option1, answer_option2]:
            self.assertIn(answer_option, answer_options)

        question.randomize_options = False
        question.save()
        answer_options = list(question.get_answer_options())
        # Question is configured *not* to display answer options in random order,
        # so we need to check if `get_answer_options` returns answer options in alphabetical order.
        self.assertEqual(len(answer_options), 3)
        self.assertEqual(answer_options, [answer_option1, answer_option2, answer_option0])


class MultipleChoiceQuestionTests(TestCase, QuantitativeQuestionTestMixin):
    """MultipleChoiceQuestion model tests."""

    def setUp(self):
        self.question_factory = MultipleChoiceQuestionFactory

    def test_str(self):
        """
        Test string representation of `MultipleChoiceQuestion` model.
        """
        question = self.question_factory(question_text='Is this a multiple choice question?')
        self.assertEqual(str(question), 'MultipleChoiceQuestion 1: Is this a multiple choice question?')

    def test_type(self):
        """
        Test that `type` property returns appropriate value.
        """
        mcq = self.question_factory(max_options_to_select=1)
        mrq = self.question_factory(max_options_to_select=5)
        self.assertEqual(mcq.type, QuestionTypes.MCQ)
        self.assertEqual(mrq.type, QuestionTypes.MRQ)


class RankingQuestionTests(TestCase, QuantitativeQuestionTestMixin):
    """RankingQuestion model tests."""

    def setUp(self):
        self.question_factory = RankingQuestionFactory

    def test_str(self):
        """
        Test string representation of `RankingQuestion` model.
        """
        question = self.question_factory(question_text='Is this a ranking question?')
        self.assertEqual(str(question), 'RankingQuestion 1: Is this a ranking question?')

    def test_type(self):
        """
        Test that `type` property returns appropriate value.
        """
        question = self.question_factory()
        self.assertEqual(question.type, QuestionTypes.RANKING)

    def test_unranked_option_value(self):
        """
        Test that `unranked_option_value` returns appropriate value.
        """
        for rank in [3, 5, 10]:
            self.question_factory(number_of_options_to_rank=rank)
        self.assertEqual(RankingQuestion.unranked_option_value(), 11)


class LikertScaleQuestionTests(TestCase, QuantitativeQuestionTestMixin):
    """LikertScaleQuestion model tests."""

    def setUp(self):
        self.question_factory = LikertScaleQuestionFactory

    def test_str(self):
        """
        Test string representation of `LikertScaleQuestion` model.
        """
        question = self.question_factory(question_text='Is this a Likert scale question?')
        self.assertEqual(str(question), 'LikertScaleQuestion 1: Is this a Likert scale question?')

    def test_type(self):
        """
        Test that `type` property returns appropriate value.
        """
        question = self.question_factory()
        self.assertEqual(question.type, QuestionTypes.LIKERT)


class AnswerOptionTests(TestCase):
    """AnswerOption model tests."""

    def test_str(self):
        """
        Test string representation of `LikertScaleQuestion` model.
        """
        question = MultipleChoiceQuestionFactory()
        answer_option = AnswerOption.objects.create(content_object=question, option_text='This is not an option.')
        self.assertEqual(str(answer_option), 'AnswerOption 1: This is not an option.')

    def test_get_data(self):
        """
        Test that `get_data` returns appropriate data.
        """
        question = MultipleChoiceQuestionFactory()
        learner = UserFactory()
        answer_option = AnswerOption.objects.create(content_object=question, option_text='This is not an option.')
        self.assertIsNone(answer_option.get_data(learner))
        answer = QuantitativeAnswer.objects.create(
            learner=learner,
            answer_option=answer_option,
            value=1,
            custom_input="I'm still providing custom input",
        )
        expected_data = {
            'value': answer.value,
            'custom_input': answer.custom_input
        }
        self.assertEqual(answer_option.get_data(learner), expected_data)


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
        knowledge_component = KnowledgeComponent.objects.create(kc_id='test_id', kc_name='test_name')
        self.assertEqual(str(knowledge_component), 'KnowledgeComponent 1: test_id, test_name')


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
