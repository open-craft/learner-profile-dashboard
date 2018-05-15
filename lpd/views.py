import json
import logging

from django.http import JsonResponse
from django.views.generic import DetailView, ListView, CreateView, UpdateView
from django.views.generic.base import TemplateView, View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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
)


# Globals

log = logging.getLogger(__name__)


# Classes

class LPDView(TemplateView):
    """
    Display LPD.
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
        Persist learner answers to LPD questions, and send up-to-date learner data to adaptive engine.
        """
        user = User.objects.get(username=request.user.username)
        qualitative_answers = json.loads(request.POST.get('qualitative_answers'))
        quantitative_answers = json.loads(request.POST.get('quantitative_answers'))

        log.info('Attempting to update answers for user %s', user)
        log.info('Request data (qualitative answers): %s', qualitative_answers)
        log.info('Request data (quantitative answers): %s', quantitative_answers)

        # Process answer data
        try:
            group_scores = self._process_qualitative_answers(user, qualitative_answers)
            answer_scores = self._process_quantitative_answers(user, quantitative_answers)
        except Exception as e:  # pylint: disable=broad-except
            log.error('The following exception occurred when trying to process answers for user %s: %s', user, e)
            return JsonResponse({'message': 'Could not update learner answers.'}, status=500)
        else:
            log.info('Answers successfully updated for user %s', user)

        # Send learner data to adaptive engine
        try:
            AdaptiveEngineAPIClient.send_learner_data(user, group_scores+answer_scores)
        except ConnectionError as e:
            log.error('The following exception occurred when trying to transmit scores for user %s: %s', user, e)
            return JsonResponse({'message': 'Could not transmit scores to adaptive engine.'}, status=500)
        else:
            log.info('Scores successfully transmitted to adaptive engine for user %s', user)
            return JsonResponse({'message': 'Learner answers updated successfully.'})

    @classmethod
    def _process_qualitative_answers(cls, user, qualitative_answers):
        """
        Process `qualitative_answers` from `user`.

        This involves:

         - Creating/updating a `QualitativeAnswer` for `user`, for each qualitative answer in request.
         - Creating/updating `Score` records for `user` and appropriate knowledge components,
           using all of the `QualitativeAnswer`s submitted so far by the `user`
           (check models.QualitativeQuestion.update_scores() for details).

        Return up-to-date `Score` records for further processing.
        """
        for qualitative_answer in qualitative_answers:
            question_id = qualitative_answer.get('question_id')
            question = QualitativeQuestion.objects.get(id=question_id)
            text = qualitative_answer.get('answer_text')
            log.info(
                'Creating or updating answer from user %s for question %s. New text: %s',
                user, question, text
            )
            QualitativeAnswer.objects.update_or_create(
                learner=user,
                question=question,
                defaults=dict(
                    text=text
                ),
            )

        return QualitativeQuestion.update_scores(learner=user)

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

            # Get value to store and compute score from
            value = QuantitativeQuestion.get_value(question_type, raw_value)

            if value is None:
                continue

            # We have a meaningful `value`, so fetch answer option that answer belongs to from DB
            answer_option = AnswerOption.objects.get(id=answer_option_id)

            # Create or update answer for answer option
            cls._update_or_create_answer(user, answer_option, value, custom_input)
            # Create or update score for adaptive engine
            score = cls._update_or_create_score(user, question_type, answer_option, value)

            if score is not None:
                scores.append(score)

        return scores

    @classmethod
    def _update_or_create_answer(cls, user, answer_option, value, custom_input):
        """
        Create or update `QuantitativeAnswer` for `user` and `answer_option`,
        taking into account `value` and `custom_input`.

        Note that this method should only be called
        if `value` is meaningful (i.e., if it is not `None`).
        """
        answer_data = dict(value=value)
        if custom_input is not None:
            answer_data['custom_input'] = custom_input

        log.info(
            'Creating or updating answer from user %s for answer option %s. New data: %s',
            user, answer_option, answer_data
        )

        QuantitativeAnswer.objects.update_or_create(
            learner=user,
            answer_option=answer_option,
            defaults=answer_data,
        )

    @classmethod
    def _update_or_create_score(cls, user, question_type, answer_option, value):
        """
        Create or update `Score` for `user` and knowledge component associated with `answer_option`, and return it.

        Note that this method should only be called
        if `value` is meaningful (i.e., if it is not `None`).
        """
        score = None
        if answer_option.influences_recommendations:
            knowledge_component = answer_option.knowledge_component
            if knowledge_component:
                score_value = QuantitativeQuestion.get_score(question_type, value)
                score_data = dict(value=score_value)
                score, _ = Score.objects.update_or_create(
                    knowledge_component=knowledge_component,
                    learner=user,
                    defaults=score_data
                )
            else:
                log.error('Could not create score because %s is not linked to a knowledge component.', answer_option)
        return score


class LearnerProfileDashboardView(object):
    model = LearnerProfileDashboard
    form_class = LearnerProfileDashboardForm


class ShowLearnerProfileDashboardView(LearnerProfileDashboardView, DetailView):
    template_name = 'view.html'


class ListLearnerProfileDashboardView(LearnerProfileDashboardView, ListView):
    template_name = 'list.html'
    paginate_by = 12
    paginate_orphans = 2


class CreateLearnerProfileDashboardView(LearnerProfileDashboardView, CreateView):
    template_name = 'edit.html'

    '''Login required for all posts'''
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        return super(CreateLearnerProfileDashboardView, self).post(request, *args, **kwargs)


class UpdateLearnerProfileDashboardView(LearnerProfileDashboardView, UpdateView):
    template_name = 'edit.html'

    '''Login required for all posts'''
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        return super(UpdateLearnerProfileDashboardView, self).post(request, *args, **kwargs)
