"""
View tests for Learner Profile Dashboard
"""

import json

from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.test import TestCase
from mock import call, MagicMock, patch
from requests import ConnectionError

from lpd.constants import QuestionTypes
from lpd.models import (
    AnswerOption,
    LearnerProfileDashboard,
    QualitativeAnswer,
    QuantitativeAnswer,
    Score,
    Section,
    Submission,
)
from lpd.tests.factories import (
    KnowledgeComponentFactory,
    MultipleChoiceQuestionFactory,
    QualitativeQuestionFactory,
    RankingQuestionFactory,
    SectionFactory,
)
from lpd.tests.mixins import UserSetupMixin


class LPDViewTests(UserSetupMixin, TestCase):
    """
    Tests for LPDView.
    """
    def setUp(self):
        super(LPDViewTests, self).setUp()
        self.home_url = reverse('lpd:home')

    def test_anonymous(self):
        """
        Test that home URL redirects to admin login for unauthenticated users.
        """
        response = self.client.get(self.home_url)
        login_url = ''.join([reverse('admin:login'), '?next=', self.home_url])
        self.assertRedirects(response, login_url)

    def test_lpd_view(self):
        """
        Test that authenticated users can access home URL.
        """
        self.login()
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)


# pylint: disable=too-many-instance-attributes,attribute-defined-outside-init
class LPDSubmitViewTests(UserSetupMixin, TestCase):
    """
    Tests for LPDSubmitView.
    """

    def setUp(self):
        super(LPDSubmitViewTests, self).setUp()
        self.section = SectionFactory()
        self.login()
        self.data = {
            'section_id': 1,
            'qualitative_answers': json.dumps([]),
            'quantitative_answers': json.dumps([]),
        }

    def _create_qualitative_questions(self, questions_influence_group_membership=False):
        """
        Create a set of qualitative questions to use for tests that verify processing of qualitative data.
        """
        self.question1 = QualitativeQuestionFactory(
            id=1, influences_group_membership=questions_influence_group_membership
        )
        self.question2 = QualitativeQuestionFactory(
            id=2, influences_group_membership=questions_influence_group_membership
        )

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

    def _assert_qualitative_answer_data(
            self, qualitative_answers, question, expected_text
    ):
        """
        Assert that quantitative answer exists for `answer_option` and `self.user`,
        and that it has `expected_value` and `expected_custom_input`.
        """
        answer = qualitative_answers.get(question=question)
        self.assertEqual(answer.learner, self.user)
        self.assertEqual(answer.text, expected_text)

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

    def _assert_score_data_equal(self, scores, knowledge_component, expected_value):
        """
        Assert that score exists for `knowledge_component` and `self.user`,
        and that its value exactly matches `expected_value`.
        """
        score = scores.get(knowledge_component=knowledge_component)
        self.assertEqual(score.learner, self.user)
        self.assertEqual(score.value, expected_value)

    def _assert_score_data_almost_equal(self, scores, knowledge_component, expected_value):
        """
        Assert that score exists for `knowledge_component` and `self.user`,
        and that its value roughly matches `expected_value`.
        """
        score = scores.get(knowledge_component=knowledge_component)
        self.assertEqual(score.learner, self.user)
        self.assertAlmostEqual(score.value, expected_value)

    def _assert_submission_data(self):
        """
        Assert that submission data matches expectations.
        """
        submissions = Submission.objects.all()
        self.assertEqual(submissions.count(), 1)

        submission = Submission.objects.get()
        self.assertEqual(submission.section, self.section)
        self.assertEqual(submission.learner, self.user)

    def test_post_invalid_data(self):
        """
        Test that `post` method returns appropriate response if something goes wrong
        while processing learner profile data.
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

        with patch('lpd.views.LPDSubmitView._process_quantitative_answers') as patched_process_quant_answers, \
                patch('lpd.views.LPDSubmitView._process_qualitative_answers') as patched_process_qual_answers, \
                patch('lpd.views.AdaptiveEngineAPIClient.send_learner_data') as patched_send_learner_data:
            patched_send_learner_data.side_effect = ConnectionError
            response = self.client.post(reverse('lpd:submit'), self.data)
            message = json.loads(response.content)['message']
            self.assertEqual(response.status_code, 500)
            self.assertEqual(message, 'Could not transmit scores to adaptive engine.')

        with patch('lpd.views.LPDSubmitView._process_quantitative_answers') as patched_process_quant_answers, \
                patch('lpd.views.LPDSubmitView._process_qualitative_answers') as patched_process_qual_answers, \
                patch('lpd.views.AdaptiveEngineAPIClient.send_learner_data') as patched_send_learner_data, \
                patch('lpd.views.LPDSubmitView._process_submission') as patched_process_submission:
            patched_process_submission.side_effect = Section.DoesNotExist
            response = self.client.post(reverse('lpd:submit'), self.data)
            message = json.loads(response.content)['message']
            self.assertEqual(response.status_code, 500)
            self.assertEqual(message, 'Could not update submission data.')

    @patch('lpd.client.AdaptiveEngineAPIClient.send_learner_data')
    @patch('lpd.views.LPDSubmitView._process_quantitative_answers')
    @patch('lpd.views.LPDSubmitView._process_qualitative_answers')
    def test_post_valid_data(
            self, patched_process_qual_answers, patched_process_quant_answers, patched_send_learner_data
    ):
        """
        Test that `post` method returns appropriate response if processing of answer data is successful.
        """
        response = self.client.post(reverse('lpd:submit'), self.data)
        message = json.loads(response.content)['message']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message, 'Learner answers updated successfully.')

    @patch('lpd.client.AdaptiveEngineAPIClient.send_learner_data')
    @patch('lpd.views.LPDSubmitView._process_quantitative_answers')
    @patch('lpd.views.LPDSubmitView._process_qualitative_answers')
    def test_post_valid_data_connection_error(
            self, patched_process_qual_answers, patched_process_quant_answers, patched_send_learner_data
    ):
        """
        Test that `post` method returns appropriate response if processing of answer data is successful.
        """
        patched_send_learner_data.side_effect = ConnectionError
        response = self.client.post(reverse('lpd:submit'), self.data)
        message = json.loads(response.content)['message']
        self.assertEqual(response.status_code, 500)
        self.assertEqual(message, 'Could not transmit scores to adaptive engine.')

    @patch('lpd.models.QualitativeQuestion.update_scores')
    @patch('lpd.client.AdaptiveEngineAPIClient.send_learner_data')
    @patch('lpd.views.LPDSubmitView._process_quantitative_answers', new=MagicMock(return_value=[]))
    def test_post_no_qualitative_answers(self, patched_send_learner_data, patched_update_scores):
        """
        Test that `post` behaves correctly if learner didn't change any of their answers to qualitative questions.

        In this case, `post` should:

        - Skip group membership calculation in this case.
        - Not attempt to send any data to the adaptive engine.
        - Update submission data.
        """
        qualitative_answers = []
        self.data['qualitative_answers'] = json.dumps(qualitative_answers)

        response = self.client.post(reverse('lpd:submit'), self.data)
        self.assertEqual(response.status_code, 200)

        qualitative_answers = QualitativeAnswer.objects.all()
        self.assertEqual(qualitative_answers.count(), 0)

        scores = Score.objects.all()
        self.assertEqual(scores.count(), 0)

        # Make sure group membership calculation was skipped
        patched_update_scores.assert_not_called()
        # Make sure no learner data was sent to adaptive engine
        patched_send_learner_data.assert_not_called()
        # Make sure submission data was updated
        self._assert_submission_data()

    @patch('lpd.models.QualitativeQuestion.update_scores')
    @patch('lpd.client.AdaptiveEngineAPIClient.send_learner_data')
    @patch('lpd.views.LPDSubmitView._process_quantitative_answers', new=MagicMock(return_value=[]))
    def test_post_qual_answers_no_influence(self, patched_send_learner_data, patched_update_scores):
        """
        Test that `post` behaves correctly if qualitative answers are not set up to influence group membership.

        In this case, `post` should:

        - Skip group membership calculation in this case.
        - Not attempt to send any data to the adaptive engine.
        - Update submission data.
        """
        self._create_qualitative_questions(questions_influence_group_membership=False)
        self._create_knowledge_components()

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

        response = self.client.post(reverse('lpd:submit'), self.data)
        self.assertEqual(response.status_code, 200)

        qualitative_answers = QualitativeAnswer.objects.all()
        self.assertEqual(qualitative_answers.count(), 2)

        scores = Score.objects.all()
        self.assertEqual(scores.count(), 0)

        # Make sure group membership calculation was skipped
        patched_update_scores.assert_not_called()
        # Make sure no learner data was sent to adaptive engine
        patched_send_learner_data.assert_not_called()
        # Make sure submission data was updated
        self._assert_submission_data()

    @patch('lpd.models.calculate_probabilities')
    @patch('lpd.client.AdaptiveEngineAPIClient.send_learner_data')
    @patch('lpd.views.LPDSubmitView._process_quantitative_answers', new=MagicMock(return_value=[]))
    def test_post_qualitative_answers(self, patched_send_learner_data, patched_calculate_probabilities):
        """
        Test that `post` correctly processes qualitative answers.
        """
        self._create_qualitative_questions(questions_influence_group_membership=True)
        self._create_knowledge_components()

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

        # Note that group probabilities do not need to sum up to 1.
        group_probabilities = {
            self.knowledge_component1.kc_id: 0.1,
            self.knowledge_component2.kc_id: 0.9,
            self.knowledge_component3.kc_id: 0.7,
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

        scores = Score.objects.all()
        self.assertEqual(scores.count(), 3)

        # Check answers individually
        self._assert_qualitative_answer_data(
            qualitative_answers, self.question1, 'This is a very clever answer.'
        )
        self._assert_qualitative_answer_data(
            qualitative_answers, self.question2, 'This is not a very clever answer, but an answer nonetheless.'
        )

        # Check scores individually
        self._assert_score_data_almost_equal(
            scores, self.knowledge_component1, expected_scores[self.knowledge_component1.kc_id]
        )
        self._assert_score_data_almost_equal(
            scores, self.knowledge_component2, expected_scores[self.knowledge_component2.kc_id]
        )
        self._assert_score_data_almost_equal(
            scores, self.knowledge_component3, expected_scores[self.knowledge_component3.kc_id]
        )

        # Make sure correct set of scores was passed to method for sending learner data to adaptive engine
        patched_send_learner_data.assert_called_once_with(self.user, list(scores))

        # Make sure submission data was updated
        self._assert_submission_data()

    @patch('lpd.client.AdaptiveEngineAPIClient.send_learner_data')
    @patch('lpd.views.LPDSubmitView._process_qualitative_answers', new=MagicMock(return_value=[]))
    def test_post_quant_answer_not_meaningful(self, patched_send_learner_data):
        """
        Test that `post` correctly processes quantitative answer whose value is not meaningful.

        When dealing with values that are not meaningful:

        - No answers or scores should be created.
        - No data should be sent to the adaptive engine.
        - A `Submission` should be created/updated to record the event.

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

        response = self.client.post(reverse('lpd:submit'), self.data)
        self.assertEqual(response.status_code, 200)

        quantitative_answers = QuantitativeAnswer.objects.all()
        self.assertEqual(quantitative_answers.count(), 0)

        scores = Score.objects.all()
        self.assertEqual(scores.count(), 0)

        # Make sure no learner data was sent to adaptive engine
        patched_send_learner_data.assert_not_called()
        # Make sure submission data was updated
        self._assert_submission_data()

    @patch('lpd.client.AdaptiveEngineAPIClient.send_learner_data')
    @patch('lpd.views.LPDSubmitView._process_qualitative_answers', new=MagicMock(return_value=[]))
    def test_post_quant_answers_meaningful(self, patched_send_learner_data):
        """
        Test that `post` correctly processes quantitative answers whose values are meaningful.

        When dealing with values that are meaningful
        and corresponding answer options are configured to influence recommendations,
        appropriate answers and scores should be created,
        and a `Submission` should be created/updated to record the event.
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
        self._assert_score_data_equal(scores, self.knowledge_component1, 0)
        self._assert_score_data_equal(scores, self.knowledge_component2, 1)
        self._assert_score_data_equal(scores, self.knowledge_component3, 0.8)

        # Make sure correct set of scores was passed to method for sending learner data to adaptive engine
        patched_send_learner_data.assert_called_once_with(self.user, list(scores))

        # Make sure submission data was updated
        self._assert_submission_data()

    @patch('lpd.client.AdaptiveEngineAPIClient.send_learner_data')
    @patch('lpd.views.LPDSubmitView._process_qualitative_answers', new=MagicMock(return_value=[]))
    def test_post_quant_answers_no_influence(self, patched_send_learner_data):
        """
        Test that `post` correctly processes quantitative answers belonging to answer options
        that are not configured to influence recommendations.

        When dealing with values that are meaningful
        and corresponding answer options are *not* configured to influence recommendations,
        appropriate answers should be created, but `post` should skip creating scores,
        and should not send any data to the adaptive engine. Also, a `Submission`
        should be created/updated to record the event.
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

        # Make sure no learner data was sent to adaptive engine
        patched_send_learner_data.assert_not_called()
        # Make sure submission data was updated
        self._assert_submission_data()

    @patch('lpd.client.AdaptiveEngineAPIClient.send_learner_data')
    @patch('lpd.views.log.error')
    @patch('lpd.views.LPDSubmitView._process_qualitative_answers', new=MagicMock(return_value=[]))
    def test_post_quant_answers_no_kc(self, patched_error, patched_send_learner_data):
        """
        Test that `post` correctly processes quantitative answers belonging to answer options
        that are configured to influence recommendations, but aren't linked to a knowledge component.

        Note that this is an edge case that should not come up in practice:
        Conceptually, each answer option that should influence recommendations
        needs to be linked to a knowledge component.

        When dealing with values that are meaningful
        and corresponding answer options are configured to influence recommendations
        but aren't linked to a knowledge component,
        appropriate answers should be created, but `post` should skip creating scores,
        and should not send any data to the adaptive engine. Also, a `Submission`
        should be created/updated to record the event.
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

        # Make sure no learner data was sent to adaptive engine
        patched_send_learner_data.assert_not_called()

        # Make sure submission data was updated
        self._assert_submission_data()


class CreateLearnerProfileDashboardViewTests(UserSetupMixin, TestCase):
    """
    Tests for CreateLearnerProfileDashboardView.
    """

    def setUp(self):
        super(CreateLearnerProfileDashboardViewTests, self).setUp()
        self.add_url = reverse('lpd:add')

    def test_anonymous(self):
        """
        Test that anonymous user can access view for creating LPDs,
        and is prompted to log in when trying to create an LPD.
        """
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.add_url)
        login_url = ''.join([reverse('admin:login'), '?next=', self.add_url])
        self.assertRedirects(response, login_url)

    def test_invalid(self):
        """
        Test that create view behaves correctly when POSTing invalid data.
        """
        self.login()
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.add_url)
        self.assertEqual(response.status_code, 200)

    def test_valid(self):
        """
        Test that create view behaves correctly when POSTing valid data.
        """
        self.login()
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)

        post_data = {'name': 'Test LPD'}
        response = self.client.post(self.add_url, post_data)
        lpd = LearnerProfileDashboard.objects.order_by('-id')[0]
        self.assertRedirects(response, reverse('lpd:view', kwargs=dict(pk=lpd.id)))


class UpdateLearnerProfileDashboardViewTests(UserSetupMixin, TestCase):
    """
    Tests for UpdateLearnerProfileDashboardView.
    """
    def setUp(self):
        super(UpdateLearnerProfileDashboardViewTests, self).setUp()
        self.lpd = LearnerProfileDashboard.objects.create(name='Test LPD')
        self.view_url = reverse('lpd:view', kwargs=dict(pk=self.lpd.id))
        self.edit_url = reverse('lpd:edit', kwargs=dict(pk=self.lpd.id))
        self.login_url = ''.join([reverse('admin:login'), '?next=', self.edit_url])

    def test_anonymous(self):
        """
        Test that anonymous user can access view for updating LPDs,
        and is prompted to log in when trying to update an LPD.
        """
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.edit_url)
        self.assertRedirects(response, self.login_url)

    def test_valid(self):
        """
        Test that update view behaves correctly when POSTing valid data.
        """
        self.login()
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)

        post_data = {'name': 'Test LPD: Update'}
        response = self.client.post(self.edit_url, post_data)
        self.assertRedirects(response, self.view_url)
        response = self.client.get(self.view_url)
        self.assertEquals(response.context['object'].name, post_data['name'])
