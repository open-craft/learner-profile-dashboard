import json

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.test import TestCase
from mock import call, patch

from lpd.constants import QuestionTypes
from lpd.models import AnswerOption, LearnerProfileDashboard, QualitativeAnswer, QuantitativeAnswer, Score
from lpd.tests.factories import (
    KnowledgeComponentFactory,
    MultipleChoiceQuestionFactory,
    QualitativeQuestionFactory,
    RankingQuestionFactory,
)


class UserSetupMixin(object):
    def setUp(self):
        self.password = 'some_password'
        self.user = get_user_model().objects.create(username='student_user')
        self.user.set_password(self.password)
        self.user.save()

        self.user2 = get_user_model().objects.create(username='student_user2')
        self.user2.set_password(self.password)
        self.user2.save()

        self.lpd = LearnerProfileDashboard.objects.create(name='Test LPD')

    def login(self, username=None, password=None):
        username = username if username else self.user.username
        password = password if password else self.password
        self.assertTrue(self.client.login(username=username, password=password))


class LearnerProfileDashboardHomeViewTestCase(UserSetupMixin, TestCase):
    def setUp(self):
        super(LearnerProfileDashboardHomeViewTestCase, self).setUp()
        self.home_url = reverse('lpd:home')

    def test_anonymous(self):
        response = self.client.get(self.home_url)
        login_url = ''.join([reverse('admin:login'), '?next=', self.home_url])
        self.assertRedirects(response, login_url)

    def test_lpd_view(self):
        self.login()
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)


# pylint: disable=too-many-instance-attributes,attribute-defined-outside-init
class LPDSubmitViewTestCase(UserSetupMixin, TestCase):
    """Tests for LPDSubmitView."""

    def setUp(self):
        super(LPDSubmitViewTestCase, self).setUp()
        self.login()
        self.data = {'qualitative_answers': json.dumps([]), 'quantitative_answers': json.dumps([])}

    def _create_quantitative_questions(self):
        """
        Create a set of quantitative questions to use for tests that verify processing of quantitative data.
        """
        self.question1 = MultipleChoiceQuestionFactory(id=1)
        self.question2 = MultipleChoiceQuestionFactory(id=2)
        self.question3 = RankingQuestionFactory(id=3, number_of_options_to_rank=5)

    def _create_knowledge_components(self):
        """
        Create a set of knowledge components to use for tests that verify processing of quantitative data.
        """
        self.knowledge_component1 = KnowledgeComponentFactory(kc_id='test_kc1')
        self.knowledge_component2 = KnowledgeComponentFactory(kc_id='test_kc2')
        self.knowledge_component3 = KnowledgeComponentFactory(kc_id='test_kc3')

    def _create_answer_options(self, influences_recommendations=True, link_knowledge_components=True):
        """
        Create a set of knowledge components to use for tests that verify processing of quantitative data.
        """
        self.answer_option1 = AnswerOption.objects.create(
            id=1,
            content_object=self.question1,
            knowledge_component=self.knowledge_component1 if link_knowledge_components else None,
            influences_recommendations=influences_recommendations,
            allows_custom_input=False,
        )
        self.answer_option2 = AnswerOption.objects.create(
            id=2,
            content_object=self.question2,
            knowledge_component=self.knowledge_component2 if link_knowledge_components else None,
            influences_recommendations=influences_recommendations,
            allows_custom_input=True,
        )
        self.answer_option3 = AnswerOption.objects.create(
            id=3,
            content_object=self.question3,
            knowledge_component=self.knowledge_component3 if link_knowledge_components else None,
            influences_recommendations=influences_recommendations,
            allows_custom_input=False,
        )

    def _assert_quantitative_answer_data(
            self, quantitative_answers, answer_option, expected_value, expected_custom_input
    ):
        """
        Assert that quantitative answer exists for `answer_option` and `self.user`,
        and that it has `expected_value` and `expected_custom_input`.
        """
        answer = quantitative_answers.get(answer_option=answer_option)
        self.assertEqual(answer.learner, self.user)
        self.assertEqual(answer.value, expected_value)
        self.assertEqual(answer.custom_input, expected_custom_input)

    def _assert_score_data(self, scores, knowledge_component, expected_value):
        """
        Assert that score exists for `knowledge_component` and `self.user`,
        and that it has `expected_value`.
        """
        score = scores.get(knowledge_component=knowledge_component)
        self.assertEqual(score.learner, self.user)
        self.assertEqual(score.value, expected_value)

    def test_post_invalid_data(self):
        """
        Test that `post` method returns appropriate response if something goes wrong
        while processing answer data.
        """
        with patch('lpd.views.LPDSubmitView._process_qualitative_answers') as patched_process_qual_answers:
            patched_process_qual_answers.side_effect = IntegrityError
            response = self.client.post(reverse('lpd:submit'), self.data)
            message = json.loads(response.content)['message']
            self.assertEqual(response.status_code, 500)
            self.assertEqual(message, 'Could not update learner answers.')

        with patch('lpd.views.LPDSubmitView._process_quantitative_answers') as patched_process_quant_answers, \
                patch('lpd.views.LPDSubmitView._process_qualitative_answers') as patched_process_qual_answers:
            patched_process_quant_answers.side_effect = IntegrityError
            response = self.client.post(reverse('lpd:submit'), self.data)
            message = json.loads(response.content)['message']
            self.assertEqual(response.status_code, 500)
            self.assertEqual(message, 'Could not update learner answers.')

    def test_post_valid_data(self):
        """
        Test that `post` method returns appropriate response if processing of answer data is successful.
        """
        with patch('lpd.views.LPDSubmitView._process_quantitative_answers'), \
                patch('lpd.views.LPDSubmitView._process_qualitative_answers'):
            response = self.client.post(reverse('lpd:submit'), self.data)
            message = json.loads(response.content)['message']
            self.assertEqual(response.status_code, 200)
            self.assertEqual(message, 'Learner answers updated successfully.')

    # pylint: disable=too-many-locals
    @patch('lpd.views.LPDSubmitView._process_quantitative_answers')
    @patch('lpd.models.calculate_probabilities')
    def test_post_process_qualitative_answers(
            self, patched_calculate_probabilities, patched_pqa):
        """
        Test that `post` correctly processes qualitative answers.
        """
        question1 = QualitativeQuestionFactory(id=1)
        question2 = QualitativeQuestionFactory(id=2)
        knowledge_component1 = KnowledgeComponentFactory(kc_id='test_kc_id_1')
        knowledge_component2 = KnowledgeComponentFactory(kc_id='test_kc_id_2')
        qualitative_answers = [
            {
                'question_id': 1,
                'answer_text': 'This is a very clever answer.',
            },
            {
                'question_id': 2,
                'answer_text': 'This is not a very clever answer, but an answer nonetheless.',
            }
        ]
        self.data['qualitative_answers'] = json.dumps(qualitative_answers)

        group_probabilities = {
            knowledge_component1.kc_id: 0.1,
            knowledge_component2.kc_id: 0.9
        }
        expected_scores = {
            kc_id: 1.0 - value
            for kc_id, value in group_probabilities.items()
        }
        patched_calculate_probabilities.return_value = group_probabilities

        response = self.client.post(reverse('lpd:submit'), self.data)
        self.assertEqual(response.status_code, 200)

        qualitative_answers = QualitativeAnswer.objects.all()
        self.assertEqual(qualitative_answers.count(), 2)

        answer1 = qualitative_answers.get(question=question1)
        self.assertEqual(answer1.learner, self.user)
        self.assertEqual(answer1.text, 'This is a very clever answer.')

        answer2 = qualitative_answers.get(question=question2)
        self.assertEqual(answer2.learner, self.user)
        self.assertEqual(answer2.text, 'This is not a very clever answer, but an answer nonetheless.')

        scores = Score.objects.all()
        self.assertEqual(scores.count(), 2)

        score1 = scores.get(knowledge_component=knowledge_component1)
        self.assertEqual(score1.learner, self.user)
        self.assertAlmostEqual(
            score1.value, expected_scores[knowledge_component1.kc_id]
        )

        score2 = scores.get(knowledge_component=knowledge_component2)
        self.assertEqual(score2.learner, self.user)
        self.assertAlmostEqual(
            score2.value, expected_scores[knowledge_component2.kc_id]
        )

    def test_post_quant_answer_not_meaningful(self):
        """
        Test that `post` correctly processes qualitative answer whose value is not meaningful.

        When dealing with values that are not meaningful,
        no answers or scores should be created.

        The only question type for which `post` might receive a value that is not meaningful (i.e., `None`)
        is `QuestionTypes.LIKERT`. See `QuantitativeQuestion.get_value` for details.
        """
        quantitative_answers = [
            {
                'question_id': 4,
                'question_type': QuestionTypes.LIKERT,
                'answer_option_id': 4,
                'answer_option_value': None,
            },
        ]
        self.data['quantitative_answers'] = json.dumps(quantitative_answers)
        with patch('lpd.views.LPDSubmitView._process_qualitative_answers'):
            response = self.client.post(reverse('lpd:submit'), self.data)
            self.assertEqual(response.status_code, 200)

            quantitative_answers = QuantitativeAnswer.objects.all()
            self.assertEqual(quantitative_answers.count(), 0)

            scores = Score.objects.all()
            self.assertEqual(scores.count(), 0)

    def test_post_quant_answers_meaningful(self):
        """
        Test that `post` correctly processes qualitative answers whose values are meaningful.

        When dealing with values that are meaningful
        and corresponding answer options are configured to influence recommendations,
        appropriate answers and scores should be created.
        """
        self._create_quantitative_questions()
        self._create_knowledge_components()
        self._create_answer_options(influences_recommendations=True, link_knowledge_components=True)

        quantitative_answers = [
            {
                'question_id': 1,
                'question_type': QuestionTypes.MCQ,
                'answer_option_id': 1,
                'answer_option_value': 1,
                'answer_option_custom_input': '',
            },
            {
                'question_id': 2,
                'question_type': QuestionTypes.MRQ,
                'answer_option_id': 2,
                'answer_option_value': 0,
                'answer_option_custom_input': 'Yellow',
            },
            {
                'question_id': 3,
                'question_type': QuestionTypes.RANKING,
                'answer_option_id': 3,
                'answer_option_value': 5,
            },
        ]
        self.data['quantitative_answers'] = json.dumps(quantitative_answers)
        with patch('lpd.views.LPDSubmitView._process_qualitative_answers'):
            response = self.client.post(reverse('lpd:submit'), self.data)
            self.assertEqual(response.status_code, 200)

            quantitative_answers = QuantitativeAnswer.objects.all()
            self.assertEqual(quantitative_answers.count(), 3)

            scores = Score.objects.all()
            self.assertEqual(scores.count(), 3)

            # Check answers individually
            self._assert_quantitative_answer_data(quantitative_answers, self.answer_option1, 1, '')
            self._assert_quantitative_answer_data(quantitative_answers, self.answer_option2, 0, 'Yellow')
            self._assert_quantitative_answer_data(quantitative_answers, self.answer_option3, 5, None)

            # Check scores individually
            self._assert_score_data(scores, self.knowledge_component1, 0)
            self._assert_score_data(scores, self.knowledge_component2, 1)
            self._assert_score_data(scores, self.knowledge_component3, 0.8)

    def test_post_quant_answers_no_influence(self):
        """
        Test that `post` correctly processes qualitative answers belonging to answer options
        that are not configured to influence recommendations.

        When dealing with values that are meaningful
        and corresponding answer options are *not* configured to influence recommendations,
        appropriate answers should be created, but `post` should skip creating scores.
        """
        self._create_quantitative_questions()
        self._create_knowledge_components()
        self._create_answer_options(influences_recommendations=False, link_knowledge_components=True)

        quantitative_answers = [
            {
                'question_id': 1,
                'question_type': QuestionTypes.MCQ,
                'answer_option_id': 1,
                'answer_option_value': 1,
            },
            {
                'question_id': 2,
                'question_type': QuestionTypes.MRQ,
                'answer_option_id': 2,
                'answer_option_value': 0,
                'answer_option_custom_input': 'Yellow',
            },
            {
                'question_id': 3,
                'question_type': QuestionTypes.RANKING,
                'answer_option_id': 3,
                'answer_option_value': 5,
            },
        ]
        self.data['quantitative_answers'] = json.dumps(quantitative_answers)
        with patch('lpd.views.LPDSubmitView._process_qualitative_answers'):
            response = self.client.post(reverse('lpd:submit'), self.data)
            self.assertEqual(response.status_code, 200)

            quantitative_answers = QuantitativeAnswer.objects.all()
            self.assertEqual(quantitative_answers.count(), 3)

            scores = Score.objects.all()
            self.assertEqual(scores.count(), 0)

            # Check answers individually
            self._assert_quantitative_answer_data(quantitative_answers, self.answer_option1, 1, None)
            self._assert_quantitative_answer_data(quantitative_answers, self.answer_option2, 0, 'Yellow')
            self._assert_quantitative_answer_data(quantitative_answers, self.answer_option3, 5, None)

    def test_post_quant_answers_no_kc(self):
        """
        Test that `post` correctly processes qualitative answers belonging to answer options
        that are configured to influence recommendations, but aren't linked to a knowledge component.

        Note that this is an edge case that should not come up in practice:
        Conceptually, each answer option that should influence recommendations
        needs to be linked to a knowledge component.

        When dealing with values that are meaningful
        and corresponding answer options are configured to influence recommendations
        but aren't linked to a knowledge component,
        appropriate answers should be created, but `post` should skip creating scores.
        """
        self._create_quantitative_questions()
        self._create_answer_options(influences_recommendations=True, link_knowledge_components=False)

        quantitative_answers = [
            {
                'question_id': 1,
                'question_type': QuestionTypes.MCQ,
                'answer_option_id': 1,
                'answer_option_value': 1,
            },
            {
                'question_id': 2,
                'question_type': QuestionTypes.MRQ,
                'answer_option_id': 2,
                'answer_option_value': 0,
                'answer_option_custom_input': 'Yellow',
            },
            {
                'question_id': 3,
                'question_type': QuestionTypes.RANKING,
                'answer_option_id': 3,
                'answer_option_value': 5,
            },
        ]
        self.data['quantitative_answers'] = json.dumps(quantitative_answers)
        with patch('lpd.views.LPDSubmitView._process_qualitative_answers'), \
                patch('lpd.views.log.error') as patched_error:
            response = self.client.post(reverse('lpd:submit'), self.data)
            self.assertEqual(response.status_code, 200)

            quantitative_answers = QuantitativeAnswer.objects.all()
            self.assertEqual(quantitative_answers.count(), 3)

            scores = Score.objects.all()
            self.assertEqual(scores.count(), 0)

            # Check answers individually
            self._assert_quantitative_answer_data(quantitative_answers, self.answer_option1, 1, None)
            self._assert_quantitative_answer_data(quantitative_answers, self.answer_option2, 0, 'Yellow')
            self._assert_quantitative_answer_data(quantitative_answers, self.answer_option3, 5, None)

            # Make sure that log.error was called to report the situation
            patched_error.assert_has_calls([
                call('Could not create score because %s is not linked to a knowledge component.', self.answer_option1),
                call('Could not create score because %s is not linked to a knowledge component.', self.answer_option2),
                call('Could not create score because %s is not linked to a knowledge component.', self.answer_option3),
            ])


class LearnerProfileDashboardCreateViewTestCase(UserSetupMixin, TestCase):
    def setUp(self):
        super(LearnerProfileDashboardCreateViewTestCase, self).setUp()
        self.add_url = reverse('lpd:add')

    def test_anonymous(self):
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.add_url)
        login_url = ''.join([reverse('admin:login'), '?next=', self.add_url])
        self.assertRedirects(response, login_url)

    def test_invalid(self):
        self.login()
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.add_url)
        self.assertEqual(response.status_code, 200)

    def test_valid(self):
        self.login()
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)

        post_data = {'name': 'Test LPD'}
        response = self.client.post(self.add_url, post_data)
        lpd = LearnerProfileDashboard.objects.order_by('-id')[0]
        self.assertRedirects(response, reverse('lpd:view', kwargs=dict(pk=lpd.id)))


class LearnerProfileDashboardUpdateViewTestCase(UserSetupMixin, TestCase):
    def setUp(self):
        super(LearnerProfileDashboardUpdateViewTestCase, self).setUp()
        self.lpd = LearnerProfileDashboard.objects.create(name='Test LPD')
        self.view_url = reverse('lpd:view', kwargs=dict(pk=self.lpd.id))
        self.edit_url = reverse('lpd:edit', kwargs=dict(pk=self.lpd.id))
        self.login_url = ''.join([reverse('admin:login'), '?next=', self.edit_url])

    def test_anonymous(self):
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.edit_url)
        self.assertRedirects(response, self.login_url)

    def test_valid(self):
        self.login()
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)

        post_data = {'name': 'Test LPD: Update'}
        response = self.client.post(self.edit_url, post_data)
        self.assertRedirects(response, self.view_url)
        response = self.client.get(self.view_url)
        self.assertEquals(response.context['object'].name, post_data['name'])
