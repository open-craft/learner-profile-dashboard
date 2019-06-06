# pylint: disable=too-many-lines

"""
View tests for Learner Profile Dashboard
"""

import json
import logging

import ddt
from django.db import IntegrityError
from django.test import override_settings, TestCase
from django.urls import reverse
from freezegun import freeze_time
from mock import call, MagicMock, patch, PropertyMock
from requests import ConnectionError

from lpd.constants import QuestionTypes
from lpd import models
from lpd.tests.factories import (
    KnowledgeComponentFactory,
    LearnerProfileDashboardFactory,
    LikertScaleQuestionFactory,
    MultipleChoiceQuestionFactory,
    QualitativeQuestionFactory,
    RankingQuestionFactory,
    SectionFactory,
)
from lpd.tests.mixins import UserSetupMixin


def silence_request_warnings(test_function):
    """
    Decorator for `test_function` that will keep it from throwing warnings about 404s or 405s.

    Cf. https://stackoverflow.com/a/46079090/1199226
    """
    def wrapper(*args, **kwargs):
        """
        Run test_function with log level raised.
        """
        # Raise logging level to ERROR
        request_logger = logging.getLogger('django.request')
        default_log_level = request_logger.getEffectiveLevel()
        request_logger.setLevel(logging.ERROR)

        # Run test
        test_function(*args, **kwargs)

        # Reset log level to default
        request_logger.setLevel(default_log_level)

    return wrapper


class HomeViewTests(UserSetupMixin, TestCase):
    """
    Tests for home view.
    """
    def setUp(self):
        super(HomeViewTests, self).setUp()
        self.home_url = reverse('home')

    def test_anonymous(self):
        """
        Test that home URL redirects to admin login for unauthenticated users.
        """
        response = self.client.get(self.home_url, follow=True)
        login_url = ''.join([reverse('admin:login'), '?next=', reverse('admin:index')])
        self.assertRedirects(response, login_url)

    def test_authenticated_student(self):
        """
        Test that home URL redirects to admin login for authenticated students.
        """
        self.student_login()
        response = self.client.get(self.home_url, follow=True)
        login_url = ''.join([reverse('admin:login'), '?next=', reverse('admin:index')])
        self.assertRedirects(response, login_url)

    def test_authenticated_admin(self):
        """
        Test that home URL redirects to admin for authenticated admins.
        """
        self.admin_login()
        response = self.client.get(self.home_url, follow=True)
        self.assertRedirects(response, reverse('admin:index'))


class LPDViewTests(UserSetupMixin, TestCase):
    """
    Tests for LPDView.
    """
    def setUp(self):
        super(LPDViewTests, self).setUp()
        self.lpd = LearnerProfileDashboardFactory(name='Test LPD')
        self.lpd_url = self.lpd.get_absolute_url()

    def test_anonymous_existing(self):
        """
        Test that URL targeting existing LPD redirects to admin login for unauthenticated users.
        """
        response = self.client.get(self.lpd_url)
        login_url = ''.join([reverse('admin:login'), '?next=', self.lpd_url])
        self.assertRedirects(response, login_url)

    def test_authenticated_existing(self):
        """
        Test that authenticated users can access URL targeting existing LPD.
        """
        # Check access for authenticated student.
        self.student_login()
        response = self.client.get(self.lpd_url)
        self.assertEqual(response.status_code, 200)

        # Reset state
        self.client.logout()

        # Check access for authenticated admin.
        self.admin_login()
        response = self.client.get(self.lpd_url)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_non_existent(self):
        """
        Test that URL targeting non-existent LPD redirects to admin login for unauthenticated users.
        """
        non_existent_lpd = LearnerProfileDashboardFactory(name='Ghost LPD')
        non_existent_lpd_url = non_existent_lpd.get_absolute_url()
        non_existent_lpd.delete()
        response = self.client.get(non_existent_lpd_url)
        login_url = ''.join([reverse('admin:login'), '?next=', non_existent_lpd_url])
        self.assertRedirects(response, login_url)

    @silence_request_warnings
    def test_authenticated_non_existent(self):
        """
        Test that authenticated users can access URL targeting non-existent LPD.
        """
        non_existent_lpd = LearnerProfileDashboardFactory(name='Ghost LPD')
        non_existent_lpd_url = non_existent_lpd.get_absolute_url()
        non_existent_lpd.delete()

        # Check access for authenticated student.
        self.student_login()
        response = self.client.get(non_existent_lpd_url)
        self.assertEqual(response.status_code, 404)

        # Reset state
        self.client.logout()

        # Check access for authenticated student.
        self.admin_login()
        response = self.client.get(non_existent_lpd_url)
        self.assertEqual(response.status_code, 404)


@freeze_time("2019-05-16 09:51:30")
class LPDExportViewTests(UserSetupMixin, TestCase):
    """
    Tests for LPDExportView.
    """

    def setUp(self):
        super(LPDExportViewTests, self).setUp()
        lpd = LearnerProfileDashboardFactory(name='Test LPD')
        self.lpd_export_url = reverse('lpd:export', kwargs={'pk': lpd.pk})

    def test_anonymous_existing(self):
        """
        Test that export URL targeting existing LPD redirects to admin login for unauthenticated users.
        """
        response = self.client.get(self.lpd_export_url)
        login_url = ''.join([reverse('admin:login'), '?next=', self.lpd_export_url])
        self.assertRedirects(response, login_url)

    @override_settings(
        USE_REMOTE_STORAGE=False,
        MEDIA_ROOT='/tmp/learner-profile-dashboard/media'
    )
    def test_authenticated_existing(self):
        """
        Test that authenticated users can access export URL targeting existing LPD.
        """
        # Check access for authenticated student.
        self.student_login()
        response = self.client.get(self.lpd_export_url)
        self.assertEqual(response.status_code, 200)

        # Reset state
        self.client.logout()

        # Check access for authenticated admin.
        self.admin_login()
        response = self.client.get(self.lpd_export_url)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_non_existent(self):
        """
        Test that export URL targeting non-existent LPD redirects to admin login for unauthenticated users.
        """
        non_existent_lpd = LearnerProfileDashboardFactory(name='Ghost LPD')
        non_existent_lpd_export_url = reverse('lpd:export', kwargs={'pk': non_existent_lpd.pk})
        non_existent_lpd.delete()
        response = self.client.get(non_existent_lpd_export_url)
        login_url = ''.join([reverse('admin:login'), '?next=', non_existent_lpd_export_url])
        self.assertRedirects(response, login_url)

    @silence_request_warnings
    def test_authenticated_non_existent(self):
        """
        Test that authenticated users can access URL targeting non-existent LPD.
        """
        non_existent_lpd = LearnerProfileDashboardFactory(name='Ghost LPD')
        non_existent_lpd_export_url = reverse('lpd:export', kwargs={'pk': non_existent_lpd.pk})
        non_existent_lpd.delete()

        # Check access for authenticated student.
        self.student_login()
        response = self.client.get(non_existent_lpd_export_url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed('export/errors/lpd.html')

        # Reset state
        self.client.logout()

        # Check access for authenticated student.
        self.admin_login()
        response = self.client.get(non_existent_lpd_export_url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed('export/errors/lpd.html')

    @override_settings(
        USE_REMOTE_STORAGE=False,
        MEDIA_ROOT='/tmp/learner-profile-dashboard/media'
    )
    def test_get_pdf_creation_successful(self):
        """
        Test that successful PDF creation results in response containing PDF,
        and database containing record of PDF export requested by learner.
        """
        self.student_login()

        # Verify initial set of PDF export records
        pdf_exports = models.LPDExport.objects.all()
        self.assertEqual(pdf_exports.count(), 0)

        # Request PDF export
        response = self.client.get(self.lpd_export_url)

        # Verify expectations about reponse
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="2019-05-16T095130_learner-profile.pdf"'
        )

        # Verify set of PDF export records
        pdf_exports = models.LPDExport.objects.all()
        self.assertEqual(pdf_exports.count(), 1)

    def test_get_pdf_creation_unsuccessful(self):
        """
        Test that unsuccessful PDF creation results in 400 response.
        """
        self.student_login()

        with patch('lpd.views.pisa.CreatePDF') as patched_create_pdf:
            type(patched_create_pdf.return_value).err = PropertyMock(return_value=True)

            response = self.client.get(self.lpd_export_url)

            self.assertEqual(response.status_code, 400)
            self.assertTemplateUsed('export/errors/lpd-export.html')


@ddt.ddt
class QuestionViewTests(UserSetupMixin, TestCase):
    """
    Tests for QuestionViews.
    """
    def setUp(self):
        super(QuestionViewTests, self).setUp()
        self.qualitative_question = QualitativeQuestionFactory()
        self.multiple_choice_question = MultipleChoiceQuestionFactory()
        self.ranking_question = RankingQuestionFactory()
        self.likert_scale_question = LikertScaleQuestionFactory()

    @property
    def questions(self):
        """
        Return list of default questions that are available to each test in this class.
        """
        return [
            self.qualitative_question,
            self.multiple_choice_question,
            self.ranking_question,
            self.likert_scale_question,
        ]

    def test_anonymous_existing(self):
        """
        Test that URL targeting existing question redirects to admin login for unauthenticated users.
        """
        for question in self.questions:
            question_url = question.get_absolute_url()
            response = self.client.get(question_url)
            login_url = ''.join([reverse('admin:login'), '?next=', question_url])
            self.assertRedirects(response, login_url)

    def test_authenticated_existing(self):
        """
        Test that authenticated users can access URL targeting existing question.
        """
        for question in self.questions:
            question_url = question.get_absolute_url()

            # Check access for authenticated student.
            self.student_login()
            response = self.client.get(question_url)
            self.assertEqual(response.status_code, 200)

            # Reset state
            self.client.logout()

            # Check access for authenticated admin.
            self.admin_login()
            response = self.client.get(question_url)
            self.assertEqual(response.status_code, 200)

    @ddt.data(
        QualitativeQuestionFactory,
        MultipleChoiceQuestionFactory,
        RankingQuestionFactory,
        LikertScaleQuestionFactory,
    )
    def test_anonymous_non_existent(self, question_factory):
        """
        Test that URL targeting non-existent question redirects to admin login for unauthenticated users.
        """
        lpd = LearnerProfileDashboardFactory(name='Ghost LPD')
        section = SectionFactory(lpd=lpd, title='Ghost section')
        non_existent_question = question_factory(section=section, question_text='Ghost question')
        non_existent_question_url = non_existent_question.get_absolute_url()
        non_existent_question.delete()
        response = self.client.get(non_existent_question_url)
        login_url = ''.join([reverse('admin:login'), '?next=', non_existent_question_url])
        self.assertRedirects(response, login_url)

    @ddt.data(
        QualitativeQuestionFactory,
        MultipleChoiceQuestionFactory,
        RankingQuestionFactory,
        LikertScaleQuestionFactory,
    )
    @silence_request_warnings
    def test_authenticated_non_existent(self, question_factory):
        """
        Test that authenticated users can access URL targeting non-existent question.
        """
        lpd = LearnerProfileDashboardFactory(name='Ghost LPD')
        section = SectionFactory(lpd=lpd, title='Ghost section')
        non_existent_question = question_factory(section=section, question_text='Ghost question')
        non_existent_question_url = non_existent_question.get_absolute_url()
        non_existent_question.delete()

        # Check access for authenticated student.
        self.student_login()
        response = self.client.get(non_existent_question_url)
        self.assertEqual(response.status_code, 404)

        # Reset state
        self.client.logout()

        # Check access for authenticated student.
        self.admin_login()
        response = self.client.get(non_existent_question_url)
        self.assertEqual(response.status_code, 404)


# pylint: disable=too-many-instance-attributes,attribute-defined-outside-init
@freeze_time("2019-04-23 07:21:30")
class LPDSubmitViewTests(UserSetupMixin, TestCase):
    """
    Tests for LPDSubmitView.
    """

    def setUp(self):
        super(LPDSubmitViewTests, self).setUp()
        self.section = SectionFactory()
        self.student_login()
        self.data = {
            'section_id': self.section.pk,
            'qualitative_answers': json.dumps([]),
            'quantitative_answers': json.dumps([]),
        }
        self.default_qualitative_answers = [
            {
                'question_id': 1,
                'answer_text': 'This is a very clever answer.',
            },
            {
                'question_id': 2,
                'answer_text': 'This is not a very clever answer, but an answer nonetheless.',
            }
        ]
        self.default_quantitative_answers = [
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

    def _create_qualitative_questions(self, questions_influence_group_membership=False):
        """
        Create a set of qualitative questions to use for tests that verify processing of qualitative data.
        """
        self.qualitative_question1 = QualitativeQuestionFactory(
            id=1, section=self.section, influences_group_membership=questions_influence_group_membership
        )
        self.qualitative_question2 = QualitativeQuestionFactory(
            id=2, section=self.section, influences_group_membership=questions_influence_group_membership
        )

    def _create_quantitative_questions(self):
        """
        Create a set of quantitative questions to use for tests that verify processing of quantitative data.
        """
        self.quantitative_question1 = MultipleChoiceQuestionFactory(id=1, section=self.section)
        self.quantitative_question2 = MultipleChoiceQuestionFactory(id=2, section=self.section)
        self.quantitative_question3 = RankingQuestionFactory(id=3, section=self.section, number_of_options_to_rank=5)

    def _create_knowledge_components(self):
        """
        Create a set of knowledge components to use for tests that verify processing
        of qualitative and quantitative data.
        """
        self.group_knowledge_component1 = KnowledgeComponentFactory(
            kc_id='test_group_kc1', kc_name='Group KC 1', lpd=self.section.lpd
        )
        self.group_knowledge_component2 = KnowledgeComponentFactory(
            kc_id='test_group_kc2', kc_name='Group KC 2', lpd=self.section.lpd
        )
        self.group_knowledge_component3 = KnowledgeComponentFactory(
            kc_id='test_group_kc3', kc_name='Group KC 3', lpd=self.section.lpd
        )

        # Note that group probabilities do not need to sum up to 1.
        self.group_probabilities = {
            self.group_knowledge_component1.kc_id: 0.1,
            self.group_knowledge_component2.kc_id: 0.9,
            self.group_knowledge_component3.kc_id: 0.7,
        }

        self.knowledge_component1 = KnowledgeComponentFactory(kc_id='test_kc1', kc_name='KC 1')
        self.knowledge_component2 = KnowledgeComponentFactory(kc_id='test_kc2', kc_name='KC 2')
        self.knowledge_component3 = KnowledgeComponentFactory(kc_id='test_kc3', kc_name='KC 3')

    def _create_answer_options(self, influences_recommendations=True, link_knowledge_components=True):
        """
        Create a set of knowledge components to use for tests that verify processing of quantitative data.
        """
        self.answer_option1 = models.AnswerOption.objects.create(
            id=1,
            content_object=self.quantitative_question1,
            knowledge_component=self.knowledge_component1 if link_knowledge_components else None,
            influences_recommendations=influences_recommendations,
            allows_custom_input=False,
        )
        self.answer_option2 = models.AnswerOption.objects.create(
            id=2,
            content_object=self.quantitative_question2,
            knowledge_component=self.knowledge_component2 if link_knowledge_components else None,
            influences_recommendations=influences_recommendations,
            allows_custom_input=True,
        )
        self.answer_option3 = models.AnswerOption.objects.create(
            id=3,
            content_object=self.quantitative_question3,
            knowledge_component=self.knowledge_component3 if link_knowledge_components else None,
            influences_recommendations=influences_recommendations,
            allows_custom_input=False,
        )

    @property
    def _qualitative_answer_data(self):
        """
        Return default answer data for qualitative questions.
        """
        return (
            (self.qualitative_question1, 'This is a very clever answer.'),
            (self.qualitative_question2, 'This is not a very clever answer, but an answer nonetheless.'),
        )

    @property
    def _quantitative_answer_data(self):
        """
        Return default answer data for quantitative questions.
        """
        return (
            (self.answer_option1, 1, None),
            (self.answer_option2, 0, 'Yellow'),
            (self.answer_option3, 5, None),
        )

    @property
    def _qualitative_score_data(self):
        """
        Return default score data for quantitative questions.
        """
        expected_scores = {
            kc_id: 1.0 - value
            for kc_id, value in self.group_probabilities.items()
        }

        return (
            (self.group_knowledge_component1, expected_scores[self.group_knowledge_component1.kc_id]),
            (self.group_knowledge_component2, expected_scores[self.group_knowledge_component2.kc_id]),
            (self.group_knowledge_component3, expected_scores[self.group_knowledge_component3.kc_id]),
        )

    @property
    def _quantitative_score_data(self):
        """
        Return default score data for quantitative questions.
        """
        return (
            (self.knowledge_component1, 0),
            (self.knowledge_component2, 1),
            (self.knowledge_component3, 0.8),
        )

    def _create_default_data(self):
        """
        Create data for default LPD for tests in this class.
        """
        self._create_qualitative_questions(questions_influence_group_membership=True)
        self._create_quantitative_questions()
        self._create_knowledge_components()
        self._create_answer_options(
            influences_recommendations=True, link_knowledge_components=True
        )

    def _create_additional_lpd(self):  # pylint: disable=no-self-use
        """
        Create LPD that is completely separate from default LPD for tests in this class.
        """
        lpd = LearnerProfileDashboardFactory()
        section = SectionFactory(lpd=lpd)

        qualitative_questions = (
            QualitativeQuestionFactory(section=section) for _ in range(2)
        )
        quantitative_questions = (
            MultipleChoiceQuestionFactory(section=section),
            MultipleChoiceQuestionFactory(section=section),
            RankingQuestionFactory(section=section),
        )

        knowledge_components = (
            KnowledgeComponentFactory(
                kc_id='additional_test_kc{n}'.format(n=n),
                kc_name='Additional Test KC {n}'.format(n=n)
            ) for n in range(3)
        )

        answer_options = (
            models.AnswerOption.objects.create(
                content_object=quantitative_question,
                knowledge_component=knowledge_component,
                influences_recommendations=True,
            )
            for quantitative_question in quantitative_questions
            for knowledge_component in knowledge_components
        )

        return {
            'section': section,
            'qualitative_questions': qualitative_questions,
            'quantitative_questions': quantitative_questions,
            'knowledge_components': knowledge_components,
            'answer_options': answer_options,
        }

    def _assert_qualitative_answer_data(self):
        """
        Assert that appropriate qualitative answers exist for each qualitative question
        in the set of default qualitative questions (as defined by `_qualitative_answer_data`).
        """
        qualitative_answers = models.QualitativeAnswer.objects.all()
        self.assertEqual(qualitative_answers.count(), 2)

        for question, expected_answer in self._qualitative_answer_data:
            answer = qualitative_answers.get(question=question)
            self.assertEqual(answer.learner, self.student_user)
            self.assertEqual(answer.text, expected_answer)

    def _assert_quantitative_answer_data(self):
        """
        Assert that appropriate quantitative answers exist for each qualitative question
        in the set of default quantitative questions (as defined by `_quantitative_answer_data`).
        """
        quantitative_answers = models.QuantitativeAnswer.objects.all()
        self.assertEqual(quantitative_answers.count(), 3)

        for answer_option, expected_value, expected_custom_input in self._quantitative_answer_data:
            answer = quantitative_answers.get(answer_option=answer_option)
            self.assertEqual(answer.learner, self.student_user)
            self.assertEqual(answer.value, expected_value)
            self.assertEqual(answer.custom_input, expected_custom_input)

    def _assert_qualitative_score_data(self, scores):
        """
        Assert that appropriate scores exist for each knowledge component
        in the set of default knowledge components (as defined by `_quantitative_score_data`).
        """
        for knowledge_component, expected_score in self._qualitative_score_data:
            score = scores.get(knowledge_component=knowledge_component)
            self.assertEqual(score.learner, self.student_user)
            self.assertAlmostEqual(score.value, expected_score)

    def _assert_quantitative_score_data(self, scores):
        """
        Assert that appropriate scores exist for each knowledge component
        in the set of default knowledge components (as defined by `_quantitative_score_data`).
        """
        for knowledge_component, expected_score in self._quantitative_score_data:
            score = scores.get(knowledge_component=knowledge_component)
            self.assertEqual(score.learner, self.student_user)
            self.assertEqual(score.value, expected_score)

    def _assert_submission_data(self):
        """
        Assert that submission data matches expectations.
        """
        submissions = models.Submission.objects.all()
        self.assertEqual(submissions.count(), 1)

        submission = models.Submission.objects.get()
        self.assertEqual(submission.section, self.section)
        self.assertEqual(submission.learner, self.student_user)

    def _assert_last_update(
            self, content, expected_profile_percentage, expected_section_percentage
    ):
        """
        Assert that `content` includes expected information about most recent submission.
        """
        last_update = content['last_update']
        timestamp = last_update['timestamp']
        completion_percentages = last_update['completion_percentages']
        self.assertEqual(timestamp, 1556004090)  # Apr 23rd, 2019, 03:21:34
        self.assertEqual(
            completion_percentages, {
                'profile': expected_profile_percentage,
                'section': expected_section_percentage,
            }
        )

    def test_post_invalid_section(self):
        """
        Test that `post` method returns appropriate response if target section does not exist.
        """
        with patch('lpd.views.Section.objects.get') as patched_section_get:
            patched_section_get.side_effect = models.Section.DoesNotExist
            response = self.client.post(reverse('lpd:submit'), self.data)
            message = json.loads(response.content)['message']
            self.assertEqual(response.status_code, 500)
            self.assertEqual(message, 'Target section does not exist.')

    def test_post_invalid_answers(self):
        """
        Test that `post` method returns appropriate response if processing answer data fails.
        """
        # Processing qualitative answers fails
        with patch('lpd.views.LPDSubmitView._process_qualitative_answers') as patched_process_qual_answers:
            patched_process_qual_answers.side_effect = IntegrityError
            response = self.client.post(reverse('lpd:submit'), self.data)
            message = json.loads(response.content)['message']
            self.assertEqual(response.status_code, 500)
            self.assertEqual(message, 'Could not update learner answers.')

        # Processing quantitative answers fails
        with patch('lpd.views.LPDSubmitView._process_quantitative_answers') as patched_process_quant_answers, \
                patch('lpd.views.LPDSubmitView._process_qualitative_answers') as patched_process_qual_answers:
            patched_process_quant_answers.side_effect = IntegrityError
            response = self.client.post(reverse('lpd:submit'), self.data)
            message = json.loads(response.content)['message']
            self.assertEqual(response.status_code, 500)
            self.assertEqual(message, 'Could not update learner answers.')

    def test_post_score_transmission_fails(self):
        """
        Test that `post` method returns appropriate response
        if transmitting scores to adaptive engine fails.
        """
        with patch('lpd.views.LPDSubmitView._process_quantitative_answers'), \
                patch('lpd.views.LPDSubmitView._process_qualitative_answers'), \
                patch('lpd.views.AdaptiveEngineAPIClient.send_learner_data') as patched_send_learner_data:
            patched_send_learner_data.side_effect = ConnectionError
            response = self.client.post(reverse('lpd:submit'), self.data)
            message = json.loads(response.content)['message']
            self.assertEqual(response.status_code, 500)
            self.assertEqual(message, 'Could not transmit scores to adaptive engine.')

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
        content = json.loads(response.content)
        message = content['message']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(message, 'Learner answers updated successfully.')
        self._assert_last_update(content, '0%', '0%')

    @patch('lpd.client.AdaptiveEngineAPIClient.send_learner_data')
    @patch('lpd.views.LPDSubmitView._process_quantitative_answers')
    @patch('lpd.views.LPDSubmitView._process_qualitative_answers')
    def test_post_valid_data_connection_error(
            self, patched_process_qual_answers, patched_process_quant_answers, patched_send_learner_data
    ):
        """
        Test that `post` method returns appropriate response if sending learner data to adaptive engine fails.
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

        - Skip group membership calculation.
        - Not attempt to send any data to the adaptive engine.
        - Update submission data.
        - Return completion percentages for section and parent LPD.
        """
        qualitative_answers = []
        self.data['qualitative_answers'] = json.dumps(qualitative_answers)

        response = self.client.post(reverse('lpd:submit'), self.data)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)

        qualitative_answers = models.QualitativeAnswer.objects.all()
        self.assertEqual(qualitative_answers.count(), 0)

        scores = models.Score.objects.all()
        self.assertEqual(scores.count(), 0)

        # Make sure group membership calculation was skipped
        patched_update_scores.assert_not_called()
        # Make sure no learner data was sent to adaptive engine
        patched_send_learner_data.assert_not_called()
        # Make sure submission data was updated
        self._assert_submission_data()
        # Make sure response contains appropriate completion percentages
        self._assert_last_update(content, '0%', '0%')

    @patch('lpd.models.QualitativeQuestion.update_scores')
    @patch('lpd.client.AdaptiveEngineAPIClient.send_learner_data')
    @patch('lpd.views.LPDSubmitView._process_quantitative_answers', new=MagicMock(return_value=[]))
    def test_post_qual_answers_no_influence(self, patched_send_learner_data, patched_update_scores):
        """
        Test that `post` behaves correctly if qualitative answers are not set up to influence group membership.

        In this case, `post` should:

        - Skip group membership calculation.
        - Not attempt to send any data to the adaptive engine.
        - Update submission data.
        - Return completion percentages for section and parent LPD.
        """
        self._create_qualitative_questions(questions_influence_group_membership=False)
        self._create_knowledge_components()

        self.data['qualitative_answers'] = json.dumps(self.default_qualitative_answers)

        response = self.client.post(reverse('lpd:submit'), self.data)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)

        self._assert_qualitative_answer_data()

        scores = models.Score.objects.all()
        self.assertEqual(scores.count(), 0)

        # Make sure group membership calculation was skipped
        patched_update_scores.assert_not_called()
        # Make sure no learner data was sent to adaptive engine
        patched_send_learner_data.assert_not_called()
        # Make sure submission data was updated
        self._assert_submission_data()
        # Make sure response contains appropriate information about most recent submission
        self._assert_last_update(content, '100%', '100%')

    @patch('lpd.models.calculate_probabilities')
    @patch('lpd.client.AdaptiveEngineAPIClient.send_learner_data')
    @patch('lpd.views.LPDSubmitView._process_quantitative_answers', new=MagicMock(return_value=[]))
    def test_post_qualitative_answers(self, patched_send_learner_data, patched_calculate_probabilities):
        """
        Test that `post` correctly processes qualitative answers.
        """
        self._create_qualitative_questions(questions_influence_group_membership=True)
        self._create_knowledge_components()

        patched_calculate_probabilities.return_value = self.group_probabilities

        self.data['qualitative_answers'] = json.dumps(self.default_qualitative_answers)

        response = self.client.post(reverse('lpd:submit'), self.data)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)

        scores = models.Score.objects.all()
        self.assertEqual(scores.count(), 3)

        # Check answers individually
        self._assert_qualitative_answer_data()

        # Check scores individually
        self._assert_qualitative_score_data(scores)

        # Make sure correct set of scores was passed to method for sending learner data to adaptive engine
        patched_send_learner_data.assert_called_once_with(self.student_user, list(scores))

        # Make sure submission data was updated
        self._assert_submission_data()

        # Make sure response contains appropriate information about most recent submission
        self._assert_last_update(content, '100%', '100%')

    @patch('lpd.views.LPDSubmitView._process_quantitative_answers', new=MagicMock(return_value=[]))
    def test_post_qual_answers_split_answers(self):
        """
        Test that `post` correctly processes qualitative answers
        consisting of comma-separated lists of values.
        """
        qualitative_question1 = QualitativeQuestionFactory(section=self.section, split_answer=False)
        qualitative_question2 = QualitativeQuestionFactory(section=self.section, split_answer=True)

        qualitative_answers = [
            {
                'question_id': 1,
                'answer_text': 'This is a very clever answer, I must say.',
            },
            {
                'question_id': 2,
                'answer_text': 'This is not a very clever answer, but an answer nonetheless.',
            }
        ]
        self.data['qualitative_answers'] = json.dumps(qualitative_answers)

        response = self.client.post(reverse('lpd:submit'), self.data)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)

        qualitative_answers = models.QualitativeAnswer.objects.all()
        self.assertEqual(qualitative_answers.count(), 3)

        # Check answers individually
        qualitative_question1_answers = qualitative_answers.filter(question=qualitative_question1)
        self.assertEqual(qualitative_question1_answers.count(), 1)

        qualitative_question1_answer = qualitative_question1_answers.get()
        self.assertEqual(qualitative_question1_answer.learner, self.student_user)
        self.assertEqual(qualitative_question1_answer.text, 'This is a very clever answer, I must say.')

        qualitative_question2_answers = qualitative_answers.filter(question=qualitative_question2)
        self.assertEqual(qualitative_question2_answers.count(), 2)

        for qualitative_question2_answer, expected_text in zip(
                qualitative_question2_answers, ['This is not a very clever answer', 'but an answer nonetheless.']
        ):
            self.assertEqual(qualitative_question2_answer.learner, self.student_user)
            self.assertEqual(qualitative_question2_answer.text, expected_text)

        # Make sure response contains appropriate information about most recent submission
        self._assert_last_update(content, '100%', '100%')

    @patch('lpd.client.AdaptiveEngineAPIClient.send_learner_data')
    @patch('lpd.views.LPDSubmitView._process_qualitative_answers', new=MagicMock(return_value=[]))
    def test_post_quant_answer_not_meaningful(self, patched_send_learner_data):
        """
        Test that `post` correctly processes quantitative answer whose value is not meaningful.

        When dealing with values that are not meaningful:

        - No answers or scores should be created.
        - No data should be sent to the adaptive engine.
        - A `Submission` should be created/updated to record the event.
        - Completion percentages for section and parent LPD should be returned.

        The only question type for which `post` might receive a value that is not meaningful (i.e., `None`)
        is `QuestionTypes.LIKERT`. See `QuantitativeQuestion.get_answer_value` for details.
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
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)

        quantitative_answers = models.QuantitativeAnswer.objects.all()
        self.assertEqual(quantitative_answers.count(), 0)

        scores = models.Score.objects.all()
        self.assertEqual(scores.count(), 0)

        # Make sure no learner data was sent to adaptive engine
        patched_send_learner_data.assert_not_called()
        # Make sure submission data was updated
        self._assert_submission_data()
        # Make sure response contains appropriate information about most recent submission
        self._assert_last_update(content, '0%', '0%')

    @patch('lpd.client.AdaptiveEngineAPIClient.send_learner_data')
    @patch('lpd.views.LPDSubmitView._process_qualitative_answers', new=MagicMock(return_value=[]))
    def test_post_quant_answers_meaningful(self, patched_send_learner_data):
        """
        Test that `post` correctly processes quantitative answers whose values are meaningful.

        When dealing with values that are meaningful
        and corresponding answer options are configured to influence recommendations,
        appropriate answers and scores should be created,
        a `Submission` should be created/updated to record the event,
        and completion percentages for section and parent LPD should be returned.
        """
        self._create_quantitative_questions()
        self._create_knowledge_components()
        self._create_answer_options(influences_recommendations=True, link_knowledge_components=True)

        self.data['quantitative_answers'] = json.dumps(self.default_quantitative_answers)

        response = self.client.post(reverse('lpd:submit'), self.data)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)

        scores = models.Score.objects.all()
        self.assertEqual(scores.count(), 3)

        # Check answers individually
        self._assert_quantitative_answer_data()

        # Check scores individually
        self._assert_quantitative_score_data(scores)

        # Make sure correct set of scores was passed to method for sending learner data to adaptive engine
        patched_send_learner_data.assert_called_once_with(self.student_user, list(scores))

        # Make sure submission data was updated
        self._assert_submission_data()

        # Make sure response contains appropriate information about most recent submission
        self._assert_last_update(content, '33%', '33%')

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
        should be created/updated to record the event,
        and completion percentages for section and parent LPD should be returned.
        """
        self._create_quantitative_questions()
        self._create_knowledge_components()
        self._create_answer_options(influences_recommendations=False, link_knowledge_components=True)

        self.data['quantitative_answers'] = json.dumps(self.default_quantitative_answers)

        response = self.client.post(reverse('lpd:submit'), self.data)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)

        scores = models.Score.objects.all()
        self.assertEqual(scores.count(), 0)

        # Check answers individually
        self._assert_quantitative_answer_data()

        # Make sure no learner data was sent to adaptive engine
        patched_send_learner_data.assert_not_called()
        # Make sure submission data was updated
        self._assert_submission_data()
        # Make sure response contains appropriate information about most recent submission
        self._assert_last_update(content, '33%', '33%')

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
        should be created/updated to record the event,
        and completion percentages for section and parent LPD should be returned.
        """
        self._create_quantitative_questions()
        self._create_answer_options(influences_recommendations=True, link_knowledge_components=False)

        self.data['quantitative_answers'] = json.dumps(self.default_quantitative_answers)

        response = self.client.post(reverse('lpd:submit'), self.data)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)

        scores = models.Score.objects.all()
        self.assertEqual(scores.count(), 0)

        # Check answers individually
        self._assert_quantitative_answer_data()

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

        # Make sure response contains appropriate information about most recent submission
        self._assert_last_update(content, '33%', '33%')

    @patch('lpd.models.calculate_probabilities')
    @patch('lpd.client.AdaptiveEngineAPIClient.send_learner_data')
    def test_post_multiple_lpds(self, patched_send_learner_data, patched_calculate_probabilities):
        """
        Test that `post` does not touch multiple LPDs.
        """
        # Create default data
        self._create_default_data()

        patched_calculate_probabilities.return_value = self.group_probabilities

        self.assertEqual(models.LearnerProfileDashboard.objects.count(), 1)
        self.assertEqual(models.Section.objects.count(), 1)

        # Create another LPD
        additional_lpd = self._create_additional_lpd()

        self.assertEqual(models.LearnerProfileDashboard.objects.count(), 2)
        self.assertEqual(models.Section.objects.count(), 2)

        # Prepare submission data
        self.data['qualitative_answers'] = json.dumps(self.default_qualitative_answers)
        self.data['quantitative_answers'] = json.dumps(self.default_quantitative_answers)

        # Submit data
        response = self.client.post(reverse('lpd:submit'), self.data)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)

        # Check answers individually
        self._assert_qualitative_answer_data()
        self._assert_quantitative_answer_data()

        # Check scores
        scores = models.Score.objects.all()
        self.assertEqual(scores.count(), 6)

        # Check scores individually
        self._assert_qualitative_score_data(scores)
        self._assert_quantitative_score_data(scores)

        # Make sure correct set of scores was passed to method for sending learner data to adaptive engine
        patched_send_learner_data.assert_called_once_with(self.student_user, list(scores))

        # Make sure submission data was updated
        self._assert_submission_data()

        # Make sure response contains appropriate information about most recent submission
        self._assert_last_update(content, '60%', '60%')

        # Make sure that no answers, scores, or submissions exist for additional LPD
        for qualitative_question in additional_lpd['qualitative_questions']:
            self.assertEqual(qualitative_question.learner_answers.count(), 0)

        for answer_option in additional_lpd['answer_options']:
            self.assertEqual(answer_option.learner_answers.count(), 0)

        for knowledge_component in additional_lpd['knowledge_components']:
            self.assertEqual(knowledge_component.scores.count(), 0)

        self.assertEqual(additional_lpd['section'].submissions.count(), 0)
