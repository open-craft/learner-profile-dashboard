# -*- coding: utf-8 -*-

"""
URLs for Learner Profile Dashboard
"""

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'lpd'

urlpatterns = [
    url(r'^$', login_required(views.LPDView.as_view()), name='home'),
    url(r'^submit$', login_required(views.LPDSubmitView.as_view()), name='submit'),
    url(r'^list$', views.ListLearnerProfileDashboardView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)$', views.ShowLearnerProfileDashboardView.as_view(), name='view'),
    url(r'^add$', views.CreateLearnerProfileDashboardView.as_view(), name='add'),
    url(r'^(?P<pk>\d+)/edit$', views.UpdateLearnerProfileDashboardView.as_view(), name='edit'),
]
