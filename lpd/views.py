"""
Views for Learner Profile Dashboard
"""

import json
import logging
import pprint
import traceback

from django.http import JsonResponse
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.views.generic.base import TemplateView, View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.decorators import method_decorator
from requests import ConnectionError

from lpd.client import AdaptiveEngineAPIClient
from lpd.models import (
    AnswerOption,
    LearnerProfileDashboard,
    LearnerProfileDashboardForm,
    QualitativeAnswer,
    QualitativeQuestion,
    QuantitativeAnswer,
    QuantitativeQuestion,
    Score,
    Section,
    Submission,
)
from lpd.templatetags.lpd_tags import get_last_update


# Globals

log = logging.getLogger(__name__)


# Classes

class LPDView(TemplateView):
    """
    Display LPD to learner.
    """
    template_name = 'view.html'

    def get_context_data(self, **kwargs):
        """
        Collect necessary information for displaying LPD.
        """
        context = super(LPDView, self).get_context_data(**kwargs)
        learner = User.objects.get(username=self.request.user.username)
        lpd = LearnerProfileDashboard.objects.first()
        context['learner'] = learner
        context['lpd'] = lpd
        return context


class LPDSubmitView(View):
    """
    Handle answer submissions from LPD.
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        """
        Persist learner answers to LPD questions, send up-to-date learner data to adaptive engine,
        and update submission data.

        Note that we currently update submission data for *all* submissions,
        irrespective of the number of answers that they contain.
        In particular, we record the date and time of a submission
        even if the learner did not update any of their answers prior to clicking the submit button
        for a given section.
        """
        user = User.objects.get(username=request.user.username)
        qualitative_answers = json.loads(request.POST.get('qualitative_answers'))
        quantitative_answers = json.loads(request.POST.get('quantitative_answers'))

        log.info('Attempting to update answers for user %s.', user)
        log.info('Request data (qualitative answers):\n%s', pprint.pformat(qualitative_answers))
        log.info('Request data (quantitative answers):\n%s', pprint.pformat(quantitative_answers))

        # Process answer data
        try:
            group_scores = self._process_qualitative_answers(user, qualitative_answers)
            answer_scores = self._process_quantitative_answers(user, quantitative_answers)
        except Exception:  # pylint: disable=broad-except
            log.error(
                'The following exception occurred when trying to process answers for user %s:\n%s',
                user,
                traceback.format_exc()
            )
            return JsonResponse({'message': 'Could not update learner answers.'}, status=500)
        else:
            log.info('Answers successfully updated for user %s.', user)

        # Send learner data to adaptive engine
        scores = group_scores + answer_scores
        if scores:
            try:
                AdaptiveEngineAPIClient.send_learner_data(user, scores)
            except ConnectionError:
                log.error(
                    'The following exception occurred when trying to transmit scores for user %s:\n%s',
                    user,
                    traceback.format_exc()
                )
                return JsonResponse({'message': 'Could not transmit scores to adaptive engine.'}, status=500)
            else:
                log.info('Scores successfully transmitted to adaptive engine for user %s.', user)

        # Update submission data
        section_id = request.POST.get('section_id')
        try:
            last_update = self._process_submission(user, section_id)
        except Section.DoesNotExist:
            log.error(
                'The following exception occurred when trying to update submission data for user %s:\n%s',
                user,
                traceback.format_exc()
            )
            return JsonResponse({'message': 'Could not update submission data.'}, status=500)
        else:
            log.info('Submission data successfully updated for user %s and section %s.', user, section_id)

        return JsonResponse({
            'message': 'Learner answers updated successfully.',
            'last_update': last_update,
        })

    @classmethod
    def _process_qualitative_answers(cls, user, qualitative_answers):
        """
        Process `qualitative_answers` from `user`.

        This involves:

         - Creating/updating one or more `QualitativeAnswer`s for `user`, for each qualitative answer in request.
         - Creating/updating `Score` records for `user` and appropriate knowledge components,
           using all relevant `QualitativeAnswer`s submitted so far by the `user`
           (check models.QualitativeQuestion.update_scores() for details).

        Return up-to-date `Score` records for further processing.
        """
        update_group_membership = False
        for qualitative_answer in qualitative_answers:
            question_id = qualitative_answer.get('question_id')
            question = QualitativeQuestion.objects.get(id=question_id)
            text = qualitative_answer.get('answer_text')

            log.info(
                'Creating or updating answer from user %s for %s. New text: %s',
                user, question, text
            )

            # Delete existing answers to make sure we don't end up keeping obsolete parts around
            QualitativeAnswer.objects.filter(learner=user, question=question).delete()

            answer_components = question.get_answer_components(text)

            log.info(
                'Answer components to store as separate answers (%d):\n%s',
                len(answer_components),
                pprint.pformat(answer_components)
            )

            for answer_component in answer_components:
                QualitativeAnswer.objects.create(
                    learner=user,
                    question=question,
                    text=answer_component,
                )

            if not update_group_membership and question.influences_group_membership:
                update_group_membership = True

        # Update scores iff learner changed their answer to one or more qualitative questions
        # that are configured to influence recommendations.
        if update_group_membership:
            return QualitativeQuestion.update_scores(learner=user)

        return []

    @classmethod
    def _process_quantitative_answers(cls, user, quantitative_answers):
        """
        Process `quantitative_answers` from `user`.

        For each quantitative answer from request, this involves:

        - Creating/updating a `QuantitativeAnswer` for `user` and appropriate answer option.
        - Creating/updating a `Score` for `user` and appropriate knowledge component.

        Notes:

        - Both of these steps only happen if we can extract a meaningful value
          from a given quantitative answer. If that's not the case
          (i.e., if value is `None`), the answer will be skipped.
        - The second step only happens if a given quantitative answer is associated with an answer option that
          - is configured to influence recommendations.
          - is linked to a knowledge component.

        Return up-to-date `Score` records for further processing.
        """
        scores = []
        for quantitative_answer in quantitative_answers:
            # Extract relevant information about answer
            question_type = quantitative_answer.get('question_type')
            answer_option_id = quantitative_answer.get('answer_option_id')
            raw_value = quantitative_answer.get('answer_option_value')
            custom_input = quantitative_answer.get('answer_option_custom_input')

            # Get answer value to store and compute score from
            answer_value = QuantitativeQuestion.get_answer_value(question_type, raw_value)

            if answer_value is None:
                continue

            # We have a meaningful `answer_value`, so fetch answer option that answer belongs to from DB
            answer_option = AnswerOption.objects.get(id=answer_option_id)

            # Create or update answer for answer option
            cls._update_or_create_answer(user, answer_option, answer_value, custom_input)
            # Create or update score for adaptive engine
            score = cls._update_or_create_score(user, question_type, answer_option, answer_value)

            if score is not None:
                scores.append(score)

        return scores

    @classmethod
    def _update_or_create_answer(cls, user, answer_option, answer_value, custom_input):
        """
        Create or update `QuantitativeAnswer` for `user` and `answer_option`,
        taking into account `answer_value` and `custom_input`.

        Note that this method should only be called
        if `answer_value` is meaningful (i.e., if it is not `None`).
        """
        answer_data = dict(value=answer_value)
        if custom_input is not None:
            answer_data['custom_input'] = custom_input

        log.info(
            'Creating or updating answer from user %s for %s. New data:\n%s',
            user,
            answer_option,
            pprint.pformat(answer_data)
        )

        QuantitativeAnswer.objects.update_or_create(
            learner=user,
            answer_option=answer_option,
            defaults=answer_data,
        )

    @classmethod
    def _update_or_create_score(cls, user, question_type, answer_option, answer_value):
        """
        Create or update `Score` for `user` and knowledge component associated with `answer_option`, and return it.

        Note that this method should only be called
        if `answer_value` is meaningful (i.e., if it is not `None`).
        """
        score = None
        if answer_option.influences_recommendations:
            knowledge_component = answer_option.knowledge_component
            if knowledge_component:
                score = QuantitativeQuestion.get_score(question_type, answer_value)
                score_data = dict(value=score)

                log.info(
                    'Creating or updating score for user %s for %s.\n'
                    '- Answer value: %s.\n'
                    '- Score: %s',
                    user,
                    answer_option,
                    answer_value,
                    score
                )

                score, _ = Score.objects.update_or_create(
                    knowledge_component=knowledge_component,
                    learner=user,
                    defaults=score_data
                )
            else:
                log.error('Could not create score because %s is not linked to a knowledge component.', answer_option)
        return score

    @classmethod
    def _process_submission(cls, user, section_id):
        """
        Update date and time at which `user` last submitted section identified by `section_id`
        and return it.
        """
        section = Section.objects.get(id=section_id)
        submission, _ = Submission.objects.update_or_create(
            section=section,
            learner=user,
            defaults={
                'updated': timezone.now()
            }
        )
        log.info('Date and time of latest submission: %s.', submission.updated.strftime('%m/%d/%Y at %I:%M %p (UTC)'))
        return get_last_update(section, user)


class LearnerProfileDashboardViewMixin(object):
    """
    Mixin for CRUD views for Learner Profile Dashboard.
    """
    model = LearnerProfileDashboard
    form_class = LearnerProfileDashboardForm


class ListLearnerProfileDashboardView(LearnerProfileDashboardViewMixin, ListView):
    """
    View for listing Learner Profile Dashboard instances.
    """
    template_name = 'list.html'
    paginate_by = 12
    paginate_orphans = 2


class ShowLearnerProfileDashboardView(LearnerProfileDashboardViewMixin, DetailView):
    """
    View for showing Learner Profile Dashboard instance.
    """
    template_name = 'show.html'


class CreateLearnerProfileDashboardView(LearnerProfileDashboardViewMixin, CreateView):
    """
    View for creating Learner Profile Dashboard instance.
    """
    template_name = 'edit.html'

    '''Login required for all posts'''
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        return super(CreateLearnerProfileDashboardView, self).post(request, *args, **kwargs)


class UpdateLearnerProfileDashboardView(LearnerProfileDashboardViewMixin, UpdateView):
    """
    View for updating Learner Profile Dashboard instance.
    """
    template_name = 'edit.html'

    '''Login required for all posts'''
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        return super(UpdateLearnerProfileDashboardView, self).post(request, *args, **kwargs)
