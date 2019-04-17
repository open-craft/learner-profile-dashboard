# -*- coding: utf-8 -*-

"""
URLs for Learner Profile Dashboard
"""

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from lpd import views


app_name = 'lpd'

urlpatterns = [
    url(r'^submit$', login_required(views.LPDSubmitView.as_view()), name='submit'),
    url(r'^(?P<pk>\d+)$', login_required(views.LPDView.as_view()), name='view'),
    url(
        r'^q_qualitative/(?P<pk>\d+)$',
        login_required(views.QualitativeQuestionView.as_view()),
        name='qualitative-question'
    ),
    url(
        r'^q_mcq/(?P<pk>\d+)$',
        login_required(views.MultipleChoiceQuestionView.as_view()),
        name='multiple-choice-question'
    ),
    url(
        r'^q_ranking/(?P<pk>\d+)$',
        login_required(views.RankingQuestionView.as_view()),
        name='ranking-question'
    ),
    url(
        r'^q_likert/(?P<pk>\d+)$',
        login_required(views.LikertScaleQuestionView.as_view()),
        name='likert-scale-question'
    ),
]
