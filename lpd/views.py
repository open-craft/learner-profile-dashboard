import json
import logging

from django.http import JsonResponse
from django.views.generic import DetailView, ListView, CreateView, UpdateView
from django.views.generic.base import TemplateView, View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator

from lpd.constants import QuestionTypes
from lpd.models import (
    AnswerOption,
    LearnerProfileDashboard,
    LearnerProfileDashboardForm,
    RankingQuestion,
    QualitativeAnswer,
    QualitativeQuestion,
    QuantitativeAnswer,
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
        Persist learner answers to LPD questions.
        """
        user = User.objects.get(username=request.user.username)
        qualitative_answers = json.loads(request.POST.get('qualitative_answers'))
        quantitative_answers = json.loads(request.POST.get('quantitative_answers'))

        log.info('Attempting to update answers for user {user}.'.format(user=user))
        log.info('Request data (qualitative answers): {data}'.format(data=qualitative_answers))
        log.info('Request data (quantitative answers): {data}'.format(data=quantitative_answers))

        try:
            self._process_qualitative_answers(user, qualitative_answers)
            self._process_quantitative_answers(user, quantitative_answers)
        except Exception as e:  # pylint: disable=broad-except
            log.error(
                'The following exception occurred when trying to process answers for user {user}: {exception}'.format(
                    user=user, exception=e
                )
            )
            response = JsonResponse({'message': 'Could not update learner answers.'}, status=500)
        else:
            response = JsonResponse({'message': 'Learner answers updated successfully.'})
        return response

    @classmethod
    def _process_qualitative_answers(cls, user, qualitative_answers):
        """
        Create or update `QualitativeAnswer` for current learner, for each qualitative answer in request.
        """
        for qualitative_answer in qualitative_answers:
            question_id = qualitative_answer.get('question_id')
            question = QualitativeQuestion.objects.get(id=question_id)
            text = qualitative_answer.get('answer_text')
            log.info(
                'Creating or updating answer from user {user} for question {question}. '
                'New text: {text}'.format(
                    user=user, question=question, text=text
                )
            )
            QualitativeAnswer.objects.update_or_create(
                learner=user,
                question=question,
                defaults=dict(
                    text=text
                ),
            )

    @classmethod
    def _process_quantitative_answers(cls, user, quantitative_answers):
        """
        Create or update `QuantitativeAnswer` for current learner, for each quantitative answer in request.
        """
        for quantitative_answer in quantitative_answers:
            question_type = quantitative_answer.get('question_type')
            answer_option_id = quantitative_answer.get('answer_option_id')
            answer_option = AnswerOption.objects.get(id=answer_option_id)
            value = quantitative_answer.get('answer_option_value')
            custom_input = quantitative_answer.get('answer_option_custom_input')
            if value is None:
                if question_type == QuestionTypes.RANKING:
                    value = RankingQuestion.unranked_option_value()
                elif question_type == QuestionTypes.LIKERT:
                    # If learner did not select a value for an answer to a Likert scale question,
                    # we simply consider it unanswered.
                    continue
            answer_data = dict(value=value)
            if custom_input:
                answer_data['custom_input'] = custom_input
            log.info(
                'Creating or updating answer from user {user} for answer option {answer_option}. '
                'New data: {data}'.format(
                    user=user, answer_option=answer_option, data=answer_data
                )
            )
            QuantitativeAnswer.objects.update_or_create(
                learner=user,
                answer_option=answer_option,
                defaults=answer_data,
            )


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
